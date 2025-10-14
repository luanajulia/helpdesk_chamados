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


@app.route("/usuarios")
def usuarios():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = Usuario.query.order_by(Usuario.departamento).all()
    colaboradores = database.session.query(database.func.count(Usuario.id), Usuario.username).group_by(Usuario.username).order_by(Usuario.username).all()
    return render_template("usuarios/usuarios.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/username")
def username():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel']
    id = session['id']
    usuarios = Usuario.query.order_by(Usuario.username).all()
    colaboradores = database.session.query(database.func.count(Usuario.id), Usuario.username).group_by(Usuario.username).order_by(Usuario.username).all()
    return render_template("usuarios/usuarios.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/email")
def email():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel']
    id = session['id']
    usuarios = Usuario.query.order_by(Usuario.email).all()
    colaboradores = database.session.query(database.func.count(Usuario.id), Usuario.username).group_by(Usuario.username).order_by(Usuario.username).all()
    return render_template("usuarios/usuarios.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/search_usuario", methods=["GET", "POST"])
def search_usuario():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        session['usuario'] = usuario
    usuario = session['usuario'] 
    conx.execute("SELECT username, email, departamento, ramal, id FROM usuario WHERE username LIKE '%"+usuario+"%'")
    rows = conx.fetchall()
    return render_template('usuarios/busca_usuario.html', rows=rows, usuario=usuario, nivel=nivel, id=id)

@app.route("/edit_user/<string:user_id>",methods=['POST','GET'])
def edit_user(user_id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM usuario WHERE id = '"+user_id+"'")
    usuarios =  conx.execute(query).fetchall()
    if request.method=='GET':
        return render_template("usuarios/edit_user.html", usuarios=usuarios, nivel=nivel, id=id_usuario, user_id=user_id)
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        ramal=request.form.get('ramal')
        departamento=request.form.get('departamento')
        nivel=request.form.get('nivel')
        conx.execute("UPDATE usuario SET username = '"+username+"', email = '"+email+"', departamento = '"+departamento+"', ramal = '"+ramal+"', nivel = '"+nivel+"' WHERE id = '"+user_id+"'")
        conx.commit()
        return redirect(url_for("usuarios"))
    query = ("SELECT TOP 1 * FROM usuario WHERE id = '"+user_id+"'")
    usuarios =  conx.execute(query).fetchall()
    return render_template("usuarios/edit_user.html",usuarios=usuarios, nivel=nivel, id=id_usuario, user_id=user_id)

@app.route("/delete_user/<string:id>",methods=['GET'])
def delete_user(id):
    conx.execute("DELETE FROM usuario WHERE id = '"+id+"'")
    conx.commit()
    flash('User Deleted','warning')
    return redirect(url_for("usuarios"))


@app.route("/controle/<niveis>")
def controle(niveis):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel']
    id = session['id']
    usuarios = conx.execute("SELECT * FROM usuario ORDER BY nivel")
    niveis = conx.execute("SELECT * FROM usuario WHERE nivel = '"+niveis+"'")
    return render_template("usuarios/controle_user.html", usuarios=usuarios, niveis=niveis, nivel=nivel, id=id)


@app.route("/ramais")
def ramais():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel']
    id = session['id']
    usuarios = Usuario.query.order_by(Usuario.username).all()
    colaboradores = database.session.query(database.func.count(Usuario.id), Usuario.username).group_by(Usuario.username).order_by(Usuario.username).all()
    return render_template("usuarios/telefone.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)
