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


@app.route("/Vip_3240_IA")
def Vip_3240_IA():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    camera = Cameras.query.order_by(Cameras.departamento).all()
    ativosstatus = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'Vip 3240 IA'   ").fetchall()
    return render_template("cameras/camera_3.html", camera=camera, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/Vip_S3020_G2")
def Vip_S3020_G2():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    camera = Cameras.query.order_by(Cameras.departamento).all()
    desativado = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'Vip S3020 G2'   ").fetchall()
    return render_template("cameras/camera_s.html", camera=camera, desativado=desativado, nivel=nivel, id=id)

@app.route("/VHD_1010")
def VHD_1010():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    camera = Cameras.query.order_by(Cameras.departamento).all()
    pendente = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'VHD 1010'   ").fetchall()
    return render_template("cameras/camera_1.html", camera=camera, pendente=pendente, nivel=nivel, id=id)

@app.route("/search_cameras/<string:cameras>",methods=['POST','GET'])
def searchcameras(cameras):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    conx.execute("SELECT * FROM cameras WHERE cameras LIKE '%"+cameras+"%'")
    camera = conx.fetchall()
    if request.method=='GET':
        conx.execute("SELECT * FROM cameras WHERE cameras LIKE '%"+cameras+"%'")
        camera = conx.fetchall()
        return render_template("cameras/busca_cameras.html", cameras=cameras, nivel=nivel, id=id, camers=camera)
    conx.execute("SELECT * FROM cameras WHERE cameras LIKE '%"+cameras+"%'")
    camera = conx.fetchall()
    return render_template("cameras/busca_cameras.html", cameras=cameras, nivel=nivel, id=id, camers=camera)


@app.route("/criar_cameras", methods=['GET', "POST"])
def criarcameras():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'GET':
        return render_template("cameras/criar_cameras.html", nivel=nivel, id=id)
    if request.method == 'POST':
        cameras=request.form.get('cameras')
        departamento=request.form.get('departamento')
        quant_cameras=request.form.get('quant_cameras')
        conx.execute("INSERT INTO cameras (cameras, departamento, quant_cameras) VALUES  ('"+cameras+"', '"+departamento+"', '"+quant_cameras+"') ")
        conx.commit()
        return redirect(url_for("cameras"))
    return render_template("cameras/criar_cameras.html", nivel=nivel, id=id)

@app.route("/cameras")
def cameras():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    camera = Cameras.query.order_by(Cameras.departamento).all()
    ativosstatus = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'Vip 3240 IA'  ").fetchall()
    desativado = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'Vip S3020 G2'  ").fetchall()
    pendente = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'VHD 1010'  ").fetchall()
    quant = conx.execute("SELECT SUM(quant_cameras) FROM cameras  ").fetchall()
    return render_template("cameras/cameras.html", camera=camera, quant=quant, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, nivel=nivel, id=id)

@app.route("/modelo_cameras")
def modelo_cameras():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    camera = Cameras.query.order_by(Cameras.cameras).all()
    ativosstatus = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'Vip 3240 IA'  ").fetchall()
    desativado = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'Vip S3020 G2'  ").fetchall()
    pendente = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'VHD 1010'  ").fetchall()
    quant = conx.execute("SELECT SUM(quant_cameras) FROM cameras  ").fetchall()
    return render_template("cameras/cameras.html", camera=camera, quant=quant, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, nivel=nivel, id=id)

@app.route("/quant_cameras")
def quant_cameras():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    camera = Cameras.query.order_by(Cameras.quant_cameras).all()
    ativosstatus = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'Vip 3240 IA'  ").fetchall()
    desativado = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'Vip S3020 G2'  ").fetchall()
    pendente = conx.execute("SELECT SUM(quant_cameras) FROM cameras WHERE cameras = 'VHD 1010'  ").fetchall()
    quant = conx.execute("SELECT SUM(quant_cameras) FROM cameras  ").fetchall()
    return render_template("cameras/cameras.html", camera=camera, quant=quant, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, nivel=nivel, id=id)

@app.route("/edit_cameras/<string:id>", methods=['POST','GET'])
def edit_cameras(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM cameras WHERE id = '"+id+"'")
    camera =  conx.execute(query).fetchall()
    if request.method=='GET':
        return render_template("cameras/edit_cameras.html",cameras=camera, nivel=nivel, id=id_usuario)
    if request.method=='POST':
        cameras=request.form.get('cameras')
        departamento=request.form.get('departamento')
        quant_cameras=request.form.get('quant_cameras')
        conx.execute("UPDATE cameras SET cameras = '"+cameras+"', departamento = '"+departamento+"', quant_cameras = '"+quant_cameras+"' WHERE id = '"+id+"'")
        conx.commit()
        return redirect(url_for("cameras"))
    query = ("SELECT TOP 1 * FROM cameras WHERE id = '"+id+"'")
    camera =  conx.execute(query).fetchall()
    return render_template("cameras/edit_antenas.html",cameras=camera, nivel=nivel, id=id_usuario)

@app.route("/delete_cameras/<string:id>",methods=['GET'])
def delete_cameras(id):
    conx.execute("DELETE FROM cameras WHERE id = '"+id+"'")
    conx.commit()
    flash('User Deleted','warning')
    return redirect(url_for("cameras"))