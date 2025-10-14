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
from inventarioapema.conexao import conx, caminho, conx_mes, conx_man

cursor = conn.cursor()

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

@app.route("/dashboard_pesquisa", methods=['GET', "POST"])
def dashboard_pesquisa():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    email = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuario_por_nome = database.session.query(database.func.count (Manutencao.id), Manutencao.username).group_by(Manutencao.username).order_by(database.func.count(Manutencao.username)).all()
    username =  database.session.query(database.func.count(Manutencao.id), Manutencao.username).group_by(Manutencao.username).order_by(Manutencao.username).all()
    tipo_de_label = database.session.query(database.func.count (Materiais.id), Materiais.localizacao).group_by(Materiais.localizacao).order_by(database.func.count(Materiais.localizacao)).all()
    equipamentos_de_label = database.session.query(database.func.count (Manutencao.id), Manutencao.tipo).group_by(Manutencao.tipo).order_by(database.func.count(Manutencao.tipo)).all()
    chamados_de_label = database.session.query(database.func.count (Manutencao.id), Manutencao.status).group_by(Manutencao.status).order_by(database.func.count(Manutencao.status)).all()   
    departamentos =  database.session.query(database.func.count(Manutencao.id), Manutencao.tipo).group_by(Manutencao.tipo).order_by(Manutencao.tipo).all()
    tipo =  database.session.query(database.func.count(Materiais.id), Materiais.localizacao).group_by(Materiais.localizacao).order_by(Materiais.localizacao).all()
    ativosstatus = database.session.query(database.func.count(Manutencao.id), Manutencao.status).group_by(Manutencao.status).order_by((Manutencao.status)).all()

    depart = []
    for amount, username in usuario_por_nome:
        depart.append(username)

    usuarios = []
    for ido, _ in usuario_por_nome:
        usuarios.append(ido)

    chamados = []
    for total_id, _ in departamentos:
        chamados.append(total_id)

    status = []
    for ides, _ in ativosstatus:
        status.append(ides)

    equipa = []
    for total, label in departamentos:
        equipa.append(label)

    cham = []
    for old, total in ativosstatus:
        cham.append(total)
    return render_template("grafico/dashboard_manutencao.html",  nivel=nivel, id=id,
                        chamados = json.dumps(chamados),
                            usuarios = json.dumps(usuarios),
                                status = json.dumps(status),
                                depart = json.dumps(depart),
                                equipa = json.dumps(equipa),
                                cham = json.dumps(cham))

@app.route("/dashboard_manutencao", methods=['GET', "POST"])
def dashboard_manutencao():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    email = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'POST':
        data_criacao = request.form.get('data_criacao')
        data_fim = request.form.get('data_fim')
        session['data_criacao'] = data_criacao
        session['data_fim'] = data_fim
    data_criacao = session['data_criacao']
    data_fim = session['data_fim']
    if data_criacao is not "":
        componente = datetime.strptime(data_criacao,  "%Y-%m-%d").date()
    if data_fim is not "":
        componente_final = datetime.strptime(data_fim,  "%Y-%m-%d").date()
    rows = conx_man.execute("SELECT  sum(total), count(id) FROM manutencao  WHERE data_criacao BETWEEN '"+data_criacao+"'  AND  '"+data_fim+"'").fetchall()
    producaos = conx_man.execute("SELECT  sum(total), count(id) FROM manutencao  WHERE data_criacao BETWEEN '"+data_criacao+"'  AND  '"+data_fim+"' AND tipo = 'Equipamento'").fetchall()
    usuario_por_nome = conx_man.execute("SELECT count(manutencao.id) AS count_1, manutencao.username AS manutencao_username FROM manutencao WHERE manutencao.data_criacao >= '"+data_criacao+"' AND manutencao.data_criacao <= '"+data_fim+"' GROUP BY manutencao.username ORDER BY count(manutencao.username)").fetchall()
    username =  conx_man.execute("SELECT count(manutencao.id) AS count_1, manutencao.username AS manutencao_username FROM manutencao WHERE manutencao.data_criacao >= '"+data_criacao+"' AND manutencao.data_criacao <= '"+data_fim+"' GROUP BY manutencao.username ORDER BY manutencao.username").fetchall()
    departamentos =  conx_man.execute("SELECT count(manutencao.id) AS count_1, manutencao.tipo AS manutencao_tipo FROM manutencao WHERE manutencao.data_criacao >= '"+data_criacao+"' AND manutencao.data_criacao <= '"+data_fim+"' GROUP BY manutencao.tipo ORDER BY manutencao.tipo").fetchall()
    ativosstatus = conx_man.execute("SELECT count(manutencao.id) AS count_1, manutencao.status AS manutencao_status FROM manutencao WHERE manutencao.data_criacao >= '"+data_criacao+"' AND manutencao.data_criacao <= '"+data_fim+"' GROUP BY manutencao.status ORDER BY manutencao.status").fetchall()
    depart = []
    for amount, username in usuario_por_nome:
        depart.append(username)

    usuarios = []
    for ido, _ in usuario_por_nome:
        usuarios.append(ido)

    chamados = []
    for total_id, _ in departamentos:
        chamados.append(total_id)

    status = []
    for ides, _ in ativosstatus:
        status.append(ides)

    equipa = []
    for total, label in departamentos:
        equipa.append(label)

    cham = []
    for old, total in ativosstatus:
        cham.append(total)
    query_predial = "SELECT id, username, email, departamento, tipo, status, operacao, data_criacao, concat(data_inicio, ' ', hora_inicio) as inicio,  concat(data_final, ' ', hora_final) as fim, indisponibilidade, indisponibilidade_manutencao from manutencao WHERE data_criacao BETWEEN '"+data_criacao+"'  AND  '"+data_fim+"'"
    query = "SELECT id, username, email, departamento, tipo, status, operacao, data_criacao, concat(data_inicio, ' ', hora_inicio) as inicio,  concat(data_final, ' ', hora_final) as fim, indisponibilidade,  indisponibilidade_manutencao from manutencao WHERE  tipo = 'Equipamento' and data_criacao BETWEEN '"+data_criacao+"'  AND  '"+data_fim+"' "
    exc = pd.read_sql(query, conx_man)
    exce = pd.read_sql(query_predial, conx_man)
    exc.to_excel(caminho+"chamados_equipamentos.xlsx", index=False)
    exce.to_excel(caminho+"periodo_de_tempo.xlsx", index=False)
    return render_template("grafico/dashboard_manutencao.html", rows=rows, producaos=producaos,
                           data_criacao=data_criacao, nivel=nivel, id=id,
                           data_fim=data_fim,
                                chamados = json.dumps(chamados),
                                    usuarios = json.dumps(usuarios),
                                        status = json.dumps(status),
                                        depart = json.dumps(depart),
                                        equipa = json.dumps(equipa),
                                        cham = json.dumps(cham))


