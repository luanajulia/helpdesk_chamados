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


@app.route("/criar_impressoras", methods=["GET", "POST"])
def criar_impressoras():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'GET':
        return render_template("impressora/criar_impressoras.html",  nivel=nivel, id=id)
    if request.method == 'POST':
        nome_impressora=request.form.get('nome_impressora')
        modelo_impressora=request.form.get('modelo_impressora')
        departamento=request.form.get('departamento')
        ip=request.form.get('ip')
        conx.execute("INSERT INTO impressora (nome_impressora, departamento, modelo_impressora, ip) VALUES  ('"+nome_impressora+"', '"+departamento+"', '"+modelo_impressora+"', '"+ip+"') ")
        conx.commit()
        return redirect(url_for("impressoras"))
    return render_template("impressora/criar_impressoras.html",  nivel=nivel, id=id)

@app.route("/impressoras")
def impressoras():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    impressoras = Impressora.query.order_by(Impressora.nome_impressora).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Samsung M4080FX'   ").fetchall()
    desativado = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'HP Laser Colorida 4303FDW'   ").fetchall()
    pendente = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Kiocera  Ecosys m4125idn'   ").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'plotter'   ").fetchall()
    quant = conx.execute("SELECT  COUNT(id) FROM impressora  ").fetchall()
    return render_template("impressora/impressoras.html", impressoras=impressoras, quant=quant, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, concluido=concluido, nivel=nivel, id=id)

@app.route("/modelo_impressoras")
def modelo_impressora():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    impressoras = Impressora.query.order_by(Impressora.modelo_impressora).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Samsung M4080FX'   ").fetchall()
    desativado = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'HP Laser Colorida 4303FDW'   ").fetchall()
    pendente = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Kiocera  Ecosys m4125idn'   ").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'plotter'   ").fetchall()
    quant = conx.execute("SELECT  COUNT(id) FROM impressora  ").fetchall()
    return render_template("impressora/impressoras.html", impressoras=impressoras, quant=quant, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, concluido=concluido, nivel=nivel, id=id)

@app.route("/departamento_impressoras")
def departamento_impressora():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    impressoras = Impressora.query.order_by(Impressora.departamento).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Samsung M4080FX'   ").fetchall()
    desativado = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'HP Laser Colorida 4303FDW'   ").fetchall()
    pendente = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Kiocera  Ecosys m4125idn'   ").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'plotter'   ").fetchall()
    quant = conx.execute("SELECT  COUNT(id) FROM impressora  ").fetchall()
    return render_template("impressora/impressoras.html", impressoras=impressoras, quant=quant, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, concluido=concluido, nivel=nivel, id=id)

@app.route("/ip_impressoras")
def ip_impressora():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    impressoras = Impressora.query.order_by(Impressora.ip).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Samsung M4080FX'   ").fetchall()
    desativado = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'HP Laser Colorida 4303FDW'   ").fetchall()
    pendente = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Kiocera  Ecosys m4125idn'   ").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'plotter'   ").fetchall()
    quant = conx.execute("SELECT  COUNT(id) FROM impressora  ").fetchall()
    return render_template("impressora/impressoras.html", impressoras=impressoras, quant=quant, ativosstatus=ativosstatus, desativado=desativado, pendente=pendente, concluido=concluido, nivel=nivel, id=id)

