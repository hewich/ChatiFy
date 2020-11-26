from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash
# To set up mongo you have to install it via the command: $pip install pymongo
#db.py will contain logic to connecting to the database/ retrieving and pushing data to db

#create a mongo client passing url from account
from user import User

client = MongoClient("mongodb+srv://test:test@chatify.ldicp.mongodb.net/<dbname>?retryWrites=true&w=majority")

#find and connect to database ChatifyDB
chat_db = client.get_database("ChatifyDB")

#pass collection name of the database "ChatifyDB" which is "users" to store user data
users_collection = chat_db.get_collection("users")

#add rooms collections for database
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")

#create message collection
messages_collection = chat_db.get_collection("messages")


#define function to save user by username, email, password
#use username as primary key
def save_user(username, email, password):
    #create password hash to pass plaintext password for security purposes
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})

#making function call to pass user to data base
#save_user("emilio", "emi@gmail.com", "testing")

def get_user(username):
    user_data = users_collection.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None

#save a room by using rooms collection and passing required data
def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one({'name': room_name,
                                           'created_by': created_by, 'created_at': datetime.now()}).inserted_id

    # need room id to save admin to list of room members
    #add room member at a time
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
    return room_id

# function to add a room member
def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
    room_members_collection.insert_one({'_id': {'room_id': ObjectId( room_id), 'username': username},
                                        'room_name': room_name,'added_by': added_by, 'added_at': datetime.now(),
                                        'is_room_admin': is_room_admin})
# function to add members to a room
def add_room_members(room_id, room_name, usernames, added_by):
    # pass a list of dictionaries
    room_members_collection.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
          'added_at': datetime.now(), 'is_room_admin': False} for username in usernames])


# function to view a room
def get_room(room_id):
    return rooms_collection.find_one({'_id': ObjectId(room_id)})

def get_room_members(room_id):
    return list(room_members_collection.find({'_id.room_id': ObjectId(room_id)}))

# get rooms for a particular user
def get_rooms_for_user(username):
    return list(room_members_collection.find({'_id.username': username}))

# Function to determine if a person is a member of the room
def is_room_member(room_id, username):
    return room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})

#Function to check is a user is the admin of a room
def is_room_admin(room_id, username):
    return room_members_collection.count_documents(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})

# Function to update name of a room
def update_room(room_id, room_name):
    rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    room_members_collection.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name'}})

# Function to remove members of a room by providing a list of all the possible values of _id
def remove_room_members(room_id, usernames):
    room_members_collection.delete_many(
        {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})

# Function to save message by saving room id, sender of messages, and the text message
def save_message(room_id, text, sender):
    messages_collection.insert_one({'room_id': room_id, 'text': text, 'sender': sender, 'created_at': datetime.now()})


MESSAGE_FETCH_LIMIT = 3
# Fetch certain messages
def get_messages(room_id, page=0):

    offset = page * MESSAGE_FETCH_LIMIT
    messages = list(messages_collection.find({'room_id': room_id}).sort('_id', DESCENDING).limit(MESSAGE_FETCH_LIMIT).skip(offset))

    for message in messages:
        message['created_at'] = message['created_at'].strftime("%d %b, %H:%M")
        return messages[::-1]

