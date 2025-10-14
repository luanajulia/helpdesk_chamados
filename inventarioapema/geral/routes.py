#rotas do nosso site
from datetime import datetime, date, timedelta, time
from time import strftime
from flask.app import T_template_filter
from sqlalchemy.sql import func
import json
from flask import Response, abort, render_template, send_file, session, url_for, redirect, request, flash
from inventarioapema import app, database, bcrypt
from inventarioapema.models import Usuario, Computadores, Softwares, Chamados, Agendamento, Impressora, Toners, Cameras, Antenas, Manutencao, Materiais, Protheus, Centro, Tecnico, Colaboradores, Ausencia, Banco
from flask_login import login_required, login_user, logout_user, current_user
from inventarioapema.forms import FormLogin, Criarconta, Criar_computadores, Criar_Softwares, ChamadoForm, Criar_Agendamento, Criar_Impressora, Criar_Camera, Criar_Antenas, Criar_Toners, ManutencaoForm, Criar_Equipamento, Form_Protheus, Criar_Centro, Criar_Tecnico, Criar_Colaborador, Criar_Ausencia, Criar_Banco
from flask_mail import Mail, Message
from sqlalchemy import desc
import os
import jinja2
from werkzeug.utils import secure_filename
import pandas as pd
import sqlite3
import pyodbc
from inventarioapema.conexao import conx

def datetimeformat(value, format="%Y-%m-%d"):
    valor = datetime.strptime(value, '%Y-%m-%d')
    return valor.strftime(format)
jinja2.filters.FILTERS['datetimeformat'] = datetimeformat

email = 'suporte@apema.com.br'
senha = 'Apema@2019'

mail_settings = {
    "MAIL_SERVER": 'smtp.office365.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": email,
    "MAIL_PASSWORD": senha
}

app.config.update(mail_settings)
mail = Mail(app)


@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        query = ("SELECT TOP 1 * FROM usuario WHERE email = '"+email+"' and senha = '"+senha+"' ")
        usuarios =  conx.execute(query).fetchall()
        for usuario in usuarios:
            if usuario[2] == email and usuario[3] == senha:
                session['logged_in'] = True
                session['email'] = email
                session['nivel'] = usuario[5]
                session['departamento'] = usuario[4]
                session['id'] = usuario[0]
                current_user = True
                if usuario[5] == 'Administrador':
                    return redirect(url_for("dashboard_adm"))
                if usuario[5] == 'gestor':
                    return redirect(url_for("portal", id_usuario=usuario[0]))
                if usuario[5] == 'RH':
                    return redirect(url_for("departamento_banco"))
                if usuario[5] == 'Lideres':
                    return redirect(url_for("portal", id_usuario=usuario[0]))
                if usuario[5] == 'usuario':
                    return redirect(url_for("portal", id_usuario=usuario[0]))
                if usuario[5] == 'Tecnico':
                    return redirect(url_for("chamados"))
                if usuario[5] == 'Manutenção':
                    return redirect(url_for("equipamentos"))
        return render_template("geral/homepage.html", msg='Usuario Incorreto')
    return render_template("geral/homepage.html")

@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    if request.method=='GET':
        return render_template("geral/criarconta.html")
    if request.method == 'POST':
        username=request.form.get('username')
        departamento=request.form.get('departamento')
        ramal=request.form.get('ramal')
        email=request.form.get('email')
        nivel=request.form.get('nivel')
        senha=request.form.get('senha')
        conx.execute("INSERT INTO usuario (username, departamento, email, ramal, nivel, senha) VALUES  ('"+username+"', '"+departamento+"', '"+email+"', '"+ramal+"', '"+nivel+"', '"+senha+"' ) ")
        conx.commit()
        return redirect(url_for("homepage"))
    return render_template("geral/criarconta.html")

@app.route("/home/<nivel>")
@login_required
def home(nivel):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivels = session['nivel'] 
    id = session['id']
    usuarios = Usuario.query.filter(Usuario.nivel == nivel).all()
    return render_template("geral/historico.html", usuarios=usuarios, nivel=nivels, id=id)

@app.route("/inventario")
def inventario():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    return render_template("geral/inventarios.html", nivel=nivel, id=id)

@app.route("/adcionar")
def adcionar():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("geral/adcionar.html", nivel=nivel, id=id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))