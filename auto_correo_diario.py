# auto_correo_diario.py
import schedule
import time
import pandas as pd
from procesador_envio_correo import procesar_evento, cargar_datos

def tarea_diaria():
    print("⏰ Iniciando revisión de eventos...")

    try:
        df = cargar_datos()[0]  # Solo necesitamos el DataFrame, no la hoja
        eventos_unicos = df["Número de evento"].dropna().unique()

        for evento in eventos_unicos:
            print(f"\n🔍 Procesando evento {evento}")
            resultado = procesar_evento(int(evento))
            print(f"→ Resultado: {resultado}")
    
    except Exception as e:
        print(f"⚠️ Error en la ejecución: {e}")

# Ejecutar todos los días a las 8:00 AM
schedule.every().day.at("08:00").do(tarea_diaria)

print("🟢 Sistema automático de correos iniciado. Esperando próxima ejecución...")

# Bucle infinito para mantener el script corriendo
while True:
    schedule.run_pending()
    time.sleep(60)
