import streamlit as st
import openai
from openai import AzureOpenAI
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from streamlit_option_menu import option_menu
from streamlit_chat import message
import plotly.express as px
import pandas as pd
import numpy as np

# Función para obtener el secreto desde Azure Key Vault
def get_secret(secret_name):
    try:
        key_vault_name = st.secrets["KEY_VAULT_NAME"]
        KVUri = f"https://{key_vault_name}.vault.azure.net"

        credential = ClientSecretCredential(
            client_id=st.secrets["AZURE_CLIENT_ID"],
            client_secret=st.secrets["AZURE_CLIENT_SECRET"],
            tenant_id=st.secrets["AZURE_TENANT_ID"]
        )
        client = SecretClient(vault_url=KVUri, credential=credential)
        retrieved_secret = client.get_secret(secret_name)
        return retrieved_secret.value
    except KeyError as e:
        st.error(f"Clave faltante en los secretos: {e}")
        return None
    except Exception as e:
        st.error(f"Error al obtener el secreto: {e}")
        return None

# Obtener la clave de API de Azure OpenAI desde Key Vault
api_key = get_secret('dammgpt')

if not api_key:
    st.stop()

# Obtener el endpoint de Azure OpenAI desde los secretos
azure_openai_endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]

# Configurar la API de OpenAI para Azure
openai.api_type = "azure"
openai.api_base = azure_openai_endpoint  # Asegúrate de que incluye 'https://'
openai.api_version = "2023-03-15-preview"
openai.api_key = api_key

# Aplicar estilos CSS personalizados
def local_css():
    st.markdown("""
        <style>
            /* Tu CSS personalizado */
        </style>
        """, unsafe_allow_html=True)

local_css()

# Título con estilo actualizado
st.markdown("""
    <div class="main-title">
        <h1>ReFill ReTrain ReJoin</h1>
    </div>
    """, unsafe_allow_html=True)

# Menú de navegación horizontal
selected = option_menu(
    menu_title=None,
    options=["Leisure", "ReFill", "Chatbot", "Análisis"],
    icons=["sun", "droplet", "robot", "bar-chart"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important"},
        "nav-link": {"--hover-color": "#e0e0e0"},
        "nav-link-selected": {"background-color": "#1abc9c"},
    }
)

choice = selected

# Definir el prompt de sistema
system_prompt = "Eres CoachGPT, un asistente virtual experto en entrenamiento y nutrición deportiva. Proporcionas consejos personalizados y motivación a los usuarios."

# Función para obtener la respuesta del modelo usando Azure OpenAI
def obtener_respuesta(messages, model='gpt4onennisi'):
    try:
        respuesta = openai.ChatCompletion.create(
            engine=model,
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        respuesta = respuesta.choices[0].message.content  # Extraer el contenido del mensaje
        return respuesta
    except Exception as e:
        st.error(f"Error al obtener la respuesta: {e}")
        print(f"Error detallado: {e}")  # Para registros adicionales
        return "Lo siento, hubo un error al procesar tu solicitud."

# Función para mostrar el formulario de login
def mostrar_login():
    st.subheader("Por favor, inicia sesión para acceder al chatbot.")
    username = st.text_input("Nombre de usuario")
    password = st.text_input("Contraseña", type="password")
    user_saved = st.secrets["username"]
    pass_saved = st.secrets["password"]
    if st.button("Iniciar sesión"):
        if username == user_saved and password == pass_saved:
            st.session_state['logged_in'] = True
            st.success("¡Has iniciado sesión correctamente!")
            st.rerun()
        else:
            st.error("Nombre de usuario o contraseña incorrectos.")

# Secciones de la aplicación
if choice == "Leisure":
    # Tu código para la sección Leisure

elif choice == "ReFill":
    # Tu código para la sección ReFill

elif choice == "Chatbot":
    st.header("Coach GPT")

    # Verificar si el usuario ha iniciado sesión
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        mostrar_login()
    else:
        # Inicializar variables de sesión si no existen
        if 'messages' not in st.session_state:
            st.session_state['messages'] = [{"role": "system", "content": system_prompt}]
        if 'historial' not in st.session_state:
            st.session_state['historial'] = []

        # Mostrar el historial del chat
        for i, msg in enumerate(st.session_state['messages'][1:]):  # Omitir el prompt de sistema
            if msg['role'] == 'user':
                message(msg['content'], is_user=True, key=f"user_{i}")
            elif msg['role'] == 'assistant':
                message(msg['content'], is_user=False, key=f"bot_{i}")

        # Entrada del usuario
        usuario_input = st.text_input("Escribe tu mensaje:", key="input")

        if st.button("Enviar"):
            if usuario_input:
                # Agregar el mensaje del usuario al historial
                st.session_state['messages'].append({"role": "user", "content": usuario_input})
                # Obtener respuesta del modelo
                respuesta = obtener_respuesta(st.session_state['messages'])
                # Agregar la respuesta del asistente al historial
                st.session_state['messages'].append({"role": "assistant", "content": respuesta})
                # Actualizar la interfaz
                st.experimental_rerun()
            else:
                st.warning("Por favor, escribe un mensaje.")

        # Botón para cerrar sesión
        if st.button("Cerrar sesión"):
            st.session_state['logged_in'] = False
            st.success("Has cerrado sesión.")
            st.experimental_rerun()

elif choice == "Análisis":
    # Tu código para la sección Análisis

# Footer con estilo actualizado
st.markdown("""
    <div class="footer">
        © 2024 Tu Nombre. Todos los derechos reservados.
    </div>
    """, unsafe_allow_html=True)
