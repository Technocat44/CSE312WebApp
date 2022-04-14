#python dotenv for environment variables
# https://docs.mongodb.com/manual/reference/method/db.collection.findOne/
# https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_update

from pymongo import MongoClient
from pymongo import ReturnDocument
"""
to check out what is happening in the db follow these steps:

  1. run docker-compose up
  2. in terminal enter >>> docker ps
  3. >>> docker exec -it <paste image id of database> /bin/bash    ||| this can also be done with our web app
  4. >>> ls
  5. >>> mongo
  6. >>> show dbs
  7. >>> use cse312
  8. >>> show collections
  9. >>> db.collection_name.find( {} ) /// this will show all documents in the collection
"""

"""
Database
Database is a physical container for collections. Each database gets its own set of files on the file system. 
A single MongoDB server typically has multiple databases.

Collection
Collection is a group of MongoDB documents. It is the equivalent of an RDBMS table. A collection exists within a 
single database. Collections do not enforce a schema. Documents within a collection can have different fields.
 Typically, all documents in a collection are of similar or related purpose.

Document
A document is a set of key-value pairs. Documents have dynamic schema. Dynamic schema means that documents in 
the same collection do not need to have the same set of fields or structure, and common fields in a collection's
 documents may hold different types of data.
"""
mongo_client = MongoClient("mongo")
db = mongo_client['cse312']

users_collection = db['users'] # one collection for users
users_id_collection = db["users_id"] # one collection for users ids
comment_and_image_name_from_html_collection = db["comment_image_name"] # a collection for uploaded comments and image names
xsrf_collection = db["tokens"] # a collection of xsrf token's created on homepage load
webchat_history = db["chat-history"]

#print(mongo_client.list_database_names())
#chat_collection.insert()
# we can store a comment and image name that a user sent as a request.
# if they only send a comment, the imageName will be None


def store_wehsocket_chat(user, message):
  webchat_history.insert_one({"username": user , "comment": message} )

def get_wehsocket_chat():
  allchat = webchat_history.find( {}, {"_id":0})
  return list(allchat)

def store_xsrf_token(token):
  xsrf_collection.insert_one({"token" : token})

def store_comment_and_image(comment: str, fileName: str):
  comment_and_image_name_from_html_collection.insert_one({"comment" : comment, "imageName" : fileName })

def store_comment_only(comment: str):
  comment_and_image_name_from_html_collection.insert_one({"comment": comment})

def verify_tokens():
  all_tokens = xsrf_collection.find( {}, {"_id":0} )
  return list(all_tokens)
  
# retreive all comments and image Names that have been posted by all users
def list_all_comments():
  all_comments = comment_and_image_name_from_html_collection.find( {} , {"_id": 0})
  return list(all_comments)

# when ever we need a new id, we go into our file collection
# find one document, (that's all we will have in this collection)
def get_next_id():
  id_object = users_id_collection.find_one({}) # retrieve the doc
  if id_object: # if there is one in there, grab the last id, convert to int, increment by 1 
    next_id = int(id_object["last_id"]) + 1 
    # update the record using the set command
    users_id_collection.update_one({}, {"$set": {"last_id": next_id}})
    return next_id # then reutnr 
  else: # if it doesn't exist this will make the first id
    users_id_collection.insert_one({"last_id": 1})
    return 1

# takes in a new user and creates them in the db
def create(user_dict):
  users_collection.insert_one(user_dict)
  user_dict.pop("_id")

# if we want to get soemthing out of the db, we don't want the _id, 
# give find another argument which says give me everything except the _id
# then use the list constructor to put all that data into a list
def list_all():
  all_users = users_collection.find({}, {"_id": 0})
  return list(all_users)

def retrieve_one(idNumber):
  oneUser = users_collection.find_one({"id":idNumber}, {"_id":0})
  print("this is in the db file, in retrieve_one functionthe response is: ", oneUser)
  # if the id does not exist, oneUser will equal null / None
  return oneUser

    # use userCollection.update({"id":idNumber}, {"$set": {"email":"<whatever is in the body>", "username":"<whatever is in the body>"}})
    # can update any field except the id!
def updateUser(userId, email, username):
  # update will either be None or an ObjectId. 
  update = users_collection.find_one_and_update({"id":userId},
                                       {"$set": {"email":email, "username": username}}, 
                                       {"_id":0},
                                       return_document= ReturnDocument.AFTER)
  print(f"this is the value of update. Could be None if the id does not exist, or the updated value == {str(update)}")
  return update

def deleteUser(userId):
  deleted = users_collection.delete_one({"id":userId})
  # deleted is an int, if it deleted the user it is 1 if it doesn't delete anything it'll be 0
  return deleted