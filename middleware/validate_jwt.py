from flask import jsonify, request
import jwt
from config import KEY_JWT


# Decorador para verificar el token
def token_required(f):
    def wrapper(*args, **kwargs):
        # Obtener el token de las cabeceras de la solicitud
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        
        # Verificar si el token está presente
        if not token:
            return jsonify({'message': 'Su sesión ha caducado'}), 401
        
        try:
            # Decodificar y verificar el token
            payload = jwt.decode(token, KEY_JWT, algorithms=['HS256'])
            
            # Agregar el usuario decodificado a la solicitud
            request.user = payload['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        # Llamar a la función con la solicitud actualizada
        return f(*args, **kwargs)
    
    # Cambiar el nombre de la función decorada para evitar el error
    wrapper.__name__ = f.__name__
    
    return wrapper
