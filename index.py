from flask import Flask, render_template,request, session, url_for, redirect, send_from_directory
import os
import pymongo
import bcrypt
from bson.objectid import ObjectId

# UPLOAD_FOLDER = os.path.abspath("./static/img/usersProfile/")

hostelP = Flask(__name__)
hostelP.config["UPLOAD_FOLDER"] = './static/img/usersProfile/'

myClient = pymongo.MongoClient("mongodb://admin:qwe123@3.209.153.124:27017")
myDb = myClient["hostelpremiumdb"]
myCollection = myDb["Users"]

hostelP.secret_key = "qwe123"


@hostelP.route('/')
def index():
    return render_template('index.html')


#Registro y vadilaciones de nuevo usuario.
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
        phone = ""
        cellphone=""
        description=""


        
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
                "avatar": avatar,
                "phone": phone,
                "cellphone": cellphone,
                "description": description
            }

            myCollection.insert_one(user_input)

            return redirect(url_for('hostArea'))

    return render_template('register.html')

@hostelP.route('/updateuser/<email>', methods=['PUT'])
def updateuser(email):
    if "email" in session:
        email = session["email"]  

    user = request.form.get("name")
    city = request.form.get("city")
    email = request.form.get("email")
    country = request.form.get("country")
    phone = request.form.get("phone")
    cellphone = request.form.get("cellphone")
    description = request.form.get("description")

    if user and city and country and email:

        myCollection.update_one({'email': email}, {'$set':{
            "name": user,
            "city": city,
            "country": country,
            "email": email,
            "phone": phone,
            "cellphone": cellphone,
            "description": description
        }})

        return redirect(url_for("hostArea"))


#Validacion de datos de inicio de sesion.
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
                session['name']=email_found['name']

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


#Cerrar y eliminar datos de sesion
@hostelP.route('/logout')
def logout():
    if "email" in session:
        session.pop("email", None)
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


#Area principal de usuario
@hostelP.route('/hostArea')
def hostArea():

    if "email" in session:
        email = session["email"]
        result = {'email': email}
        user = myCollection.find_one(result)
        id_user = str(user['_id'])
        return render_template('hostArea.html', id = id_user, data_user=user)        
    else:
        return redirect(url_for("login"))


#LLenado de datos de perfil de usuario
@hostelP.route('/profile/<id>')
def profile(id):
    dataUser = myCollection.find_one({'_id': ObjectId(id)})
    response = []
    response.append({
        '_id':dataUser['_id'],
        'name':dataUser['name'],
        'city':dataUser['city'],
        'country':dataUser['country'],
        'email':dataUser['email'],
        'avatar':dataUser['avatar'],
        'phone':dataUser['phone'],
        'cellphone':dataUser['cellphone'],
        'description':dataUser['description']
    })

    return render_template("userProfile.html", data_user = response)

#Guardar cambio de datos de usuario
@hostelP.route('/editProfile/<id>', methods=["POST"])
def editprofile(id):
    name = request.form.get('name')
    phone = request.form.get('phone')
    description = request.form.get('description')
    city = request.form.get('city')
    country = request.form.get('country')
    cellphone = request.form.get('cellphone')
    
    myCollection.update_one({'_id': ObjectId(id)}, {"$set":{
        "name": name,
        "city": city,
        "country": country,
        "phone": phone,
        "cellphone": cellphone,
        "description": description
    }})
    return redirect(url_for("hostArea"))


#Formulario para cambio de Avatar
@hostelP.route('/avatar/<id>')
def avatar(id):
    dataUser = myCollection.find_one({'_id': ObjectId(id)})
    response = []
    response.append({
        '_id':dataUser['_id'],  
        'name':dataUser['name'],      
        'avatar':dataUser['avatar'],        
    })

    return render_template("avatar.html", data_user = response)


#Guardar cambio de imagen.
# @hostelP.route('/editAvatar/<id>', methods=["POST"])
# def editavatar(id):

    # avatar = request.files['avatarUser']
    # avatarU = avatar.filename
    # avatar.save(os.path.join(hostelP.config['UPLOAD_FOLDER'], avatarU))

    # myCollection.update_one({'_id': ObjectId(id)}, {'$set': {
    #     'avatar': avatarU
    # }})
    
    # return redirect(url_for("hostArea"))

    # f = request.files['avatarUser']
    # avatarUser = f.filename
    # f.save(os.path.join(hostelP.config["UPLOAD_FOLDER"], avatarUser))

    # myCollection.update_one({'_id': ObjectId(id)}, {"$set":{
    #     "avatar": avatarUser        
    # }})

    # return redirect(url_for("hostArea"))


    # if request.method == "POST":

    #     if "ourfile" not in request.files:
    #         message = "The form has no file part"
    #         # return redirect(url_for("avatar", message=message))

    #     f = request.files["ourfile"]

    #     if f.filename == "":
    #         message = "No file selected"
    #         # return redirect(url_for("avatar", message=message))

    #     filename = f.filename
    #     f.save(os.path.join(hostelP.config["UPLOAD_FOLDER"], filename))
    #     # return redirect(url_for("get_file", filename=filename))
    #     myCollection.update_one({'_id': ObjectId(id)}, {"$set":{
    #         'avatar': filename
    #     }})




# @hostelP.route('/avatar', methods=["GET", "POST"])
# def avatar():    
#     avatarUpload = ""       
    
#     if request.method == "POST":

#         if "ourfile" not in request.files:
#             message = "The form has no file part"
#             return redirect(url_for("avatar", message=message))

#         f = request.files["ourfile"]

#         if f.filename == "":
#             message = "No file selected"
#             return redirect(url_for("avatar", message=message))

#         filename = f.filename
#         f.save(os.path.join(hostelP.config["UPLOAD_FOLDER"], filename))
#         # return redirect(url_for("get_file", filename=filename))
#         myCollection.update_one({'email': email}, {"$SET":{
#             'avatar': filename
#         }})
#         return redirect(url_for('profile'))
        


#     if "email" in session:
#         email = session["email"]  
#         user = myCollection.find_one({'email': email})
#         response = user        
#         return render_template('avatar.html', email = email, data_user=response, avatar=avatarUpload)        
#     else:
#         return redirect(url_for("login"))



@hostelP.route('/avatar/<filename>')
def get_file(filename):
    return send_from_directory(hostelP.config["UPLOAD_FOLDER"], filename)


@hostelP.route('/users')
def users():
    users = myCollection.find()
    response = users
    print(response)
    return render_template('users.html', allusers=response)


if __name__ == "__main__":
    hostelP.run(debug=True, port=4000)
