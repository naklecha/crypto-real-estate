from flask import Flask, jsonify, request, session 
from flask_restful import Resource, Api
from pymongo import MongoClient

# ------------------------------------------------------

# Flask app
app = Flask(__name__)
app.secret_key = 'i love white chocolate'
api = Api(app)

# ------------------------------------------------------

# Connecting to the WT2 collection
client = MongoClient('localhost', 27017)
db = client['WT2']
nickname = db['nickname']
land_record = db['land_record']

# ------------------------------------------------------

class getxy(Resource):
    def get(self):
        req = eval(request.data)
        try: # region - 1,2,3,4 clockwise
            find = land_record.find_one({"region": req["region"],"x": req["x"],"y": req["y"]})
            find.pop('_id')
            print(find)
            return find,200
        except:
            return {},400
    def post(self):
        req = eval(request.data)
        try:
            myquery = {"region": req["region"],"x": req["x"],"y": req["y"]}
            newvalues ={ "$set":  { "nickname": req["nickname"], "status":req["status"],"price":req["price"]}}
            land_record.update_one(myquery, newvalues)
            check = land_record.find_one({"region": req["region"],"x": req["x"],"y": req["y"]})
            if(check==None):
                raise Exception
            return "Success" 
        except:
            return {},400

api.add_resource(getxy, '/getxy')

# ------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

# ------------------------------------------------------