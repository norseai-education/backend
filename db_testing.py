from database import MongoDBHandler

db_handler = MongoDBHandler("mongodb://172.16.0.177:27019")
print("Connecting to database...\n")
db_handler.connect("amc8_database")
print("Connected to database...\n")

print(db_handler.list_collections())

# db_handler.clear_collection("math_related")
# test = db_handler.find_documents("math_related")
# print(test)