@app.route("/edit_impressoras/<string:id>", methods=['POST','GET'])
def edit_impressoras(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM impressora WHERE id = '"+id+"'")
    impressoras = conx.execute(query).fetchall()
    if request.method=='GET':
        return render_template("impressora/edit_impressoras.html", impressoras=impressoras, id=id_usuario, nivel=nivel)
    if request.method=='POST':
        nome_impressora=request.form.get('nome_impressora')
        modelo_impressora=request.form.get('modelo_impressora')
        departamento=request.form.get('departamento')
        ip=request.form.get('ip')
        conx.execute("UPDATE impressora SET nome_impressora = '"+nome_impressora+"', departamento = '"+departamento+"', modelo_impressora = '"+modelo_impressora+"', ip = '"+ip+"' WHERE id = '"+id+"'")
        conx.commit()
        return redirect(url_for("impressoras"))
    query = ("SELECT TOP 1 * FROM impressora WHERE id = '"+id+"'")
    impressoras = conx.execute(query).fetchall()
    return render_template("impressora/edit_impressoras.html",impressoras=impressoras, id=id_usuario, nivel=nivel)

@app.route("/delete_impressoras/<string:id>",methods=['GET'])
def delete_impressoras(id):
    conx.execute("DELETE FROM impressora WHERE id = '"+id+"'")
    conx.commit()
    flash('User Deleted','warning')
    return redirect(url_for("impressoras"))

@app.route("/criar_toners",methods=['GET', "POST"])
def criartoner():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'GET':
        return render_template("impressora/criar_toners.html",  nivel=nivel, id=id)
    if request.method == 'POST':
        quant_toners=request.form.get('quant_toners')
        toners=request.form.get('toners')
        conx.execute("INSERT INTO toners (quant_toners, toners) VALUES  ('"+quant_toners+"', '"+toners+"') ")
        conx.commit()
        return redirect(url_for("toners"))
    return render_template("impressora/criar_toners.html",  nivel=nivel, id=id)

@app.route("/toners")
def toners():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    toners = Toners.query.order_by(Toners.toners).all()
    quant = conx.execute("SELECT  COUNT(id) as quat FROM toners  ").fetchall()
    return render_template("impressora/toners.html", toners=toners, quant=quant, nivel=nivel, id=id)

@app.route("/quant_toners")
def quant_toners():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    toners = Toners.query.order_by(Toners.quant_toners).all()
    quant = conx.execute("SELECT  SUM(quant_toners) FROM toners  ").fetchall()
    return render_template("impressora/toners.html", toners=toners, quant=quant, nivel=nivel, id=id)

@app.route("/edit_toners/<string:id>", methods=['POST','GET'])
def edit_toners(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM toners WHERE id = '"+id+"'")
    toner = conx.execute(query).fetchall()
    if request.method=='GET':
        return render_template("impressora/edit_toners.html",toners=toner, nivel=nivel, id=id_usuario)
    if request.method=='POST':
        toners=request.form.get('toners')
        quant_toners=request.form.get('quant_toners')
        conx.execute("UPDATE toners SET toners = '"+toners+"', quant_toners = '"+quant_toners+"' WHERE id = '"+id+"'")
        conx.commit()
        return redirect(url_for("toners"))
    query = ("SELECT TOP 1 * FROM toners WHERE id = '"+id+"'")
    toner = conx.execute(query).fetchall()
    return render_template("impressora/edit_toners.html",toners=toner, nivel=nivel, id=id_usuario)

@app.route("/delete_toners/<string:id>",methods=['GET'])
def delete_toners(id):
    conx.execute("DELETE FROM toners WHERE id = '"+id+"'")
    conx.commit()
    flash('User Deleted','warning')
    return redirect(url_for("toners"))

@app.route("/search_impressoras/<string:nome_impressora>",methods=['POST','GET'])
def searchimpre(nome_impressora):
    if not session.get('logged_in'):
            return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method=='GET':
        conx.execute("SELECT * FROM impressora WHERE nome_impressora LIKE '%"+nome_impressora+"%'")
        impressoras = conx.fetchall()
        return render_template("impressora/busca_impressoras.html", impressoras=impressoras, nivel=nivel, id=id)
    conx.execute("SELECT * FROM impressora WHERE nome_impressora LIKE '%"+nome_impressora+"%'")
    impressoras = conx.fetchall()
    return render_template("impressora/busca_impressoras.html", impressoras=impressoras, nivel=nivel, id=id)


@app.route("/Samsung")
def Samsung():
    if not session.get('logged_in'):
            return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    impressoras = Impressora.query.order_by(Impressora.nome_impressora).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Samsung M4080FX'   ").fetchall()
    return render_template("impressora/impressora_s.html", impressoras=impressoras, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/HP_Colorida")
def HP_Colorida():
    if not session.get('logged_in'):
            return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    impressoras = Impressora.query.order_by(Impressora.nome_impressora).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'HP Laser Colorida 4303FDW'   ").fetchall()
    return render_template("impressora/impressoras_h.html", impressoras=impressoras, desativado=ativosstatus, nivel=nivel, id=id)

@app.route("/Kiocera")
def Kiocera():
    if not session.get('logged_in'):
            return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    impressoras = Impressora.query.order_by(Impressora.nome_impressora).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'Kiocera  Ecosys m4125idn'   ").fetchall()
    return render_template("impressora/impressoras_k.html", impressoras=impressoras, pendente=ativosstatus, nivel=nivel, id=id)

@app.route("/Plotter")
def Plotter():
    if not session.get('logged_in'):
            return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    impressoras = Impressora.query.order_by(Impressora.nome_impressora).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM impressora WHERE modelo_impressora = 'plotter'   ").fetchall()
    return render_template("impressora/impressoras_p.html", impressoras=impressoras, concluido=ativosstatus, nivel=nivel, id=id)




@app.route("/toner/Samsung")
def t_Samsung():
    if not session.get('logged_in'):
            return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    toners = Toners.query.order_by(Toners.toners).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM toners WHERE toners = 'Samsung M4080FX'   ").fetchall()
    return render_template("impressora/toner_s.html", toners=toners, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/toner/HP_Colorida")
def t_HP_Colorida():
    toners = Toners.query.order_by(Toners.toners).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM toners WHERE toners = 'HP Laser Colorida 4303FDW'   ").fetchall()
    return render_template("impressora/toner_h.html", toners=toners, ativosstatus=ativosstatus)

@app.route("/toner/Kiocera")
def t_Kiocera():
    toners = Toners.query.order_by(Toners.toners).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM toners WHERE toners = 'Kiocera  Ecosys m4125idn'   ").fetchall()
    return render_template("impressora/toner_k.html", toners=toners, ativosstatus=ativosstatus)

@app.route("/toner/Plotter")
def t_Plotter():
    toners = Toners.query.order_by(Toners.toners).all()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM toners WHERE toners = 'plotter'   ").fetchall()
    return render_template("impressora/impressoras_p.html", toners=toners, ativosstatus=ativosstatus)

@app.route("/search_toners/<string:toners>",methods=['POST','GET'])
def search_toner(toners):
    if not session.get('logged_in'):
            return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method=='GET':
        conx.execute("SELECT * FROM toners WHERE toners LIKE '%"+toners+"%'")
        toner = conx.fetchall()
        return render_template("impressora/buscar_toner.html", toners=toner, nivel=nivel, id=id, toner=toners)
    conx.execute("SELECT * FROM toners WHERE toners LIKE '%"+toners+"%'")
    toner = conx.fetchall()
    return render_template("impressora/buscar_toner.html", toners=toner, nivel=nivel, id=id, toner=toners)
