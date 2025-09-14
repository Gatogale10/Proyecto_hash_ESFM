import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import hashlib
import io
import zipfile
import boto3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Configurar boto3 para usar S3
s3_client = boto3.client(
    's3',
    aws_access_key_id='PRIVADO',
    aws_secret_access_key="PRIVADO",
    region_name='us-west-2'
)

# Datos del bucket de S3
BUCKET_NAME = 'firmadigitalalejandro'


# Nombre del archivo CSV en S3
USERS_CSV_S3_KEY = 'credentials/users.csv'

# Función para encriptar contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Cargar usuarios desde S3
def load_users():
    try:
        obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=USERS_CSV_S3_KEY)
        return pd.read_csv(io.BytesIO(obj['Body'].read()))
    except s3_client.exceptions.NoSuchKey:
        # Si el archivo no existe, crear un DataFrame vacío
        df = pd.DataFrame(columns=['username', 'password_hash', 'private_key_path', 'public_key_path'])
        save_users(df)
        return df

# Guardar usuarios en S3
def save_users(users):
    csv_buffer = io.StringIO()
    users.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=BUCKET_NAME, Key=USERS_CSV_S3_KEY, Body=csv_buffer.getvalue())

# Verificar credenciales
def verify_user(username, password):
    users = load_users()
    hashed_password = hash_password(password)
    user_row = users[(users['username'] == username) & (users['password_hash'] == hashed_password)]
    if not user_row.empty:
        return user_row.iloc[0]['private_key_path'], user_row.iloc[0]['public_key_path']
    return None, None

# Crear una nueva cuenta de usuario
def create_user(username, password):
    users = load_users()
    if username in users['username'].values:
        st.error("El usuario ya existe. Elige un nombre de usuario diferente.")
        return False, None, None, None, None
    private_key_path, public_key_path, private_key, public_key = generate_keys(username)
    new_user = pd.DataFrame([[username, hash_password(password), private_key_path, public_key_path]], 
                            columns=['username', 'password_hash', 'private_key_path', 'public_key_path'])
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return True, private_key_path, public_key_path, private_key, public_key

# Generar claves RSA y guardar en S3
def generate_keys(username):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    private_key_path = f"keys/private_key_{username}.pem"
    public_key_path = f"keys/public_key_{username}.pem"

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    s3_client.put_object(Bucket=BUCKET_NAME, Key=private_key_path, Body=private_key_pem)
    s3_client.put_object(Bucket=BUCKET_NAME, Key=public_key_path, Body=public_key_pem)

    st.write(f"Private key saved to: s3://{BUCKET_NAME}/{private_key_path}")
    st.write(f"Public key saved to: s3://{BUCKET_NAME}/{public_key_path}")

    return private_key_path, public_key_path, private_key, public_key

