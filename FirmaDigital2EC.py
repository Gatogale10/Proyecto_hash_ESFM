import streamlit as st
from hashlib import sha256
from ecdsa import SigningKey, SECP256k1
import binascii

st.set_page_config(page_title="ECDSA Digital Signature App", layout="centered")
st.title("🔐 ECDSA Digital Signature System")

st.markdown("""
This application demonstrates how digital signatures work using Elliptic Curve Cryptography (ECC).
It consists of three main modules:
1. **Key Generation** - Create a private and public key pair.
2. **Signing Module** - Sign a message with your private key.
3. **Verification Module** - Verify the signature using the public key.
""")

# Key Generation Section
st.sidebar.header("1. Key Generation")
if st.sidebar.button("Generate Key Pair"):
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()

    st.session_state['private_key'] = sk.to_string().hex()
    st.session_state['public_key'] = vk.to_string().hex()

if 'private_key' in st.session_state:
    st.subheader("Key Generation:")
    st.markdown("The private key `d` is a randomly generated number. The public key `Q = dG` is derived using elliptic curve multiplication.")
    st.code(f"Private Key (d): {st.session_state['private_key']}")
    st.code(f"Public Key (Q = dG): {st.session_state['public_key']}")

# Signing Module
st.sidebar.header("2. Signing")
message = st.sidebar.text_area("Enter message to sign", "Hello world")
if st.sidebar.button("Sign Message") and 'private_key' in st.session_state:
    sk = SigningKey.from_string(bytes.fromhex(st.session_state['private_key']), curve=SECP256k1)
    digest = sha256(message.encode()).digest()
    signature = sk.sign(digest)

    r = int.from_bytes(signature[:len(signature)//2], byteorder='big')
    s = int.from_bytes(signature[len(signature)//2:], byteorder='big')

    st.session_state['message_hash'] = sha256(message.encode()).hexdigest()
    st.session_state['r'] = r
    st.session_state['s'] = s
    st.session_state['signature'] = signature.hex()

if 'r' in st.session_state:
    st.subheader("Signing Module")
    st.markdown("The message is hashed with SHA-256. Using the private key and the hash, a digital signature is created consisting of values `r` and `s`.")
    st.code(f"Message Hash: {st.session_state['message_hash']}")
    st.code(f"Signature component r: {st.session_state['r']}")
    st.code(f"Signature component s: {st.session_state['s']}")

# Verification Module
st.sidebar.header("3. Verification")
if st.sidebar.button("Verify Signature") and 'public_key' in st.session_state and 'signature' in st.session_state:
    vk = SigningKey.from_string(bytes.fromhex(st.session_state['private_key']), curve=SECP256k1).verifying_key
    digest = sha256(message.encode()).digest()
    try:
        valid = vk.verify(bytes.fromhex(st.session_state['signature']), digest)
        st.session_state['verification'] = "✅ Signature is VALID" if valid else "❌ Signature is INVALID"
    except:
        st.session_state['verification'] = "❌ Signature is INVALID (verification error)"

if 'verification' in st.session_state:
    st.subheader("Verification Module")
    st.markdown("The system checks if the signature matches the message hash and public key.")
    st.success(st.session_state['verification']) if "✅" in st.session_state['verification'] else st.error(st.session_state['verification'])
