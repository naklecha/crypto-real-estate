from flask import *
from flask_restful import Resource, Api
from pymongo import MongoClient
import requests
from web3 import Web3
import time

rpc = "http://127.0.0.1:8545"

web3 = Web3(Web3.HTTPProvider(rpc))

PATH = "http://127.0.0.1:5000/"

# ------------------------------------------------------

# Flask app
app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')
app.secret_key = 'i love white chocolate'
api = Api(app)

# ------------------------------------------------------

abi = '[{"constant":true,"inputs":[],"name":"check","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"wallet","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"landCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"land_record","outputs":[{"name":"region","type":"uint256"},{"name":"x","type":"uint256"},{"name":"y","type":"uint256"},{"name":"owner","type":"address"},{"name":"price","type":"uint256"},{"name":"status","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"region","type":"uint256"},{"name":"x","type":"uint256"},{"name":"y","type":"uint256"}],"name":"initLand","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"funds","type":"uint256"}],"name":"addFunds","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"doneInit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"login","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"landid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"buyLand","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"landid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"sellLand","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
contract_addr = "0x8fDd21C593c5693788E0248b4C86bB66375f8dA7"
contract = web3.eth.contract(address=contract_addr, abi=abi)

# ------------------------------------------------------

class home(Resource):
    def get(self):
        return make_response(render_template('homepage.html'),200,{'Content-Type': 'text/html'})
api.add_resource(home, '/')

# ------------------------------------------------------

class regions(Resource):
    def get(self):
        if("signedin" in session and session["signedin"]):
            return make_response(render_template('regions.html'),200,{'Content-Type': 'text/html'})
        else:
            return make_response(render_template('message.html',message="Please login to access marketplace."),400,{'Content-Type': 'text/html'})
api.add_resource(regions, '/regions')

# ------------------------------------------------------

class grid(Resource):
    def get(self,reg):
        if("signedin" in session and session["signedin"]):
            return make_response(render_template('grid.html', region=reg),200,{'Content-Type': 'text/html'})
        else:
            return make_response(render_template('message.html',message="Please login to access marketplace."),400,{'Content-Type': 'text/html'})
api.add_resource(grid, '/grid/<reg>')

# ------------------------------------------------------

def calculateowner(reg, pub, sign):
    ret = []
    for i in range(1,101):
        t = contract.caller().land_record(100*(int(reg)-1)+i)
        if(t[3] == pub and sign):
            ret.append(1)
        elif(t[-1] == 1):
            ret.append(2)
        else:
            ret.append(0)
    return ret

@app.route("/checkowner/<reg>", methods=["GET"])
def checkowner(reg):
    def eventStream(pub, sign):
        ret = calculateowner(reg, pub, sign)
        yield "event: message\ndata: %s\n\n" %(str(ret))
        while True:
            check = calculateowner(reg, pub, sign)
            if(ret != check):
                ret = check
                yield "event: message\ndata: %s\n\n" %(str(ret))
            time.sleep(2)
    return Response(eventStream(session["public"], ("signedin" in session) and session["signedin"]), mimetype="text/event-stream")

# ------------------------------------------------------

class getBalance(Resource):
    def get(self):
        if(session["signedin"]):
            return contract.caller().wallet(session["public"])
        else:
            return "Not logged in", 400
api.add_resource(getBalance,"/getBalance")

# ------------------------------------------------------

class xy(Resource):
    def get(self,id):
        s = contract.caller().land_record(int(id)+1)
        print(s)
        return s,200
api.add_resource(xy, '/xy/<id>')

# ------------------------------------------------------

class buy(Resource):
    def get(self, id, price):
        if("signedin" in session and session["signedin"]):
            try:
                transaction  = contract.functions.buyLand(int(id)+1,int(price)).buildTransaction()
                transaction['nonce'] = web3.eth.getTransactionCount(session["public"])
                transaction['gas'] = 3000000
                signed_tx = web3.eth.account.signTransaction(transaction, session["private"])
                tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
                return make_response(render_template('message.html',message="Bought item!"),400,{'Content-Type': 'text/html'})
            except:
                return make_response(render_template('message.html',message="Could not buy item."),400,{'Content-Type': 'text/html'})
        else:
            return make_response(render_template('message.html',message="Please login to buy land."),400,{'Content-Type': 'text/html'})
api.add_resource(buy, '/buy/<id>/<price>')

# ------------------------------------------------------

class sell(Resource):
    def get(self, id, price):
        if("signedin" in session and session["signedin"]):
            try:
                transaction  = contract.functions.sellLand(int(id)+1,int(price)).buildTransaction()
                transaction['nonce'] = web3.eth.getTransactionCount(session["public"])
                transaction['gas'] = 3000000
                signed_tx = web3.eth.account.signTransaction(transaction, session["private"])
                tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
                return make_response(render_template('message.html',message="Sold item!"),400,{'Content-Type': 'text/html'})
            except:
                return make_response(render_template('message.html',message="Could not sell item."),400,{'Content-Type': 'text/html'})
        else:
            return make_response(render_template('message.html',message="Please login to sell land."),400,{'Content-Type': 'text/html'})
api.add_resource(sell, '/sell/<id>/<price>')

# ------------------------------------------------------

class login(Resource):
    def post(self):
        #req = eval(request.data.decode())
        req = request.form
        try:
            public_key = req["public"]
            private_key = req["private"]
            #if(not contract.caller().cd(public_key)): return make_response(render_template('message.html',message="Account does not exist"),400,{'Content-Type': 'text/html'})
            transaction  = contract.functions.login().buildTransaction()
            transaction['nonce'] = web3.eth.getTransactionCount(public_key)
            transaction['gas'] = 3000000
            signed_tx = web3.eth.account.signTransaction(transaction, private_key)
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            session["signedin"] = True
            session["public"] = public_key
            session["private"] = private_key
            return redirect("/", code=303)
        except:
            return make_response(render_template('message.html',message="Wrong private key"),400,{'Content-Type': 'text/html'})
    def get(self):
        return make_response(render_template('login.html'),200,{'Content-Type': 'text/html'})
api.add_resource(login, '/login')

# ------------------------------------------------------

class logout(Resource):
    def get(self):
        session["signedin"] = False;
        return redirect("/", code=303)
api.add_resource(logout, '/logout')

# ------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

# ------------------------------------------------------