#This is a demonstraition about flask using sqlalchemy
================================
##this app displays creats edits and delets items

#apps you need to have:

*python download link - https://www.python.org/downloads/

*terminal download link - https://git-scm.com/downloads

*virtualbox download link - https://www.virtualbox.org/wiki/Downloads

*vagrant download link - https://www.vagrantup.com/downloads.html

*full-stack-nanodegree repo download link - 

how to use:
move your folder to the full-stack-nanodegree repo after download
you "cd" into your folder then
run vagrant up once it loads you run
vagrant ssh once there you input this
command "cd /vagrant" then run python DB_Setup to create your DataBase
then run python DB_Init to populate your DataBase with data NOTE:IT WILL DELETE ALL DATA ON DATABASE BE CAREFUL!!!!!! 
then run python app.py
then on your web browser type localhost:5000 and you're all set
NOTE:THE DELETE AND EDIT BUTTONS SHOW UP IF YOU ARE THE CREATOR OF THE ITEM AND IF YOU ARE THE CREATOR YOU HAVE TO GO INTO THE ITEMS DETAILS!!!!!!	