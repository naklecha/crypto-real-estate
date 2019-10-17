from pymongo import MongoClient

# Connecting to the WT2 collection
client = MongoClient('localhost', 27017)
db = client['WT2']
nickname = db['nickname']
land_record = db['land_record']

for region in range(4):
    for x in range(64):
        for y in range(64):
            myquery = {"region": region,"x": x,"y": y, "nickname":"_empty", "price":0, "status": "no owner"}
            land_record.insert_one(myquery)