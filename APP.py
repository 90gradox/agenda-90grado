import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# CONFIGURACIÓN ESTILO "APPLE GLASS"
st.set_page_config(page_title="90GRADOX App", page_icon="📸", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F2F2F7; }
    [data-testid="stSidebar"] { background-color: #1C1C1E; color: white; }
    .main-card { 
        background-color: white; padding: 25px; border-radius: 15px; 
        border: 1px solid #D1D1D6; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    .stButton>button {
        background-color: #0A84FF; color: white; border-radius: 12px;
        width: 100%; border: none; height: 3em; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ARCHIVO DE DATOS
ARCHIVO = "DB_90Gradox_Master.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO):
        try: return pd.read_csv(ARCHIVO, sep=";", encoding="utf-8-sig")
        except: return pd.DataFrame(columns=["Nombre", "WhatsApp", "Tipo", "Fecha", "Hora", "Precio", "Anticipo", "Nota"])
    return pd.DataFrame(columns=["Nombre", "WhatsApp", "Tipo", "Fecha", "Hora", "Precio", "Anticipo", "Nota"])

if 'datos' not in st.session_state:
    st.session_state.datos = cargar_datos()

# MENÚ LATERAL
with st.sidebar:
    st.title("90GRADOX")
    opcion = st.radio("MENÚ", ["➕ Nueva Sesión", "📸 Ver Agendas", "🧮 Calculadora"])

# --- MODULO: NUEVA SESIÓN ---
if opcion == "➕ Nueva Sesión":
    st.header("Registrar Sesión")
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("👤 CLIENTE").upper()
        whatsapp = st.text_input("📱 WHATSAPP")
        tipo = st.selectbox("🎞️ TIPO", ["STUDIO","REVELACION","EXTERIOR","PROFESIONAL", "CUMPLEAÑOS", "BEBE", "MATERNIDAD", "15 AÑOS", "BODA", "POLITICO", "EVENTO SOCIAL"])
    
    with col2:
        fecha = st.date_input("📅 FECHA", datetime.now())
        hora = st.time_input("⏰ HORA", datetime.now())
        precio = st.number_input("💵 TOTAL", min_value=0)
        anticipo = st.number_input("💰 ABONO", min_value=0)
    
    nota = st.text_area("📝 NOTA").upper()
    
    if st.button("GUARDAR EN IPHONE"):
        nueva = pd.DataFrame([{
            "Nombre": nombre, "WhatsApp": whatsapp, "Tipo": tipo,
            "Fecha": fecha.strftime("%d/%b/%Y"), "Hora": hora.strftime("%I:%M %p"),
            "Precio": precio, "Anticipo": anticipo, "Nota": nota
        }])
        st.session_state.datos = pd.concat([st.session_state.datos, nueva], ignore_index=True)
        st.session_state.datos.to_csv(ARCHIVO, sep=";", index=False, encoding="utf-8-sig")
        st.success(f"✅ Guardado: {nombre}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MODULO: VER AGENDAS ---
elif opcion == "📸 Ver Agendas":
    st.header("Agenda 90GRADOX")
    if not st.session_state.datos.empty:
        # Buscador rápido para iPhone
        busqueda = st.text_input("🔍 Buscar cliente...").upper()
        df_filtrado = st.session_state.datos[st.session_state.datos['Nombre'].str.contains(busqueda)]
        
        st.dataframe(df_filtrado, use_container_width=True)
        
        st.divider()
        sel = st.selectbox("Selecciona para enviar recordatorio:", df_filtrado.index, 
                           format_func=lambda x: f"{df_filtrado.loc[x, 'Nombre']} - {df_filtrado.loc[x, 'Fecha']}")
        
        c = df_filtrado.loc[sel]
        
        # BOTÓN WHATSAPP CON TU MENSAJE
        mensaje = (f"Hola {c['Nombre']}, te saludamos de *90GRADOX*. 📸 "
                   f"Te recordamos tu sesión *{c['Tipo']}* "
                   f"el día *{c['Fecha']}* a las *{c['Hora']}*. ¡Te esperamos!")
        
        link_wa = f"https://wa.me/{c['WhatsApp']}?text={urllib.parse.quote(mensaje)}"
        st.link_button("💬 ENVIAR WHATSAPP", link_wa)
        
        if st.button("🗑️ ELIMINAR SESIÓN", type="secondary"):
            st.session_state.datos = st.session_state.datos.drop(sel)
            st.session_state.datos.to_csv(ARCHIVO, sep=";", index=False, encoding="utf-8-sig")
            st.rerun()
    else:
        st.info("No hay citas.")