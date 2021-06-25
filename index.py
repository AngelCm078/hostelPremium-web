
from flask import Flask, render_template,request, session, url_for, redirect
import os
import pymongo
import bcrypt
from bson.objectid import ObjectId


hostelP = Flask(__name__)
hostelP.config["UPLOAD_FOLDER"] = './static/img/usersProfile/'

myClient = pymongo.MongoClient("mongodb://admin:qwe123@3.209.153.124:27017")
myDb = myClient["hostelpremiumdb"]
myCollection = myDb["Users"]
propertieCollection = myDb["Properties"]

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
        avatar = "perfil.png"
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
    response = []
    propertie = propertieCollection.find()

    for data in propertie:
        response.append({
            '_id':data['_id'],
            'city':data['city'],
            'rooms':data['rooms'],
            'country':data['country'],
            'price':data['price'],
            'adress':data['adress'],
            'description':data['description'],
            'location':data['location'],
            'cover':data['cover'],
            'images':data['images'],
            'status':data['status'],
            'idUSer':data['idUSer'],            
        })
    if "email" in session:
        email = session["email"]    
        result = {'email': email}
        user = myCollection.find_one(result)
        id_user = str(user['_id'])
        return render_template('hostArea.html', id = id_user, data_user=user, properties=response)        
    else:
        return redirect(url_for("login"))

@hostelP.route('/delete/<id>')
def delete(id):
        propertieCollection.delete_one({'_id': ObjectId(id)})
        return redirect(url_for("hostArea"))

#LLenado de datos de propiedad
@hostelP.route('/properties/<id>')
def properties(id):
    user = myCollection.find()
    
    data = propertieCollection.find_one({'_id': ObjectId(id)})  
    response = []  
    response.append({
        '_id':data['_id'],
        'city':data['city'],
        'rooms':data['rooms'],
        'country':data['country'],
        'price':data['price'],
        'adress':data['adress'],
        'description':data['description'],
        'location':data['location'],
        'cover':data['cover'],
        'images':data['images'],
        'idUSer':data['idUSer']
    })          

    return render_template("userPropertie.html", data_propertie = response, data_user=user)

#Guardar cambio de datos de la propiedad
@hostelP.route('/editPropertie/<id>', methods=["POST"])
def editpropertie(id):
    city = request.form.get('city')
    rooms = request.form.get('rooms')
    country = request.form.get('country')
    price = request.form.get('price')
    adress = request.form.get('adress')
    description = request.form.get('description')
    location= request.form.get('location')

    propertieCollection.update_one({'_id': ObjectId(id)}, {"$set":{
        
        "city": city,
        "country": country,
        "rooms": rooms,
        "price": price,
        "description": description,
        "adress": adress,
        "location": location
    }})

    return redirect(url_for("hostArea"))

@hostelP.route('/cotizar/<id>')
def cotizar(id):    

    user = myCollection.find()

    data = propertieCollection.find_one({'_id': ObjectId(id)})  
    res = []  
    res.append({
        '_id':data['_id'],
        'city':data['city'],
        'rooms':data['rooms'],
        'country':data['country'],
        'price':data['price'],
        'adress':data['adress'],
        'description':data['description'],
        'location':data['location'],
        'cover':data['cover'],
        'images':data['images'],
        'idUSer':data['idUSer']
    }) 

    return render_template("cotizar.html", data_propertie = res, data_user=user)



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

# Guardar cambio de imagen.
@hostelP.route('/editavatar/<id>', methods=["POST"])
def editavatar(id):

    avatar = request.files['avatar']
    avatarU = avatar.filename
    avatar.save(os.path.join(hostelP.config['UPLOAD_FOLDER'], avatarU))

    myCollection.update_one({'_id': ObjectId(id)}, {'$set': {
        'avatar': avatarU
    }})
    
    return redirect(url_for("hostArea"))

#formulario para agregar propiedad
@hostelP.route('/propertie', methods=['POST', 'GET'])
def propertie():

    message = ""

    if "email" in session:
        email = session["email"]
        result = {'email': email}
        user = myCollection.find_one(result)

        return render_template('propertie.html',  data_user=user)


#agregar propiedad en base de datos
@hostelP.route('/addpropertie', methods=["POST"])
def addpropertie():
    city = request.form.get('city')
    rooms = request.form.get('rooms')
    country = request.form.get('country')
    price = request.form.get('price')
    adress = request.form.get('adress')
    description = request.form.get('description')
    location= request.form.get('location')
    cover = request.files['cover']
    lcover = cover.filename
    cover.save(os.path.join(hostelP.config['UPLOAD_FOLDER'], lcover))
    imageMain = request.files.getlist('imageMain[]')
    name_images =[]
    for image in imageMain:
            image.save(os.path.join(hostelP.config['UPLOAD_FOLDER'], image.filename))
            name_images.append(image.filename)

    email = session["email"]
    result = {'email': email}
    data_user=myCollection.find_one(result)
    idUSer = str(data_user['_id'])

    data_propertie = {
        "city": city,
        "rooms": rooms,
        "country": country,
        "price": price,
        "adress": adress,
        "description": description,
        "location": location,
        "cover": lcover,
        "images": name_images,
        "idUSer": idUSer,
        "status": True
    }
            
    propertieCollection.insert_one(data_propertie)

    return redirect(url_for("hostArea"))

  


@hostelP.route('/users')
def users():
    users = myCollection.find()
    response = users
    print(response)
    return render_template('users.html', allusers=response)

@hostelP.route('/allProperties')
def allProperties():
    properties = propertieCollection.find()
    response = properties
    print (response)
    return render_template('allProperties.html', allproperties = response)




if __name__ == "__main__":
    hostelP.run(debug=True)
