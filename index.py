from os import name
from re import U
from flask import Flask, render_template, jsonify, Response, request, session, url_for, redirect
import pymongo
import bcrypt
from bson import json_util
from bson.objectid import ObjectId

hostelP = Flask(__name__)

myClient = pymongo.MongoClient("mongodb://admin:qwe123@3.209.153.124:27017")
myDb = myClient["hostelpremiumdb"]
myCollection = myDb["Users"]

hostelP.secret_key = "qwe123"


@hostelP.route('/')
def index():
    return render_template('index.html')


@hostelP.route('/register', methods=['POST', 'GET'])
def register():

    message = ""

    if "email" in session:
        return redirect(url_for('hostArea'))

    if request.method == "POST":

        user = request.form.get("name")
        city = request.form.get("city")
        country = request.form.get("country")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        rol = request.form.get("rol")
        avatar = "https://www.aicad.es/profesorado-e-investigacion/img/anonimo.a5821669.jpg"

        user_found = myCollection.find_one({"name": user})
        email_found = myCollection.find_one({"email": email})


        #Validar que todos los campos este llenos correctamente
        if user == "" or city == "" or country == "" or email == "" or password1 == "" or password2 == "" or rol == "" or avatar == "":
            
            message = 'you must fill out the complete form'
            return render_template('register.html', message=message)
        
        #validacion de correo electronico, solo un correo por cuenta
        if email_found:

            message = 'This email already exists in database'
            return render_template('register.html', message=message)

        #Validacion de contraseña
        if password1 != password2:

            message = 'Passwords should match!'
            return render_template('register.html', message=message)

        else:

            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())

            user_input = {
                "name": user,
                "city": city,
                "country": country,
                "email": email,
                "password": hashed,
                "rol": rol,
                "avatar": avatar
            }

            myCollection.insert_one(user_input)

            return render_template("index.html")

    return render_template('register.html')


@hostelP.route('/login', methods=['POST', 'GET'])
def login():
    message = 'Please Login to your acount'

    if "email" in session:
        return redirect(url_for('hostArea'))
    
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        email_found = myCollection.find_one({"email": email})

        if email_found:

            email_val = email_found['email']
            passwordcheck = email_found['password'] 

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                
                session['email'] = email_val

                return redirect(url_for('hostArea'))

            else:
                if "email" in session:
                    return redirect(url_for('hostArea'))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)

    return render_template('login.html', message=message)

@hostelP.route('/logout')
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("index.html")
    else:
        return render_template('index.html')


@hostelP.route('/hostArea')
def hostArea():


    if "email" in session:
        email = session["email"] 

        

        return render_template('hostArea.html', email=email)
    else:
        return redirect(url_for("login"))


# @hostelP.route('/add_user', methods=['POST'])
# def add_user():
#     if request.method == 'POST':
#         dataUser = {
#             'name': request.form['name'],
#             'city': request.form['city'],
#             'country': request.form['country'],
#             'email': request.form['email'],
#             'password': request.form['password'],
#             'rol': request.form['rol'],
#             'avatar': "https://www.aicad.es/profesorado-e-investigacion/img/anonimo.a5821669.jpg"
#             #https://reqres.in/img/faces/9-image.jpg
#         }
        
#         result = myCollection.insert_one(dataUser)
    
#     return render_template('index.html')

@hostelP.route('/users')
def users():
    users = myCollection.find()
    response = users
    print(response)
    # return Response(response, mimetype='application/json')
    return render_template('users.html', allusers=response)


if __name__ == "__main__":
    hostelP.run(debug=True)
