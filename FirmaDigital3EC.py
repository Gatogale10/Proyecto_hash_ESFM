# Improved version of the ECDSA Digital Signature App with better UI
import streamlit as st
from hashlib import sha256
from ecdsa import SigningKey, SECP256k1

st.set_page_config(page_title="ECDSA Digital Signature App", layout="centered")

st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
        }
        .stButton>button {
            color: white;
            background: #0066cc;
            border-radius: 0.5rem;
        }
        .stTextArea textarea {
            background-color: #ffffff;
            border-radius: 0.5rem;
        }
        .stCodeBlock {
            background-color: #eeeeee;
            border-radius: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("ECDSA Digital Signature System")

st.markdown("""
This application demonstrates how digital signatures work using Elliptic Curve Cryptography (ECC).
It consists of three main modules:
1. **Key Generation** - Create a private and public key pair.
2. **Signing** - Sign a message with your private key.
3. **Verification** - Verify the signature using the public key.
""")

# Sidebar Controls
st.header("📌 Controls")
col1, col2 = st.columns(2)
with col1:
    gen_key = st.button("🔑 Generate Keys")
with col2:
    sign_msg = st.button("✍️ Sign Message")

message = st.text_area("Enter a message", "Hello world")
verify = st.button("✅ Verify Signature")

# Generate Keys
if gen_key:
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()
    st.session_state['private_key'] = sk.to_string().hex()
    st.session_state['public_key'] = vk.to_string().hex()

# Display Keys
if 'private_key' in st.session_state:
    st.subheader("Key Generation")
    st.markdown("- A private key `d` is generated randomly.")
    st.markdown("- The public key `Q = dG` is derived from the private key.")
    st.code(f"Private Key (hex): {st.session_state['private_key']}")
    st.code(f"Public Key (hex): {st.session_state['public_key']}")

# Sign the message
if sign_msg and 'private_key' in st.session_state:
    sk = SigningKey.from_string(bytes.fromhex(st.session_state['private_key']), curve=SECP256k1)
    digest = sha256(message.encode()).digest()
    signature = sk.sign(digest)
    r = int.from_bytes(signature[:len(signature) // 2], byteorder='big')
    s = int.from_bytes(signature[len(signature) // 2:], byteorder='big')

    st.session_state['message_hash'] = sha256(message.encode()).hexdigest()
    st.session_state['r'] = r
    st.session_state['s'] = s
    st.session_state['signature'] = signature.hex()

# Show Signing Info
if 'r' in st.session_state:
    st.subheader(" Message Signing")
    st.markdown("""
    - The message is hashed using SHA-256.
    - The signature (r, s) is generated from the private key and message hash.
    """)
    st.code(f"SHA-256 Hash: {st.session_state['message_hash']}")
    st.code(f"Signature r: {st.session_state['r']}")
    st.code(f"Signature s: {st.session_state['s']}")

# Signature Verification
if verify and 'public_key' in st.session_state and 'signature' in st.session_state:
    sk = SigningKey.from_string(bytes.fromhex(st.session_state['private_key']), curve=SECP256k1)
    vk = sk.get_verifying_key()
    digest = sha256(message.encode()).digest()
    try:
        valid = vk.verify(bytes.fromhex(st.session_state['signature']), digest)
        st.session_state['verification_result'] = "✅ Signature is VALID" if valid else "❌ Signature is INVALID"
    except Exception as e:
        st.session_state['verification_result'] = f"❌ Verification failed: {str(e)}"

# Show Verification Result
if 'verification_result' in st.session_state:
    st.subheader("Signature Verification")
    st.info("Hash is recalculated and signature is validated against public key.")
    if "✅" in st.session_state['verification_result']:
        st.success(st.session_state['verification_result'])
    else:
        st.error(st.session_state['verification_result'])

footer_html = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 80px;
    background-color: #800040;
    color: white;
    text-align:center;
    justify-content: 
    padding: 10px 0;
    font-size: 16px;
}

.texto-footer
{
display: flex
text-align: end;
}
</style>

<div class="footer">
<div class="texto-footer">
    © 2025 Digital Signature | Todos los derechos reservados | ESFM
</div>
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)