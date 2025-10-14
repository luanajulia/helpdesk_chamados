#rotas do nosso site
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
conn = pyodbc.connect('Driver={SQL Server};'
'Server=192.168.1.16;'
'Database=SIGA;'
'UID=SIGA;'
'PWD=SIGA')

cursor = conn.cursor()




email = 'suporte@apema.com.br'
senha = 'Apema@2019'
def datetimeformat(value, format="%Y-%m-%d"):
    valor = datetime.strptime(value, '%Y-%m-%d')
    return valor.strftime(format)
jinja2.filters.FILTERS['datetimeformat'] = datetimeformat

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


'''
@app.route("/perfil/<id_usuario>")
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        return render_template("perfil.html", usuario=current_user)
    else:
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", usuario=usuario)
'''    




@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    formcadastro = Criar_Softwares()
    if formcadastro.validate_on_submit():
        softwares = Softwares(nome=formcadastro.nome.data,
                              validade=formcadastro.validade.data,
                              versao=formcadastro.versao.data,
                              usando=formcadastro.usando.data)
        database.session.add(softwares)
        database.session.commit()
        return redirect(url_for("software"))
    return render_template("cadastro.html", form=formcadastro)

@app.route("/search_soft/<string:nome>",methods=['POST','GET'])
def search_soft(nome):
    softwares = Softwares.query.filter(Softwares.nome == nome).first()
    if request.method=='GET':
        softwares = Softwares.query.filter(Softwares.nome == nome).first()
        return render_template("busca_softwares.html", softwares=softwares)
    softwares = Softwares.query.filter(Softwares.nome == nome).first()
    database.session.query(Softwares.nome == nome).first()
    return render_template("busca_softwares.html", softwares=softwares)

@app.route("/edit_softwares/<string:id>",methods=['POST','GET'])
def edit_softwares(id):
    softwares = Softwares.query.filter(Softwares.id == id).first()
    if request.method=='GET':
        return render_template("edit_soft.html",softwares=softwares)
    
    if request.method=='POST':
        nome=request.form.get('nome')
        validade=request.form.get('validade')
        versao=request.form.get('versao')
        usando=request.form.get('usando')
        softwares.nome = nome
        softwares.validade = validade
        softwares.versao = versao
        softwares.usando = usando
        database.session.add(softwares)
        database.session.commit()
        return redirect(url_for("software"))
    softwares = Softwares.query.filter(Softwares.id == id).first()
    database.session.query(Softwares.id == id).first()
    return render_template("edit_soft.html",softwares=softwares)

@app.route("/delete_softwares/<string:id>",methods=['GET'])
def delete_softwares(id):
    softwares = Softwares.query.filter(Softwares.id == id).first()
    database.session.delete(softwares)
    database.session.commit()
    flash('computador Deleted','warning')
    return redirect(url_for("softwares"))

@app.route("/software")
def software(): 
    softwares = Softwares.query.order_by(Softwares.id).all()
    colaboradores = database.session.query(database.func.count(Softwares.id), Softwares.nome).group_by(Softwares.nome).order_by(Softwares.nome).all()
    return render_template("softwares.html", softwares=softwares, current_user=current_user, colaboradores=colaboradores)
        



@app.route("/reunioes")
def reunioes():
    reuniao = Agendamento.query.order_by(Agendamento.data).all()
    colaboradores = database.session.query(database.func.count(Agendamento.id), Agendamento.data).group_by(Agendamento.data).order_by(Agendamento.data).all()
    return render_template("reunioes.html", reuniao=reuniao, colaboradores=colaboradores)


                                            

'''
#Reunioes e Agendamento
@app.route("/agendamento",methods=['GET', "POST"])
def agendamento():
    formagendamento = Criar_Agendamento()
    if formagendamento.validate_on_submit():
        reuniao = Agendamento(username=formagendamento.username.data,
                            sala=formagendamento.sala.data,
                            horario=formagendamento.horario.data,
                            data=formagendamento.data.data,
                            id_usuario=current_user.id)
        database.session.add(reuniao)
        database.session.commit()
        return redirect(url_for("agendamento", id_reuniao=reuniao.id))
    return render_template("agendamento.html", form=formagendamento)


@app.route("/reuniao/<id_usuario>")
@login_required
def reuniao(id_usuario):
    reuniao = Agendamento.query.filter(Agendamento.id_usuario == id_usuario).all()
    return render_template("reuniao.html", reuniao=reuniao)
'''

 

        
## manuais 



