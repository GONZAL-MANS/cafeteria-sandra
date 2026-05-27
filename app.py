import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from datetime import datetime

# Conectar Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
cliente = gspread.authorize(creds)
planilla = cliente.open("PEDIDOS SANDRA").sheet1

# Modelo
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=st.secrets["GEMINI_API_KEY"])

# Herramienta
@tool
def registrar_pedido(producto: str, cantidad: int) -> str:
    """Registra un pedido de un cliente en Google Sheets.
    Úsala cuando el cliente confirme que quiere pedir algo."""
    hora = datetime.now().strftime("%H:%M")
    planilla.append_row([hora, producto, cantidad])
    return f"✅ Pedido registrado: {cantidad}x {producto} a las {hora}"

tools = [registrar_pedido]
llm_con_tools = llm.bind_tools(tools)

# Historial
if "historial" not in st.session_state:
    st.session_state.historial = [
        SystemMessage(content="""Eres el asistente virtual de la Cafetería de Sandra en Bolivia.
        Eres amable y respondes como un empleado real. El menú es:
        Café negro 10 Bs, Café con leche 15 Bs, Capuchino 20 Bs,
        Té 8 Bs, Jugo natural 12 Bs, Sándwich 25 Bs, Torta 18 Bs.
        Cuando un cliente confirme un pedido, usa la herramienta registrar_pedido.
        Responde siempre en el idioma en que te hablen.""")
    ]

# Interfaz
st.title("☕ Cafetería de Sandra")
st.write("Hola, soy el asistente virtual. ¿En qué te puedo ayudar?")

for mensaje in st.session_state.historial[1:]:
    if isinstance(mensaje, HumanMessage):
        with st.chat_message("user"):
            st.write(mensaje.content)
    elif isinstance(mensaje, AIMessage):
        if isinstance(mensaje.content, str) and mensaje.content:
            with st.chat_message("assistant"):
                st.write(mensaje.content)

pregunta = st.chat_input("Escribe tu mensaje aquí...")
if pregunta:
    st.session_state.historial.append(HumanMessage(content=pregunta))
    with st.chat_message("user"):
        st.write(pregunta)

    respuesta = llm_con_tools.invoke(st.session_state.historial)

    if respuesta.tool_calls:
        for llamada in respuesta.tool_calls:
            if llamada["name"] == "registrar_pedido":
                resultado = registrar_pedido.invoke(llamada["args"])
                st.success(resultado)

    st.session_state.historial.append(respuesta)

    if isinstance(respuesta.content, str) and respuesta.content:
        with st.chat_message("assistant"):
            st.write(respuesta.content)
    elif isinstance(respuesta.content, list):
        for bloque in respuesta.content:
            if isinstance(bloque, dict) and bloque.get("type") == "text" and bloque.get("text"):
                with st.chat_message("assistant"):
                    st.write(bloque["text"])
