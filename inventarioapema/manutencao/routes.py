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
from inventarioapema.conexao import conx_manutencao, caminho,conx_mes, conx

def datetimeformat(value, format="%Y-%m-%d"):
    valor = datetime.strptime(value, '%Y-%m-%d')
    return valor.strftime(format)
jinja2.filters.FILTERS['datetimeformat'] = datetimeformat

def datetimeformat_completa(value, format="%d/%m/%Y %H:%M"):
    valor = datetime.strptime(value, '%d/%m/%Y %H:%M')
    return valor.strftime(format)
jinja2.filters.FILTERS['datetimeformat_completa'] = datetimeformat_completa

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




@app.route("/produtos", methods=['GET', 'POST'])
def produtos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if request.method == 'POST':
        produto = request.form.get('produto')
        session['produto'] = produto
    produto = session['produto']
    conx_manutencao.execute("SELECT  codigo, equipamento  FROM materiais WHERE codigo LIKE '%"+produto+"%'")
    rows = conx_manutencao.fetchall()
    acesso = Protheus.query.filter(Protheus.usuario == current_user.username).first()
    return render_template('manutencao/automatico.html', rows=rows, produto=produto, acesso=acesso, nivel=nivel, id=id_usuario)


@app.route("/manutencao/<id_usuario>", methods=["GET", "POST"])
def manutencao(id_usuario):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    query = ("SELECT TOP 1 * FROM usuario WHERE id = '"+id_usuario+"' ")
    usuarios =  conx.execute(query).fetchall()
    os = request.form.get('os')
    maquinas = conx.execute("select H1_CCUSTO, H1_CODIGO, H1_DESCRI, CTT_DESC01, CTT_CUSTO  from [192.168.1.16].[SIGA].[dbo].[SH1010]  right JOIN [192.168.1.16].[SIGA].[dbo].[CTT010] ON  CTT_CUSTO = H1_CCUSTO WHERE SH1010.D_E_L_E_T_ = ''").fetchall()
    for usuario in usuarios:
        if request.method=='GET':
            return render_template("manutencao/portal_manutencao.html",maquinas=maquinas, usuarios=usuarios, nivel=nivel, id=id)
        if request.method == 'POST':
            horas=datetime.now().strftime('%d/%m/%Y %H:%M')
            username=usuario[1]
            departamento=usuario[4]
            email=usuario[2]
            tipo=request.form.get('tipo')
            status=request.form.get('status')
            descricao=request.form.get('descricao')
            os=request.form.get('os')
            id_int=f'{id}'
            if os != "":
                maquinas = conx.execute("select H1_CCUSTO, H1_CODIGO, H1_DESCRI, CTT_DESC01, CTT_CUSTO  from [192.168.1.16].[SIGA].[dbo].[SH1010]  right JOIN [192.168.1.16].[SIGA].[dbo].[CTT010] ON  CTT_CUSTO = H1_CCUSTO WHERE SH1010.D_E_L_E_T_ = '' AND H1_CODIGO = '"+os+"'").fetchall()
                for maquina in maquinas:
                    equipamento=maquina[2]
                    localizacao=maquina[3]
                    conx_manutencao.execute("INSERT INTO manutencao (username, departamento, email, tipo, status, descricao, id_usuario, data_criacao, os, equipamento, localizacao) VALUES  ('"+username+"', '"+departamento+"', '"+email+"', '"+tipo+"', '"+status+"', '"+descricao+"', '"+id_int+"', '"+horas+"', '"+os+"', '"+equipamento+"', '"+localizacao+"' ) ")
                    conx_manutencao.commit()
                    return redirect(url_for("historico", id_usuario=id, os=os, id=id))
            conx_manutencao.execute("INSERT INTO manutencao (username, departamento, email, tipo, status, descricao, id_usuario, data_criacao) VALUES  ('"+username+"', '"+departamento+"', '"+email+"', '"+tipo+"', '"+status+"', '"+descricao+"', '"+id_int+"', '"+horas+"') ")
            conx_manutencao.commit()
        return redirect(url_for("historico", id_usuario=id, os=os, id=id))
    return render_template("manutencao/portal_manutencao.html",  usuarios=usuarios, os=os, maquinas=maquinas, id=id)