@app.route("/dashboard_inventario")
def dashboard_inventario():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    email = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    departamentos = database.session.query(database.func.count(Computadores.id), Computadores.memoria).group_by(Computadores.memoria).order_by(Computadores.memoria).all()
    tipo_de_label = database.session.query(database.func.count(Computadores.id), Computadores.disco_rigido).group_by(Computadores.disco_rigido).order_by(Computadores.disco_rigido).all()
    impre = database.session.query(database.func.count(Impressora.id), Impressora.modelo_impressora).group_by(Impressora.modelo_impressora).order_by(Impressora.modelo_impressora).all()
    tipo = database.session.query(database.func.count(Computadores.id), Computadores.tipo).group_by(Computadores.tipo).order_by(database.func.count(Computadores.tipo)).all()
    ativosstatus = database.session.query(database.func.count(Computadores.id), Computadores.processador).group_by(Computadores.processador).order_by((Computadores.processador)).all()
    ativos = database.session.query(database.func.count(Computadores.id)).all()
    desativado = database.session.query(database.func.count(Antenas.id)).all()
    concluido = database.session.query(database.func.count(Cameras.id)).all()
    impres = database.session.query(database.func.count(Impressora.id)).all()
    aberto = database.session.query(database.func.sum(Toners.quant_toners)).all()
    ant = database.session.query(database.func.count(Antenas.id), Antenas.antenas).group_by(Antenas.antenas).order_by(Antenas.antenas).all()
    linha = database.session.query(database.func.count(Chamados.status), Chamados.data_criacao).group_by(Chamados.data_criacao).order_by(Chamados.data_criacao).all()
    ton = database.session.query(database.func.sum(Toners.quant_toners), Toners.toners).group_by(Toners.toners).order_by(Toners.toners).all()
    cam = database.session.query(database.func.sum(Cameras.quant_cameras), Cameras.cameras).group_by(Cameras.cameras).order_by(Cameras.cameras).all()

    usuarios = []
    for ido, _ in tipo:
        usuarios.append(ido)

    chamados = []
    for total_id, _ in departamentos:
        chamados.append(total_id)

    status = []
    for ides, _ in ativosstatus:
        status.append(ides)

    grafico = []
    for total, _ in linha:
        grafico.append(total)

    depart = []
    for amount, _ in tipo_de_label:
        depart.append(amount)
        
    impressoras = []
    for barra, _ in impre:
        impressoras.append(barra)

    antenas = []
    for anti, _ in ant:
        antenas.append(anti)

    toners = []
    for tonn, _ in ton:
        toners.append(tonn)

    cameras = []
    for came, _ in cam:
        cameras.append(came)

    

    return render_template("grafico/dashboard_inventario.html", nivel=nivel, id=id,
                           chamados = json.dumps(chamados),
                            grafico = json.dumps(grafico),
                              usuarios = json.dumps(usuarios),
                                status = json.dumps(status),
                                  depart = json.dumps(depart),
                                    ativos=ativos, desativado=desativado, concluido=concluido, aberto=aberto, impres=impres, 
                                      impressoras = json.dumps(impressoras),
                                        antenas = json.dumps(antenas),
                                            toners = json.dumps(toners),
                                            cameras = json.dumps(cameras))
    
