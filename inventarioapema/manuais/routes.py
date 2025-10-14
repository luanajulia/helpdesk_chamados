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

conn = pyodbc.connect('Driver={SQL Server};'
'Server=192.168.1.16;'
'Database=SIGA;'
'UID=SIGA;'
'PWD=SIGA')



@app.route("/backoffice_fiscal")
def backoffice_fiscal():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/backoffice_fiscal.html", nivel=nivel, id=id)

@app.route("/financ_fiscal")
def financ_fiscal():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/financ_fiscal.html", nivel=nivel, id=id)

@app.route("/rh")
def rh():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/rh.html", nivel=nivel, id=id)

@app.route("/avaliacao")
def avaliacao():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if departamento == "RH":
         
        colaborador =   email
        departamento =  departamento
        acesso = "avaliacao"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-AVALIACAO-E-PESQUISA-DE-DESEMPENHO_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "avaliacao"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-AVALIACAO-E-PESQUISA-DE-DESEMPENHO_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    

@app.route("/cargo_salario")
def cargo_salario():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "RH":
         
        colaborador =  email
        departamento =  departamento
        acesso = "cargo_salario"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-CARGOS-E-SALARIOS_V12_AP01OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "cargo_salario"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-CARGOS-E-SALARIOS_V12_AP01OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/Beneficios")
def Beneficios():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "RH":
         
        colaborador =  email
        departamento =  departamento
        acesso = "Beneficios"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-BENEFICIOS_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "Beneficios"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-BENEFICIOS_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html")
    
@app.route("/gestao")
def gestao():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "RH":
         
        colaborador =  email
        departamento =  departamento
        acesso = "gestao"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--GESTAO-DE-PESSOAL_V12_AP03-OK.html", id=id, nivel=nivel)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "gestao"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--GESTAO-DE-PESSOAL_V12_AP03-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/seguranca")
def seguranca():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "RH":
         
        colaborador =  email
        departamento =  departamento
        acesso = "seguranca"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--MEDICINA-E-SEGURANCA-DO-TRABALHO_V12_AP01-OK.html", id=id, nivel=nivel)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "seguranca"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--MEDICINA-E-SEGURANCA-DO-TRABALHO_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/ponto_eletronico")
def ponto_eletronico():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "RH" :
         
        colaborador =  email
        departamento =  departamento
        acesso = "ponto_eletronico"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("arquivo.html", nome="PROTHEUS--PONTO-ELETRONICO_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "ponto_eletronico"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--PONTO-ELETRONICO_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/recrutamento")
def recrutamento():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "RH":
         
        colaborador =  email
        departamento =  departamento
        acesso = "recrutamento"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--Recrutamento-e-Selecao-apostila-presencial_v1180.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "recrutamento"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--Recrutamento-e-Selecao-apostila-presencial_v1180.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/treinamentos_rh")
def treinamentos_rh():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "RH":
        colaborador =  email
        departamento =  departamento
        acesso = "treinamentos"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conx.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--TREINAMENTOS_V12_AP01--OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "treinamentos"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--TREINAMENTOS_V12_AP01--OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
  

@app.route("/livros_fiscais")
def livros_fiscais():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "livros_fiscais"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--LIVROS-FISCAIS_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "livros_fiscais"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--LIVROS-FISCAIS_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/tesouraria")
def tesouraria():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Financeiro":
         
        colaborador =  email
        departamento =  departamento
        acesso = "tesouraria"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-TESOURARIA_V12_AP04.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "tesouraria"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-TESOURARIA_V12_AP04.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/tes")
def tes():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "tes"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--TES-2--OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "tes"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--TES-2--OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/telecobranca")
def telecobranca():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Financeiro":
        colaborador =  email
        departamento =  departamento
        acesso = "telecobranca"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--TELECOBRANCA_V12_AP01.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "telecobranca"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--TELECOBRANCA_V12_AP01.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    

@app.route("/taf")
def taf():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "taf"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--TAF-ECF_V12_AP01--OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "taf"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--TAF-ECF_V12_AP01--OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/sped")
def sped():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "sped"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--SPED-FISCAL-E-SPED-CONTRIBUICOES_V12_AP01.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "sped"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--SPED-FISCAL-E-SPED-CONTRIBUICOES_V12_AP01.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    

