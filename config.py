KEY_FLASK = 'PONER AQUI LA CLAVE DE FLASK'
KEY_ENCRYPT_TOKEN = 'CLAVE PARA ENCRIPTAR EL TOKEN CON CRYPTOGRAPHY, debe de estar en bytes' 
KEY_JWT = 'CLAVE PARA GENERAR LOS JWT'
MONGO_URI = 'mongodb://localhost:27017/'


# Esta configuración es para el envio de correos usando gmail
# para ello debes de crear una cuenta de gmail y usarla para emitir los correos
# y usar ese correo para emitir los correos desde el backend
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'AQUI VA EL USERNAME DE LA CUENTA DE GMAIL'
MAIL_PASSWORD = 'Aquí va la contraseña de la cuenta de gmail, no debe ser la de inicio de sesión'
MAIL_DEFAULT_SENDER = 'Aquí va el correo de la cuenta de gmail'

# CONFIGURE OF MAIL RESET PASSWORD
USER_ADMIN_EMAIL = 'Aquí va el correo del administrador del sistema
