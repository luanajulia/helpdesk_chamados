import pyodbc

conx_man = pyodbc.connect('Driver={SQL Server};''Server=192.168.1.203;''Database=FABmanutencao;''UID=sa;''PWD=Serfeliz@1505')
conx_manutencao = conx_man.cursor()

conx_suporte = pyodbc.connect('Driver={SQL Server};''Server=192.168.1.203;''Database=TECsuporte;''UID=sa;''PWD=Serfeliz@1505')
conx = conx_suporte.cursor()

conx_banco = pyodbc.connect('Driver={SQL Server};''Server=192.168.1.203;''Database=DPbancohoras;''UID=sa;''PWD=Serfeliz@1505')
conx_rh = conx_banco.cursor()

caminho = ("C:/inetpub/wwwroot/PROJETO_HELPDESK/inventarioapema/static/")

conx_mes = pyodbc.connect('Driver={SQL Server};''Server=192.168.1.203;''Database=FABautomacao;''UID=sa;''PWD=Serfeliz@1505')
conx_mes = conx_mes.cursor()