@app.route("/roteiro")
def roteiro():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "roteiro"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--ROTEIRO-DE-FORMULA_V12_AP01--OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "roteiro"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--ROTEIRO-DE-FORMULA_V12_AP01--OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/PisCofins")
def PisCofins():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "PisCofins"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--MP-Sped-PisCofins-V11.80.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "PisCofins"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--MP-Sped-PisCofins-V11.80.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/formacao")
def formacao():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "formacao"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--FORMACAO-LIVROS-FISCAIS_V12_AP01.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "formacao"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--FORMACAO-LIVROS-FISCAIS_V12_AP01.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/fluxo_caixa")
def fluxo_caixa():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Financeiro":
         
        colaborador =  email
        departamento =  departamento
        acesso = "fluxo_caixa"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-FLUXO-DE-CAIXA_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "fluxo_caixa"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-FLUXO-DE-CAIXA_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/contas_receber")
def contas_receber():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Financeiro":
         
        colaborador =  email
        departamento =  departamento
        acesso = "contas_receber"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--CONTAS-A-RECEBER_V12_AP02-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "contas_receber"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--CONTAS-A-RECEBER_V12_AP02-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/contas_pagar")
def contas_pagar():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Financeiro" :
         
        colaborador =  email
        departamento =  departamento
        acesso = "contas_pagar"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-CONTAS-A-PAGAR_V12_AP02-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "contas_pagar"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS-CONTAS-A-PAGAR_V12_AP02-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/cnab")
def cnab():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Financeiro":
         
        colaborador =  email
        departamento =  departamento
        acesso = "cnab"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--CNAB_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "cnab"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--CNAB_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/bloco")
def bloco():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "bloco"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--BLOCO-K_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "bloco"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--BLOCO-K_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/MP_speed")
def MP_speed():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Fiscal":
         
        colaborador =  email
        departamento =  departamento
        acesso = "MP_speed"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--Apostila_MP_SPED_Fiscal.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "MP_speed"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--Apostila_MP_SPED_Fiscal.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)

### MANUFATURA ##  
@app.route("/processos")
def processos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Processos":
        colaborador =  email
        departamento =  departamento
        acesso = "processos"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conx.commit()
        return render_template("manuais/pcp.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/expedicao_qualidade")
def expedicao_qualidade():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Qualidade":
         
        colaborador =  email
        departamento =  departamento
        acesso = "expedicao_qualidade"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/treinamento.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/acd")
def acd():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Tecnologia da Informação":
         
        colaborador =  email
        departamento =  departamento
        acesso = "acd"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/treinamento.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
        
        
@app.route("/video_compras")
def video_compras():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Compras":
        conn = sqlite3.connect( 'C:/Users/luanavieira/Documents/PROJETOS_PYTHON/PROJETO_HELPDESK/instance/comunidade.db', check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "cadastro_produto"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/video.html")
    elif  departamento == "Tecnologia da Informacao":
         
        colaborador =  email
        departamento =  departamento
        acesso = "cadastro_produto"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/video.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
caminho = 'C:/inetpub/wwwroot/PROJETO_HELPDESK/instance/comunidade.db'        
## estoque custo ##
@app.route("/custos")
def custos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Custo":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "custos"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--CUSTOS-II_V12_AP02-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "custos"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--CUSTOS-II_V12_AP02-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/estoque_avancado")
def estoque_avancado():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Custo":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "estoque_avancado"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--ESTOQUE-AVANÇADO_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "estoque_avancado"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--ESTOQUE-AVANCADO_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/estoque")
def estoque():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "Custo":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "estoque"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--ESTOQUE_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "estoque"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--ESTOQUE_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)


@app.route("/backoffice/<string:departamento>")
def backoffice(departamento):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    email = session['email']
    nivel = session['nivel']
    if departamento == "financeiro":
        return render_template("manuais/backoffice.html", departamento="financeiro", nivel=nivel, id=id)
    if departamento == "fiscal":
        return render_template("manuais/backoffice_fiscal.html", departamento="fiscal", nivel=nivel, id=id)
    if departamento == "estoque":
        return render_template("manuais/backoffice_estoque.html", departamento="estoque", nivel=nivel, id=id)
    if departamento == "projetos":
        return render_template("manuais/backoffice_projetos.html", departamento="projetos", nivel=nivel, id=id)
    if departamento == "controladoria":
        return render_template("manuais/backoffice_controladoria.html", departamento="controladoria", nivel=nivel, id=id)
    if departamento == "compras":
        return render_template("manuais/backoffice_compras.html", departamento="compras", nivel=nivel, id=id)
    if departamento == "contratos":
        return render_template("manuais/backoffice_contratos.html", departamento="contratos", nivel=nivel, id=id)
    if departamento == "vendas":
        return render_template("manuais/backoffice_vendas.html", departamento="vendas", nivel=nivel, id=id)

    
