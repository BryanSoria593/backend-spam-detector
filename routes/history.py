from flask import app, jsonify, render_template, Blueprint, request, session, redirect,  Response
import subprocess
from bson import json_util
from bson.objectid import ObjectId
import pymongo

# My imports
from db.connection import connect
from middleware.validate_jwt import token_required


client = connect()
database = client['tesis']

history = Blueprint('history', __name__)

mimetype = mimetype = 'application/json'


@history.route('/all', methods=['GET'])
@token_required
def get_all_email():
    try:
        correos = database['reports']        
        mails = correos.find({}).sort('dateOfReport', pymongo.DESCENDING)

        mail_list = list(mails)

        if len(mail_list) == 0:
            return jsonify({'ok': False, 'message': 'No hay correos', 'mails': []})

        response = {'ok': True, 'mails': mail_list}
        return Response(json_util.dumps(response), mimetype), 200

    except:
        return jsonify({'message': 'Ocurrió un error al obtener los correos'}), 500


