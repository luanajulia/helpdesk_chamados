# import the necessary components first
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
novo = 'novo'

conn = sqlite3.connect( 'C:/Users/luanavieira/Documents/PROJETOS_PYTHON/PROJETO_HELPDESK/instance/comunidade.db', check_same_thread=False)
cur = conn.cursor()
cur.execute("SELECT id, username, departamento, tipo, status FROM manutencao WHERE status LIKE '"+novo+"'")
quant = "SELECT  COUNT(*) FROM manutencao WHERE status LIKE 'novo'"
rows = cur.fetchall()
quantidades = cur.execute(quant).fetchall()
# Define SMTP server and authentication details
smtp_server = 'smtp.outlook.com'
smtp_port = 587
smtp_username = 'suporte@apema.com.br'
smtp_password = 'Apema@2019'
for quantidade in quantidades:
    html = f"""<p>Bom dia,<br> Quantidade de Chamados em aberto: {quantidade[0]}<p>"""
    html += f""" <table  style="border: 1px solid #333;">"""
    html += f"""<tr>"""
    html += f"""<th scope="col" style="border: 1px solid #333;">OS</th>"""
    html += f"""<th scope="col" style="border: 1px solid #333;">Usuario</th>"""
    html += f"""<th scope="col" style="border: 1px solid #333;">Departamento</th>"""
    html += f"""<th scope="col" style="border: 1px solid #333;">Tipo</th>"""
    html += f"""<th scope="col" style="border: 1px solid #333;">Status</th>"""
    html += f"""<th scope="col" style="border: 1px solid #333;">Editar</th>"""
    html += f"""</tr>"""
    for row in rows:
        html += f"""<tr>"""
        html += f"""<td style='border: 1px solid #333;'>{row[0]}</td>"""
        html += f"""<td style="border: 1px solid #333;">{row[1]}</td>"""
        html += f"""<td style="border: 1px solid #333;">{row[2]}</td>"""
        html += f"""<td style="border: 1px solid #333;">{row[3]}</td>"""
        html += f"""<td style="border: 1px solid #333;">{row[4]}</td>"""
        html += f"""<td style="border: 1px solid #333;">http://192.168.1.51:8090/edit_chamados_manutencao/{row[0]}</td>"""
        html += f"""</tr>"""
    html += f"""</table>"""

# Create an email message
message = MIMEText(html, "html")
message['Subject'] = 'Diario: Chamados que estão em abertos'
message['From'] = 'suporte@apema.com.br'
message['To'] = 'suporte@apema.com.br'

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