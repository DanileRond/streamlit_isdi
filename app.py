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
openai.api_version = "2023-12-01-preview"
openai.api_key = api_key

# Aplicar estilos CSS personalizados
def local_css():
    st.markdown("""
        <style>
            /* Importar fuente desde Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

            /* Aplicar fuente a toda la aplicación */
            html, body, [class*="css"]  {
                font-family: 'Roboto', sans-serif;
                background-color: #f5f5f5;
            }

            /* Estilos del título principal */
            .main-title {
                text-align: center;
                padding: 20px 0;
                background-color: #ffffff;
                margin-bottom: 20px;
                border-bottom: 1px solid #e0e0e0;
            }
            .main-title h1 {
                color: #333333;
                font-weight: 700;
            }

            /* Estilos del menú de navegación */
            .css-1n543e5 {
                background-color: #ffffff !important;
                padding: 0;
                margin-bottom: 20px;
            }
            .nav-link {
                font-size: 16px !important;
                color: #333333 !important;
                padding: 10px 20px !important;
                margin: 0 5px !important;
                border-radius: 5px;
            }
            .nav-link:hover {
                background-color: #e0e0e0 !important;
                color: #333333 !important;
            }
            .nav-link-selected {
                background-color: #1abc9c !important;
                color: #ffffff !important;
            }

            /* Estilos de los encabezados de sección */
            .stMarkdown h2 {
                color: #333333;
                font-weight: 500;
                margin-top: 0;
            }

            /* Estilos del contenido */
            .stContainer {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            /* Estilos de imágenes */
            img {
                border-radius: 8px;
            }

            /* Estilos del chat */
            .streamlit-chat-message {
                background-color: #f9f9f9;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
            .streamlit-chat-message-user {
                background-color: #1abc9c;
                color: #ffffff;
            }

            /* Estilos de botones */
            .stButton > button {
                background-color: #1abc9c;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 16px;
            }
            .stButton > button:hover {
                background-color: #17a085;
                color: #ffffff;
            }

            /* Estilos del footer */
            .footer {
                text-align: center;
                padding: 10px 0;
                color: #999999;
                font-size: 14px;
                margin-top: 40px;
            }
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
            engine=model,  # Usamos 'engine' en lugar de 'model' para Azure OpenAI
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
            st.experimental_rerun()
        else:
            st.error("Nombre de usuario o contraseña incorrectos.")

# Secciones de la aplicación
if choice == "Leisure":
    st.header("Actividades de Ocio")
    
    # Usar columnas para una mejor disposición
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("estrella-damm.jpg", use_column_width=True)
    with col2:
        st.markdown("""
            - **Deportes al aire libre**
            - **Gimnasio y fitness**
            - **Eventos deportivos**
            - **Festivales / Música**
            - **Cultura**
            - **Barcelona**
        """)

elif choice == "ReFill":
    st.header("Consulta los litros que quedan o faltan en tu suscripción")
    
    # Usar columnas para una mejor disposición
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            ### Te quedan **10 litros** este mes
            ¿Necesitas más? Renueva tu suscripción para disfrutar de más beneficios.
        """)
        
        # Generar datos de muestra para el consumo
        fechas = pd.date_range(start='2023-01-01', periods=10, freq='D')
        consumo_isotonica = np.random.randint(1, 5, size=10)  # Litros consumidos por día
        consumo_proteica = np.random.randint(0, 3, size=10)
        
        df_consumo = pd.DataFrame({
            'Fecha': fechas,
            'Agua Isotónica': consumo_isotonica,
            'Agua Proteica': consumo_proteica
        })
        
        # Gráfico de barras apiladas para mostrar el consumo
        df_consumo_melted = df_consumo.melt(id_vars='Fecha', value_vars=['Agua Isotónica', 'Agua Proteica'], var_name='Producto', value_name='Litros')
        fig_consumo = px.bar(df_consumo_melted, x='Fecha', y='Litros', color='Producto', title='Consumo de Productos por Día')
        st.plotly_chart(fig_consumo, use_container_width=True)
        
        # Gráfico circular para mostrar la distribución total del consumo
        total_consumo = df_consumo[['Agua Isotónica', 'Agua Proteica']].sum().reset_index()
        total_consumo.columns = ['Producto', 'Litros']
        fig_pie = px.pie(total_consumo, values='Litros', names='Producto', title='Distribución Total del Consumo')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.image("fake_qr.jpg", use_column_width=True)

elif choice == "Chatbot":
    st.header("Coach GPT")
    
    # Verificar si el usuario ha iniciado sesión
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        mostrar_login()
    else:
        # Inicializar variables de sesión si no existen
        if 'messages' not in st.session_state:
            # Añadimos el prompt de sistema al inicio del historial
            st.session_state['messages'] = [{"role": "system", "content": system_prompt}]
        if 'historial' not in st.session_state:
            st.session_state['historial'] = []

        # Mostrar el historial del chat
        for i, msg in enumerate(st.session_state['messages'][1:]):  # Omitimos el prompt de sistema al mostrar
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
                # Obtener respuesta del modelo utilizando todo el historial
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
    st.header("Análisis de Entrenamiento Deportivo")
    
    # Generar datos de muestra
    fechas = pd.date_range(start='2023-01-01', periods=10, freq='D')
    calorias = np.random.randint(400, 800, size=10)
    max_hr = np.random.randint(150, 190, size=10)
    zonas_entrenamiento = np.random.randint(1, 5, size=10)
    
    df = pd.DataFrame({
        'Fecha': fechas,
        'Calorías': calorias,
        'Frecuencia Cardíaca Máxima': max_hr,
        'Zona de Entrenamiento': zonas_entrenamiento
    })
    
    # Gráfico de barras de calorías
    fig_calorias = px.bar(df, x='Fecha', y='Calorías', title='Calorías Quemadas por Día')
    st.plotly_chart(fig_calorias, use_container_width=True)
    
    # Gráfico de líneas de frecuencia cardíaca máxima
    fig_hr = px.line(df, x='Fecha', y='Frecuencia Cardíaca Máxima', markers=True, title='Frecuencia Cardíaca Máxima por Día')
    st.plotly_chart(fig_hr, use_container_width=True)
    
    # Gráfico de pastel de zonas de entrenamiento
    df_zonas = df.groupby('Zona de Entrenamiento').size().reset_index(name='Conteo')
    fig_zonas = px.pie(df_zonas, values='Conteo', names='Zona de Entrenamiento', title='Distribución de Zonas de Entrenamiento')
    st.plotly_chart(fig_zonas, use_container_width=True)
    
    # Puedes agregar más gráficos si lo deseas

# Footer con estilo actualizado
st.markdown("""
    <div class="footer">
        © 2024 Tu Nombre. Todos los derechos reservados.
    </div>
    """, unsafe_allow_html=True)
