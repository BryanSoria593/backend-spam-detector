import jwt
from datetime import datetime, timedelta
import pytz
# Clave secreta para firmar el token.
from config import KEY_JWT

def encode_token(payload, hours= None):
    # Obtener la zona horaria de Ecuador (GMT-5)
    timezone = pytz.timezone('America/Guayaquil')

    # Obtener la fecha y hora actual en la zona horaria de Ecuador
    now = datetime.now(timezone)

    # Calcular la fecha de expiración sumando una hora
    exp_time = now + timedelta(hours=hours)

    # Agregar la fecha de expiración al payload
    payload['exp'] = exp_time

    # Generar el token
    token = jwt.encode(payload, KEY_JWT, algorithm='HS256')
    # retorna el token cuando estes fuera del sistema operativo Centos 7
    # return token 

    # Devolver el token como cadena
    new_token = token.decode('utf-8')
    formatted_token = new_token.strip("b'")

    return formatted_token


# Función para decodificar y verificar un token JWT
def decode_token(token):
    try:
        # Decodificar el token y verificar la firma
        payload = jwt.decode(token, KEY_JWT, algorithms=['HS256'])

        # Verificar si el token ha expirado
        exp_time = datetime.utcfromtimestamp(payload['exp'])
        if datetime.utcnow() > exp_time:
            raise jwt.ExpiredSignatureError('Token expirado')

        # Devolver el payload decodificado
        return payload
    except jwt.DecodeError:
        # Error de decodificación del token
        raise jwt.DecodeError('Token inválido o mal formateado')
    except jwt.ExpiredSignatureError:
        # Error de token expirado
        raise jwt.ExpiredSignatureError('Token expirado')
