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
from inventarioapema.conexao import conx_rh, caminho, conx_mes, conx_rh, conx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3


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


@app.route("/email_enviar/<string:departamento>")
def enviar(departamento):
    matriculas = conx_rh.execute("SELECT max(idColaborador) as idColaborador, MatColaborador from controle_banco group by MatColaborador").fetchall()
    saldos = conx_rh.execute("SELECT idColaborador, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, MatColaborador, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status from controle_banco ").fetchall()
    datas = conx_rh.execute("select MAX(data) as date from  data_ultima").fetchall()
    if departamento == "Fabrica":
        return redirect(url_for("email_fabrica", departamento="PCP"))
    if departamento == "Compras":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '8114' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, 
                                 IIF((Saldo)<-100, IIF((Saldo)<-100, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')), 
                                 CONCAT('-', (cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - 
                                 (cast((Saldo)as int)/60))*60))), '0#'))), CONCAT('-', (cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#'))) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status 
                                 FROM relatorio  WHERE saldo is not null and centro_custo = '8114     ' """).fetchall()
        html =  render_template("email/dep_col_banco.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Vendas":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '3113' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, 
                                 CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - 
                                 (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, centro_custo, matricula,  
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and 
                                 ( centro_custo = '3111     ' or centro_custo = '3113     ' or centro_custo = '3115     ' )   ORDER BY nome """).fetchall()
        html =  render_template("email/dep_vendas.html", pessoas=pessoas,   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
    if departamento == "Orcamentos":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '3114' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, 
                                 CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - 
                                 (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, centro_custo, matricula,  
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  WHERE saldo is not null and centro_custo =  '3114     '""").fetchall()
        html =  render_template("email/dep_col_banco.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Desenvolvimento de Projetos":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '4111' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, 
                                 CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - 
                                 (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, centro_custo, matricula,  
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  WHERE saldo is not null and centro_custo =  '4111     '  """).fetchall()
        html =  render_template("email/dep_col_banco.html", pessoas=pessoas,  departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
    if departamento == "Qualidade":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '8114' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, 
                                 CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status 
                                 FROM relatorio  WHERE saldo is not null and 
                                 ( centro_custo = '7111     ' or centro_custo = '7112     ' or centro_custo = '7113     'or centro_custo = '7114     'or centro_custo = '7115     'or centro_custo = '5141     'or centro_custo = '5182     ' )   ORDER BY nome""").fetchall()
        html =  render_template("email/dep_qualidade.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "TI":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '2151' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status 
                                 FROM relatorio  WHERE  saldo is not null and   centro_custo = '2151     '   ORDER BY nome """).fetchall()
        html =  render_template("email/dep_col_banco.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Diretoria":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC IN ('2111', '2115', '2116','2118','2123','2131')   """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status 
                                 FROM relatorio  WHERE saldo is not null and ( centro_custo = '2111     ' or centro_custo = '2115     ' or centro_custo = '2116     'or centro_custo = '2118     'or centro_custo = '2123     'or centro_custo = '2131     ')    ORDER BY nome """).fetchall()
        html =  render_template("email/dep_diretoria.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Manutencao":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '6111' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status 
                                 FROM relatorio WHERE saldo is not null and centro_custo = '6111     '   ORDER BY nome """).fetchall()
        html =  render_template("email/dep_col_banco.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Corte":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC IN ('5111', '5123','5112','5115' )""").fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status 
                                 FROM relatorio  WHERE saldo is not null and 
                                 ( centro_custo = '5111     ' or centro_custo = '5123     'or centro_custo = '5112     ' or centro_custo = '5115     ' ) ORDER BY nome """).fetchall()
        html =  render_template("email/dep_corte.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Processos":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '8117' """).fetchall()
        rows =  conx_rh.execute("""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status 
                                 FROM relatorio WHERE saldo is not null and centro_custo = '8117     '   ORDER BY nome """).fetchall()
        html =  render_template("email/dep_col_banco.html", pessoas=pessoas,   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
    if departamento == "Linha":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC IN ('5141' ,'5161','5162','5171','5173' )   """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, 
                                 CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status 
                                 FROM relatorio WHERE saldo is not null and 
                                 (centro_custo = '5141     ' or centro_custo = '5161     'or centro_custo = '5162     'or centro_custo = '5171     'or centro_custo = '5173     ' )    
                                 ORDER BY nome """).fetchall()
        html =  render_template("email/dep_linha.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Usinagem":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC IN ('5133' ,'5134')   """).fetchall()
        rows =  conx_rh.execute(f""" SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio 
                                 WHERE saldo is not null and (centro_custo = '5133     ' or centro_custo = '5134     'or centro_custo = '5131     ' )    ORDER BY nome """).fetchall()
        html =  render_template("email/dep_usinagem.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "RH":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC IN ('2111','2115' ,'2116','2118')  """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and ( centro_custo = '2111     ' or centro_custo = '2115     ' or centro_custo = '2116     'or centro_custo = '2118     ')   
                                 ORDER BY nome """).fetchall()
        html =  render_template("email/dep_rh.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Financeiro":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '2123'  """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and centro_custo = '2123     '   ORDER BY nome """).fetchall()
        html =  render_template("email/dep_col_banco.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Fiscal":
        rows =  conx_rh.execute("  SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  WHERE saldo is not null  and centro_custo = '2131     '   ORDER BY nome ").fetchall()
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '2131' """).fetchall()
        html =  render_template("email/dep_col_banco.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Montagem":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC in ('5181', '5182',  '5183')   """).fetchall()
        rows =  conx_rh.execute(f"""  SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null  and ( centro_custo = '5181     ' or centro_custo = '5182     ' or centro_custo = '5183     ')    ORDER BY nome """).fetchall()
        html =  render_template("email/dep_montangem.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Expedicao":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '2165'   """).fetchall()
        rows =  conx_rh.execute(f"""  SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and centro_custo = '2165     '   ORDER BY nome """).fetchall()
        html =  render_template("email/dep_col_banco.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Almoxarifado":
        pessoas = conx_rh.execute("  SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  WHERE matricula = '001478' ORDER BY nome  ").fetchall()
        rows =  conx_rh.execute("  SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  WHERE saldo is not null and (centro_custo = '2161     ' or matricula = '001478')  ORDER BY nome ").fetchall()
        html =  render_template("email/dep_col_banco.html",   departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    smtp_server = 'smtp.outlook.com'
    smtp_port = 587
    smtp_username = 'suporte@apema.com.br'
    smtp_password = 'Apema@2019'

    
    # Create an email message
    message = MIMEText(html, "html")
    message['Subject'] = 'Controle de Banco de Horas'
    message['From'] = 'suporte@apema.com.br'
    if departamento == "Compras":
        message['To'] = 'antoniocardoso@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Vendas":
        message['To'] = 'rodolfozampieri@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Orcamentos":
        message['To'] = 'solangeinoue@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Desenvolvimento de Projetos":
        message['To'] = 'ricksouza@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Qualidade":
        message['To'] = 'mendes@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "TI":
        message['To'] = 'marcopessolato@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Diretoria":
        message['To'] = 'luanavieira@apema.com.br'
    if departamento == "Manutencao":
        message['To'] = 'garibaldi@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Corte":
        message['To'] = 'jubertmendes@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Processos":
        message['To'] = 'arthurbos@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Linha":
        message['To'] = 'robertimmartins@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Usinagem":
        message['To'] = 'adrianopurcino@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "RH":
        message['To'] = 'soraiamoura@apema.com.br'
    if departamento == "Financeiro":
        message['To'] = 'soraiamoura@apema.com.br'
    if departamento == "Fiscal":
        message['To'] = 'soraiamoura@apema.com.br'
    if departamento == "Montagem":
        message['To'] = 'carlosgomes@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Expedicao":
        message['To'] = 'evanildosantana@apema.com.br; soraiamoura@apema.com.br'
    if departamento == "Almoxarifado":
        message['To'] = 'henriquesantarelli@apema.com.br; soraiamoura@apema.com.br'
    # Establish a connection to the SMTP server
    smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
    smtp_connection.starttls()

    # Log in to the SMTP server
    smtp_connection.login(smtp_username, smtp_password)

    # Send the email
    smtp_connection.send_message(message)

    # Close the SMTP connection
    smtp_connection.quit()
    print('Enviado')
    return redirect(url_for("departamento_banco"))


@app.route("/email_fabrica/<string:departamento>", methods=["GET", "POST"])
def email_fabrica(departamento):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    datas = conx_rh.execute("select MAX(data) as date from  data_ultima").fetchall()
    matriculas = conx_rh.execute("SELECT max(idColaborador) as idColaborador, MatColaborador from controle_banco group by MatColaborador").fetchall()
    saldos = conx_rh.execute(f"""SELECT idColaborador, 
                              concat( left(format(abs(Saldo), '0#.0#'), 2), ':', right(Saldo, 2)) as Saldo, 
                              MatColaborador, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status from controle_banco """).fetchall()
    if departamento == "PCP":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '8113' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and   centro_custo = '8113     '   ORDER BY nome """).fetchall()
        html = render_template("email/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Pintura"))
    if departamento == "Pintura":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '5191' """).fetchall()
        rows =  conx_rh.execute("""SELECT nome, 
                                 CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and   centro_custo = '5191     '   ORDER BY nome """).fetchall()
        html = render_template("email/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Manutencao"))
    if departamento == "Manutencao":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '6111' """).fetchall()
        rows =  conx_rh.execute("  SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  WHERE saldo is not null and   centro_custo = '6111     '   ORDER BY nome ").fetchall()
        html = render_template("email/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Corte"))
    if departamento == "Corte":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC IN ('5111' , '5123','5112' ,'5115' ) """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and 
                                 ( centro_custo = '5111     ' or centro_custo = '5123     'or centro_custo = '5112     ' or centro_custo = '5115     ' ) ORDER BY nome """).fetchall()
        html = render_template("email/dep_corte.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Processos"))
    if departamento == "Processos":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '8117' """).fetchall()
        rows =  conx_rh.execute("""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio 
                                 WHERE saldo is not null and   centro_custo = '8117     '   ORDER BY nome """).fetchall()
        html = render_template("email/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Linha"))
    if departamento == "Linha":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC IN ('5141','5161','5162','5171','5173' )  """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio 
                                 WHERE saldo is not null and 
                                 (centro_custo = '5141     ' or centro_custo = '5161     'or centro_custo = '5162     'or centro_custo = '5171     'or centro_custo = '5173     ' )   
                                 ORDER BY nome """).fetchall()
        html = render_template("email/dep_linha.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Usina"))
    if departamento == "Usina":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC in ('5133' ,'5134','5131' ) """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio 
                                 WHERE saldo is not null and (centro_custo = '5133     ' or centro_custo = '5134     'or centro_custo = '5131     ' )    ORDER BY nome """).fetchall()
        html = render_template("email/dep_usinagem.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Montagem"))
    if departamento == "Montagem":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC IN ('5181' , '5182','5183') """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and ( centro_custo = '5181     ' or centro_custo = '5182     ' or centro_custo = '5183     ')    ORDER BY nome """).fetchall()
        html = render_template("email/dep_montangem.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'

        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Expedicao"))
    if departamento == "Expedicao":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '2165' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                 WHERE saldo is not null and   centro_custo = '2165     '   ORDER BY nome """).fetchall()
        html = render_template("email/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("email_fabrica", departamento="Almoxarifado"))
    if departamento == "Almoxarifado":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME as nome, RA_CC as centro_custo, RA_MAT as matricula, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM HSRA_010 WHERE RA_CC = '2161' """).fetchall()
        rows =  conx_rh.execute(f"""SELECT nome, CONCAT((cast((Saldo)as int)/60) ,':',  
                                 FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                                 centro_custo, matricula,  IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio  
                                 WHERE saldo is not null and   centro_custo = '2161     '   ORDER BY nome """).fetchall()
        html = render_template("email/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        smtp_server = 'smtp.outlook.com'
        smtp_port = 587
        smtp_username = 'suporte@apema.com.br'
        smtp_password = 'Apema@2019'

        
        # Create an email message
        message = MIMEText(html, "html")
        message['Subject'] = 'Controle de Banco de Horas'
        message['From'] = 'suporte@apema.com.br'
        message['To'] = 'sebastiaoandrade@apema.com.br; soraiamoura@apema.com.br'
        # Establish a connection to the SMTP server
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()

        # Log in to the SMTP server
        smtp_connection.login(smtp_username, smtp_password)

        # Send the email
        smtp_connection.send_message(message)

        # Close the SMTP connection
        smtp_connection.quit()
        return redirect(url_for("departamento_banco"))


@app.route("/departamento_banco", methods=["GET", "POST"])
def departamento_banco():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method == 'POST':
        data=request.form.get('data')
        conx_rh.execute("INSERT INTO data_ultima(data) VALUES(?)", (data))
        conx_rh.commit()
    datas = conx_rh.execute("select MAX(data) as date from  data_ultima").fetchall()
    return render_template("controle/departamento_banco.html",  nivel=nivel, datas=datas, id=id)

@app.route("/departamento_colaboradores_banco/<string:departamento>", methods=["GET", "POST"])
def departamento_colaboradores_banco(departamento):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    datas = conx_rh.execute("select MAX(data) as date from  data_ultima").fetchall()
    matriculas = conx_rh.execute("SELECT max(idColaborador) as idColaborador, MatColaborador from controle_banco group by MatColaborador").fetchall()
    saldos = conx_rh.execute("SELECT idColaborador, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, MatColaborador, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status from controle_banco ").fetchall()
    if departamento == "Fabrica":
        pessoas = conx_rh.execute(f"""SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN
                                    ( '5111     ' , '5123     ' , '5115     '  , '2161     ' , '2165     ' , '5112     ' , '5131     ' ,
                                    '5133     ' , '5134     ' ,'5141     ' , '5161     ' , '5162     ' , '5171     ' , '5173     ' , '5181     ', 
                                   '5182     ' , '5183     ' , '6111     ' , '5191     ' ,'8113     ', '8117     ' )  """).fetchall()
        rows = conx_rh.execute("""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE 
                                ( centro_custo = '5111     ' or centro_custo = '5123     ' or centro_custo = '5115     '  or centro_custo = '2161     ' or 
                                centro_custo = '2165     ' or centro_custo = '5112     ' or centro_custo = '5131     ' or centro_custo = '5133     ' or 
                                centro_custo = '5134     ' or centro_custo = '5141     ' or centro_custo = '5161     ' or centro_custo = '5162     ' or 
                                centro_custo = '5171     ' or centro_custo = '5173     ' or centro_custo = '5181     ' or centro_custo = '5182     ' or 
                                centro_custo = '5183     ' or centro_custo = '6111     ' or centro_custo = '5191     ' or centro_custo = '8113     ' or 
                                centro_custo = '8117     ' ) ORDER BY nome """).fetchall()  
        return render_template("controle/dep_fabrica.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Compras":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '8114' ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo  IN ('8114     ') ORDER BY nome  """).fetchall()
        return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Vendas":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '3113' ").fetchall()
        rows = conx_rh.execute("""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE ( centro_custo = '3111' or centro_custo = '3113' or centro_custo = '3115' ) and saldo is not null ORDER BY nome """).fetchall()
        return render_template("controle/dep_vendas.html", pessoas=pessoas,  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
    if departamento == "Orcamentos":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '3114' ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE  saldo is not null and centro_custo  IN ('3114     ') ORDER BY nome  """).fetchall()
        return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Desenvolvimento de Projetos":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '4111' ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE  saldo is not null and centro_custo  IN ('4111     ') ORDER BY nome """).fetchall()
        return render_template("controle/dep_col_banco.html", pessoas=pessoas, nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
    if departamento == "Qualidade":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '8114' ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE
                               ( centro_custo = '7111     ' or centro_custo = '7112     ' or centro_custo = '7113     'or centro_custo = '7114     'or 
                               centro_custo = '7115     'or centro_custo = '5141     'or centro_custo = '5182     ' ) and saldo is not null ORDER BY nome""").fetchall()
        return render_template("controle/dep_qualidade.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "TI":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2151' ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo  IN ('2151     ') ORDER BY nome """).fetchall()
        return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Diretoria":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('2111', '2115', '2116','2118','2123','2131')   ").fetchall()
        rows = conx_rh.execute("""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE
                               ( centro_custo = '2111     ' or centro_custo = '2115     ' or centro_custo = '2116     'or centro_custo = '2118     '
                               or centro_custo = '2123     'or centro_custo = '2131     ') and saldo is not null  ORDER BY nome """).fetchall()
        return render_template("controle/dep_diretoria.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Manutencao":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '6111' ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo  IN ('6111     ') ORDER BY nome """).fetchall()
        return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Corte":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('5111', '5123','5112','5115' )").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and
                               ( centro_custo = '5111     ' or centro_custo = '5123     'or centro_custo = '5112     ' or centro_custo = '5115     ' ) 
                               ORDER BY nome """).fetchall()
        return render_template("controle/dep_corte.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Processos":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '8117' ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo  IN ('8117     ') ORDER BY nome """).fetchall()
        return render_template("controle/dep_col_banco.html", pessoas=pessoas,  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
    if departamento == "Linha":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('5141' ,'5161','5162','5171','5173' )   ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE 
                               (centro_custo = '5141     ' or centro_custo = '5161     'or centro_custo = '5162     'or centro_custo = '5171     'or centro_custo = '5173     ' ) AND saldo IS NOT NULL   
                               ORDER BY nome """).fetchall()
        return render_template("controle/dep_linha.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Usinagem":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('5133' ,'5134')   ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo IN ( '5133     ' ,'5134     ' )   ORDER BY nome """).fetchall()
        return render_template("controle/dep_usinagem.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "RH":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('2111','2115' ,'2116','2118')   ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE
                               (centro_custo = '2111     ' or centro_custo = '2115     ' or centro_custo = '2116     'or centro_custo = '2118     ') AND saldo IS NOT NULL ORDER BY nome """).fetchall()
        return render_template("controle/dep_rh.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Financeiro":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2123'  ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo  IN ('2123     ') ORDER BY nome  """).fetchall()
        return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Fiscal":
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo  IN ('2131     ') ORDER BY nome """).fetchall()
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2131' ").fetchall()
        return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Montagem":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC in ('5181', '5182',  '5183')   ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo IN ('5181     ', '5182     ',  '5183     ')   ORDER BY nome """).fetchall()
        return render_template("controle/dep_montangem.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Expedicao":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2165'   ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and centro_custo  IN ('2165     ') ORDER BY nome """).fetchall()
        return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
    if departamento == "Almoxarifado":
        pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2161'   ").fetchall()
        rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and (centro_custo = '2161     ' OR  matricula = '001478') ORDER BY nome """).fetchall()
        return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=departamento, rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)

@app.route("/departamento_gestor", methods=["GET", "POST"])
def departamento_gestor():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    colaboradores= conx.execute("SELECT * FROM usuario where id = '"+str(id)+"'").fetchall()
    datas = conx_rh.execute("select MAX(data) as date from  data_ultima").fetchall()
    matriculas = conx_rh.execute("SELECT max(idColaborador) as idColaborador, MatColaborador from controle_banco group by MatColaborador").fetchall()
    saldos = conx_rh.execute("SELECT idColaborador, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, MatColaborador, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status from controle_banco ").fetchall()
    for colaborador in colaboradores:
        if colaborador[4]  == "Lideres":
            pessoas = conx_rh.execute(f"""SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC in 
                                    (  '5111     ' , '5123     ' , '5115     '  ,
                                    '2161     ' ,'2165     ' , '5112     ' , '5131     ' , '5133     ' , '5134     ' ,'5141     ' ,
                                   '5161     ', '5162     ' ,'5171     ' ,'5173     ' , '5181     ' , '5182     ' ,
                                   '5183     ','6111     ' ,  '5191     ', '8113     ' ,'8117     ' )""").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo  IN (  '5111     ' , '5123     ' , '5115     '  ,
                                    '2161     ' ,'2165     ' , '5112     ' , '5131     ' , '5133     ' , '5134     ' ,'5141     ' ,
                                   '5161     ', '5162     ' ,'5171     ' ,'5173     ' , '5181     ' , '5182     ' ,
                                   '5183     ','6111     ' ,  '5191     ', '8113     ' ,'8117     ' )ORDER BY nome  """).fetchall()
            return render_template("controle/dep_fabrica.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Compras":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '8114' ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo  IN ('8114     ') ORDER BY nome  """).fetchall()
            return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Vendas":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '3113' ").fetchall()
            rows = conx_rh.execute("""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE ( centro_custo = '3111' or centro_custo = '3113' or centro_custo = '3115' ) and saldo is not null ORDER BY nome """).fetchall()
            return render_template("controle/dep_vendas.html", pessoas=pessoas,  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        if colaborador[4]  == "Orcamentos":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '3114' ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE  saldo is not null and centro_custo  IN ('3114     ') ORDER BY nome  """).fetchall()
            return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Desenvolvimento de Projetos":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '4111' ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE  saldo is not null and centro_custo  IN ('4111     ') ORDER BY nome """).fetchall()
            return render_template("controle/dep_col_banco.html", pessoas=pessoas, nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        if colaborador[4]  == "Qualidade":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '8114' ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE
                                ( centro_custo = '7111     ' or centro_custo = '7112     ' or centro_custo = '7113     'or centro_custo = '7114     'or 
                                centro_custo = '7115     'or centro_custo = '5141     'or centro_custo = '5182     ' ) and saldo is not null ORDER BY nome""").fetchall()
            return render_template("controle/dep_qualidade.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "TI":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2151' ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo  IN ('2151     ') ORDER BY nome """).fetchall()
            return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Diretoria":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('2111', '2115', '2116','2118','2123','2131')   ").fetchall()
            rows = conx_rh.execute("""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE
                                ( centro_custo = '2111     ' or centro_custo = '2115     ' or centro_custo = '2116     'or centro_custo = '2118     '
                                or centro_custo = '2123     'or centro_custo = '2131     ') and saldo is not null  ORDER BY nome """).fetchall()
            return render_template("controle/dep_diretoria.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Manutencao":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '6111' ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo  IN ('6111     ') ORDER BY nome """).fetchall()
            return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Corte":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('5111', '5123','5112','5115' )").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and
                                ( centro_custo = '5111     ' or centro_custo = '5123     'or centro_custo = '5112     ' or centro_custo = '5115     ' ) 
                                ORDER BY nome """).fetchall()
            return render_template("controle/dep_corte.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Processos":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '8117' ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo  IN ('8117     ') ORDER BY nome """).fetchall()
            return render_template("controle/dep_col_banco.html", pessoas=pessoas,  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)
        if colaborador[4]  == "Linha":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('5141' ,'5161','5162','5171','5173' )   ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE 
                                (centro_custo = '5141     ' or centro_custo = '5161     'or centro_custo = '5162     'or centro_custo = '5171     'or centro_custo = '5173     ' ) AND saldo IS NOT NULL   
                                ORDER BY nome """).fetchall()
            return render_template("controle/dep_linha.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Usinagem":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('5133' ,'5134')   ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo IN ( '5133     ' ,'5134     ' )   ORDER BY nome """).fetchall()
            return render_template("controle/dep_usinagem.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "RH":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC IN ('2111','2115' ,'2116','2118')   ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE
                                (centro_custo = '2111     ' or centro_custo = '2115     ' or centro_custo = '2116     'or centro_custo = '2118     ') AND saldo IS NOT NULL ORDER BY nome """).fetchall()
            return render_template("controle/dep_rh.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Financeiro":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2123'  ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo  IN ('2123     ') ORDER BY nome  """).fetchall()
            return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Fiscal":
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo  IN ('2131     ') ORDER BY nome """).fetchall()
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2131' ").fetchall()
            return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Montagem":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC in ('5181', '5182',  '5183')   ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo IN ('5181     ', '5182     ',  '5183     ')   ORDER BY nome """).fetchall()
            return render_template("controle/dep_montangem.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Expedicao":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2165'   ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                    WHERE saldo is not null and centro_custo  IN ('2165     ') ORDER BY nome """).fetchall()
            return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos, pessoas=pessoas)
        if colaborador[4]  == "Almoxarifado":
            pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE RA_CC = '2161'   ").fetchall()
            rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                        WHERE saldo is not null and (centro_custo = '2161     ' OR  matricula = '001478') ORDER BY nome """).fetchall()
            return render_template("controle/dep_col_banco.html",  nivel=nivel, id=id, departamento=colaborador[4] , rows=rows, datas=datas, matriculas=matriculas, saldos=saldos)




@app.route("/criarcolaboradores", methods=["GET", "POST"])
def criarcolaboradores():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    if request.method=='GET':
        depart = conx_rh.execute("SELECT DISTINCT RTRIM(centro_custo) AS centro_custo FROM relatorio where saldo is not null").fetchall()
        departamentos = conx_rh.execute("SELECT RTRIM(CTT_CUSTO) AS CTT_CUSTO, CTT_DESC01 AS DESC_CUSTO FROM  [192.168.1.16].[SIGA].[dbo].[CTT010] WHERE  CTT010.D_E_L_E_T_ <>'*' ").fetchall()
        return render_template("controle/adcionar_colaborador.html", departamentos=departamentos, nivel=nivel, id=id, depart=depart)
    if request.method == 'POST':
        departamentos = conx_rh.execute("SELECT CTT_CUSTO, CTT_DESC01 AS DESC_CUSTO FROM  [192.168.1.16].[SIGA].[dbo].[CTT010] WHERE  CTT010.D_E_L_E_T_ <>'*' ").fetchall()
        username=request.form.get('username')
        ccusto=request.form.get('ccusto')
        mat=request.form.get('mat')
        try:
            conx_rh.execute("INSERT INTO HSRA_010 (RA_NOME, RA_CC, RA_MAT) VALUES  ('"+username+"', '"+ccusto+"', '"+mat+"' ) ")
            conx_rh.execute("INSERT INTO relatorio (nome, centro_custo, matricula) VALUES  ('"+username+"', '"+ccusto+"', '"+mat+"' ) ")
            conx_rh.commit()
            return redirect(url_for("controle_banco_pj", mat=mat))
        except:
            return render_template("controle/adcionar_colaborador.html", departamentos=departamentos, nivel=nivel, id=id)
    return render_template("controle/adcionar_colaborador.html", departamentos=departamentos, nivel=nivel, id=id, depart=depart)

@app.route("/colaboradores_banco", methods=["GET", "POST"])
def colaboradores_banco():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010").fetchall()
    datas = conx_rh.execute("select MAX(data) as date from  data_ultima").fetchall()
    rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null  ORDER BY nome """).fetchall()
    matriculas = conx_rh.execute("SELECT max(idColaborador) as idColaborador, MatColaborador from controle_banco group by MatColaborador").fetchall()
    saldos = conx_rh.execute(f"""SELECT idColaborador, CONCAT((cast((Saldo)as int)/60) ,':',  
                              FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                              MatColaborador, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status from controle_banco """).fetchall()
    return render_template("controle/dep_col_banco.html", rows=rows, saldos=saldos, nivel=nivel, id=id, datas=datas, matriculas=matriculas, pessoas=pessoas)

