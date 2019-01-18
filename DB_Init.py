from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from DB_Setup import *

engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Delete Categories if exisitng.
session.query(Category).delete()
# Delete Items if exisitng.
session.query(Items).delete()
# Delete Users if exisitng.
session.query(User).delete()

# Create users
User1 = User(name="lorem iposum",
              email="nbaynom0@skype.com",
              picture='http://dummyimage.com/200x200.png/ff4444/ffffff')
session.add(User1)
session.commit()

User2 = User(name="lorem jposum",
             email="rgress1@t.co",
             picture='http://dummyimage.com/200x200.png/cc0000/ffffff')
session.add(User2)
session.commit()



# Create categories
Category1 = Category(name="Sports",
                      user_id=1)
session.add(Category1)
session.commit()



Category3 = Category(name="Gaming Consoles",
                      user_id=2)
session.add(Category3)
session.commit()


Category5 = Category(name="Computers",
                      user_id=1)
session.add(Category5)
session.commit()

# Populate a category with items
Item1 = Items(name="Football Boots",
               date=datetime.datetime.now(),
               description="Shoes to play football in.",
               picture="https://img-lon.snizl.com/offers/full/36332b6ab3489ef33121d8b1aee6d633a638698c.jpg",
               category_id=1,
               user_id=1)
session.add(Item1)
session.commit()

Item2 = Items(name="Basketball",
               date=datetime.datetime.now(),
               description="A Basketball.",
               picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT9n5ffO3xN_hBrK7eO1zlJNCmdGIq8dF88Yg2FR7b-PSEizGA-",
               category_id=1,
               user_id=1)
session.add(Item2)
session.commit()

Item3 = Items(name="Football",
               date=datetime.datetime.now(),
               description="A Football.",
               picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQjWcgkJmdTeXvz-ruCKbRONvYHMN2PVyObADlFK4-0sC9vttZ1dA",
               category_id=1,
               user_id=1)
session.add(Item3)
session.commit()

Item4 = Items(name="PS4",
               date=datetime.datetime.now(),
               description="The Next Gen Sony Console.",
               picture="https://psmedia.playstation.com/is/image/psmedia/ps4-gold-screen-03-eu-30may17?$MediaCarousel_SmallImage$",
               category_id=2,
               user_id=2)
session.add(Item4)
session.commit()

Item5 = Items(name="Xbox One",
               date=datetime.datetime.now(),
               description="The Next Gen Xbox Console.",
               picture="https://target.scene7.com/is/image/Target/GUEST_f832dbaa-0857-4545-8dab-dda53a9f236a?wid=488&hei=488&fmt=webp",
               category_id=2,
               user_id=2)
session.add(Item5)
session.commit()

Item6 = Items(name="Dell OptiPlex 3050 MT",
               date=datetime.datetime.now(),
               description="Now With An Intel Core i5, 4GB RAM And A 500GB HDD Running Ubuntu OS.",
               picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgHRZ8XYKCxSJPzHYDXLQiWvp125zJF1gegRYZntjCiJ4IFFOP",
               category_id=3,
               user_id=1)
session.add(Item6)
session.commit()

print ("Your database has been populated with data!")