# Firmar un archivo
def sign_file(file_data, private_key):
    signature = private_key.sign(
        file_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# Verificar la firma de un archivo
def verify_file(file_path, signature_data, public_key_path):
    public_key_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=public_key_path)
    public_key = serialization.load_pem_public_key(public_key_obj['Body'].read())

    with open(file_path, "rb") as f:
        file_data = f.read()

    try:
        public_key.verify(
            signature_data,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        st.success(f"Firma del archivo '{file_path}' verificada exitosamente.")
    except Exception as e:
        st.error(f"La verificación de la firma del archivo '{file_path}' falló: {e}")

# Función principal
def main():

    ### DESIGN ###

    # CSS personalizado para cambiar el color de los objetos clicables
    custom_css = """
    <style>
    /* Cambiar el color de los botones */
    .stButton>button {
        background-color: #012154;
        color: #012154;
    }

    /* Cambiar el color de los enlaces */
    a {
        color: #012154;
    }

    /* Cambiar el color de los select boxes */
    .stSelectbox div[data-baseweb="select"] {
        background-color: white;
        color: #012154;
    }

    /* Cambiar el color de los radio buttons */
    .stRadio div[role="radiogroup"] {
        color: #012154;
    }
    </style>
    """

    # Insertar el CSS en la aplicación usando st.markdown
    st.markdown(custom_css, unsafe_allow_html=True)
    
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bitter:ital,wght@0,100..900;1,100..900&family=PT+Serif:ital,wght@0,400;0,700;1,400;1,700&display=swap');
        .main {
            background-color: #ffffff;
        }
    
        h1{
            color: #012154;
            text-align: center;
            font-family: "Bitter", serif;
        }
        body {
            color: #012154;
            text-align: center;
            font-family: 'Bitter', sans-serif;
        }
        .stButton>button {
            background-color: #ffffff;
            color: #012154
            font-family: "Bitter", serif;
        }
        .image-container {
        text-align: right; /* Alinea la imagen a la izquierda */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .logo-container {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            padding: 10px;
        }
        .logo-container img {
            width: 200px;
        }
        </style>
        <div class="logo-container">
            <img src="logo_ipn.png" alt="logo">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("Firma Digital")
    st.write("Uso de álgebras modernas para criptografía y seguridad")

    ### FUNCTIONALITY ###

    # Verificar si el usuario está autenticado
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Mostrar formulario de inicio de sesión si el usuario no está autenticado
    if not st.session_state.authenticated:

        menu = ["Inicio de Sesión", "Crear Cuenta"]
        tab1, tab2 = st.tabs(menu)

        with tab1:
            st.subheader("Inicio de Sesión")
            username = st.text_input("Nombre de Usuario", key="login_username")
            password = st.text_input("Contraseña", type='password', key="login_password")
            if st.button("Iniciar Sesión", key="login_button"):
                private_key_path, public_key_path = verify_user(username, password)
                if private_key_path and public_key_path:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.private_key_path = private_key_path
                    st.session_state.public_key_path = public_key_path
                    st.success("Inicio de sesión exitoso")
                    #st.experimental_rerun()
                else:
                    st.error("Nombre de usuario o contraseña incorrectos")
        with tab2:
            st.subheader("Crear Cuenta")
            st.write("No olvides/pierdas tu contraseña. Todavía no hay forma de recuperarla.")
            username = st.text_input("Elige un Nombre de Usuario", key="create_username")
            password = st.text_input("Elige una Contraseña", type='password', key="create_password")
            if st.button("Crear Cuenta", key="create_button"):
                success, private_key_path, public_key_path, private_key, public_key = create_user(username, password)
                if success:
                    st.success("Cuenta creada exitosamente. Ahora puedes iniciar sesión.")
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.private_key_path = private_key_path
                    st.session_state.public_key_path = public_key_path
                    #st.experimental_rerun()

                    # Claves en formato PEM para la descarga
                    private_key_pem = private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption()
                    )

                    # Crear un archivo ZIP en memoria
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                        zip_file.writestr(f"private_key_{username}.pem", private_key_pem)
                    zip_buffer.seek(0)

                    # Botón de descarga para el archivo ZIP
                    st.download_button(
                        label="Descargar Clave Privada",
                        data=zip_buffer,
                        file_name=f"private_key_{username}.zip",
                        mime="application/zip",
                        key="download_private_key"
                    )

    else:
        # Mostrar las opciones de firma digital si el usuario está autenticado
        menu = ["Firmar Archivo", "Verificar Firma", "Cerrar Sesión", "Ver Usuarios"]
        tab1, tab2, tab3, tab4 = st.tabs(menu)

        with tab1:
            st.subheader("Firmar Archivo")
            st.write("Una vez firmado el archivo, no olvides descargar el ARCHIVO DE FIRMA .sig")
            file = st.file_uploader("Selecciona un archivo", key="sign_file_uploader")
            if st.button("Firmar Archivo", key="sign_button") and file:
                file_data = file.read()
                private_key_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=st.session_state.private_key_path)
                private_key = serialization.load_pem_private_key(
                    private_key_obj['Body'].read(),
                    password=None,
                )
                signature = sign_file(file_data, private_key)
                st.success("Archivo firmado exitosamente.")
                
                # Botón de descarga para el archivo .sig
                st.download_button(
                    label="Descargar archivo de firma",
                    data=signature,
                    file_name=f"{file.name}.sig",
                    mime="application/octet-stream",
                    key="download_signature"
                )

        with tab2:
            st.subheader("Verificar Firma de Archivo")
            file = st.file_uploader("Selecciona un archivo", key="verify_file_uploader")
            signature_file = st.file_uploader("Selecciona el archivo de firma", type=['sig'], key="verify_signature_file_uploader")
            users = load_users()
            username = st.selectbox("Selecciona el usuario que firmó el archivo", users['username'].tolist(), key="verify_username")
            if st.button("Verificar Firma", key="verify_button") and file and signature_file and username:
                file_path = f"/tmp/{file.name}"
                signature_data = signature_file.read()
                with open(file_path, "wb") as f:
                    f.write(file.read())
                public_key_path = users[users['username'] == username]['public_key_path'].values[0]
                verify_file(file_path, signature_data, public_key_path)

        with tab3:
            if st.button("Cerrar Sesión", key="logout_button"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.private_key_path = None
                st.session_state.public_key_path = None
                st.success("Has cerrado sesión exitosamente")
                #st.experimental_rerun()

        with tab4:
            st.subheader("Lista de Usuarios Registrados")
            users = load_users()
            st.dataframe(users.drop(columns=['password_hash']))
            # Botón para descargar el archivo CSV de usuarios
            #st.download_button(
            #    label="Descargar CSV de Usuarios",
            #    data=users.to_csv(index=False),
            #    file_name='users.csv',
            #    mime='text/csv',
            #    key="download_users_csv"
            #)

    # Texto de pie de página

    st.write("Profesor Eliseo Sarmiento")

if __name__ == '__main__':
    main()