@app.route("/colaboradores_banco_predio", methods=["GET", "POST"])
def colaboradores_banco_predio():
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id = session['id']
    datas = conx_rh.execute("select MAX(data) as date from  data_ultima").fetchall()
    pessoas = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010").fetchall()
    rows = conx_rh.execute(f"""SELECT nome as RA_NOME, matricula as RA_MAT, CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS saldo, centro_custo as RA_CC, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status FROM relatorio
                                WHERE saldo is not null and ( centro_custo = '3114     ' or  centro_custo = '4111     'or centro_custo = '2151     ' or
                            centro_custo = '2111     ' or centro_custo = '2115     ' or centro_custo = '2116     ' or centro_custo = '2118     ' or 
                            centro_custo = '2123     ' or centro_custo = '8114     ' or centro_custo = '1111     ' or centro_custo = '3111     ' or 
                            centro_custo = '3113     ' or centro_custo = '3115     '  )  ORDER BY nome """).fetchall()
    matriculas = conx_rh.execute("SELECT max(idColaborador) as idColaborador, MatColaborador from controle_banco group by MatColaborador").fetchall()
    saldos = conx_rh.execute(f"""SELECT idColaborador, CONCAT((cast((Saldo)as int)/60) ,':',  
                              FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                              MatColaborador, IIF(floor(Saldo)<0, 'Negativo', 'Positivo') as status from controle_banco """).fetchall()
    return render_template("controle/dep_col_banco.html", pessoas=pessoas, rows=rows, saldos=saldos, nivel=nivel, id=id, datas=datas, matriculas=matriculas)

