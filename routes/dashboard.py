from datetime import datetime
from flask import jsonify, Blueprint,  Response, request

from bson import json_util

import pymongo

# My imports
from db.connection import connect
from middleware.validate_jwt import token_required


client = connect()
database = client['tesis']

dashboard = Blueprint('dashboard', __name__)

mimetype = mimetype = 'application/json'


@dashboard.route('/detected-ham', methods=['GET'])
@token_required
def get_ham_email():
    try:
        correos = database['normal_mail']
        normal_mail = correos.find({}).sort(
            'dateOfAnalysis', pymongo.DESCENDING)

        normal_mail_list = list(normal_mail)
        if len(normal_mail_list) == 0:
            return jsonify({'ok': False, 'message': 'No hay correos', 'normal_mail': [], 'count_normal_mail': 0})
        response = {'ok': True, 'data': {
            'normal_mail': normal_mail_list,
        }}
        return Response(json_util.dumps(response), mimetype), 200

    except:
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500


@dashboard.route('/detected-spam', methods=['GET'])
@token_required
def get_spam_email():
    try:
        correos = database['report_mail']
        spam_mail = correos.find({}).sort('dateOfAnalysis', pymongo.DESCENDING)
        spam_mail_list = list(spam_mail)
        if len(spam_mail_list) == 0:
            return jsonify({'ok': False, 'message': 'No hay correos', 'spam_mails': [], 'count_spam_mails': 0})

        response = {'ok': True, 'data': {
            'spam_mails': spam_mail_list,
        }}
        return Response(json_util.dumps(response), mimetype), 200

    except:
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500


@dashboard.route('/sent-alert', methods=['GET'])
@token_required
def get_sent_alert_email():
    try:
        correos = database['alert_sent_user']
        alert_user = correos.find({}).sort(
            'dateOfAnalysis', pymongo.DESCENDING)
        alert_user_list = list(alert_user)
        if len(alert_user_list) == 0:
            return jsonify({'ok': False, 'message': 'No hay correos', 'alert_user': [], 'count_alert_user': 0})

        response = {'ok': True, 'data': {
            'alert_user': alert_user_list,
        }}
        return Response(json_util.dumps(response), mimetype), 200

    except:
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500


@dashboard.route('/spam-report', methods=['GET'])
@token_required
def get_spam_report():
    try:
        correos = database['reports']
        mails = correos.find({'prediction': 'spam'}).sort(
            'dateOfReport', pymongo.DESCENDING)
        mail_list = list(mails)
        if len(mail_list) == 0:
            return jsonify({'ok': False, 'message': 'No hay correos', 'mails': []})
        response = {'ok': True, 'data': {
            'mails': mail_list,
        }}

        return Response(json_util.dumps(response), mimetype), 200
    except:
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500


@dashboard.route('/mails-dashboard', methods=['GET'])
@token_required
def get_email_from():
    try:
        correos = database['reports']
        mailsFrom = correos.aggregate([
            {'$group': {'_id': {'from': '$from', 'prediction': '$prediction'},
                        'counts': {'$sum': 1}}},
            {'$project': {'_id': 0, 'user': '$_id.from', 'cargo': 'Remitente',
                          'detection': '$_id.prediction', 'counts': 1}},
            {'$sort': {'counts': -1}}
        ])

        mailsTo = correos.aggregate([
            {'$unwind': '$to'},
            {'$group': {'_id': {'to': '$to', 'prediction': '$prediction'},
                'counts': {'$sum': 1}}},
            {'$project': {'_id': 0, 'user': '$_id.to', 'cargo': 'Receptor',
                'detection': '$_id.prediction', 'counts': 1}},
            {'$sort': {'counts': -1}}
            ])

        mailFrom_list = list(mailsFrom)
        mailTo_list = list(mailsTo)

        response = {'ok': True, 'mailsFrom': mailFrom_list,
                    'mailsTo': mailTo_list}
        return Response(json_util.dumps(response), mimetype), 200

    except:
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500

