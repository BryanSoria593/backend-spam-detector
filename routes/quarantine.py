import app
from flask import Blueprint, request, jsonify, render_template, Flask, request, jsonify

from jwt.exceptions import DecodeError, ExpiredSignatureError
from middleware.generate_jwt import encode_token, decode_token

import bcrypt
from cryptography.fernet import Fernet

from logic.insertDB.insert import insert_report
from logic.actions.emailProcessing import get_namefile_and_idmail, get_values_dictionary, read_email_content
from db.connection import connect

from config import KEY_ENCRYPT_TOKEN

client = connect()
database = client['tesis']

# global variable
quarantine = Blueprint('quarantine', __name__)

def remove_random_letters(token_part):
    return token_part[5:-5]

def separate_token(token):
    parts = token.split('.')
    header = remove_random_letters(parts[0])
    payload = remove_random_letters(parts[1])
    signature = remove_random_letters(parts[2])
    modified_token = '.'.join([header, payload, signature])
    return modified_token

@quarantine.route('/validate/<token>', methods=['GET'])
def validate_token_mail(token):
    try:
        if not token:
            return render_template('404.html')

        rebuild_token = separate_token(token)
        
        token_decode = decode_token(rebuild_token)
        uuid_ = token_decode['uuid']
        prediction_ = token_decode['prediction']
        path_ = token_decode['path']

        if not uuid_ or not prediction_ or not path_:
            return render_template('404.html')

        f = Fernet(KEY_ENCRYPT_TOKEN)
        uuid_deco = f.decrypt(uuid_).decode('utf-8')
        prediction_deco = f.decrypt(prediction_).decode('utf-8')
        path_deco = f.decrypt(path_).decode('utf-8')

        if not prediction_deco == 'spam':
            return render_template('404.html')        

        return render_template('quarantine.html')
    except DecodeError:
        return render_template('404.html')
    except ExpiredSignatureError:
        return render_template('404.html')
    except Exception as e:
        print(e)
        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500

@quarantine.route('/accept/<token>', methods=['GET'])
def accept_quarantine(token):
    try:
        collection = database['reports']
        if not token:
            return jsonify({'ok': False, 'message': 'No se ha podido reportar'}), 400

        rebuild_token = separate_token(token)
        token_decode = decode_token(rebuild_token)
        print(token_decode)
        uuid_ = token_decode['uuid']
        prediction_ = token_decode['prediction']
        path_ = token_decode['path']

        f = Fernet(KEY_ENCRYPT_TOKEN)
        uuid_deco = f.decrypt(uuid_).decode('utf-8')
        prediction_deco = f.decrypt(prediction_).decode('utf-8')
        path_deco = f.decrypt(path_).decode('utf-8')


        if not prediction_deco == 'spam':
            return jsonify({'ok': False, 'message': 'No se ha podido reportar'}), 400
                        
        verify_duplicate = collection.find_one({'uuid': uuid_deco})
        if verify_duplicate:
            return jsonify({'ok': False, 'message': 'Correo ya reportado'}), 400

        file_mail, id_mail = get_namefile_and_idmail(path_deco)
        dictionary = read_email_content(path_deco)
        from_, to_, subject, body, name_attachments, id_group = get_values_dictionary(dictionary)

        verify_insert = insert_report(
            uuid_deco, from_, to_, subject, body, 
            id_mail, name_attachments, prediction_deco, path_deco, file_mail, id_group
        )
        if not verify_insert:
            return jsonify({'ok': False, 'message': 'No se ha podido reportar'}), 400

        return jsonify({'ok': True, 'message': 'Correo reportado con el administrador, Gracias'}), 200

    except Exception as e:
        print(e)

        return jsonify({'ok': False, 'message': 'Ha ocurrido un error'}), 500



