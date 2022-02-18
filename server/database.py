from logging import root
import mysql.connector
#python dotenv
# the password has to match in docker compose and here

mydb = mysql.connector.connect(
  host="mysql",
  user="test",
  password="password",
  db = "mydb"
)
print(mydb)