@app.route("/manutencao_portal")
def manutencao_portal():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx_manutencao.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM manutencao ORDER BY id DESC ").fetchall()
    ativosstatus =conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'novo' ").fetchall()
    desativado = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'atribuido' ").fetchall()
    concluido = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'fechado' ").fetchall()
    aberto = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'reaberto' ").fetchall()
    return render_template("manutencao/chamados_manutencao.html", chamados=chamados, ativosstatus=ativosstatus, desativado=desativado, concluido=concluido, aberto=aberto, nivel=nivel, id=id)

@app.route("/dados/<string:tipo>")
def dashboard_dados(tipo):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    chamados = conx_manutencao.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM manutencao where tipo = '"+tipo+"' ORDER BY id DESC ").fetchall()
    ativosstatus =conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'novo' ").fetchall()
    desativado = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'atribuido' ").fetchall()
    concluido = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'fechado' ").fetchall()
    aberto = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'reaberto' ").fetchall()
    conta = conx_manutencao.execute(f"""UPDATE manutencao SET indisponibilidade = CONCAT((DATEDIFF(MINUTE,  data_criacao, (concat(data_final, ' ', hora_final)))/ 60),'.', 
                                    FORMAT(((((FLOOR(RIGHT(hora_final, 2)) - FLOOR(RIGHT(data_criacao, 2)))/ 60) - FLOOR((FLOOR(RIGHT(hora_final, 2)) - 
                                    FLOOR(RIGHT(data_criacao, 2)))/ 60))*60),'0#')) where data_final  is not null; 
                                    update manutencao set indisponibilidade_manutencao = CONCAT((DATEDIFF(MINUTE,   concat(data_inicio, ' ', hora_inicio), 
                                    concat(data_final, ' ', hora_final))/ 60), ':', FORMAT(((((FLOOR(RIGHT(hora_final, 2)) - FLOOR(RIGHT(hora_inicio, 2)))/ 60) - 
                                    FLOOR((FLOOR(RIGHT(hora_final, 2)) - FLOOR(RIGHT(hora_inicio, 2)))/ 60))*60),'0#')) WHERE data_inicio is not null;""").commit()
    consulta = f"""SELECT id, username, email, departamento, tipo, status, operacao, data_criacao, 
                    concat(data_inicio, ' ', hora_inicio) as inicio,  concat(data_final, ' ', hora_final) as fim, 
                    indisponibilidade, indisponibilidade_manutencao  from manutencao   """
    exc = pd.read_sql(consulta, conx_mes)
    exc.to_excel(caminho+"arquivoquery.xlsx", index=False)
    return render_template("manutencao/chamados_manutencao.html", chamados=chamados, ativosstatus=ativosstatus, desativado=desativado, concluido=concluido, aberto=aberto, nivel=nivel, id=id_usuario)

@app.route("/usuario_manutencao/<string:username>")
def dashboard_usuario(username):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    chamados = conx_manutencao.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM manutencao where username = '"+username+"' ORDER BY id DESC ").fetchall()
    ativosstatus =conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'novo' ").fetchall()
    desativado = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'atribuido' ").fetchall()
    concluido = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'fechado' ").fetchall()
    aberto = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'reaberto' ").fetchall()
    conta = conx_manutencao.execute(f"""UPDATE manutencao SET indisponibilidade = CONCAT((DATEDIFF(MINUTE,  data_criacao, (concat(data_final, ' ', hora_final)))/ 60),'.', 
                                    FORMAT(((((FLOOR(RIGHT(hora_final, 2)) - FLOOR(RIGHT(data_criacao, 2)))/ 60) - FLOOR((FLOOR(RIGHT(hora_final, 2)) - 
                                    FLOOR(RIGHT(data_criacao, 2)))/ 60))*60),'0#'))  where data_final is not null; 
                                    update manutencao set indisponibilidade_manutencao = CONCAT((DATEDIFF(MINUTE,   concat(data_inicio, ' ', hora_inicio), 
                                    concat(data_final, ' ', hora_final))/ 60), ':', FORMAT(((((FLOOR(RIGHT(hora_final, 2)) - FLOOR(RIGHT(hora_inicio, 2)))/ 60) - 
                                    FLOOR((FLOOR(RIGHT(hora_final, 2)) - FLOOR(RIGHT(hora_inicio, 2)))/ 60))*60),'0#')) WHERE data_inicio is not null;""").commit()
    consulta = f"""SELECT id, username, email, departamento, tipo, status, operacao, data_criacao, 
                    concat(data_inicio, ' ', hora_inicio) as inicio,  concat(data_final, ' ', hora_final) as fim, 
                    indisponibilidade, indisponibilidade_manutencao  from manutencao"""    
    exc = pd.read_sql(consulta, conx_mes)
    exc.to_excel(caminho+"arquivoquery.xlsx", index=False)
    return render_template("manutencao/chamados_manutencao.html", chamados=chamados, ativosstatus=ativosstatus, desativado=desativado, concluido=concluido, aberto=aberto, nivel=nivel, id=id_usuario)