@dashboard.route('/get-whitelist', methods=['POST'])
@token_required
def get_user_filter():
    try:
        blacklist = database['user_filter_list']
        type_user = request.json['type_user']
        mails = blacklist.find({'type_user': 'white'})
        mail_list = list(mails)
        for mail in mail_list:
            mail['_id'] = str(mail['_id'])  # Convertimos el objeto ObjectId a una cadena
            mail['date'] = str(mail['date'])
        if len(mail_list) == 0:
            return jsonify({'ok': False, 'message': 'No hay correos', 'mails': []})
        response = {'ok': True, 'data':{
            'mails': mail_list,
        }}
        
        return Response(json_util.dumps(response), mimetype), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500


@dashboard.route('/update-whitelist', methods=['PUT'])
@token_required
def update_whitelist():
    try:
        whitelist = database['user_filter_list']
        email = request.json['email']
        newUsername = request.json['newUsername']
        newEmail = request.json['newEmail']

        verify_email = whitelist.find_one({'email': email})
        if not verify_email:
            return jsonify({'ok': False, 'message': 'No se encontró el correo'})

        verify_update = whitelist.update_one({'email': email}, {'$set': {'username': newUsername, 'email': newEmail}})
        
        if not verify_update:
            return jsonify({'ok': False, 'message': 'No se pudo actualizar el correo'})

        # Obtener el dato actualizado
        updated_data = whitelist.find_one({'email': newEmail})

        return jsonify({'ok': True, 'message': 'Correo actualizado', 'updateUser': {
            '_id': str(updated_data['_id']),
            'username': updated_data['username'],
            'email': updated_data['email']
        }}), 200
    except:
        return jsonify({'message': 'Ocurrió un error al actualizar el correo'}), 500

@dashboard.route('/delete-whitelist', methods=['POST'])
@token_required
def delete_whitelist():
    try:
        whitelist = database['user_filter_list']
        email = request.json['email']

        if not email:
            return jsonify({'ok': False, 'message': 'Datos incompletos'}), 400

        verify_email = whitelist.find_one({'email': email})
        if not verify_email:
            return jsonify({'ok': False, 'message': 'No se encontró el correo'})
        
        verify_delete = whitelist.delete_one({'email': email})
        if not verify_delete:
            return jsonify({'ok': False, 'message': 'No se pudo eliminar el correo'})

        return jsonify({'ok': True, 'message': 'Correo eliminado'}), 200
    except:
        return jsonify({'message': 'Ocurrió un error al eliminar el correo'}), 500



@dashboard.route('/get-blacklist', methods=['POST'])
@token_required
def get_blacklist():
    try:
        blacklist = database['user_filter_list']
        type_user = request.json['type_user']
        mails = blacklist.find({'type_user': 'black'})
        mail_list = list(mails)
        for mail in mail_list:
            mail['_id'] = str(mail['_id'])  # Convertimos el objeto ObjectId a una cadena
            mail['date'] = str(mail['date'])
        if len(mail_list) == 0:
            return jsonify({'ok': False, 'message': 'No hay correos', 'mails': []})
        response = {'ok': True, 'data':{
            'mails': mail_list,
        }}
        
        return Response(json_util.dumps(response), mimetype), 200
    except:
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500


@dashboard.route('/add-user-filter', methods=['POST'])
@token_required
def post_add_whitelist():
    try:
        username = request.json['username']
        email = request.json['email']
        whitelist = database['user_filter_list']
        type_user = request.json['type_user']

        if not username or not email or not type_user:
            return jsonify({'ok': False, 'message': 'Datos incompletos'}), 400
    
        verify_email = whitelist.find_one({'email': email})
        if verify_email:
            return jsonify({'ok': False, 'message': 'El correo ya existe en la lista blanca'})

        # Insertar el objeto en la base de datos
        inserted_object = {'email': email, 'username': username, 'type_user': type_user, 'date': datetime.now()}
        verify_insert = whitelist.insert_one(inserted_object)

        if not verify_insert:
            return jsonify({'ok': False, 'message': 'No se pudo agregar el correo a la lista blanca'}), 400

        # Obtener el objeto insertado de la base de datos y devolverlo en la respuesta
        inserted_object['_id'] = str(verify_insert.inserted_id)
        print(inserted_object)
        return jsonify({'ok': True, 'message': 'Correo agregado a la lista blanca', 'newUser': inserted_object}), 200

    except:
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500
