import streamlit as st
import openai
from openai import AzureOpenAI
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from streamlit_option_menu import option_menu
from streamlit_chat import message
import plotly.express as px  # Importar Plotly Express
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
openai.api_version = "2023-12-01-preview"
openai.api_key = api_key

# Definir el prompt de sistema
system_prompt = "Eres CoachGPT (DEMO), un asistente virtual experto en entrenamiento y nutrición deportiva. Serás usado para una demostración de proyecto en la empresa que trabajo. Para ello proporcionas consejos personalizados y motivación a los usuarios que prueben esta App / hablen contigo. Empieza presentándote y pregunta en qué puedes ayudar respecto a planificación deportiva y de hidratación.Se supone que estas sincronizado con la App de Strava/ del gimnasio de la persona con la que hablas y te basas en sus últimos entrenamientos (inventatelos). Todo esto es una demo pero deberías actuar como si todo fuera real, claro. Muchas gracias!"

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
        <h1>WellDamm</h1>
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

# Función para obtener la respuesta del modelo usando Azure OpenAI
def obtener_respuesta(messages, model='gpt4onennisi'):
    cliente = AzureOpenAI(
        azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
        api_key=api_key,
        api_version="2023-12-01-preview"
    )
    try:
        respuesta = cliente.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000,
            tool_choice=None,
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
    user_saved = st.secrets["username"]
    pass_saved = st.secrets["password"]
    with st.form(key='login_form'):
        username = st.text_input("Nombre de usuario")
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button(label='Iniciar sesión')
        if submit_button:
            if username == user_saved and password == pass_saved:
                st.session_state['logged_in'] = True
                st.success("¡Has iniciado sesión correctamente!")
                st.rerun()  # Forzar recarga del script
            else:
                st.error("Nombre de usuario o contraseña incorrectos.")

# Secciones de la aplicación
if choice == "Leisure":
    st.header("Actividades de Ocio")
    # Añadir imagen 'estrella-damm.jpg'
    st.image('estrella-damm.jpg', caption='Estrella Damm', use_column_width=True)
    # Puedes añadir más contenido aquí si lo deseas

elif choice == "ReFill":
    st.header("Consulta los litros que quedan o faltan en tu suscripción")
    # Datos de ejemplo para el gráfico de consumo
    df_consumo = pd.DataFrame({
        'Bebida': ['Proteica', 'Mineral'],
        'Consumo (litros)': [12, 8]
    })

    # Crear gráfico de barras
    fig = px.bar(df_consumo, x='Bebida', y='Consumo (litros)', color='Bebida',
                 title='Consumo de Bebidas')

    st.plotly_chart(fig)

    # Tabla con plan de hidratación para una maratón
    st.subheader("Plan de Hidratación para Maratón")
    plan_hidratacion = pd.DataFrame({
        'Kilómetro': [5, 10, 15, 20, 25, 30, 35, 40],
        'Bebida': ['Agua', 'Bebida Isotónica', 'Agua', 'Gel Energético', 'Agua', 'Bebida Isotónica', 'Agua', 'Gel Energético'],
        'Cantidad (ml)': [200, 250, 200, 30, 200, 250, 200, 30]
    })
    st.table(plan_hidratacion)

elif choice == "Chatbot":
    st.header("Coach GPT")

    # Verificar si el usuario ha iniciado sesión
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        mostrar_login()
    else:
        # Inicializar variables de sesión si no existen
        if 'messages' not in st.session_state:
            # Añadimos el prompt de sistema al inicio del historial
            st.session_state['messages'] = [{"role": "system", "content": system_prompt}]
        
        # Mostrar el historial del chat
        for i, msg in enumerate(st.session_state['messages'][1:]):  # Omitimos el prompt de sistema al mostrar
            if msg['role'] == 'user':
                message(msg['content'], is_user=True, key=f"user_{i}")
            elif msg['role'] == 'assistant':
                message(msg['content'], is_user=False, key=f"bot_{i}")

        # Entrada del usuario con formulario
        with st.form(key='chat_form'):
            usuario_input = st.text_input("Escribe tu mensaje:", key="input")
            submit_button = st.form_submit_button(label='Enviar')
            if submit_button:
                if usuario_input:
                    # Agregar el mensaje del usuario al historial
                    st.session_state['messages'].append({"role": "user", "content": usuario_input})
                    # Obtener respuesta del modelo utilizando todo el historial
                    respuesta = obtener_respuesta(st.session_state['messages'])
                    # Agregar la respuesta del asistente al historial
                    st.session_state['messages'].append({"role": "assistant", "content": respuesta})
                    st.rerun()  # Forzar recarga para actualizar el chat
                else:
                    st.warning("Por favor, escribe un mensaje.")

        # Botón para cerrar sesión
        if st.button("Cerrar sesión"):
            st.session_state['logged_in'] = False
            st.session_state['messages'] = []  # Opcional: limpiar el historial de mensajes
            st.success("Has cerrado sesión.")
            st.rerun()  # Forzar recarga del script

elif choice == "Análisis":
    st.header("Análisis de Entrenamiento Deportivo")
    # Datos de ejemplo para el análisis
    time = pd.date_range(start='2023-01-01 10:00', periods=60, freq='T')  # 60 minutos
    heart_rate = np.random.normal(150, 10, size=(60,))
    calories = np.cumsum(np.random.normal(10, 2, size=(60,)))
    training_zone = np.random.choice(['Zona 1', 'Zona 2', 'Zona 3', 'Zona 4', 'Zona 5'], size=(60,))

    df_analysis = pd.DataFrame({
        'Tiempo': time,
        'Frecuencia Cardíaca': heart_rate,
        'Calorías Acumuladas': calories,
        'Zona de Entrenamiento': training_zone
    })

    # Gráfico de frecuencia cardíaca
    fig_hr = px.line(df_analysis, x='Tiempo', y='Frecuencia Cardíaca',
                     title='Frecuencia Cardíaca Durante el Entrenamiento')
    st.plotly_chart(fig_hr)

    # Gráfico de calorías quemadas
    fig_calories = px.line(df_analysis, x='Tiempo', y='Calorías Acumuladas',
                           title='Calorías Quemadas Durante el Entrenamiento')
    st.plotly_chart(fig_calories)

    # Gráfico de zonas de entrenamiento (Gráfico de pastel)
    st.subheader("Distribución de Zonas de Entrenamiento")
    zone_counts = df_analysis['Zona de Entrenamiento'].value_counts().reset_index()
    zone_counts.columns = ['Zona de Entrenamiento', 'Tiempo en Minutos']
    fig_zone_pie = px.pie(zone_counts, names='Zona de Entrenamiento', values='Tiempo en Minutos',
                          title='Tiempo Total en Cada Zona de Entrenamiento')
    st.plotly_chart(fig_zone_pie)

# Footer con estilo actualizado
st.markdown("""
    <div class="footer">
        © 2024 Tu Nombre. Todos los derechos reservados.
    </div>
    """, unsafe_allow_html=True)
