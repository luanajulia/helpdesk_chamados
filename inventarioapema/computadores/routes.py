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


@app.route("/computadores", methods=["GET", "POST"])
def computador():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'GET':
        return render_template("computadores/computador.html",  nivel=nivel, id=id)
    if request.method == 'POST':
        te=request.form.get('te')
        processador=request.form.get('processador')
        memoria=request.form.get('memoria')
        disco_rigido=request.form.get('disco_rigido')
        disco_rigido_2=request.form.get('disco_rigido_2')
        tipo=request.form.get('tipo')
        monitores=request.form.get('monitores')
        usuario=request.form.get('usuario')
        conx.execute(f"""INSERT INTO computadores (te, processador, memoria, disco_rigido, disco_rigido_2, tipo, monitores, usuario) VALUES  
                     ('{te}', '{processador}', '{memoria}', '{disco_rigido}', '{disco_rigido_2}', '{tipo}', '{monitores}', '{usuario}' ) """)
        conx.commit()
        return redirect(url_for("computadores"))
    return render_template("computadores/computador.html",  nivel=nivel, id=id)

@app.route("/maquinas/<id_computadores>")
@login_required
def maquinas(id_computadores):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.get(int(id_computadores))
    return render_template("computadores/maquinas.html", computadores=computadores, nivel=nivel, id=id)

@app.route("/computador")
def computadores():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.order_by(Computadores.usuario).all()
    colaboradores = conx.execute("SELECT  COUNT(id) as quant FROM computadores  ").fetchall()
    return render_template("computadores/computadores.html", computadores=computadores, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/processador")
def processador():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.order_by(Computadores.processador).all()
    colaboradores = conx.execute("SELECT  COUNT(id) as quant FROM computadores  ").fetchall()
    return render_template("computadores/computadores.html", computadores=computadores, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/memoria")
def memoria():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.order_by(Computadores.memoria).all()
    colaboradores = conx.execute("SELECT  COUNT(id) as quant FROM computadores  ").fetchall()
    return render_template("computadores/computadores.html", computadores=computadores, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/disco1")
def disco1():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.order_by(Computadores.disco_rigido).all()
    colaboradores = conx.execute("SELECT  COUNT(id) as quant FROM computadores  ").fetchall()
    return render_template("computadores/computadores.html", computadores=computadores, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/disco2")
def disco2():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.order_by(Computadores.disco_rigido_2).all()
    colaboradores = conx.execute("SELECT  COUNT(id) as quant FROM computadores  ").fetchall()
    return render_template("computadores/computadores.html", computadores=computadores, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/monitor")
def monitor():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.order_by(Computadores.monitores).all()
    colaboradores = conx.execute("SELECT  COUNT(id) as quant FROM computadores  ").fetchall()
    return render_template("computadores/computadores.html", computadores=computadores, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/tipo")
def tipo():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.order_by(Computadores.tipo).all()
    colaboradores = conx.execute("SELECT  COUNT(id) as quant FROM computadores  ").fetchall()
    return render_template("computadores/computadores.html", computadores=computadores, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/te")
def te():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    computadores = Computadores.query.order_by(Computadores.te).all()
    colaboradores = conx.execute("SELECT  COUNT(id) as quant FROM computadores  ").fetchall()
    return render_template("computadores/computadores.html", computadores=computadores, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/search_computadores/<string:usuario>",methods=['POST','GET'])
def searchcomp(usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    conx.execute("SELECT * FROM computadores WHERE computadores.usuario LIKE '%"+usuario+"%'")
    computadores = conx.fetchall()
    if request.method=='GET':
        conx.execute("SELECT * FROM computadores WHERE computadores.usuario LIKE '%"+usuario+"%'")
        computadores = conx.fetchall()
        return render_template("computadores/busca_computador.html", computadores=computadores, nivel=nivel, id=id, usuario=usuario)
    conx.execute("SELECT * FROM computadores WHERE computadores.usuario LIKE '%"+usuario+"%'")
    computadores = conx.fetchall()
    return render_template("computadores/busca_computador.html", computadores=computadores, nivel=nivel, id=id, usuario=usuario)

@app.route("/edit_computador/<string:id>",methods=['POST','GET'])
def edit_computador(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM computadores WHERE id = '"+id+"'")
    computadores = conx.execute(query).fetchall()
    if request.method=='GET':
        return render_template("computadores/edit_computador.html",computadores=computadores, nivel=nivel, id=id_usuario)
    if request.method=='POST':
        te=request.form.get('te')
        processador=request.form.get('processador')
        memoria=request.form.get('memoria')
        disco_rigido=request.form.get('disco_rigido')
        disco_rigido_2=request.form.get('disco_rigido_2')
        tipo=request.form.get('tipo')
        usuario=request.form.get('usuario')
        conx.execute("UPDATE computadores SET usuario = '"+usuario+"', tipo = '"+tipo+"', disco_rigido_2 = '"+disco_rigido_2+"', disco_rigido = '"+disco_rigido+"', memoria = '"+memoria+"', processador = '"+processador+"', te = '"+te+"' WHERE id = '"+id+"'")
        conx.commit()
        return redirect(url_for("computadores"))
    query = ("SELECT TOP 1 * FROM computadores WHERE id = '"+id+"'")
    computadores = conx.execute(query).fetchall()
    return render_template("computadores/edit_computador.html",computadores=computadores, nivel=nivel, id=id_usuario)

@app.route("/delete_computador/<string:id>",methods=['GET'])
def delete_computador(id):
    conx.execute("DELETE FROM computadores WHERE id = '"+id+"'")
    conx.commit()
    flash('User Deleted','warning')
    return redirect(url_for("computadores"))