@app.route("/delete/<string:id>", methods=["GET", "POST"])
def delete(id):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    ## delete
    saldos = conx_rh.execute("SELECT TOP 1 * from controle_banco WHERE idColaborador = '"+id+"'").fetchall()
    for saldo in saldos:
        excluir = "update controle_banco set deletado = 's'  WHERE idColaborador = '"+id+"'" 
        conx_rh.execute(excluir)
        conx_rh.commit()
        flash('computador Deleted','warning')
        return redirect(url_for("recalculo", mat=saldo[2]))
    
@app.route("/delete_col/<string:mat>", methods=["GET", "POST"])
def delete_colaborador(mat):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    ## delete
    excluir = "delete from HSRA_010 WHERE RA_MAT = '"+mat+"'" 
    conx_rh.execute(excluir)
    conx_rh.commit()
    flash('computador Deleted','warning')
    return redirect(url_for("colaboradores_banco"))

@app.route("/controle_banco/<string:mat>", methods=["GET", "POST"])
def controle_banco(mat):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    datas_atuais=datetime.now().strftime('%Y-%m-%d')
    rows = conx_rh.execute(f"""SELECT *, Intervaloc_fin, CONCAT(((Trabalhado_total)/60) ,':', 
                            FORMAT(((((cast((Trabalhado_total)as real)/60)) - ((Trabalhado_total)/60))*60), '0#')) AS Trabalhado_total, 
                            CONCAT((cast((Saldo)as int)/60) ,':',  FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo, 
                            concat((cast((Compensado_total)as int)/60) ,':', abs(FORMAT(((((cast((Compensado_total)as real)/60)) - (cast((Compensado_total)as int)/60))*60), '0#'))) 
                            AS Compensado_total from controle_banco WHERE MatColaborador = '{mat}' ORDER BY idColaborador DESC""").fetchall()
    dados = conx_rh.execute(f"""SELECT TOP 1  RA_NOME, RA_CC, RA_MAT FROM [192.168.1.16].[SIGA].[dbo].[SRA010], [192.168.1.16].[SIGA].[dbo].[SRJ010], [192.168.1.16].[SIGA].[dbo].[CTT010] 
                            WHERE  
                            SRA010.RA_MAT = '{mat}'   """).fetchall()
    datas = conx_rh.execute("select MAX(Data) as date from  controle_banco").fetchall()
    saldos = conx_rh.execute("SELECT TOP 1 Saldo, idColaborador from controle_banco  WHERE Saldo IS NOT NULL AND MatColaborador = '"+mat+"' ORDER BY idColaborador DESC").fetchall()
    mat=mat
    return render_template("controle/controle_banco.html", datas_atuais=datas_atuais, rows=rows, dados=dados, mat=mat, nivel=nivel, id=id_usuario, datas=datas, saldos=saldos)

