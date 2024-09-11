import pymongo

# Create a MongoDB client
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Create a database
db = client["mydatabase"]

# Create a collection
collection = db["mycollection"]

# Insert data into the collection
collection.insert_one({"name": "John", "age": 30})

# Retrieve data from the collection
data = collection.find_one({"name": "John"})
print(data)