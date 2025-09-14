# Proyecto de Algoritmo Hash

# En siguiente proyecto se estara creando una pagina web donde se pueden firmar digitalmente un archivo
# dado por el usuario, al igual se intentara implementar un malware , que encripte los archivos de la computadora
# y pida un rescate de 0 pesos(para que no haya problema), una vez dado el rescate mandara la contraseña al correo de la persona.

# Importamos las librerias a utilizar
import streamlit as st
from streamlit.components.v1 import html
from PIL import Image
import pandas as pd
import hashlib
import io
import zipfile
import boto3
import os
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import smtplib
from email.mime.text import MIMEText

# Configuración de la página
st.set_page_config(page_title="Firma Digital y Simulador de Ransomware", layout="wide")


# Generar claves RSA
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Serializar las claves
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


# Función para firmar un archivo
def sign_file(private_key_pem, file_data):
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    signature = private_key.sign(
        file_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


# Función para verificar firma
def verify_signature(public_key_pem, file_data, signature):
    public_key = serialization.load_pem_public_key(public_key_pem)
    try:
        public_key.verify(
            signature,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False


# Función para calcular hash
def calculate_hash(file_data):
    sha256_hash = hashlib.sha256(file_data).hexdigest()
    return sha256_hash


# Simulador de ransomware (solo para demostración, no ejecuta acciones reales)
def simulate_ransomware():
    st.warning("⚠️ SIMULACIÓN DE RANSOMWARE (NO REAL) ⚠️")

    # Generar clave de encriptación
    key = Fernet.generate_key()
    cipher = Fernet(key)

    # Simular encriptación de archivos
    with st.expander("📁 Simulando encriptación de archivos..."):
        uploaded_file2 = st.file_uploader("Sube un archivo ", type=None)

        if uploaded_file2 is not None:
            file_data2 = uploaded_file2.getvalue()

            # Mostrar información del archivo
            st.subheader("Información del archivo")
            col1 = st.columns(1)

            with col1:
                st.write(f"Nombre: {uploaded_file2.name}")
                st.write(f"Tamaño: {len(file_data2)} bytes")

        if st.button("Encriptar archivo"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
                status_text.text(f"Encriptando archivos... {i + 1}% completado")

            status_text.text("✅ Todos los archivos han sido encriptados simuladamente")

            # Mostrar mensaje de rescate
            st.error("¡Todos tus archivos han sido encriptados! (Simulación)")
            st.write("Para recuperar tus archivos, debes pagar un rescate de 0 Bitcoins.")

            # Formulario para "pagar" rescate
            with st.form("ransom_form"):
                email = st.text_input("Ingresa tu correo electrónico para recibir la clave de desencriptación")
                submit_button = st.form_submit_button("Pagar rescate de 0 pesos")

                if submit_button:
                    if email:
                        # Simular envío de correo (no se envía realmente)
                        st.success(f"¡Pago simulado exitoso! Se enviará la clave a {email} (simulación)")
                        st.code(f"Clave de desencriptación (simulada): {key.decode()}")
                    else:
                        st.warning("Por favor ingresa un correo electrónico válido")




# Interfaz de usuario con Streamlit
def main():
    ### Diseño ###

    # Cargar imagen

    try:
        logo = Image.open('logo_ipn.png')
        st.image(logo, width=120)
    except FileNotFoundError:
        # st.error("No se encontró el archivo logo_ipn.png")

        st.markdown("""<div style="width:80px; height:80px; background-color:#900C3F;"></div>""",
                    unsafe_allow_html=True)

    # Color guinda del IPN (aproximado)
    IPN_GUINDA = "#900C3F"
    COLOR_FONDO = "#f43e17"
    COLOR_FONDO2 = "#ff2d00"

    # Fondo
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {COLOR_FONDO2}20;  /* 20 es para 20% de opacidad */
                background-image: none;

            }}

            /* Opcional: estilo para los contenedores principales */
            .stContainer, .stTextInput, .stButton>button {{
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Título principal con el logo del IPN
    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <h1 style="color: {IPN_GUINDA}; margin-left: 20px;">Generador de Firma Digital</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.title("Firma Digital")
    st.write("Uso de álgebras modernas para criptografía y seguridad")


    #Funcionalidad
    st.title("Proyecto de Firma Digital y Simulación de Ransomware")

    tab1, tab2 = st.tabs(["Firma Digital", "Simulación Ransomware"])

    with tab1:
        st.header("🔏 Firma Digital de Documentos")

        # Generar o cargar claves
        if 'private_key' not in st.session_state or 'public_key' not in st.session_state:
            private_key, public_key = generate_keys()
            st.session_state.private_key = private_key
            st.session_state.public_key = public_key
        else:
            private_key = st.session_state.private_key
            public_key = st.session_state.public_key

        # Subir archivo para firmar
        uploaded_file = st.file_uploader("Sube un archivo para firmar", type=None)

        if uploaded_file is not None:
            file_data = uploaded_file.getvalue()

            # Mostrar información del archivo
            st.subheader("Información del archivo")
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"Nombre: {uploaded_file.name}")
                st.write(f"Tamaño: {len(file_data)} bytes")

            with col2:
                file_hash = calculate_hash(file_data)
                st.write(f"SHA-256 Hash:")
                st.code(file_hash)

            # Firmar archivo
            if st.button("Firmar archivo"):
                signature = sign_file(private_key, file_data)
                st.session_state.signature = signature
                st.success("Archivo firmado correctamente!")
                st.write("Firma digital:")
                st.code(signature.hex())

                # Crear archivo zip con el original y la firma
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                    zip_file.writestr(uploaded_file.name, file_data)
                    zip_file.writestr(uploaded_file.name + ".sig", signature)

                # Descargar archivo firmado
                st.download_button(
                    label="Descargar archivo firmado",
                    data=zip_buffer.getvalue(),
                    file_name=uploaded_file.name + ".signed.zip",
                    mime="application/zip"
                )

        # Verificar firma
        st.subheader("Verificar firma")
        verify_file = st.file_uploader("Sube el archivo original para verificar", key="verify_file")
        verify_sig = st.file_uploader("Sube el archivo de firma (.sig)", key="verify_sig")

        if verify_file and verify_sig:
            file_data = verify_file.getvalue()
            signature = verify_sig.read()

            if st.button("Verificar firma"):
                is_valid = verify_signature(public_key, file_data, signature)
                if is_valid:
                    st.success("✅ La firma es válida!")
                else:
                    st.error("❌ La firma no es válida!")

    with tab2:
        st.header("💀 Simulador de Ransomware (Solo demostración)")
        st.warning("""
        Esta es una simulación inofensiva para propósitos educativos. 
        No se encriptarán archivos reales ni se causará daño alguno.
        """)

        if st.button("Iniciar simulación (no hará daño)"):
            simulate_ransomware()


if __name__ == "__main__":
    main()
