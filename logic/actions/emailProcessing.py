import mailparser

def get_namefile_and_idmail(path):
    try:
        path = path.strip()
        file_mail = path.rsplit('/', 1)[-1]
        id_mail = file_mail[:file_mail.find('-')]
        return file_mail, id_mail
    except Exception as e:
        print('la ruta del archivo no cumple con el formato de zimbra')


def get_values_dictionary(dictionary):
    from_ = dictionary['from']
    to_ = dictionary['to']
    subject = dictionary['subject']
    body = dictionary['body']
    name_attachments = dictionary['attachments']
    id_group = dictionary['id_group']
    return from_, to_, subject, body, name_attachments, id_group


def read_email_content(path):
    try:
        with open(path, "rb") as f:
            # Crea un diccionario vacío
            email = {}
            msg = mailparser.parse_from_bytes(f.read())
            email['date'] = msg.headers.get('Date', 'Fecha no encontrada')
            email['from'] = msg.from_[0][1]
            email['to'] = msg.to[0][1]
            email['id_group'] = msg.headers.get('Message-ID', 'ID no encontrado')
            email['subject'] = msg.headers.get(
                'Subject', 'Asunto no encontrado')

            # Se obtiene el cuerpo del mensaje, caso contrario se muestra un mensaje de que no hay mensaje
            body = msg.text_plain[0] if len(
                msg.text_plain) > 0 else 'No hay mensaje'
            body = delete_spaces_between_lines(body)
            email['body'] = body

            email['attachments'] = []
            for file in msg.attachments:
                email['attachments'].append(file.get('filename'))

            f.close()
            return email
    except Exception as e:
        print(e)
        print('Este archivo no será leído, ya que proviene del usuario detected')


def delete_spaces_between_lines(text):
    return ''.join(text.splitlines())


