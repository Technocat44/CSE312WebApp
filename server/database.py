#python dotenv for environment variables
# the password has to match in docker compose and here
import pymongo
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
mongo_client = pymongo.MongoClient("mongo")
db = mongo_client['cse312']
chat_collection = db['chat']
#print(mongo_client.list_database_names())
#chat_collection.insert()

mydict= {"username": "james", "message":"hello"}
x = chat_collection.insert_one(mydict)
