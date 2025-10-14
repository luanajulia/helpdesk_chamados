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
from inventarioapema.conexao import conx, conx_man

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

@app.route("/chamados")
def chamados():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM  chamados where id > '422' ORDER BY id DESC ").fetchall()
    ativosstatus =conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'novo'and  id > '422' ").fetchall()
    desativado = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'atribuido' and id > '422' ").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'fechado' and id > '422'").fetchall()
    aberto = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'reaberto' and id > '422'").fetchall()
    return render_template("chamados/chamados.html", chamados=chamados, ativosstatus=ativosstatus, desativado=desativado, concluido=concluido, aberto=aberto, nivel=nivel, id=id)

@app.route("/portal_adm/<id_usuario>", methods=["GET", "POST"])
def portal_adm(id_usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    query = ("SELECT TOP 1 * FROM usuario WHERE id = '"+id_usuario+"' ")
    usuarios =  conx.execute(query).fetchall()
    for usuario in usuarios:
        if request.method=='GET':
            return render_template("chamados/portal.html", usuarios=usuarios, nivel=nivel)
        if request.method == 'POST':
            horas=datetime.now().strftime('%d/%m/%Y %H:%M')
            username=usuario[1]
            departamento=usuario[4]
            email=usuario[2]
            tipo=request.form.get('tipo')
            status=request.form.get('status')
            descricao=request.form.get('descricao')
            conx.execute(f"""INSERT INTO chamados (username, departamento, email, tipo, status, descricao, id_usuario, data_criacao) VALUES  
                         ('{username}', '{departamento}', '{email}', '{tipo}', '{status}', '{descricao}', '{id_usuario}', '{horas}' ) """)
            conx.commit()
            return redirect(url_for("historico", id_usuario=id_usuario))
    return render_template("chamados/portal.html", usuarios=usuarios, nivel=nivel)

@app.route("/historico/<id_usuario>")
def historico(id_usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados  WHERE id_usuario = '"+id_usuario+"'   ").fetchall()
    historico = conx_man.execute("SELECT  *, CONVERT (DATE, data_criacao) AS datas FROM manutencao  WHERE id_usuario = '"+id_usuario+"' ").fetchall()
    return render_template("chamados/historico.html", chamados=chamados, historico=historico, nivel=nivel, id=id)

@app.route("/portal/<id_usuario>", methods=["GET", "POST"])
def portal(id_usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    query = ("SELECT TOP 1 * FROM usuario WHERE id = '"+id_usuario+"' ")
    usuarios =  conx.execute(query).fetchall()
    for usuario in usuarios:
        if request.method=='GET':
            return render_template("chamados/portal.html", usuarios=usuarios, nivel=nivel, id=id)
        if request.method == 'POST':
            horas=datetime.now().strftime('%d/%m/%Y %H:%M')
            username=usuario[1]
            departamento=usuario[4]
            email=usuario[2]
            tipo=request.form.get('tipo')
            status=request.form.get('status')
            descricao=request.form.get('descricao')
            conx.execute(f"""INSERT INTO chamados (username, departamento, email, tipo, status, descricao, id_usuario, data_criacao) VALUES 
                          ('{username}', '{departamento}', '{email}', '{tipo}', '{status}', '{descricao}', '{id_usuario}', '{horas}' ) """)
            conx.commit()
            msg = Message("Novo Chamado",  sender = app.config.get("MAIL_USERNAME"), recipients= ['suporte@apema.com.br', 'marcopessolato@apema.com.br', 'nicolascaminada@apema.com.br', 'luanavieira@apema.com.br'])
            msg.body = f''' 
Ola Voce tem um novo chamado de {username},\n
{username} esta com problema de: {tipo},\n
Descrição: {descricao}\n
Este é seu E-mail: {email}, seu chamado foi registrado no dia: {horas}\n
Clique aqui para ir até o chamado: http://192.168.1.51:8090
'''
            mail.send(msg)
            return redirect(url_for("historico", id_usuario=id_usuario))
    return render_template("chamados/portal.html", usuarios=usuarios, nivel=nivel, id=id)



@app.route("/edit_chamados/<string:id>",methods=['POST','GET'])
def edit_chamados(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id'] 
    usuario = Usuario.query.order_by(Usuario.nivel).all()
    query = ("SELECT TOP 1 * FROM chamados WHERE id = '"+id+"'")
    chamados =  conx.execute(query).fetchall()
    if request.method=='GET':
        return render_template("chamados/edit_chamados.html",chamados=chamados, usuario=usuario, nivel=nivel, id=id_usuario)
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        departamento=request.form.get('departamento')
        tipo=request.form.get('tipo')
        status=request.form.get('status')
        atribuido=request.form.get('atribuido')
        feedback=request.form.get('feedback')
        conx.execute("UPDATE chamados SET username = '"+username+"', email = '"+email+"', departamento = '"+departamento+"', tipo = '"+tipo+"', status = '"+status+"', atribuido = '"+atribuido+"', feedback = '"+feedback+"' WHERE id = '"+id+"'")
        conx.commit()
        if status == 'atribuido':
            msg = Message("Novo Chamado",  sender = app.config.get("MAIL_USERNAME"), recipients= [f'''{email}'''])
            msg.body = f''' 
Ola Seu chamado sobre: {tipo},\n
Esta sendo acompanhado por: {atribuido},\n
Retorno: {feedback},\n
Clique aqui para ir até o chamado: http://192.168.1.51:8090 \n
Obrigada pela Atenção :) \n
Tenha um Otimo Trabalho 
'''
            mail.send(msg)   
        if status == 'fechado':
            msg = Message("Novo Chamado",  sender = app.config.get("MAIL_USERNAME"), recipients= [f'''{email}'''])
            msg.body = f''' 
Ola Seu chamado sobre: {tipo},\n
Foi Fechado,\n
Retorno: {feedback},\n
Clique aqui para ir até o chamado: http://192.168.1.51:8090 \n
Obrigada pela Atenção :) \n
Tenha um Otimo Trabalho 
'''
            mail.send(msg) 
        return redirect(url_for("chamados")) 
    query = ("SELECT TOP 1 * FROM chamados WHERE id = '"+id+"'")
    chamados =  conx.execute(query).fetchall()
    usuario = Usuario.query.order_by(Usuario.nivel).all()
    return render_template("chamados/edit_chamados.html",chamados=chamados, usuario=usuario,nivel=nivel, id=id_usuario)

@app.route("/edit_chamados_adm/<string:id>",methods=['POST','GET'])
def edit_chamados_adm(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id'] 
    usuario = Usuario.query.order_by(Usuario.nivel).all()
    query = ("SELECT TOP 1 * FROM chamados WHERE id = '"+id+"'")
    chamados =  conx.execute(query).fetchall()
    if request.method=='GET':
        return render_template("chamados/edit_chamados_user.html",chamados=chamados, usuario=usuario, nivel=nivel, id=id_usuario)
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        departamento=request.form.get('departamento')
        tipo=request.form.get('tipo')
        status=request.form.get('status')
        atribuido=request.form.get('atribuido')
        feedback=request.form.get('feedback')
        conx.execute("UPDATE chamados SET username = '"+username+"', email = '"+email+"', departamento = '"+departamento+"', tipo = '"+tipo+"', status = '"+status+"', atribuido = '"+atribuido+"', feedback = '"+feedback+"' WHERE id = '"+id+"'")
        conx.commit()
        return redirect(url_for("chamados"))    
    query = ("SELECT TOP 1 * FROM chamados WHERE id = '"+id+"'")
    chamados =  conx.execute(query).fetchall()
    usuario = Usuario.query.order_by(Usuario.nivel).all()
    return render_template("chamados/edit_chamados_user.html",chamados=chamados, nivel=nivel, id=id_usuario)

@app.route("/delete_chamados/<string:id>",methods=['GET'])
def delete_chamados(id):
    conx.execute("DELETE FROM chamados WHERE id = '"+id+"'")
    conx.commit()
    flash('User Deleted','warning')
    return redirect(url_for("chamados"))


@app.route("/fila_de_espera")
def fila_de_espera():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados  WHERE  id > '448' ").fetchall()
    return render_template("chamados/fila_de_espera.html", chamados=chamados, nivel=nivel, id=id)

@app.route("/descricao/<string:id>")
def descricaoadm(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if int(id) == Chamados.query.get(int(id)):
        return render_template("chamados/descricao.html", descricao=descricao, nivel=nivel, id=id_usuario)
    else:
        descricao = Chamados.query.get(int(id))
        return render_template("chamados/descricao.html", descricao=descricao, nivel=nivel, id=id_usuario)

@app.route("/Atribuido/84")
def atribuidos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados WHERE status = 'atribuido' and atribuido = 'Luana Julia' and  id > '448'").fetchall()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'atribuido'   ").fetchall()
    return render_template("chamados/chamados.html", chamados=chamados, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/Atribuido")
def atribuidoss():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados  WHERE  id > '448'").fetchall()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'atribuido' and    id > '448'  ").fetchall()
    return render_template("chamados/chamados.html",chamados=chamados, ativosstatus=ativosstatus, nivel=nivel, id=id)


@app.route("/Atribuido/<atribuido>")
@login_required
def atribuido(atribuido):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados WHERE atribuido = '"+atribuido+"' AND status = 'atribuido'  and  id > '448'").fetchall()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'atribuido' and  id > '448'  ").fetchall()
    status="ATRIBUIDO"
    return render_template("chamados/chamados.html", chamados=chamados, ativosstatus=ativosstatus, nivel=nivel, id=id,  status=status)

@app.route("/Fechado")
def Fechado():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados where status = 'fechado' AND id > '448'").fetchall()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'fechado' and  id > '448' ").fetchall()
    status="FECHADO"
    return render_template("chamados/chamados.html", chamados=chamados, ativosstatus=ativosstatus, nivel=nivel, id=id, status=status)

@app.route("/Novo")
def Novo():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados where status = 'novo' AND  id > '448'").fetchall()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'novo' and  id > '448'  ").fetchall()
    status="NOVO"
    return render_template("chamados/chamados.html", chamados=chamados, ativosstatus=ativosstatus, nivel=nivel, id=id, status=status)

@app.route("/Reaberto")
def Reaberto():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados where status = 'reaberto' AND id > '448'").fetchall()
    ativosstatus = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'reaberto' and  id > '448'  ").fetchall()
    status="REABERTO"
    return render_template("chamados/chamados.html", chamados=chamados, ativosstatus=ativosstatus, nivel=nivel, id=id, status=status)

@app.route("/Computador")
def Computador_chamado():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados where  tipo = 'Computador' AND  id > '448'").fetchall()
    status="COMPUTADOR"
    return render_template("chamados/chamados.html", chamados=chamados, nivel=nivel, id=id, status=status)

@app.route("/Outro")
def Outros_chamados():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados where tipo = 'Outro' AND id > '448'").fetchall()
    status="OUTRO"
    return render_template("chamados/chamados.html", chamados=chamados, nivel=nivel, id=id, status=status)

@app.route("/Protheus")
def Protheus_chamados():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados where tipo = 'Protheus' AND id > '448'").fetchall()
    status="PROTHEUS"
    return render_template("chamados/chamados.html", chamados=chamados, nivel=nivel, id=id, status=status)

@app.route("/Rede")
def Rede_chamados():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados where tipo = 'Rede' AND id > '448'").fetchall()
    status="REDE"
    return render_template("chamados/chamados.html", chamados=chamados, nivel=nivel, id=id, status=status)

@app.route("/Telefone")
def Telefone_chamados():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados  where tipo = 'Telefone' AND  id > '448'").fetchall()
    status="TELEFONE"
    return render_template("chamados/chamados.html", chamados=chamados, nivel=nivel, id=id, status=status)

@app.route("/Toner")
def Toner_chamados():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados  where tipo = 'Toner' AND  id > '448'").fetchall()
    status="TONER"
    return render_template("chamados/chamados.html", chamados=chamados, nivel=nivel, id=id, status=status)


@app.route("/Impressora")
def Impressora_chamado():
    if not session.get('logged_in'):
            return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados  where tipo = 'Impressora' AND  id > '448'").fetchall()
    status="IMPRESSORA"
    return render_template("chamados/chamados.html", chamados=chamados, nivel=nivel, id=id, status=status)

@app.route("/tecnico/<atribuido>")
def tecnico(atribuido):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados WHERE atribuido = '"+atribuido+"' AND  id > '448'").fetchall()
    status=atribuido
    return render_template("chamados/chamados.html", chamados=chamados, nivel=nivel, id=id, status=status)

@app.route("/departamento/<string:departamento>")
def dashboard_departamento(departamento):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    chamados = conx.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM chamados WHERE departamento = '"+departamento+"' and id > '448'").fetchall()
    ativosstatus =conx.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'novo'  and id > '448'").fetchall()
    desativado = conx.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'atribuido'  and id > '448'").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'fechado'  and id > '448'").fetchall()
    aberto = conx.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'reaberto'  and id > '448' ").fetchall()
    return render_template("chamados/chamados.html", chamados=chamados, ativosstatus=ativosstatus, desativado=desativado, concluido=concluido, aberto=aberto, nivel=nivel, id=id_usuario)
