# app_elliptic_fp.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from math import gcd
from PIL import Image
import os
import random
import pandas as pd

st.set_page_config(page_title="Curvas Elípticas sobre F_p", layout="wide")

# ---------------------------
# 🔹 Estilos CSS personalizados
# ---------------------------
custom_css = """
<style>
/* Fondo general */
main {
    background-color: #f4f7fa;
}

/* Títulos */
h1, h2, h3 {
    color: #2c3e50;
    font-family: 'Trebuchet MS', sans-serif;
}

/* Subtítulos y cajas */
section[data-testid="stSidebar"] {
    background-color: #eef3f7;
}
div.stButton button {
    background-color: #2e86de;
    color: white;
    border-radius: 10px;
    height: 45px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 12px;
    padding: 8px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------
# Helpers: primalidad (Miller-Rabin)
# ---------------------------
def is_probable_prime(n, k=7):
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n-1)
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            continue
        composite = True
        for _ in range(s-1):
            x = (x*x) % n
            if x == n-1:
                composite = False
                break
        if composite:
            return False
    return True

# ---------------------------
# Tonelli-Shanks para sqrt modular en primos
# ---------------------------
def tonelli_shanks(n, p):
    n %= p
    if n == 0:
        return 0
    if p == 2:
        return n
    if pow(n, (p-1)//2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p+1)//4, p)
    s = 0
    q = p-1
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p-1)//2, p) != p-1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q+1)//2, p)
    while True:
        if t == 0:
            return 0
        if t == 1:
            return r
        i = 1
        t2i = (t * t) % p
        while i < m:
            if t2i == 1:
                break
            t2i = (t2i * t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p

# ---------------------------
# Cálculos de curva en F_p
# ---------------------------
def discriminant_mod_p(a, b, p):
    return (-16 * (4 * pow(a, 3, p) + 27 * pow(b, 2, p))) % p

def points_on_curve_fp(a, b, p):
    pts = []
    for x in range(p):
        rhs = (pow(x, 3, p) + (a % p) * x + (b % p)) % p
        y0 = tonelli_shanks(rhs, p)
        if y0 is None:
            continue
        y1, y2 = y0 % p, (-y0) % p
        pts.append((x, y1))
        if y2 != y1:
            pts.append((x, y2))
    return sorted(pts)

# ---------------------------
# Mapeo a toro para 3D (visual)
# ---------------------------
def map_to_torus_modular(xs, ys, p, R=2.2, r=0.7):
    if len(xs) == 0:
        return np.array([]), np.array([]), np.array([])
    xs, ys = np.array(xs), np.array(ys)
    u = 2*np.pi * xs / p
    v = 2*np.pi * ys / p
    X = (R + r * np.cos(v)) * np.cos(u)
    Y = (R + r * np.cos(v)) * np.sin(u)
    Z = r * np.sin(v)
    return X, Y, Z

# ---------------------------
# Interfaz Streamlit
# ---------------------------
st.title("🎯 Curvas Elípticas sobre el campo finito F_p")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Parámetros (F_p)")
    a = st.number_input("Coeficiente a", value=-1, step=1)
    b = st.number_input("Coeficiente b", value=1, step=1)
    p = st.number_input("Primo p", value=43, step=1, min_value=3)
    show_list = st.checkbox("Mostrar tabla de puntos", value=True)
    compute_group_info = st.checkbox("Mostrar información del grupo", value=True)

    img_path = "/mnt/data/6e632cd2-bba9-4239-93a3-532578144221.png"
    if os.path.exists(img_path):
        st.image(Image.open(img_path), caption="Referencia", width=280)

with col2:
    st.subheader("📊 Resultados y gráficas")
    if not is_probable_prime(int(p)):
        st.error(f"p = {p} no parece primo. Introduce un primo válido.")
    else:
        p = int(p)
        disc = discriminant_mod_p(a, b, p)
        if disc % p == 0:
            st.error("La curva es singular (Δ ≡ 0). Cambia a o b.")
        else:
            st.success(f"✅ p={p} es primo y la curva es no singular (Δ mod p = {disc}).")
            pts = points_on_curve_fp(a, b, p)
            n_points = len(pts) + 1
            st.metric("Número de puntos", n_points)

            if show_list:
                df = pd.DataFrame(pts, columns=["x","y"])
                st.dataframe(df, height=250)

            # 🔹 Gráfico 2D
            xs, ys = [x for x,y in pts], [y for x,y in pts]
            fig2 = go.Figure()
            if xs:
                fig2.add_trace(go.Scatter(x=xs, y=ys, mode='markers',
                                          marker=dict(size=7, color="#e74c3c"),
                                          name=f'Puntos en F_{p}'))
            fig2.update_layout(
                title=f"Curva en F_{p}: y² = x³ + {a}x + {b}",
                xaxis=dict(title="x (mod p)"),
                yaxis=dict(title="y (mod p)"),
                height=400,
                plot_bgcolor="#f9f9f9"
            )
            st.plotly_chart(fig2, use_container_width=True)

            # 🔹 Gráfico 3D
            X3, Y3, Z3 = map_to_torus_modular(xs, ys, p)
            u = np.linspace(0, 2*np.pi, 60)
            v = np.linspace(0, 2*np.pi, 30)
            U, V = np.meshgrid(u, v)
            RT, rt = 2.2, 0.7
            XT = (RT + rt*np.cos(V)) * np.cos(U)
            YT = (RT + rt*np.cos(V)) * np.sin(U)
            ZT = rt*np.sin(V)

            fig3 = go.Figure()
            fig3.add_trace(go.Surface(x=XT, y=YT, z=ZT, opacity=0.18, showscale=False))
            if len(X3) > 0:
                fig3.add_trace(go.Scatter3d(x=X3, y=Y3, z=Z3, mode='markers',
                                            marker=dict(size=4, color='#2980b9')))
            fig3.update_layout(height=600, title="Puntos en el toro (visualización)")
            st.plotly_chart(fig3, use_container_width=True)

            if compute_group_info:
                st.markdown("#### 📌 Información rápida")
                st.write(f"Total de puntos (incluye infinito): **{n_points}**")
                bound_low = p + 1 - 2 * int(np.sqrt(p))
                bound_high = p + 1 + 2 * int(np.sqrt(p))
                st.write(f"Cota de Hasse: {bound_low} ≤ |E(F_p)| ≤ {bound_high}")

st.caption("🔎 Usa Tonelli–Shanks para raíces cuadradas mod p. Solo representación y visualización.")
