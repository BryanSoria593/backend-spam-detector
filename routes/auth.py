import app
from flask import Blueprint, request, jsonify
from flask import Flask, request, jsonify
from middleware.validate_jwt import token_required
from middleware.generate_jwt import encode_token, decode_token
from jwt.exceptions import DecodeError, ExpiredSignatureError
import bcrypt
import yagmail
from db.connection import connect
from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, USER_ADMIN_EMAIL

client = connect()
database = client['tesis']
collection = database['user']

# global variable
auth = Blueprint('auth', __name__)

app = Flask(__name__)


# mail
app.MAIL_SERVER = MAIL_SERVER
app.MAIL_PORT = MAIL_PORT
app.MAIL_USE_TLS = MAIL_USE_TLS
app.MAIL_USERNAME = MAIL_USERNAME
app.MAIL_PASSWORD = MAIL_PASSWORD
app.MAIL_DEFAULT_SENDER = MAIL_DEFAULT_SENDER


@auth.route('/register', methods=['POST'])
def request_register():
    try:
        
        yag = yagmail.SMTP(app.MAIL_USERNAME, app.MAIL_PASSWORD)

        mail_sent_validate = USER_ADMIN_EMAIL

        username = request.json['username']
        email = request.json['email']
        password = request.json['password']
        confirmPassword = request.json['confirmPassword']

        if not username or not email or not password or not confirmPassword:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        if password != confirmPassword:
            return jsonify({'ok': False, 'message': 'Las contraseñas no coinciden'}), 400

        user_data = collection.find_one({'email': email})
        if user_data:
            return jsonify({'ok': False, 'message': 'El usuario ya existe'}), 401
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        token = encode_token({"username": username, "email": email}, 2)

        add_user = collection.insert_one(
            {'username': username, 'email': email, 'password': hashed_password.decode('utf-8'), 'active': False, 'reject': False})

        destination = [mail_sent_validate]
        asunto = 'Registro de usuario'
        html = f'<h1>Registro de usuario</h1><p>Para registrar el usuario, ingresa al siguiente link: <a href="http://localhost:4200/auth/activate-account/{token}">Registrar usuario</a></p>'

        yag.send(destination, asunto, contents=html)
        

        return jsonify({'ok': True, 'message': 'Usuario registrado, espere a que el administrador lo habilite'}), 200

    except Exception as e:
        print(Exception)
        print(e)
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500


@auth.route('/activate-account', methods=['POST'])
def activate_user():
    try:
        token = request.json['token']        
        if not token:
            return jsonify({'ok': False, 'message': 'Datos incompletos.'}), 400
        info_user = decode_token(token)
        email = info_user['email']

        verify_user = collection.find_one({'email': email})

        is_active = verify_user['active']
        if is_active == 'rechazado':
            return jsonify({'ok': False, 'message': 'El usuario ya fue rechazado'}), 401

        if not verify_user:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        if not email:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        active_user = collection.update_one(
            {'email': email}, {'$set': {'active': True}})

        if not active_user:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        return jsonify({'ok': True, 'message': 'Usuario activado'}), 200

    except:
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500


@auth.route('/reject-account', methods=['POST'])
def reject_user():
    try:
        token = request.json['token']
        if not token:
            return jsonify({'ok': False, 'message': 'Datos incompletos.'}), 400
        info_user = decode_token(token)
        email = info_user['email']

        verify_user = collection.find_one({'email': email})

        if not verify_user:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        is_reject = verify_user['reject']
        if is_reject == 'rechazado':
            return jsonify({'ok': False, 'message': 'El usuario ya fue rechazado'}), 401

        reject_user = collection.update_one(
            {'email': email}, {'$set': {'reject': True}})

        if not reject_user:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        return jsonify({'ok': True, 'message': 'Usuario rechazado'}), 200

    except Exception as e:
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500


@auth.route('/login', methods=['POST'])
def request_login():
    try:
        email = request.json['email']
        password = request.json['password']
        if not email or not password:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        user_data = collection.find_one({'email': email})
        if not user_data:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        username = user_data['username']
        active_user = user_data['active']
        reject_user = user_data['reject']

        if reject_user:
            return jsonify({'ok': False, 'message': 'El usuario fue rechazado'}), 401

        if not active_user:
            return jsonify({'ok': False, 'message': 'El usuario no está activo'}), 401

        hashed_password = user_data['password']
        decoded_password = hashed_password.encode('utf-8')

        if not bcrypt.checkpw(password.encode('utf-8'), decoded_password):
            return jsonify({'ok': False, 'message': 'Usuario o contraseña incorrectos'}), 401
        
        token = encode_token({"username": username, "email": email}, 2)
        return jsonify({'ok': True, 'message': 'Login success', 'data': {"username": username, "email": email, "token": token}}), 200
        
        return jsonify({'ok': False, 'message': 'Usuario o contraseña incorrectos'}), 401

    except Exception as e:
        print(e)
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500


@auth.route('/reset-password/get-email', methods=['POST'])
def validate_email():
    # this a function validate that exist user with email and send email with token
    try:

        yag = yagmail.SMTP(app.MAIL_USERNAME, app.MAIL_PASSWORD)

        email = request.json['email']

        if not email:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        if not collection.find_one({'email': email}):
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        token = encode_token({"email": email}, 2)

        destination = [email]
        asunto = 'Recuperar contraseñas'
        html = f'<h1>Recuperar contraseña</h1><p>Para recuperar tu contraseña, ingresa al siguiente link: <a href="http://localhost:4201/auth/reset-password/{token}">Recuperar contraseña</a></p>'

        yag.send(destination, asunto, contents=html)

        return jsonify({'ok': True, 'message': 'Correo enviado'}), 200
    except:
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500

