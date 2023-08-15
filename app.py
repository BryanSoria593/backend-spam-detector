from flask import Flask, redirect, jsonify, flash, render_template
from flask_cors import CORS
from routes.auth import auth
from routes.history import history
from routes.dashboard import dashboard
from routes.quarantine import quarantine
from config import KEY_FLASK

app = Flask(__name__)
app.secret_key = KEY_FLASK

CORS(app)

@app.errorhandler(404)
def redirect_to_home(error):
    # 404.html is a template in the templates folder
    return render_template('404.html'), 404
    

app.register_blueprint(auth, url_prefix='/auth',)
app.register_blueprint(dashboard, url_prefix='/dashboard')
app.register_blueprint(history, url_prefix='/history')
app.register_blueprint(quarantine, url_prefix='/quarantine')
