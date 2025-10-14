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
from inventarioapema.conexao import conx_rh

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

conn = pyodbc.connect('Driver={SQL Server};'
'Server=192.168.1.16;'
'Database=SIGA;'
'UID=SIGA;'
'PWD=SIGA')

cursor = conn.cursor()

@app.route("/criarcolaborador", methods=["GET", "POST"])
def criarcolaborador():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if request.method=='GET':
        return render_template("banco/criar_colaborador.html", nivel=nivel, id=id_usuario)
    if request.method=='POST':
        colaborador=request.form.get('colaborador')
        departamento=request.form.get('departamento')
        matricula=request.form.get('matricula')
        responsavel=f'{id_usuario}'
        conx_rh.execute(f"""INSERT INTO colaboradores(colaborador, departamento, matricula, responsavel) VALUES  
                        ('{colaborador}', '{departamento}', '{matricula}', '{responsavel}') """)
        conx_rh.commit()
        return redirect(url_for("colaboradores"))
    return render_template("banco/criar_colaborador.html", nivel=nivel, id=id_usuario)

@app.route("/edit_colaborador/<string:id>", methods=['POST','GET'])
def edit_colaborador(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM colaboradores WHERE id = '"+id+"'")
    colaboradores = conx_rh.execute(query).fetchall()
    if request.method=='GET':
        return render_template("banco/edit_colaborador.html", colaboradores=colaboradores, id=id_usuario, nivel=nivel)
    if request.method=='POST':
        colaborador=request.form.get('colaborador')
        departamento=request.form.get('departamento')
        matricula=request.form.get('matricula')
        conx_rh.execute("UPDATE colaboradores SET colaborador = '"+colaborador+"', matricula = '"+matricula+"', departamento = '"+departamento+"' WHERE id = '"+id+"'")
        conx_rh.commit()
        return redirect(url_for("colaboradores"))
    query = ("SELECT TOP 1 * FROM colaboradores WHERE id = '"+id+"'")
    colaboradores = conx_rh.execute(query).fetchall()
    return render_template("banco/edit_colaborador.html", colaboradores=colaboradores, id=id_usuario, nivel=nivel)

@app.route("/colaboradores")
def colaboradores():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    query = ("SELECT * FROM colaboradores ORDER BY id")
    colaboradores = conx_rh.execute(query).fetchall()
    return render_template("banco/colaborador.html", colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/ausencia/<string:id_usuario>", methods=["GET", "POST"])
def ausencia(id_usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    query = ("SELECT TOP 1 * FROM colaboradores WHERE id = '"+id_usuario+"'")
    colaboradores = conx_rh.execute(query).fetchall()
    if request.method=='GET':
        return render_template("banco/criar_hora.html", colaboradores=colaboradores, id=id, nivel=nivel)
    if request.method=='POST':
        colaborador=request.form.get('colaborador')
        departamento=request.form.get('departamento')
        matricula=request.form.get('matricula')
        data=request.form.get('data')
        tipo_ausencia=request.form.get('tipo_ausencia')
        motivo=request.form.get('motivo')
        periodo_ausencia=request.form.get('periodo_ausencia')
        gerencia=request.form.get('gerencia')
        responsavel=str(id)
        conx_rh.execute(f"""INSERT INTO ausencia ( colaborador, matricula , departamento, data , tipo_ausencia , motivo  , periodo_ausencia , gerencia, responsavel) 
                        VALUES ('{colaborador}',  '{matricula}',   '{departamento}', '{data}', '{tipo_ausencia}', '{motivo}', '{periodo_ausencia}',   '{gerencia}', '{responsavel}')""")
        conx_rh.commit()
        return redirect(url_for("colaboradores"))
    return render_template("banco/criar_hora.html",  colaboradores=colaboradores, id=id, nivel=nivel)

@app.route("/adcionar/<string:id_usuario>", methods=["GET", "POST"])
def adcionar_horas(id_usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    query = ("SELECT TOP 1 * FROM colaboradores WHERE id = '"+id_usuario+"'")
    colaboradores = conx_rh.execute(query).fetchall()
    if request.method=='GET':
        return render_template("banco/criar_hora_banco.html", colaboradores=colaboradores, id=id, nivel=nivel)
    if request.method=='POST':
        colaborador=request.form.get('colaborador')
        area=request.form.get('area')
        matricula=request.form.get('matricula')
        data=request.form.get('data')
        atividade=request.form.get('atividade')
        periodo=request.form.get('periodo')
        responsavel=str(id)
        conx_rh.execute("INSERT INTO banco (colaborador,  matricula , area  , data  , atividade, periodo , responsavel ) VALUES ('"+colaborador+"', '"+matricula+"', '"+area+"', '"+data+"',  '"+atividade+"',  '"+periodo+"', '"+responsavel+"')")
        conx_rh.commit()
        return redirect(url_for("colaboradores"))
    return render_template("banco/criar_hora_banco.html", colaboradores=colaboradores, id=id, nivel=nivel)

@app.route("/edit_ausencia/<string:id_usuario>", methods=["GET", "POST"])
def edit_ausencia(id_usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    query = ("SELECT TOP 1 * FROM ausencia WHERE id = '"+id_usuario+"'")
    colaboradores = conx_rh.execute(query).fetchall()
    if request.method=='GET':
        return render_template("banco/edit_hora.html", colaboradores=colaboradores, id=id, nivel=nivel)
    if request.method=='POST':
        colaborador=request.form.get('colaborador')
        departamento=request.form.get('departamento')
        matricula=request.form.get('matricula')
        data=request.form.get('data')
        tipo_ausencia=request.form.get('tipo_ausencia')
        motivo=request.form.get('motivo')
        periodo_ausencia=request.form.get('periodo_ausencia')
        gerencia=request.form.get('gerencia')
        responsavel=str(id)
        conx_rh.execute(f"""UPDATE ausencia SET colaborador = '{colaborador}', matricula = '{matricula}', 
                        departamento = '{departamento}', data = '{data}', tipo_ausencia = '{tipo_ausencia}', 
                        motivo = '{motivo}', periodo_ausencia = '{periodo_ausencia}', gerencia = '{gerencia}', 
                        responsavel = '{responsavel}' WHERE id = '{id_usuario}'""")
        conx_rh.commit()
        return redirect(url_for("banco", id=id))
    return render_template("banco/edit_hora.html",  colaboradores=colaboradores, id=id, nivel=nivel)

@app.route("/edit_adcionar/<string:id_usuario>", methods=["GET", "POST"])
def edit_adcionar(id_usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    query = ("SELECT TOP 1 * FROM banco WHERE id = '"+id_usuario+"'")
    colaboradores = conx_rh.execute(query).fetchall()
    if request.method=='GET':
        return render_template("banco/edit_banco.html", colaboradores=colaboradores, id=id, nivel=nivel)
    if request.method=='POST':
        colaborador=request.form.get('colaborador')
        area=request.form.get('area')
        matricula=request.form.get('matricula')
        data=request.form.get('data')
        atividade=request.form.get('atividade')
        periodo=request.form.get('periodo')
        responsavel=str(id)
        conx_rh.execute(f"""UPDATE banco SET colaborador = '{colaborador}', matricula = '{matricula}', 
                        area = '{area}', data = '{data}', atividade = '{atividade}', periodo = '{periodo}', 
                        responsavel = '{responsavel}' WHERE id = '{id_usuario}'""")
        conx_rh.commit()
        return redirect(url_for("ausencia_horas", id=id))
    return render_template("banco/edit_banco.html", colaboradores=colaboradores, id=id, nivel=nivel)

@app.route("/delete_colaborador/<string:id>",methods=['GET'])
def delete_colaboradores(id):
    conx_rh.execute("DELETE FROM colaboradores WHERE id = '"+id+"'")
    conx_rh.commit()
    flash('User Deleted','warning')
    flash('computador Deleted','warning')
    return redirect(url_for("colaboradores"))

@app.route("/delete_ausencia/<string:id>",methods=['GET'])
def delete_ausencia(id):
    conx_rh.execute("DELETE FROM ausencia WHERE id = '"+id+"'")
    conx_rh.commit()
    flash('User Deleted','warning')
    return redirect(url_for("colaboradores"))

@app.route("/delete_banco/<string:id>",methods=['GET'])
def delete_banco(id):
    conx_rh.execute("DELETE FROM banco WHERE id = '"+id+"'")
    conx_rh.commit()
    flash('User Deleted','warning')
    return redirect(url_for("colaboradores"))

@app.route("/banco/<string:id>")
def banco(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    dados = conx_rh.execute("SELECT * FROM ausencia WHERE responsavel = '"+id+"'").fetchall()
    dados_banco = conx_rh.execute("SELECT * FROM banco WHERE responsavel = '"+id+"'").fetchall()
    return render_template("banco/banco_horas.html", dados=dados, dados_banco=dados_banco, nivel=nivel, id=id_usuario)

@app.route("/ausencia_horas/<string:id>")
def ausencia_horas(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    dados_banco = conx_rh.execute("SELECT * FROM banco WHERE responsavel = '"+id+"'").fetchall()
    return render_template("banco/ausencia_horas.html",  dados_banco=dados_banco, nivel=nivel, id=id_usuario)


@app.route("/ausencia_form/<string:id>")
def ausencia_form(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if int(id) == conx_rh.execute("SELECT * FROM ausencia WHERE id = '"+id+"'").fetchall():
        return render_template("banco/formulario_ausencia.html", nivel=nivel, id=id_usuario)
    else:
        dados =  conx_rh.execute("SELECT * FROM ausencia WHERE id = '"+id+"'").fetchall()
        return render_template("banco/formulario_ausencia.html", dados=dados, nivel=nivel, id=id_usuario)
    
@app.route("/banco_form/<string:id>")
def banco_form(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    dados = conx_rh.execute("SELECT * FROM banco WHERE id = '"+id+"'").fetchall()
    return render_template("banco/formulario_banco.html", dados=dados, nivel=nivel, id=id_usuario)
    
