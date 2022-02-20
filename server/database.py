#python dotenv for environment variables
# the password has to match in docker compose and here
from pymongo import MongoClient
"""
to check out what is happening in the db follow these steps:

  1. run docker-compose up
  2. in terminal enter >>> docker ps
  3. >>> docker exec -it <paste image id of database> /bin/bash    ||| this can also be done with our web app
  4. >>> ls
  5. >>> mysql
  6. >>> show databases
  7. >>> 
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


print(mongo_client.list_database_names())
#chat_collection.insert()

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