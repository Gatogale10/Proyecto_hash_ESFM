# Esta es la pagina inicial que se hara con streamlit

import streamlit as st
from PIL import Image
""""""
# Cargar imagen

try:
    logo = Image.open('no.png')
    st.image(logo, width=120)
except FileNotFoundError:
    #st.error("No se encontró el archivo logo_ipn.png")
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


st.subheader("Proyecto para la generación de firmas digitales seguras.")

# Descripción
st.write(
    """
    Esta aplicación te permite generar una firma digital única para tus documentos. 
    Utiliza técnicas de criptografía para garantizar la seguridad de tus archivos.
    """
)


st.markdown("---")
st.subheader("¿Cómo funciona?")
st.write(
    """
    1. **Carga tu documento:** Selecciona el archivo que deseas firmar digitalmente.
    2. **Genera tu firma:** El sistema procesará el documento y generará una firma digital única.
    3. **Descarga el documento firmado:** Obtén el documento con la firma digital integrada.
    """
)


st.markdown("---")
st.subheader("¡Empieza a firmar tus documentos de forma segura!")

# Información IPN
st.markdown(
    f"""
    <div style="background-color: {IPN_GUINDA}; color: white; padding: 10px; text-align: center; margin-top: 50px;">
        <p style="margin: 0;">Instituto Politécnico Nacional</p>
        <p style="margin: 0;">"La Técnica al Servicio de la Patria"</p>
    </div>
    """,
    unsafe_allow_html=True,
)