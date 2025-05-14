# front_envio_correo.py
import streamlit as st
from procesador_envio_correo import procesar_evento, obtener_historial
import pandas as pd

st.set_page_config(page_title="Gestión de Correos de Eventos", layout="centered")

st.title("📬 Herramienta de Envío de Correos - Educación Continua")

# --- SECCIÓN: EVENTO ---
st.header("📌 Gestión por evento")
numero_evento = st.text_input("Número del evento", placeholder="Ej: 1")
col1, col2 = st.columns(2)

with col1:
    procesar = st.button("📨 Procesar y Enviar")
with col2:
    reenviar = st.button("🔁 Reenviar todos los correos")

# --- MENSAJE DE ESTADO ---
if procesar and numero_evento:
    with st.spinner("Enviando correos nuevos..."):
        resultado = procesar_evento(
            numero_evento=int(numero_evento),
            reenviar_todo=False
        )
    st.success(resultado)

elif reenviar and numero_evento:
    with st.spinner("Reenviando todos los correos del evento..."):
        resultado = procesar_evento(
            numero_evento=int(numero_evento),
            reenviar_todo=True
        )
    st.success("Reenvío completado. " + resultado)

elif (procesar or reenviar) and not numero_evento:
    st.error("⚠️ Por favor, ingresa el número del evento.")

# --- SECCIÓN: HISTORIAL DE ENVÍOS ---
st.header("📄 Historial de envíos por evento")

if numero_evento:
    log_df = obtener_historial(int(numero_evento))
    if not log_df.empty:
        log_df["Estado"] = log_df["Estado"].apply(lambda x: "✅ ENVIADO" if "ENVIADO" in x else "❌ ERROR")
        st.dataframe(log_df.sort_values(by="Fecha", ascending=False))
    else:
        st.info("No hay registros de envío para este evento.")

# Juana es la mejor
