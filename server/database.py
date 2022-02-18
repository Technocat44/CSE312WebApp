from logging import root
import mysql.connector


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="9Hannah14@$blink182",
  db = "users"
)
print(mydb)