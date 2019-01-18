from flask import Flask, render_template, url_for
from flask import request, redirect, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from DB_Setup import *
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import os
import random
import datetime
import string
import json
import httplib2
import requests
# Import login_required from login_decorator.py
from login_addon import login_mandatory

# Create Flask instance

app = Flask(__name__)


# Connect client_id

client_id = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
app_name = "item-catalog"


# Connect to database
engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=False')
Base.metadata.bind = engine
# Create session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# GConnect


@app.route('/gconnect', methods=['POST'])
def googleConnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Get authorization code
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)

    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, cancell.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the right google account.
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps("user ID doesn't match previously given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps('''Token's client ID does not match
            app's client ID.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    saved_access_token = login_session.get('access_token')
    saved_google_id = login_session.get('google_id')
    if saved_access_token is not None and google_id == saved_google_id:
        response = make_response(json.dumps('''Current user is
        already logged in.'''), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # save the access token in the session for future refrence.
    login_session['access_token'] = access_token
    login_session['google_id'] = google_id

    # Get account info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    info = answer.json()

    login_session['username'] = info['name']
    login_session['picture'] = info['picture']
    login_session['email'] = info['email']

    # check if account exists, if it doesn't create new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = newUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome</h1> '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '''style = "width: 300px; height: 300px;border-radius:
        150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'''
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Extra Functions


def newUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# LOGOUT - Remove a current user's token and restart their login_session


@app.route('/logout')
def googleDisconnect():
        # Only logout a logged in user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not logged in.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    output = h.request(url, 'GET')[0]
    if output['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['google_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = redirect(url_for('Home'))
        flash("You are now logged out.")
        return response
    else:
        # if the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# Home


@app.route('/')
@app.route('/home/')
def Home():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Items).order_by(desc(Items.date)).limit(5)
    return render_template('home.html', categories=categories, items=items)

# Display a Category's Items


@app.route('/<path:category_name>/')
def viewCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category=category).all()
    print (items)
    count = session.query(Items).filter_by(category=category).count()
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_items.html',
                               category_name=category.name,
                               categories=categories,
                               items=items,
                               count=count)
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template('Items.html',
                               category=category.name,
                               categories=categories,
                               items=items,
                               count=count,
                               user=user)

# Display an Items info


@app.route('/<path:category_name>/<path:item_name>/')
@app.route('/home/<path:category_name>/<path:item_name>/')
def viewItem(category_name, item_name):
    item = session.query(Items).filter_by(name=item_name).one_or_none()
    creator = getUserInfo(item.user_id)
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_iteminfo.html',
                               item=item,
                               category=category_name,
                               categories=categories,
                               creator=creator)
    else:
        return render_template('item_info.html',
                               item=item,
                               category=category_name,
                               categories=categories,
                               creator=creator)


# Add an item


@app.route('/add/', methods=['GET', 'POST'])
@login_mandatory
def createItem():
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = Items(
            name=request.form['name'],
            description=request.form['description'],
            picture=request.form['picture'],
            category=session.query(Category).filter_by(name=request.form
                                                       ['category']).one(),
            date=datetime.datetime.now(),
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Item Successfully Created!')
        return redirect(url_for('Home'))
    else:
        return render_template('Create_Items.html',
                               categories=categories,)

# Edit an item


@app.route('/edit/<path:item_name>/', methods=['GET', 'POST'])
@app.route('/home/edit/<path:item_name>/', methods=['GET', 'POST'])
@login_mandatory
def editItem(item_name):
    changedItem = session.query(Items).filter_by(name=item_name).one_or_none()
    categories = session.query(Category).all()
    # check if the logged in user is the owner of item
    creator = getUserInfo(changedItem.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this item. This item belongs to %s"
              % creator.name)
        return redirect(url_for('Home'))
    # POST methods
    if request.method == 'POST':
        if request.form['name']:
            changedItem.name = request.form['name']
        if request.form['description']:
            changedItem.description = request.form['description']
        if request.form['picture']:
            changedItem.picture = request.form['picture']
        if request.form['category']:
            category = session.query(Category).filter_by(name=request.form
                                                         ['category']).one()
            changedItem.category = category
        time = datetime.datetime.now()
        changedItem.date = time
        session.add(changedItem)
        session.commit()
        flash('Category Item Successfully Edited!')
        return redirect(url_for('viewCategory',
                                category_name=changedItem.category.name))
    else:
        return render_template('Edit_Items.html',
                               item=changedItem,
                               categories=categories)

# Delete an item
session = DBSession()


@app.route('/delete/<path:item_name>/',
           methods=['GET', 'POST'])
@login_mandatory
def removeItem(item_name):
    deletedItem = session.query(Items).filter_by(name=item_name).one_or_none()
    categories = session.query(Category).all()
    # check if the logged in user is the owner of item
    creator = getUserInfo(deletedItem.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot delete this item. This item belongs to %s"
              % creator.name)
        return redirect(url_for('Home'))
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash('Item Successfully Deleted! '+deletedItem.name)
        return redirect(url_for('Home'))
    else:
        return render_template('Delete_Items.html',
                               item=deletedItem)


# JSON


@app.route('/home/JSON')
def allItemsJSON():
    categories = session.query(Category).all()
    category_dict = [c.serialize for c in categories]
    for c in range(len(category_dict)):
        items = [i.serialize for i in session.query(Items)
                 .filter_by(category_id=category_dict[c]["id"]).all()]
        if items:
            category_dict[c]["Item"] = items
    return jsonify(Category=category_dict)


@app.route('/home/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/home/items/JSON')
def itemsJSON():
    items = session.query(Items).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/home/<path:category_name>/items/JSON')
def categoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/home/<path:category_name>/<path:item_name>/JSON')
def ItemJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(name=item_name,
                                           category=category).one()
    return jsonify(items=[items.serialize])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
