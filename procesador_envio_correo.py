
# procesador_envio_correo.py
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from envio_correos import enviar_correo
import os

# Config Google Sheets
RUTA_JSON = "google.json"
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1kQzayuhHiNeLjBlnpEXfIzSavmzKvEcpnyHiat-8umQ/edit?gid=0#gid=0"
LOG_FILE = "registro_envios.log"

# ✉️ Credenciales fijas de envío
gmail = "miguezuletamedina@gmail.com"
password = "bglfevprxkzpdfgj"  # Reemplázala con la real

def cargar_datos():
    credenciales = Credentials.from_service_account_file(RUTA_JSON, scopes=SCOPE)
    cliente = gspread.authorize(credenciales)
    hoja = cliente.open_by_url(SPREADSHEET_URL).sheet1
    return pd.DataFrame(hoja.get_all_records()), hoja

def guardar_datos(hoja, df):
    try:
        print(f"📄 Guardando en hoja: {hoja.title} con {len(df)} filas")
        hoja.clear()
        hoja.update([df.columns.values.tolist()] + df.values.tolist())
        print("✅ Datos guardados exitosamente")
    except Exception as e:
        print(f"❌ Error al guardar datos en Google Sheets: {e}")

def procesar_evento(numero_evento: int, reenviar_todo=False):
    hoy = datetime.today().date()
    df, hoja = cargar_datos()

    enviados = 0
    errores = 0

    for idx, row in df[df["Número de evento"] == numero_evento].iterrows():
        nombre = row["Nombre"]
        correo = row["Correo"]
        estado = row["Estado"].strip().lower()

        try:
            # 1. Envío inicial
            if estado == "no ha pagado" and (not row["Envío Inicial"] or reenviar_todo):
                asunto = f"📄 Información del evento {numero_evento}"
                cuerpo = f"""
Hola {nombre},

Gracias por tu interés en el evento número {numero_evento}.
Te recordamos que tu inscripción está pendiente de pago.

📌 Información general:
- Fecha del evento: {row['Fecha del Evento']}
- Link de pago: [INSERTA AQUÍ LINK DE PAGO]

Cualquier duda, contáctanos.

Saludos cordiales,  
Universidad CES
"""
                enviar_correo(correo, asunto, cuerpo, gmail, password)
                df.at[idx, "Envío Inicial"] = str(hoy)
                enviados += 1

            # 2. Recordatorio cada 7 días si no ha pagado
            elif estado == "no ha pagado" and row["Envío Inicial"]:
                ultima_fecha = row.get("Último Recordatorio", "")
                dias_desde_ultimo = (
                    (hoy - datetime.strptime(ultima_fecha, "%Y-%m-%d").date()).days
                    if ultima_fecha else 999
                )
                if dias_desde_ultimo >= 7 or reenviar_todo:
                    asunto = f"🔔 Recordatorio de pago — Evento {numero_evento}"
                    cuerpo = f"""
Hola {nombre},

Este es un recordatorio amigable para informarte que tu inscripción al evento número {numero_evento} aún está pendiente de pago.

📅 Fecha del evento: {row['Fecha del Evento']}
🔗 Link de pago: [INSERTA AQUÍ LINK DE PAGO]

Si ya realizaste el pago, por favor ignora este mensaje.

Saludos cordiales,  
Universidad CES
"""
                    enviar_correo(correo, asunto, cuerpo, gmail, password)
                    df.at[idx, "Último Recordatorio"] = str(hoy)
                    enviados += 1

            # 3. Confirmación si ya pagó
            elif estado == "pagado" and (not row["Confirmación Enviada"] or reenviar_todo):
                asunto = f"✅ Confirmación de inscripción — Evento {numero_evento}"
                cuerpo = f"""
Hola {nombre},

Confirmamos tu inscripción al evento número {numero_evento}.

📅 Fecha: {row['Fecha del Evento']}
📍 Lugar: Universidad CES

Gracias por completar el proceso. ¡Nos vemos en el evento!

Atentamente,  
Universidad CES
"""
                enviar_correo(correo, asunto, cuerpo, gmail, password)
                df.at[idx, "Confirmación Enviada"] = str(hoy)
                enviados += 1

            # 4. Recordatorio un día antes si ya pagó
            elif estado == "pagado":
                fecha_evento = datetime.strptime(row["Fecha del Evento"], "%Y-%m-%d").date()
                dias_faltantes = (fecha_evento - hoy).days
                if dias_faltantes == 1 and (not row.get("Correo Día Antes Enviado") or reenviar_todo):
                    asunto = f"📢 Recordatorio: Asiste mañana al evento {numero_evento}"
                    cuerpo = f"""
Hola {nombre},

Te recordamos que mañana se llevará a cabo el evento número {numero_evento} al que estás inscrito.

📅 Fecha: {row['Fecha del Evento']}
📍 Lugar: Universidad CES

¡Nos vemos pronto!

Atentamente,  
Universidad CES
"""
                    enviar_correo(correo, asunto, cuerpo, gmail, password)
                    df.at[idx, "Correo Día Antes Enviado"] = str(hoy)
                    enviados += 1

        except Exception as e:
            errores += 1
            print(f"❌ Error al enviar a {correo}: {e}")

    print(f"💾 Cambios detectados, guardando datos para evento {numero_evento}")
    guardar_datos(hoja, df)

    return f"✅ Correos enviados: {enviados} | ❌ Errores: {errores} | Base actualizada para el evento {numero_evento}."

def obtener_historial(numero_evento: int):
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    with open(LOG_FILE, "r", encoding="utf-8") as log:
        lineas = log.readlines()

    registros = []
    for linea in lineas:
        partes = linea.strip().split(" | ")
        if len(partes) == 4:
            fecha, correo, asunto, estado = partes
            if f"evento {numero_evento}" in asunto.lower():
                registros.append({
                    "Fecha": fecha,
                    "Correo": correo,
                    "Asunto": asunto,
                    "Estado": estado
                })

    return pd.DataFrame(registros)