@app.route("/status/<string:status>")
def dashboard_status(status):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    chamados = conx_manutencao.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM manutencao where status = '"+status+"' ORDER BY id DESC ").fetchall()
    ativosstatus =conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'novo' ").fetchall()
    desativado = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'atribuido' ").fetchall()
    concluido = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'fechado' ").fetchall()
    aberto = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'reaberto' ").fetchall()
    conta = conx_manutencao.execute(f"""UPDATE manutencao SET indisponibilidade = CONCAT((DATEDIFF(MINUTE,  data_criacao, (concat(data_final, ' ', hora_final)))/ 60),'.', 
                                    FORMAT(((((FLOOR(RIGHT(hora_final, 2)) - FLOOR(RIGHT(data_criacao, 2)))/ 60) - FLOOR((FLOOR(RIGHT(hora_final, 2)) - 
                                    FLOOR(RIGHT(data_criacao, 2)))/ 60))*60),'0#'))  where data_final is not null; 
                                    update manutencao set indisponibilidade_manutencao = CONCAT((DATEDIFF(MINUTE,   concat(data_inicio, ' ', hora_inicio), 
                                    concat(data_final, ' ', hora_final))/ 60), ':', FORMAT(((((FLOOR(RIGHT(hora_final, 2)) - 
                                    FLOOR(RIGHT(hora_inicio, 2)))/ 60) - FLOOR((FLOOR(RIGHT(hora_final, 2)) - FLOOR(RIGHT(hora_inicio, 2)))/ 60))*60),'0#')) 
                                    WHERE data_inicio is not null;""").commit()
    consulta = f"""SELECT id, username, email, departamento, tipo, status, operacao, data_criacao, 
                    concat(data_inicio, ' ', hora_inicio) as inicio,  concat(data_final, ' ', hora_final) as fim, 
                    indisponibilidade, indisponibilidade_manutencao  from manutencao"""
    exc = pd.read_sql(consulta, conx_mes)
    exc.to_excel(caminho+"arquivoquery.xlsx", index=False)
    return render_template("manutencao/chamados_manutencao.html", chamados=chamados, ativosstatus=ativosstatus, desativado=desativado, concluido=concluido, aberto=aberto, nivel=nivel, id=id_usuario)


