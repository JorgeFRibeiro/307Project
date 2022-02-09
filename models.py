from flask_login import UserMixin

# User model that stores information regarding the person logged in atm
# TODO: Connect to database, Make fields actually what we need, will require
#       edits to signup.html and auth.py for user field changes 

class User(UserMixin):

    # Some of these fields are required
    id = "hi"
    email = "hello@world.com"
    password = "World"
    name = "Bob"
    # End of warning