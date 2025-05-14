# envio_correos.py
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

LOG_FILE = "registro_envios.log"

def enviar_correo(destinatario, asunto, cuerpo, gmail, password, cc=None, bcc=None, adjunto_path=None):
    try:
        msg = EmailMessage()
        msg["Subject"] = asunto
        msg["From"] = gmail
        msg["To"] = destinatario
        if cc:
            msg["Cc"] = cc
        if bcc:
            msg["Bcc"] = bcc

        msg.set_content(cuerpo)

        # Adjuntar archivo si se proporciona
        if adjunto_path and os.path.exists(adjunto_path):
            with open(adjunto_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(adjunto_path)
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail, password)
            smtp.send_message(msg)

        registrar_log(destinatario, asunto, "ENVIADO")

    except Exception as e:
        registrar_log(destinatario, asunto, f"ERROR: {e}")
        raise e

def registrar_log(destinatario, asunto, estado):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{datetime.now()} | {destinatario} | {asunto} | {estado}\n")

