from pymongo import MongoClient
from datetime import datetime

url = "mongodb://localhost:27017/"

client = MongoClient(url)

db = client["tesis"]


def insert_report(uuid_mail, from_, to_, subject, body, id_mail, name_attachments, prediction, path, file_mail, id_group):
    try:
        collection = db["reports"]
        verify_insert = collection.insert_one(
            {
                'uuid': uuid_mail,
                'dateOfReport': datetime.now(),
                'from': from_,
                'to': to_,
                'subject': subject,
                'message': body,
                'id_mail': id_mail,
                'name_attachments': name_attachments,
                'prediction': prediction,
                'path': path,
                'file_name': file_mail,
                'id_group': id_group
            })
        if not verify_insert.inserted_id:
            return False
        return True

    except:
        print('Error al insertar los datos en insert_report')
        return False
