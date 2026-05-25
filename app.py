import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

st.title("☕ Cafetería de Sandra")
st.write("Hola, soy el asistente virtual de la cafetería. ¿En qué te puedo ayudar?")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=st.secrets["GEMINI_API_KEY"])

if "historial" not in st.session_state:
    st.session_state.historial = [
        SystemMessage(content="""Eres un asistente virtual de una cafetería en Bolivia llamada Cafetería de Sandra. 
        Eres amable y respondes como un empleado real. El menú es:
        Café negro 10 Bs, Café con leche 15 Bs, Capuchino 20 Bs, 
        Té 8 Bs, Jugo natural 12 Bs, Sándwich 25 Bs, Torta 18 Bs.
        Responde siempre en el idioma en que te hablen.""")
    ]

for mensaje in st.session_state.historial[1:]:
    if isinstance(mensaje, HumanMessage):
        with st.chat_message("user"):
            st.write(mensaje.content)
    elif isinstance(mensaje, AIMessage):
        with st.chat_message("assistant"):
            st.write(mensaje.content)

pregunta = st.chat_input("Escribe tu mensaje aquí...")

if pregunta:
    st.session_state.historial.append(HumanMessage(content=pregunta))
    with st.chat_message("user"):
        st.write(pregunta)
    respuesta = llm.invoke(st.session_state.historial)
    st.session_state.historial.append(AIMessage(content=respuesta.content))
    with st.chat_message("assistant"):
        st.write(respuesta.content)