@app.route("/videos/<string:departamento>")
def videos(departamento):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    email = session['email']
    nivel = session['nivel']
    if departamento == "compras":
        return render_template("manuais/video.html", departamento="compras", nivel=nivel, id=id)
    if departamento == "financeiro":
        return render_template("manuais/videos_financeiro.html", departamento="financeiro", nivel=nivel, id=id)
    if departamento == "fiscal":
        return render_template("manuais/videos_fiscal.html", departamento="fiscal", nivel=nivel, id=id)
    if departamento == "estoque":
        return render_template("manuais/videos_estoque.html", departamento="estoque", nivel=nivel, id=id)
    if departamento == "projetos":
        return render_template("manuais/videos_projetos.html", departamento="projetos", nivel=nivel, id=id)
    if departamento == "controladoria":
        return render_template("manuais/videos_controladoria.html", departamento="controladoria", nivel=nivel, id=id)
    if departamento == "contratos":
        return render_template("manuais/videos_contratos.html", departamento="contratos", nivel=nivel, id=id)
    if departamento == "vendas":
        return render_template("manuais/videos_vendas.html", departamento="vendas", nivel=nivel, id=id)
    if departamento == "pcp":
        return render_template("manuais/videos_vendas.html", departamento="pcp", nivel=nivel, id=id)
    
@app.route("/manufatura")
def manufatura():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/manufatura.html", departamento="compras", nivel=nivel, id=id)

@app.route("/manuais_videos/pcp")
def manuais_videos_pcp():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="pcp", nivel=nivel, id=id)


@app.route("/backoffice/pcp")
def pcp():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "PCP":
        conn = sqlite3.connect( 'C:\inetpub\wwwroot\PROJETO_HELPDESK\instance\comunidade.db', check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "cargo_salario"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/pcp.html", nome="PROTHEUS-PCP_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)



## controladoria ##
@app.route("/ativo_fixo")
def ativo_fixo():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "controladoria":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "ativo_fixo"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--ATIVO-FIXO_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
        conn = sqlite3.connect( caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "ativo_fixo"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--ATIVO-FIXO_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/contabilidade")
def contabilidade():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "controladoria":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "contabilidade"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--CONTABILIDADE-GERENCIAL_V12_AP01-OK.html", nivel=nivel, id=id)
    elif  departamento == "Tecnologia da Informacao":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "contabilidade"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--CONTABILIDADE-GERENCIAL_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/fechamento")
def fechamento():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "controladoria":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "fechamento"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--FECHAMENTO-CONTABIL_V12_AP01-OK.html")
    elif  departamento == "Tecnologia da Informacao":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "fechamento"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--FECHAMENTO-CONTABIL_V12_AP01-OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)
    
@app.route("/sped_contabil")
def sped_contabil():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    if  departamento == "controladoria":
        conn = sqlite3.connect(caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "sped_contabil"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--SPED-CONTABIL_V12_AP01--OK.html")
    elif  departamento == "Tecnologia da Informacao":
        conn = sqlite3.connect( caminho, check_same_thread=False)
        conx = conn.conx()
        colaborador =  email
        departamento =  departamento
        acesso = "sped_contabil"
        conx.execute("INSERT INTO acesso(colaborador, departamento, acesso) values (?, ?, ?)", (colaborador, departamento, acesso))
        conn.commit()
        return render_template("manuais/arquivo.html", nome="PROTHEUS--SPED-CONTABIL_V12_AP01--OK.html", nivel=nivel, id=id)
    else:
        return  render_template("manuais/valido.html", nivel=nivel, id=id)

    
    
## manuais 
@app.route("/manuais")
def manuais():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/manuais.html", nivel=nivel, id=id)

@app.route("/manuais_treinamento")
def treinamentos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/treinamento.html", nivel=nivel, id=id)

@app.route("/manuais_videos/financeiro")
def manuais_videos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="financeiro", nivel=nivel, id=id)

@app.route("/manuais_videos/fiscal")
def manuais_videos_fiscal():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="fiscal", nivel=nivel, id=id)

@app.route("/manuais_videos/estoque")
def manuais_videos_estoque():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="estoque", nivel=nivel, id=id)

@app.route("/manuais_videos/projetos")
def manuais_videos_projetos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="projetos", nivel=nivel, id=id)

@app.route("/manuais_videos/controladoria")
def manuais_videos_controladoria():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="controladoria", nivel=nivel, id=id)

@app.route("/manuais_videos/compras")
def manuais_videos_compras():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="compras", nivel=nivel, id=id)

@app.route("/manuais_videos/contratos")
def manuais_videos_contratos():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="contratos", nivel=nivel, id=id)

@app.route("/manuais_videos/vendas")
def manuais_videos_vendas():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    departamento = session['departamento'] 
    email = session['email']
    nivel = session['nivel']
    id = session['id']
    return render_template("manuais/videos_manuais.html", departamento="vendas", nivel=nivel, id=id)