@app.route("/os_manutencao/<string:id>")
def os_manutencao(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if int(id) == conx_manutencao.execute("SELECT  * FROM manutencao WHERE id = '"+id+"' ").fetchall():
        return render_template("manutencao/OS_manutencao.html", nivel=nivel, id=id_usuario)
    else:
        querys = ("SELECT  * FROM manutencao WHERE id = '"+id+"' ")
        chamados = conx_manutencao.execute(querys).fetchall()
        return render_template("manutencao/OS_manutencao.html", chamados=chamados, nivel=nivel, id=id_usuario)
    
@app.route("/os_manutencao_completa/<string:id>")
def os_manutencao_completa(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if int(id) == conx_manutencao.execute("SELECT  * FROM manutencao WHERE id = '"+id+"' ").fetchall():
        return render_template("manutencao/os_manutencao_completo.html")
    else:
        querys = ("SELECT TOP 1 * FROM manutencao WHERE id = '"+id+"' ")
        chamados = conx_manutencao.execute(querys).fetchall()
        return render_template("manutencao/os_manutencao_itens.html", chamados=chamados, nivel=nivel, id= id_usuario)

@app.route("/descricao_manutencao/<string:id>")
def descricaoman(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if int(id) == Manutencao.query.get(int(id)):
        return render_template("manutencao/descricao.html", descricao=descricao, nivel=nivel, id=id_usuario)
    else:
        descricao = Manutencao.query.get(int(id))
        return render_template("manutencao/descricao.html", descricao=descricao, nivel=nivel, id=id_usuario)

@app.route("/edit_chamados_manutencao/<string:id>", methods=['POST','GET'])
def edit_chamados_manutencao(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM manutencao WHERE id = '"+id+"' ")
    manutencao = conx_manutencao.execute(query).fetchall()
    usuario = conx_manutencao.execute("SELECT  * FROM tecnico ").fetchall()
    protheus = conx_manutencao.execute("SELECT  * FROM protheus ").fetchall()
    if request.method=='GET':
        return render_template("manutencao/edit_manutencao.html", manutencaos=manutencao, id=id_usuario, protheus=protheus, usuario=usuario, nivel=nivel)
    if request.method=='POST':
        status=request.form.get('status')
        feedback=request.form.get('feedback')
        data_inicio=request.form.get('data_inicio')
        data_final=request.form.get('data_final')
        hora_inicio=request.form.get('hora_inicio')
        hora_final=request.form.get('hora_final')
        operacao=request.form.get('operacao')
        tecnico=request.form.get('tecnico')
        conx_manutencao.execute(f"""UPDATE manutencao SET  status = '{status}', 
                                feedback = '{feedback}', data_inicio = '{data_inicio}', 
                                data_final = '{data_final}', hora_inicio = '{hora_inicio}', 
                                hora_final = '{hora_final}', operacao = '{operacao}', 
                                tecnico = '{tecnico}' WHERE id = '{id}'""")
        conx_manutencao.commit()
        return redirect(url_for("manutencao_portal"))
    manutencao = conx_manutencao.execute(query).fetchall()
    usuario = conx_manutencao.execute("SELECT  * FROM tecnico ").fetchall()
    protheus = conx_manutencao.execute("SELECT  * FROM protheus ").fetchall()
    return render_template("manutencao/edit_manutencao.html", manutencaos=manutencao, id=id_usuario, protheus=protheus, nivel=nivel)

        
@app.route("/edit_chamados_publico/<string:id>", methods=['POST','GET'])
def edit_chamados_publico(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM manutencao WHERE id = '"+id+"' ")
    manutencao = conx_manutencao.execute(query).fetchall()
    usuario = conx_manutencao.execute("SELECT  * FROM tecnico ").fetchall()
    protheus = conx_manutencao.execute("SELECT  * FROM protheus ").fetchall()
    if request.method=='GET':
        return render_template("manutencao/edit_manutencao.html", manutencao=manutencao, id=id_usuario, protheus=protheus, usuario=usuario, nivel=nivel)  
    if request.method=='POST':
        username=request.form.get('username')
        departamento=request.form.get('departamento')
        email=request.form.get('email')
        tipo=request.form.get('tipo')
        status=request.form.get('status')
        feedback=request.form.get('feedback')
        data_inicio=request.form.get('data_inicio')
        data_final=request.form.get('data_final')
        hora_inicio=request.form.get('hora_inicio')
        hora_final=request.form.get('hora_final')
        operacao=request.form.get('operacao')
        tecnico=request.form.get('tecnico')
        conx_manutencao.execute(f"""UPDATE manutencao SET 
                                username = '{username}', email = '{email}', 
                                departamento = '{departamento}', tipo = '{tipo}', 
                                status = '{status}', feedback = '{feedback}', 
                                data_inicio = '{data_inicio}', data_final = '{data_final}', 
                                hora_inicio = '{hora_inicio}', hora_final = '{hora_final}', 
                                operacao = '{operacao}', tecnico = '{tecnico}' WHERE id = '{id}'""")
        conx_manutencao.commit()
        return redirect(url_for("manutencao_portal"))
    return render_template("manutencao/edit_manutencao.html", manutencao=manutencao, id=id_usuario, protheus=protheus, usuario=usuario, nivel=nivel)  


@app.route("/delete_os/<string:id>",methods=['GET'])
def delete_os(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    chamados = Manutencao.query.filter(Manutencao.id == id).first()
    database.session.delete(chamados)
    database.session.commit()
    flash('computador Deleted','warning')
    return redirect(url_for("manutencao_portal"))

@app.route("/protheus/<string:id>", methods=["GET", "POST"])
def protheus(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        session['codigo'] = codigo
    codigo = session['codigo'] 
    conn = pyodbc.connect('Driver={SQL Server};''Server=192.168.1.16;''Database=SIGA;''UID=SIGA;''PWD=SIGA')
    cursor = conn.cursor()
    cursor.execute("SELECT B1_COD, B1_DESC  FROM SB1010 WHERE D_E_L_E_T_='' AND (B1_COD LIKE '%"+codigo+"%' OR B1_DESC LIKE '%"+codigo+"%')")
    rows = cursor.fetchall()
    manutencao = Manutencao.query.filter(Manutencao.id == id).first()
    codigo = request.form.get('codigo')
    return render_template('manutencao/protheus_tabela.html', rows=rows, codigo=codigo, manutencao=manutencao, id=id_usuario,  nivel=nivel)  

@app.route("/delete_cod/<string:id>",methods=['GET'])
def delete_cod(id):
    protheus = Protheus.query.filter(Protheus.id == id).first()
    database.session.delete(protheus)
    database.session.commit()
    flash('computador Deleted','warning')
    return redirect(url_for("edit_chamados_manutencao", id=protheus.id_manutencao))

@app.route("/protheus_form/<id>", methods=["GET", "POST"])
def protheus_form(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    manutencao = Manutencao.query.filter(Manutencao.id == id).first()
    codigo = request.form.get('codigo')
    conn = pyodbc.connect('Driver={SQL Server};''Server=192.168.1.16;''Database=SIGA;''UID=SIGA;''PWD=SIGA')
    cursor = conn.cursor()
    cursor.execute("SELECT B1_COD, B1_DESC  FROM SB1010 WHERE B1_COD = '"+codigo+"'")
    if request.method=='POST':
        codigo=request.form.get('codigo')
        descricao=request.form.get('descricao')
        conx_manutencao.execute("insert into protheus(id_manutencao, codigo, descricao)  values ('"+id+"', '"+codigo+"', '"+descricao+"')") 
        conx_manutencao.commit()
        return redirect(url_for("edit_chamados_manutencao", id=id))
    return render_template("manutencao/protheus.html",  os=os, id=id_usuario, manutencao=manutencao, nivel=nivel)  



@app.route("/cadastro_equipamento", methods=["GET", "POST"])
def cadastro_equipamento():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if request.method=='GET':
        return render_template("manutencao/criar_materiais.html")
    if request.method == 'POST':
        codigo=request.form.get('codigo')
        equipamento=request.form.get('equipamento')
        localizacao=request.form.get('localizacao')
        caracteristica=request.form.get('caracteristica')
        prev=request.form.get('prev')
        pred=request.form.get('pred')
        conx_manutencao.execute(f"""INSERT INTO materiais (codigo, equipamento, localizacao, caracteristica, prev, pred) VALUES  
                                ('{codigo}', '{equipamento}', '{localizacao}', '{caracteristica}', '{prev}', '{pred}' ) """)
        conx_manutencao.commit()
        return redirect(url_for("equipamentos"))
    return render_template("manutencao/criar_materiais.html", nivel=nivel, id=id_usuario)  

@app.route("/edit_equipamentos/<string:id>", methods=['POST','GET'])
def edit_equipamentos(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM materiais WHERE id = '"+id+"'")
    equipamentos =  conx_manutencao.execute(query).fetchall()
    if request.method=='GET':
        return render_template("manutencao/edit_materiais.html", equipamentos=equipamentos, id=id_usuario, nivel=nivel)
    if request.method=='POST':
        codigo=request.form.get('codigo')
        equipamento=request.form.get('equipamento')
        localizacao=request.form.get('localizacao')
        caracteristica=request.form.get('caracteristica')
        prev=request.form.get('prev')
        pred=request.form.get('pred')
        desativado=request.form.get('desativado')
        conx_manutencao.execute(f"""UPDATE materiais SET codigo = '{codigo}', 
                                equipamento = '{equipamento}', localizacao = '{localizacao}', caracteristica = '{caracteristica}', 
                                prev = '{prev}', pred = '{pred}', desativado = '{desativado}' WHERE id = '{id}'""")
        conx_manutencao.commit()
        return redirect(url_for("equipamentos"))
    query = ("SELECT TOP 1 * FROM materiais WHERE id = '"+id+"'")
    equipamentos =  conx_manutencao.execute(query).fetchall()
    return render_template("manutencao/edit_materiais.html", equipamentos=equipamentos, id=id_usuario, nivel=nivel)

@app.route("/delete_materiais/<string:id>",methods=['GET'])
def delete_materiais(id):
    conx_manutencao.execute("DELETE FROM materiais WHERE id = '"+id+"'")
    conx_manutencao.commit()
    flash('User Deleted','warning')
    return redirect(url_for("equipamentos"))

@app.route("/fila_de_espera_manutencao")
def fila_de_espera_man():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx_manutencao.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM manutencao where status != 'Fechado' ").fetchall()
    return render_template("manutencao/fila_de_espera.html", chamados=chamados, nivel=nivel, id=id)  

@app.route("/equipamentos")
def equipamentos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = conx.execute(f"""select H1_CCUSTO, H1_CODIGO, H1_DESCRI, CTT_DESC01, CTT_CUSTO  from 
                            [192.168.1.16].[SIGA].[dbo].[SH1010]  right JOIN [192.168.1.16].[SIGA].[dbo].[CTT010] 
                            ON  CTT_CUSTO = H1_CCUSTO WHERE SH1010.D_E_L_E_T_ = ''""").fetchall()
    return render_template("manutencao/equipamentos.html", usuarios=usuarios,  id=id, nivel=nivel)

@app.route("/equipamentos_desativado")
def equipamentos_desativado():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = Materiais.query.order_by(Materiais.id).all()
    colaboradores = database.session.query(database.func.count(Materiais.id), Materiais.equipamento).group_by(Materiais.equipamento).order_by(Materiais.equipamento).all()
    return render_template("manutencao/equipamentos_desativado.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/codigo")
def codigo():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = Materiais.query.order_by(Materiais.equipamento).all()
    colaboradores = database.session.query(database.func.count(Materiais.id), Materiais.equipamento).group_by(Materiais.equipamento).order_by(Materiais.equipamento).all()
    return render_template("manutencao/equipamentos.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/localização")
def localização():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = Materiais.query.order_by(Materiais.localizacao).all()
    colaboradores = database.session.query(database.func.count(Materiais.id), Materiais.equipamento).group_by(Materiais.equipamento).order_by(Materiais.equipamento).all()
    return render_template("manutencao/equipamentos.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/prev")
def prev():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = Materiais.query.order_by(desc(Materiais.prev)).all()
    colaboradores = database.session.query(database.func.count(Materiais.id), Materiais.equipamento).group_by(Materiais.equipamento).order_by(Materiais.equipamento).all()
    return render_template("manutencao/equipamentos.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/pred")
def pred():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = Materiais.query.order_by(desc(Materiais.pred)).all()
    colaboradores = database.session.query(database.func.count(Materiais.id), Materiais.equipamento).group_by(Materiais.equipamento).order_by(Materiais.equipamento).all()
    return render_template("manutencao/equipamentos.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/caracteristica")
def caracteristica():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = Materiais.query.order_by(desc(Materiais.caracteristica)).all()
    colaboradores = database.session.query(database.func.count(Materiais.id), Materiais.equipamento).group_by(Materiais.equipamento).order_by(Materiais.equipamento).all()
    return render_template("manutencao/equipamentos.html", usuarios=usuarios, colaboradores=colaboradores, nivel=nivel, id=id)

@app.route("/Atribuido_manutencao")
def atribuidosss():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    chamados = conx_manutencao.execute("SELECT  *, CONVERT (DATE, data_criacao) AS data FROM manutencao ORDER BY id DESC ").fetchall()
    ativosstatus = conx_manutencao.execute("SELECT  COUNT(id) FROM manutencao WHERE status = 'atribuido' ").fetchall()
    return render_template("manutencao/atribuidos_manutencao.html", chamados=chamados, ativosstatus=ativosstatus, nivel=nivel, id=id)

@app.route("/search_materiais/<string:equipamento>",methods=['POST','GET'])
def search_materiais(equipamento):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    codigo = Materiais.query.filter(Materiais.equipamento == equipamento).first()
    if request.method=='GET':
        codigo = Materiais.query.filter(Materiais.equipamento == equipamento).first()
        return render_template("busca_materiais.html", codigo=codigo)
    codigo = Materiais.query.filter(Materiais.equipamento == equipamento).first()
    database.session.query(Materiais.equipamento == equipamento).first()
    return render_template("manutencao/busca_materiais.html", codigo=codigo, nivel=nivel, id=id_usuario)



@app.route("/adcionar_tecnico", methods=["GET", "POST"])
def add_tecnico():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if request.method=='POST':
        usuario = request.form.get('usuario')
        nivel=request.form.get('nivel')
        conx_manutencao.execute("insert into tecnico(usuario, nivel)  values ( '"+usuario+"', '"+nivel+"')") 
        conx_manutencao.commit()
        return redirect(url_for("tech"))
    return render_template("manutencao/add_tecnico.html",  nivel=nivel, id=id_usuario)

@app.route("/edit_tecnico/<string:id>", methods=['POST','GET'])
def edit_tecnico(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    query = ("SELECT TOP 1 * FROM tecnico WHERE id = '"+id+"'")
    tecnico =  conx_manutencao.execute(query).fetchall()
    if request.method=='GET':
        return render_template("manutencao/edit_tecnico.html", tecnicos=tecnico, id=id_usuario, nivel=nivel)
    if request.method=='POST':
        usuario=request.form.get('usuario')
        nivel=request.form.get('nivel')
        status=request.form.get('status')
        conx_manutencao.execute("UPDATE tecnico SET usuario = '"+usuario+"', nivel = '"+nivel+"', status = '"+status+"' WHERE id = '"+id+"'")
        conx_manutencao.commit()
        return redirect(url_for("tech"))
    return render_template("manutencao/edit_tecnico.html", tecnicos=tecnico, id=id_usuario, nivel=nivel)

@app.route("/tecnicos")
def tech():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios =conx_manutencao.execute("SELECT *  FROM tecnico").fetchall()
    return render_template("manutencao/tecnicos.html", usuarios=usuarios, nivel=nivel, id=id)

@app.route("/tecnicos_desativado")
def tecnicos_desativado():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = conx_manutencao.execute("SELECT *  FROM tecnico").fetchall()
    return render_template("manutencao/tecnico_desativado.html", usuarios=usuarios, nivel=nivel, id=id)

@app.route("/centro_custo", methods=["GET", "POST"])
def centro_custo():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'GET':
        return render_template('manutencao/usernames.html', rows=rows, usuario=usuario, nivel=nivel, id=id)
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        session['usuario'] = usuario
    usuario = session['usuario'] 
    conx_manutencao.execute("SELECT username  FROM usuario WHERE username LIKE '%"+usuario+"%'")
    rows = conx_manutencao.fetchall()
    return render_template('manutencao/usernames.html', rows=rows, usuario=usuario, nivel=nivel, id=id)

@app.route("/usuarios_cc")
def usuarios_cc():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    usuarios = Centro.query.order_by(Centro.usuario).all()
    return render_template("usuarios/usuarios_cc.html", usuarios=usuarios, nivel=nivel, id=id)

@app.route("/edit_user_dapartamento",methods=['GET', "POST"])
def centro():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    usuario = request.form.get('usuario')
    conx_manutencao.execute("SELECT username  FROM usuario WHERE username LIKE '%"+usuario+"%'")
    rows = conx_manutencao.fetchall()
    if request.method=='POST':
        usuario = request.form.get('usuario')
        departamento=request.form.get('departamento')
        conx_manutencao.execute("insert into centro(usuario, departamento)  values ( '"+usuario+"', '"+departamento+"')") 
        conx_manutencao.commit()
        return redirect(url_for("usuarios_cc"))
    return render_template("usuarios/usuarios_cc.html", id=id_usuario,  nivel=nivel)  

@app.route("/delete_cc/<string:id>",methods=['GET'])
def delete_cc(id):
    conx_manutencao.execute("DELETE FROM centro WHERE id = '"+id+"'")
    conx_manutencao.commit()
    flash('User Deleted','warning')
    return redirect(url_for("usuarios_cc"))