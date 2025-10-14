from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pyodbc

import urllib.parse
from sqlalchemy import create_engine
server = '192.168.1.203'
params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=192.168.1.203;DATABASE=TECsuporte;UID=sa;PWD=Serfeliz@1505;')

connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
engine = create_engine(connection_string)

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] =   "mssql+pyodbc:///?odbc_connect=%s" % params
app.config["SECRET_KEY"] = "a23c4f2fe076b10bccd840626a026aa0"


database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "homepage"


from inventarioapema import routes
from inventarioapema.antenas import routes
from inventarioapema.banco_horas import routes
from inventarioapema.cameras import routes
from inventarioapema.chamados import routes
from inventarioapema.computadores import routes
from inventarioapema.geral import routes
from inventarioapema.grafico import routes
from inventarioapema.impressora import routes
from inventarioapema.manuais import routes
from inventarioapema.manutencao import routes
from inventarioapema.usuarios import routes
from inventarioapema.controle import routes

