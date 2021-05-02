from flask import Flask, render_template, jsonify, Response, request
import pymongo
from bson import json_util
from bson.objectid import ObjectId
from datetime import date

hostelP = Flask(__name__)

myClient = pymongo.MongoClient("mongodb://admin:qwe123@3.209.153.124:27017")
myDb = myClient["HostalPremiumDb"]
myCollection = myDb["Users"]

today = date.today



@hostelP.route('/')
def index():
    return render_template('index.html')


@hostelP.route('/register')
def register():
    return render_template('register.html')


@hostelP.route('/login')
def login():
    return render_template('login.html')


@hostelP.route('/hostArea')
def hostArea():
    return render_template('hostArea.html')


@hostelP.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        dataUser = {
            'name': request.form['name'],
            'city': request.form['city'],
            'country': request.form['country'],
            'email': request.form['email'],
            'password': request.form['password'],
            'rol': request.form['rol']
        }
        
        result = myCollection.insert_one(dataUser)
    
    return render_template('index.html')

@hostelP.route('/users')
def users():
    users = myCollection.find()
    response = users
    print(response)
    # return Response(response, mimetype='application/json')
    return render_template('users.html', allusers=response)


if __name__ == "__main__":
    hostelP.run(debug=True)