@app.route("/recalculo/<string:mat>", methods=["GET", "POST"])
def recalculo(mat):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    rows = conx_rh.execute("select idColaborador from controle_banco where MatColaborador = '"+mat+"' and deletado is NULL").fetchall()
    for row in rows:
        horas = conx_rh.execute("select ((SUM(Trabalhado_total))-(SUM(Compensado_total))) from controle_banco where MatColaborador =  '"+mat+"'  and idColaborador <= '"+str(row[0])+"' and deletado is NULL").fetchall()
        for hora in horas:
            conx_rh.execute("update controle_banco SET Saldo = '"+str(hora[0])+"' where MatColaborador = '"+mat+"' and  idColaborador = '"+str(row[0])+"' and deletado is NULL")
            conx_rh.execute("UPDATE relatorio SET saldo = (?) where matricula = (?)", (str(hora[0]), mat) )
    conx_rh.commit()
    return redirect(url_for("controle_banco", mat=mat))

@app.route("/controle_banco_pj/<string:mat>", methods=["GET", "POST"])
def controle_banco_pj(mat):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    dados = conx_rh.execute("SELECT RA_NOME, RA_CC, RA_MAT FROM HSRA_010 WHERE  RA_MAT = '"+mat+"'").fetchall()
    rows = conx_rh.execute(f"""SELECT *, CONCAT((cast((Saldo)as int)/60) ,':',  
                            FORMAT(abs((((((cast((Saldo)as real)/60)) - (cast((Saldo)as int)/60))*60))), '0#')) AS Saldo 
                            from controle_banco WHERE MatColaborador = '{mat}' ORDER BY idColaborador DESC""").fetchall()
    datas = conx_rh.execute("select MAX(Data) as date from  controle_banco").fetchall()
    saldos = conx_rh.execute("SELECT TOP 1 Saldo, idColaborador from controle_banco  WHERE Saldo IS NOT NULL AND MatColaborador = '"+mat+"' ORDER BY idColaborador DESC").fetchall()
    mat=mat
    return render_template("controle/controle_banco.html", rows=rows, dados=dados, mat=mat, nivel=nivel, id=id_usuario, datas=datas, saldos=saldos)

