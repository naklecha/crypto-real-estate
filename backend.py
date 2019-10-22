from flask import Flask, jsonify, request, session 
from flask_restful import Resource, Api
from pymongo import MongoClient
import requests

PATH = "http://127.0.0.1:5000/"

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

class xy(Resource):
    def get(self):
        req = eval(request.data)
        print(req)
        try: # region - 0,1,2,3 clockwise 
            # expecting {'region': 1, 'x': 1, 'y': 1}
            find = land_record.find_one({"region": req["region"],"x": req["x"],"y": req["y"]})
            find.pop('_id')
            print(find)
            return find,200
        except:
            return {},400
    def post(self):
        req = eval(request.data)
        try: # expecting req to be like {'region': 1, 'x': 1, 'y': 1, 'nickname': '_empty', 'price': 0, 'status': 'no owner'}
            myquery = {"region": req["region"],"x": req["x"],"y": req["y"]}
            newvalues ={ "$set":  { "nickname": req["nickname"], "status":req["status"],"price":req["price"]}}
            land_record.update_one(myquery, newvalues)
            check = land_record.find_one({"region": req["region"],"x": req["x"],"y": req["y"]})
            if(check==None):
                raise Exception
            return "Success" 
        except:
            return {},400

api.add_resource(xy, '/xy')

# ------------------------------------------------------

class buy(Resource):
    def post(self):
            req = eval(request.data) # expecting {'region': 1, 'x': 1, 'y': 1, 'nickname': '_empty', 'price': 100}
            print(req)
            getxy = requests.get(PATH+"xy",json = {"region": req["region"],"x": req["x"],"y": req["y"]})
            getxy = eval(getxy._content)
            print(getxy)
            if(getxy['price']<=req['price']):
                postxy = requests.post(PATH+"xy",json = {"region": req["region"],"x": req["x"],"y": req["y"], 'nickname': req['nickname'], 'price': req['price'], 'status': 'not for sale'})          
                return eval(postxy._content)
            else:
                return "Not enough funds", 400
api.add_resource(buy, '/buy')

# ------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

# ------------------------------------------------------