@app.route("/dashboard_adm", methods=['GET', "POST"])
def dashboard_adm():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    email = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    tipo_de_label =  conx.execute("SELECT  COUNT(id), departamento FROM chamados WHERE  id > '448' group by departamento").fetchall()
    impre = database.session.query(database.func.count(Impressora.id), Impressora.modelo_impressora).group_by(Impressora.modelo_impressora).order_by(Impressora.modelo_impressora).all()
    departamentos = conx.execute("SELECT  COUNT(id), tipo FROM chamados WHERE  id > '448' group by tipo").fetchall()
    tipo = conx.execute("SELECT  COUNT(id), departamento FROM chamados WHERE  id > '448' group by departamento").fetchall()
    ativosstatus = conx.execute("SELECT  COUNT(id), status FROM chamados WHERE  id > '448' group by status").fetchall()
    ativos = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'novo' and  id > '448'   ").fetchall()
    desativado = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'atribuido' and  id > '448'    ").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'fechado' and  id > '448'  ").fetchall()
    aberto = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'reaberto' and  id > '448'  ").fetchall()
    ant = database.session.query(database.func.count(Antenas.id), Antenas.antenas).group_by(Antenas.antenas).order_by(Antenas.antenas).all()
    linha = database.session.query(database.func.count(Chamados.status), Chamados.data_criacao).group_by(Chamados.data_criacao).order_by(Chamados.data_criacao).all()
    ton = conx.execute("SELECT  sum(quant_toners), toners FROM toners where  id > '448'  group by toners ").fetchall()
    cam = conx.execute("SELECT  sum(quant_cameras), cameras FROM cameras where  id > '448' group by cameras").fetchall()
    chamados_de_label = conx.execute("SELECT  COUNT(id), status FROM chamados WHERE  id > '448' group by status").fetchall()
    resolvido = conx.execute("SELECT  COUNT(id), atribuido FROM chamados WHERE  id > '448' group by atribuido").fetchall()

    tecnico=[]
    for resolucao, _ in resolvido:
        tecnico.append(resolucao)

    tecnico_label=[]
    for resolucao, label_tecnico in resolvido:
        tecnico_label.append(label_tecnico)

    usuarios = []
    for ido, _ in tipo:
        usuarios.append(ido)

    chamados = []
    for total_id, _ in departamentos:
        chamados.append(total_id)

    status = []
    for ides, _ in ativosstatus:
        status.append(ides)

    grafico = []
    for total, _ in linha:
        grafico.append(total)

    depart = []
    for amount, departamento in tipo_de_label:
        depart.append(departamento)
        
    impressoras = []
    for barra, _ in impre:
        impressoras.append(barra)

    antenas = []
    for anti, _ in ant:
        antenas.append(anti)

    toners = []
    for tonn, _ in ton:
        toners.append(tonn)

    cameras = []
    for came, _ in cam:
        cameras.append(came)
        
    cham = []
    for amounts, chama in chamados_de_label:
        cham.append(chama)

    label = []
    for total, legend in departamentos:
        label.append(legend)

    return render_template("grafico/dashboard.html", nivel=nivel, id=id,
                           chamados = json.dumps(chamados),
                            grafico = json.dumps(grafico),
                              usuarios = json.dumps(usuarios),
                                status = json.dumps(status),
                                  depart = json.dumps(depart),
                                    ativos=ativos, desativado=desativado, concluido=concluido, aberto=aberto,
                                      impressoras = json.dumps(impressoras),
                                        antenas = json.dumps(antenas),
                                            toners = json.dumps(toners),
                                            label = json.dumps(label),
                                            tecnico = json.dumps(tecnico),
                                            tecnico_label = json.dumps(tecnico_label),
                                            cameras = json.dumps(cameras))

