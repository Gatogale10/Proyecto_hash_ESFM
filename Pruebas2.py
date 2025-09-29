# app_elliptic.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import os

st.set_page_config(page_title="Curvas Elípticas - Visualizador", layout="wide")

# -----------------------------------------
# Utilidades matemáticas
# -----------------------------------------
def rhs(x, a, b):
    return x**3 + a*x + b

def real_points_on_curve(x_vals, a, b):
    ys_pos = []
    ys_neg = []
    xs_pos = []
    xs_neg = []
    for x in x_vals:
        val = rhs(x, a, b)
        if val >= 0:
            y = np.sqrt(val)
            xs_pos.append(x); ys_pos.append(y)
            xs_neg.append(x); ys_neg.append(-y)
    return (np.array(xs_pos), np.array(ys_pos)), (np.array(xs_neg), np.array(ys_neg))

# Solo para p primos con p % 4 == 3 (simplificación): calcular sqrt modular
def modular_sqrt_simple(a, p):
    # Devuelve una raíz cuadrada de a módulo p si existe, o None.
    # Solo fiable cuando p % 4 == 3 (fórmula rápida).
    if a % p == 0:
        return 0
    if pow(a, (p-1)//2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p+1)//4, p)
    # Si p % 4 != 3 no implementamos Tonelli-Shanks aquí (simplificamos).
    return None

# Mapeo simple a toro para visualización 3D
def map_to_torus(x_vals, y_vals, R=2.0, r=0.7):
    # Normalizamos x,y a [0, 2pi]
    if len(x_vals) == 0:
        return np.array([]), np.array([]), np.array([])
    xs = np.array(x_vals)
    ys = np.array(y_vals)
    u = 2*np.pi * (xs - xs.min()) / max(xs.ptp(), 1e-9)
    v = 2*np.pi * (ys - ys.min()) / max(ys.ptp(), 1e-9)
    X = (R + r*np.cos(v)) * np.cos(u)
    Y = (R + r*np.cos(v)) * np.sin(u)
    Z = r * np.sin(v)
    return X, Y, Z

# -----------------------------------------
# Interfaz
# -----------------------------------------
st.title("Visualizador de Curvas Elípticas (2D y 3D)")
st.markdown("Visualiza curvas \(y^2 = x^3 + a x + b\). Ajusta parámetros y observa la curva real y una proyección 3D tipo toro.")

# Mostrar imagen si existe (proporcionaste una imagen en el entorno)
img_path = "/mnt/data/6e632cd2-bba9-4239-93a3-532578144221.png"
if os.path.exists(img_path):
    st.image(Image.open(img_path), caption="Referencia / ejemplo (solo ilustración)", use_column_width=False, width=400)

# Parámetros
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("Parámetros de la curva")
    a = st.slider("a", min_value=-10.0, max_value=10.0, value=-1.0, step=0.1)
    b = st.slider("b", min_value=-10.0, max_value=10.0, value=1.0, step=0.1)
    xmin = st.number_input("x mínimo", value=-5.0, step=0.5)
    xmax = st.number_input("x máximo", value=5.0, step=0.5)
    samples = st.slider("Resolución (puntos en x)", 200, 5000, 800)

    st.markdown("**Opciones de puntos discretos**")
    show_real_pts = st.checkbox("Mostrar puntos reales (muestras)", value=True)
    show_finite_field = st.checkbox("Mostrar puntos sobre F_p (campo finito)", value=False)
    p_field = None
    if show_finite_field:
        p_field = st.number_input("p primo (solo p%4==3 soportado aquí)", min_value=3, value=43, step=2)

with col2:
    st.subheader("Gráficas")
    # Prepare x range
    xs = np.linspace(xmin, xmax, samples)
    # Real curve points
    (xr_pos, yr_pos), (xr_neg, yr_neg) = real_points_on_curve(xs, a, b)

    # 2D plot (Plotly)
    fig2d = go.Figure()
    # continuous approximation: plot y = sqrt(rhs) and -sqrt(rhs) where defined
    if len(xr_pos) > 0:
        fig2d.add_trace(go.Scatter(x=xr_pos, y=yr_pos, mode='lines', name='y = +sqrt(...)'))
    if len(xr_neg) > 0:
        fig2d.add_trace(go.Scatter(x=xr_neg, y=yr_neg, mode='lines', name='y = -sqrt(...)'))

    # Optionally show samples as scatter
    if show_real_pts:
        # sample some x and compute real y when possible
        sample_xs = np.linspace(xmin, xmax, 200)
        px_pos_x, px_pos_y = [], []
        px_neg_x, px_neg_y = [], []
        for x0 in sample_xs:
            val = rhs(x0, a, b)
            if val >= 0:
                y0 = np.sqrt(val)
                px_pos_x.append(x0); px_pos_y.append(y0)
                px_neg_x.append(x0); px_neg_y.append(-y0)
        if px_pos_x:
            fig2d.add_trace(go.Scatter(x=px_pos_x, y=px_pos_y, mode='markers', marker=dict(size=4), name='Muestra +y'))
            fig2d.add_trace(go.Scatter(x=px_neg_x, y=px_neg_y, mode='markers', marker=dict(size=4), name='Muestra -y'))

    fig2d.update_layout(title=f"Curva elíptica: y^2 = x^3 + ({a})x + ({b})",
                        xaxis_title="x", yaxis_title="y", height=450)
    st.plotly_chart(fig2d, use_container_width=True)

    # 3D torus-like mapping
    # For the 3D display, concatenamos las ramas +y y -y para más continuidad
    x_for_3d = np.concatenate([xr_pos, xr_neg])
    y_for_3d = np.concatenate([yr_pos, yr_neg])
    X3, Y3, Z3 = map_to_torus(x_for_3d, y_for_3d, R=2.2, r=0.7)

    fig3d = go.Figure()
    # Torus surface (light mesh), parametrize for visualization
    u = np.linspace(0, 2*np.pi, 60)
    v = np.linspace(0, 2*np.pi, 30)
    U, V = np.meshgrid(u, v)
    R_t = 2.2; r_t = 0.7
    XT = (R_t + r_t * np.cos(V)) * np.cos(U)
    YT = (R_t + r_t * np.cos(V)) * np.sin(U)
    ZT = r_t * np.sin(V)
    fig3d.add_trace(go.Surface(x=XT, y=YT, z=ZT, opacity=0.25, showscale=False, name='Torus'))

    if len(X3) > 0:
        fig3d.add_trace(go.Scatter3d(x=X3, y=Y3, z=Z3, mode='markers+lines',
                                    marker=dict(size=3), line=dict(width=2),
                                    name='Curva mapeada'))

    fig3d.update_layout(scene=dict(
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        zaxis=dict(visible=False)),
                        height=650,
                        title="Proyección 3D tipo toro (representación)")

    st.plotly_chart(fig3d, use_container_width=True)

# -----------------------------------------
# Opcional: puntos sobre F_p
# -----------------------------------------
if show_finite_field:
    st.markdown("### Puntos sobre el campo finito \(\\mathbb{{F}}_p\\) (visualización discreta)")
    p = int(p_field)
    if p <= 2:
        st.error("El primer primo aceptable es p >= 3")
    else:
        if p % 4 != 3:
            st.warning("Solo se realiza sqrt modular con la fórmula rápida (p % 4 == 3). Si p % 4 != 3, puede que no se muestre correctamente.")
        xs_mod = np.arange(0, p, 1)
        pts_x = []
        pts_y = []
        for xm in xs_mod:
            rhs_m = (xm**3 + a * xm + b) % p
            y_root = modular_sqrt_simple(rhs_m, p)
            if y_root is not None:
                y1 = y_root % p
                y2 = (-y_root) % p
                pts_x.append(xm); pts_y.append(y1)
                if y2 != y1:
                    pts_x.append(xm); pts_y.append(y2)
        if len(pts_x) == 0:
            st.info("No se encontraron raíces cuadradas en F_p con los parámetros dados (o p no compatible).")
        else:
            # Map modular points into torus for visualization: normalizamos según 0..p-1
            u = 2*np.pi * np.array(pts_x) / p
            v = 2*np.pi * np.array(pts_y) / p
            R_t = 2.2; r_t = 0.7
            Xf = (R_t + r_t * np.cos(v)) * np.cos(u)
            Yf = (R_t + r_t * np.cos(v)) * np.sin(u)
            Zf = r_t * np.sin(v)
            figm = go.Figure()
            figm.add_trace(go.Surface(x=XT, y=YT, z=ZT, opacity=0.2, showscale=False, name='Torus'))
            figm.add_trace(go.Scatter3d(x=Xf, y=Yf, z=Zf, mode='markers',
                                       marker=dict(size=4, color='red'), name='Puntos en F_p'))
            figm.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
                               height=600, title=f"Puntos en F_{p} mapeados al toro")
            st.plotly_chart(figm, use_container_width=True)

st.markdown("---")
st.caption("Nota: la proyección 3D tipo toro es una herramienta visual para intuir la estructura; no es una representación canónica de la curva elíptica como grupo complejo.")
