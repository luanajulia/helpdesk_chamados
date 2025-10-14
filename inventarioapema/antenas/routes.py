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


@app.route("/Antena_6")
def antenas_6():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    antena = Antenas.query.order_by(Antenas.antenas).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena 6'   ").fetchall()
    return render_template("antenas/antenas_6.html", antena=antena, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/Antena_Fininha")
def antenas_fininha():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    antena = Antenas.query.order_by(Antenas.departamento).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena Fininha'   ").fetchall()
    return render_template("antenas/antenas_fininha.html", antena=antena, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/Antena_LR")
def antenas_lr():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    antena = Antenas.query.order_by(Antenas.departamento).all()
    ativosstatus =  conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena LR'   ").fetchall()
    return render_template("antenas/antena_lr.html", antena=antena, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/Antena_Pro-1")
def antenas_pro():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    antena = Antenas.query.order_by(Antenas.departamento).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena Pro-1'   ").fetchall()
    return render_template("antenas/antenas_pro-1.html", antena=antena, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/search_antenas/<string:antenas>",methods=['POST','GET'])
def search_antenas(antenas):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method=='GET':
        conx.execute("SELECT * FROM antenas WHERE antenas LIKE '%"+antenas+"%'")
        antena = conx.fetchall()
        return render_template("antenas/busca_antenas.html", antens=antena, nivel=nivel, id=id, antenas=antenas)
    conx.execute("SELECT * FROM antenas WHERE antenas LIKE '%"+antenas+"%'")
    antena = conx.fetchall()
    return render_template("antenas/busca_antenas.html", antens=antena, nivel=nivel, id=id)

@app.route("/edit_antenas/<string:id>", methods=['POST','GET'])
def edit_antenas(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM antenas WHERE id = '"+id+"'")
    antena = conx.execute(query).fetchall()
    if request.method=='GET':
        return render_template("antenas/edit_antenas.html", antenas=antena, nivel=nivel, id=id_usuario)
    if request.method=='POST':
        antenas=request.form.get('antenas')
        departamento=request.form.get('departamento')
        conx.execute("UPDATE antenas SET antenas = '"+antenas+"', departamento = '"+departamento+"' WHERE id = '"+id+"'")
        conx.commit()
        return redirect(url_for("antenas"))
    query = ("SELECT TOP 1 * FROM antenas WHERE id = '"+id+"'")
    antena = conx.execute(query).fetchall()
    return render_template("antenas/edit_antenas.html",antenas=antena, nivel=nivel, id=id_usuario)

@app.route("/criar_antenas",methods=['GET', "POST"])
def criarantena():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'GET':
        return render_template("antenas/criar_antenas.html",  nivel=nivel, id=id)
    if request.method == 'POST':
        antenas = request.form.get('antena')
        departamento = request.form.get('departamento')
        conx.execute("INSERT INTO antenas (antenas, departamento) VALUES  ('"+antenas+"', '"+departamento+"') ")
        conx.commit()
        return redirect(url_for("antenas"))
    return render_template("antenas/criar_antenas.html",  nivel=nivel, id=id)

@app.route("/delete_antenas/<string:id>",methods=['GET'])
def delete_antenas(id):
    conx.execute("DELETE FROM antenas WHERE id = '"+id+"'")
    conx.commit()
    flash('User Deleted','warning')
    return redirect(url_for("antenas"))

@app.route("/antenas")
def antenas():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    antena = Antenas.query.order_by(Antenas.departamento).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena 6'   ").fetchall()
    desativado =  conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena Fininha'   ").fetchall()
    pendente = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena LR'   ").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena Pro-1'   ").fetchall()
    return render_template("antenas/antenas.html", antena=antena, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, concluido=concluido, nivel=nivel, id=id)

@app.route("/modelo_antenas")
def modelo_antenas():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    antena = Antenas.query.order_by(Antenas.antenas).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena 6'   ").fetchall()
    desativado =  conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena Fininha'   ").fetchall()
    pendente = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena LR'   ").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM antenas WHERE antenas = 'Antena Pro-1'   ").fetchall()
    return render_template("antenas/antenas.html", antena=antena, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, concluido=concluido, nivel=nivel, id=id)