@app.route("/dashboard", methods=['GET', "POST"])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    email = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'POST':
        data_criacao = request.form.get('data_criacao')
        data_fim = request.form.get('data_fim')
        session['data_criacao'] = data_criacao
        session['data_fim'] = data_fim
    data_criacao = session['data_criacao']
    data_fim = session['data_fim']
    if data_criacao is not "":
        componente = datetime.strptime(data_criacao,  "%Y-%m-%d").date()
    if data_fim is not "":
        componente_final = datetime.strptime(data_fim,  "%Y-%m-%d").date()
    tipo_de_label = database.session.query(database.func.count (Chamados.id), Chamados.departamento).group_by(Chamados.departamento).order_by(database.func.count(Chamados.departamento)).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    impre = database.session.query(database.func.count(Impressora.id), Impressora.modelo_impressora).group_by(Impressora.modelo_impressora).order_by(Impressora.modelo_impressora).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    departamentos = database.session.query(database.func.count(Chamados.id), Chamados.tipo).group_by(Chamados.tipo).order_by(database.func.count(Chamados.id), Chamados.tipo).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    tipo = database.session.query(database.func.count(Chamados.id), Chamados.departamento).group_by(Chamados.departamento).order_by(database.func.count(Chamados.departamento)).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    ativosstatus = database.session.query(database.func.count(Chamados.id), Chamados.status).group_by(Chamados.status).order_by((Chamados.status)).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    ativos = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'novo' AND data_criacao BETWEEN '"+data_criacao+"'  AND  '"+data_fim+"'").fetchall()
    desativado = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'atribuido' AND data_criacao BETWEEN '"+data_criacao+"'  AND  '"+data_fim+"'").fetchall()
    concluido = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'fechado' AND data_criacao BETWEEN '"+data_criacao+"'  AND  '"+data_fim+"'").fetchall()
    aberto = conx.execute("SELECT  COUNT(id) FROM chamados WHERE status = 'reaberto' AND data_criacao BETWEEN '"+data_criacao+"'  AND  '"+data_fim+"'").fetchall()
    ant = database.session.query(database.func.count(Antenas.id), Antenas.antenas).group_by(Antenas.antenas).order_by(Antenas.antenas).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    linha = database.session.query(database.func.count(Chamados.status), Chamados.data_criacao).group_by(Chamados.data_criacao).order_by(Chamados.data_criacao).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    ton = database.session.query(database.func.sum(Toners.quant_toners), Toners.toners).group_by(Toners.toners).order_by(Toners.toners).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    cam = database.session.query(database.func.sum(Cameras.quant_cameras), Cameras.cameras).group_by(Cameras.cameras).order_by(Cameras.cameras).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    chamados_de_label = database.session.query(database.func.count (Chamados.id), Chamados.tipo).group_by(Chamados.tipo).order_by(database.func.count(Chamados.tipo)).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()
    resolvido = database.session.query(database.func.count(Chamados.id), Chamados.atribuido).group_by(Chamados.atribuido).order_by(database.func.count(Chamados.atribuido)).where(Chamados.data_criacao >= componente).where(Chamados.data_criacao <= componente_final).all()

    tecnico=[]
    for resolucao, _ in resolvido:
        tecnico.append(resolucao)

    tecnico_label=[]
    for resolucao, label_tecnico in resolvido:
        tecnico_label.append(label_tecnico)

    usuarios = []
    for ido, _ in tipo:
        usuarios.append(ido)

    chamados = []
    for total_id, _ in departamentos:
        chamados.append(total_id)

    status = []
    for ides, _ in ativosstatus:
        status.append(ides)

    grafico = []
    for total, _ in linha:
        grafico.append(total)

    depart = []
    for amount, departamento in tipo_de_label:
        depart.append(departamento)
        
    impressoras = []
    for barra, _ in impre:
        impressoras.append(barra)

    antenas = []
    for anti, _ in ant:
        antenas.append(anti)

    toners = []
    for tonn, _ in ton:
        toners.append(tonn)

    cameras = []
    for came, _ in cam:
        cameras.append(came)
        
    cham = []
    for amounts, chama in chamados_de_label:
        cham.append(chama)

    label = []
    for total, legend in departamentos:
        label.append(legend)

    return render_template("grafico/dashboard.html", data_criacao=data_criacao, data_fim=data_fim, id=id, nivel=nivel,
                           chamados = json.dumps(chamados),
                            grafico = json.dumps(grafico),
                              usuarios = json.dumps(usuarios),
                                status = json.dumps(status),
                                  depart = json.dumps(depart),
                                    ativos=ativos, desativado=desativado, concluido=concluido, aberto=aberto,
                                      impressoras = json.dumps(impressoras),
                                        antenas = json.dumps(antenas),
                                            toners = json.dumps(toners),
                                            label = json.dumps(label),
                                            tecnico = json.dumps(tecnico),
                                            tecnico_label = json.dumps(tecnico_label),
                                            cameras = json.dumps(cameras))