@auth.route('/validate-token-auth', methods=['POST'])
def validate_token_auth():
    try:
        token = request.json['token']
        if not token:
            return jsonify({'ok': False, 'message': 'Datos incompletos.'}), 400
        
        response = decode_token(token)

        email = response['email']
        username = response['username']

     
        if not email:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        findUser = collection.find_one({'email': email})
        if not findUser:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401


        return jsonify({'ok': True, 'message': 'Token válido', 'data': {"email": email,"username":username, "token": token}}), 200

    except DecodeError as e:
        return jsonify({'ok': False, 'message': str(e)}), 401
    except ExpiredSignatureError as e:
        return jsonify({'ok': False, 'message': str(e)}), 401
    except Exception as e:
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500

@auth.route('/validate-token', methods=['POST'])
def validate_token():
    try:
        token = request.json['token']
        if not token:
            return jsonify({'ok': False, 'message': 'Datos incompletos.'}), 400
        
        response = decode_token(token)

        email = response['email']
     
        if not email:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        findUser = collection.find_one({'email': email})
        if not findUser:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401


        return jsonify({'ok': True, 'message': 'Token válido', 'data': {"email": email, "token": token}}), 200

    except DecodeError as e:
        return jsonify({'ok': False, 'message': str(e)}), 401
    except ExpiredSignatureError as e:
        return jsonify({'ok': False, 'message': str(e)}), 401
    except Exception as e:
        print(e)
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500


@auth.route('/reset-password/update-password', methods=['POST'])
def response_update_password():
    try:
        token = request.json['token']
        password = request.json['password']
        confirmPassword = request.json['confirmPassword']
        if not password or not confirmPassword:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400
        if password != confirmPassword:
            return jsonify({'ok': False, 'message': 'Las contraseñas no coinciden'}), 400

        response = decode_token(token)
        email = response['email']

        verifyUser = collection.find_one({'email': email})
        if not verifyUser:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        collection.update_one({'email': email}, {
                              '$set': {'password': password.decode('utf-8')}})

        return jsonify({'ok': True, 'message': 'Contraseña actualizada'}), 200

    except:
        return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400


@auth.route('/validate-password', methods=['POST'])
def response_validate_password():
    try:
        email = request.json['email']
        password = request.json['password']

        if not email or not password:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        verifyUser = collection.find_one({'email': email})
        if not verifyUser:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        stored_password = verifyUser['password'].encode('utf-8')

        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return jsonify({'ok': False, 'message': 'Contraseña incorrecta'}), 401

        return jsonify({'ok': True, 'message': 'Contraseña correcta'}), 200

    except:
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error.'}), 400


@auth.route('/update-profile', methods=['POST'])
# @token_required
def update_profile():
    try:
        currentUsername = request.json['currentUsername']
        currentEmail = request.json['currentEmail']
        newUsername = request.json['newUsername']
        newEmail = request.json['newEmail']
        password = request.json['password']

        if not currentUsername or not currentEmail or not newUsername or not newEmail or not password:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        verifyUser = collection.find_one({'email': currentEmail})
        if not verifyUser:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        stored_password = verifyUser['password'].encode('utf-8')

        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return jsonify({'ok': False, 'message': 'Contraseña incorrecta'}), 401

        # update email and username

        updateUser = collection.update_one({'email': currentEmail},
                                           {'$set': {'username': newUsername, 'email': newEmail}})

        token = encode_token({"username": newUsername, "email": newEmail}, 2)

        return jsonify({'ok': True, 'message': 'User pofile updated', 'data': {"username": newUsername, "email": newEmail, "token": token}}), 200

    except:
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error.'}), 400


@auth.route('/update-password', methods=['POST'])
def update_password():
    try:
        currentEmail = request.json['email']
        currentPassword = request.json['currentPassword']
        newPassword = request.json['newPassword']
        confirmNewPassword = request.json['confirmNewPassword']

        if not currentEmail or not currentPassword or not newPassword or not confirmNewPassword:
            return jsonify({'ok': False, 'message': 'Datos incompletos o incorrectos.'}), 400

        if newPassword != confirmNewPassword:
            return jsonify({'ok': False, 'message': 'Las contraseñas no coinciden'}), 400

        verifyUser = collection.find_one({'email': currentEmail})
        if not verifyUser:
            return jsonify({'ok': False, 'message': 'El usuario no existe'}), 401

        hashed_password = bcrypt.hashpw(
            currentPassword.encode('utf-8'), bcrypt.gensalt())
        stored_password = verifyUser['password'].encode('utf-8')

        if not bcrypt.checkpw(currentPassword.encode('utf-8'), stored_password):
            return jsonify({'ok': False, 'message': 'Contraseña incorrecta'}), 401

        newPassword = bcrypt.hashpw(
            newPassword.encode('utf-8'), bcrypt.gensalt())

        updateUser = collection.update_one({'email': currentEmail},
                                           {'$set': {'password': newPassword.decode('utf-8')}})

        return jsonify({'ok': True, 'message': 'Contraseña actualizada, vuelva a iniciar sesión'}), 200

    except Exception as e:
        return jsonify({'ok': False, 'message': 'Ocurrió un error'}), 400
