# app_elliptic_fp.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from math import gcd
from PIL import Image
import os
import random

st.set_page_config(page_title="Curvas Elípticas sobre F_p", layout="wide")

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
    # write n-1 as d*2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    # witnesses
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
    """Resuelve x^2 ≡ n (mod p). Devuelve None si no tiene solución,
       o una raíz r tal que r^2 % p == n%p.
       p debe ser primo."""
    n %= p
    if n == 0:
        return 0
    if p == 2:
        return n
    # Legendre
    if pow(n, (p-1)//2, p) != 1:
        return None
    # caso p % 4 == 3 (fácil)
    if p % 4 == 3:
        r = pow(n, (p+1)//4, p)
        return r
    # factor p-1 = q * 2^s con q odd
    s = 0
    q = p-1
    while q % 2 == 0:
        q //= 2
        s += 1
    # find z a non-cuadratico
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
        # find smallest i (0<i<m) tal que t^(2^i) = 1
        i = 1
        t2i = (t * t) % p
        while i < m:
            if t2i == 1:
                break
            t2i = (t2i * t2i) % p
            i += 1
        # update
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p

# ---------------------------
# Cálculos de curva en F_p
# ---------------------------
def discriminant_mod_p(a, b, p):
    # Δ = -16(4a^3 + 27 b^2)
    val = (-16 * (4 * pow(a, 3, p) + 27 * pow(b, 2, p))) % p
    return val

def points_on_curve_fp(a, b, p):
    pts = []
    for x in range(p):
        rhs = (pow(x, 3, p) + (a % p) * x + (b % p)) % p
        y0 = tonelli_shanks(rhs, p)
        if y0 is None:
            continue
        y1 = y0 % p
        y2 = (-y0) % p
        pts.append((x, y1))
        if y2 != y1:
            pts.append((x, y2))
    # ordenar para presentación
    pts = sorted(pts)
    return pts

# ---------------------------
# Mapeo a toro para 3D (visual)
# ---------------------------
def map_to_torus_modular(xs, ys, p, R=2.2, r=0.7):
    if len(xs) == 0:
        return np.array([]), np.array([]), np.array([])
    xs = np.array(xs)
    ys = np.array(ys)
    u = 2*np.pi * xs / p
    v = 2*np.pi * ys / p
    X = (R + r * np.cos(v)) * np.cos(u)
    Y = (R + r * np.cos(v)) * np.sin(u)
    Z = r * np.sin(v)
    return X, Y, Z

# ---------------------------
# Interfaz Streamlit
# ---------------------------
st.title("Curvas Elípticas sobre el campo finito F_p")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Parámetros (F_p)")
    a = st.number_input("a (entero)", value=-1, step=1)
    b = st.number_input("b (entero)", value=1, step=1)
    p = st.number_input("p (primo)", value=43, step=1, min_value=3)
    show_list = st.checkbox("Mostrar lista de puntos (tabular)", value=True)
    compute_group_info = st.checkbox("Mostrar número de puntos (orden de E(F_p))", value=True)

    # Cargar imagen de referencia si existe
    img_path = "/mnt/data/6e632cd2-bba9-93a3-532578144221.png"
    if os.path.exists(img_path):
        st.image(Image.open(img_path), caption="Referencia (ilustración)", width=300)

with col2:
    # Validaciones
    st.subheader("Resultados / Gráficas")
    if not is_probable_prime(int(p)):
        st.error(f"p = {p} no parece primo (prueba rápida). Introduce un primo.")
    else:
        p = int(p)
        disc = discriminant_mod_p(a, b, p)
        if disc % p == 0:
            st.error("La curva es singular modulo p (discriminante ≡ 0). Cambia a o b.")
        else:
            st.success(f"p={p} es probablemente primo y la curva es no singular (Δ mod p = {disc}).")

            pts = points_on_curve_fp(a, b, p)
            n_points = len(pts) + 1  # +1 por el punto en el infinito
            st.metric("Número de puntos |E(F_p)| (incluye infinito)", n_points)

            if show_list:
                # Mostrar tabla simple
                import pandas as pd
                df = pd.DataFrame(pts, columns=["x","y"])
                st.dataframe(df)

            # Plot 2D: scatter x vs y
            xs = [x for (x,y) in pts]
            ys = [y for (x,y) in pts]
            fig2 = go.Figure()
            if xs:
                fig2.add_trace(go.Scatter(x=xs, y=ys, mode='markers', marker=dict(size=6),
                                          name=f'Puntos en F_{p}'))
            fig2.update_layout(title=f"Puntos de la curva en F_{p}: y^2 = x^3 + {a}x + {b} (mod {p})",
                               xaxis=dict(title="x (mod p)"), yaxis=dict(title="y (mod p)"),
                               height=450)
            st.plotly_chart(fig2, use_container_width=True)

            # Plot 3D: torus mapping
            X3, Y3, Z3 = map_to_torus_modular(xs, ys, p, R=2.2, r=0.7)
            # torus surface for reference
            u = np.linspace(0, 2*np.pi, 60)
            v = np.linspace(0, 2*np.pi, 30)
            U, V = np.meshgrid(u, v)
            RT = 2.2; rt = 0.7
            XT = (RT + rt * np.cos(V)) * np.cos(U)
            YT = (RT + rt * np.cos(V)) * np.sin(U)
            ZT = rt * np.sin(V)

            fig3 = go.Figure()
            fig3.add_trace(go.Surface(x=XT, y=YT, z=ZT, opacity=0.22, showscale=False, name='Torus'))
            if len(X3) > 0:
                fig3.add_trace(go.Scatter3d(x=X3, y=Y3, z=Z3, mode='markers',
                                           marker=dict(size=4, color='red'), name='Puntos F_p'))
            fig3.update_layout(scene=dict(xaxis=dict(visible=False),
                                          yaxis=dict(visible=False),
                                          zaxis=dict(visible=False)),
                               height=650, title=f"Puntos en F_{p} mapeados al toro (visualización)")
            st.plotly_chart(fig3, use_container_width=True)

            # Opcional: detalles del grupo
            if compute_group_info:
                st.markdown("#### Información rápida del grupo E(F_p)")
                st.write(f"Total de puntos (incluye infinito): **{n_points}**")
                # Podemos dar la cota de Hasse
                bound_low = p + 1 - 2 * int(np.sqrt(p))
                bound_high = p + 1 + 2 * int(np.sqrt(p))
                st.write(f"Cota de Hasse: {bound_low} ≤ |E(F_p)| ≤ {bound_high}")
                st.info("Si quieres operaciones sobre puntos (suma, multiplicación por escalar), dímelo y las añado.")

st.caption("Nota: Tonelli–Shanks se usa aquí para obtener raíces cuadradas mod p para cualquier primo p. Este app trabaja sólo con representación y visualización de E(F_p).")