@app.route("/controle_banco_form/<string:mat>", methods=["GET", "POST"])
def controle_banco_form(mat):
    if not session.get('logged_in'):
        return redirect(url_for('homepage'))
    emails = session['email'] 
    nivel = session['nivel'] 
    id_usuario = session['id']
    if request.method == 'POST':
        data=request.form.get('data')
        data_insercao=datetime.now().strftime('%d/%m/%Y %H:%M')
        trabalhado_ini=request.form.get('trabalhado_ini')
        trabalhado_fin=request.form.get('trabalhado_fin')
        compensado_ini=request.form.get('compensado_ini')
        compensado_fin=request.form.get('compensado_fin')
        intervalo_ini=request.form.get('intervalo_ini')
        intervalo_fin=request.form.get('intervalo_fin')
        intervaloc_ini=request.form.get('intervaloc_ini')
        intervaloc_fin=request.form.get('intervaloc_fin')
        conx_rh.execute("INSERT INTO controle_banco(Matcolaborador, Data, Trabalhado_ini, Trabalhado_fin, Compensado_ini, Compensado_fin, Intervalo_ini, Intervalo_fin, Intervaloc_ini, Intervaloc_fin, data_insercao, inserido) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                        (mat, data, trabalhado_ini, trabalhado_fin, compensado_ini, compensado_fin, intervalo_ini, intervalo_fin, intervaloc_ini, intervaloc_fin, data_insercao, emails))
        conx_rh.execute("update controle_banco SET Trabalhado_total = DATEDIFF(MINUTE, Trabalhado_ini, Trabalhado_fin) where Intervalo_ini = ''")
        conx_rh.execute("update controle_banco SET Trabalhado_total = (DATEDIFF(MINUTE, Trabalhado_ini, Trabalhado_fin) -  DATEDIFF(MINUTE, Intervalo_ini, Intervalo_fin))  where Intervalo_ini != ''")
        conx_rh.execute("update controle_banco SET Compensado_total = (DATEDIFF(MINUTE, Compensado_ini, Compensado_fin) -  DATEDIFF(MINUTE, Intervaloc_ini, intervaloc_fin))  where Intervaloc_ini != ''")
        conx_rh.execute("update controle_banco SET Compensado_total = DATEDIFF(MINUTE, Compensado_ini, Compensado_fin) where Intervaloc_ini = ''")
        conx_rh.execute("update controle_banco SET Trabalhado_total = '0' WHERE Trabalhado_ini  = ''")
        conx_rh.execute("update controle_banco SET Compensado_total = '0' WHERE Compensado_ini = ''")
        conx_rh.commit()
        return redirect(url_for("controle_banco_submit", mat=mat))
    return render_template("controle_banco.html", nivel=nivel, id=id_usuario)
               

@app.route("/controle_banco_submit/<string:mat>", methods=["GET", "POST"])
def controle_banco_submit(mat):
    datas = conx_rh.execute("SELECT TOP 1 Trabalhado_total, Compensado_total, Saldo, idColaborador from controle_banco where MatColaborador = '"+mat+"'  ORDER BY idColaborador DESC").fetchall()
    saldos = conx_rh.execute("SELECT TOP 1 Saldo from controle_banco  WHERE Saldo IS NOT NULL AND MatColaborador = '"+mat+"' ORDER BY idColaborador DESC").fetchall()
    for data in datas:
        if saldos:
            trabalhado=int(data[0])
            compensado=int(data[1])
            id_data=data[3]
            for saldo in saldos:
                if trabalhado == 0:
                    maximo=(int(saldo[0])-compensado)
                else:
                    maximo=(int(saldo[0])+trabalhado)
                print(maximo)
                conx_rh.execute("update controle_banco SET Saldo = (?) where idColaborador = (?)", (maximo, id_data) )
                conx_rh.commit()
                conx_rh.execute("UPDATE relatorio SET saldo = (?) where matricula = (?)", (maximo, mat) )
                conx_rh.commit()
        else:
            trabalhado=f'{data[0]}'
            compensado=f'-{data[1]}'
            id_data=data[3]
            if trabalhado != '0':
                conx_rh.execute("update controle_banco SET Saldo = (?) where idColaborador = (?)", (trabalhado, id_data) )
                conx_rh.commit()
                conx_rh.execute("UPDATE relatorio SET saldo = (?) where matricula = (?)", (trabalhado, mat) )
                conx_rh.commit()
                conx_rh.execute("UPDATE HSRA_010 SET saldo = (?) where RA_MAT = (?)", (trabalhado, mat) )
                conx_rh.commit()
            elif compensado != '0':
                conx_rh.execute("update controle_banco SET Saldo = (?) where idColaborador = (?)", (compensado, id_data) )
                conx_rh.commit()
                conx_rh.execute("UPDATE relatorio SET saldo = (?) where matricula = (?)", (compensado, mat) )
                conx_rh.commit()
    return redirect(url_for("controle_banco", mat=mat))

