# --------------------------------------------------
# TelecomLab - App principal
# Hecho por: Paola Itzel Ornelas Galván
# Para la asignatura Infraestructura y Redes de Comunicación, Universidad de Granada
# --------------------------------------------------

import streamlit as st
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from utils.calculations import (
    db_to_linear,
    linear_to_db,
    splitter_loss as perdida_split,
    received_power as potencia_recibida,
    max_distance as distancia_maxima,
    ci_omnidirectional,
    ci_sectorized_120,
    ci_sectorized_60,
    mm1_metrics,
)

# --------------------------------------------------
# Configuración de la página
# --------------------------------------------------
st.set_page_config(
    page_title="TelecomLab · IRC",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CSS personalizado
# --------------------------------------------------
st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #555;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .card {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            text-align: center;
            border-top: 4px solid #1e88e5;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            color: black;
        }
        .card-icon {
            font-size: 2.5rem;
        }
        .card-title {
            margin: 0.3rem 0;
            color: black;
        }
        .card-desc {
            font-size: 0.9rem;
            margin: 0;
            color: black;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
        }
        .success-box {
            background-color: #d4edda;
            border-left: 6px solid #28a745;
            padding: 0.75rem 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        .warning-box {
            background-color: #fff3cd;
            border-left: 6px solid #ffc107;
            padding: 0.75rem 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        .error-box {
            background-color: #f8d7da;
            border-left: 6px solid #dc3545;
            padding: 0.75rem 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Barra lateral - con menú desplegable funcional
# --------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3209/3209250.png", width=80)
st.sidebar.title("📡 TelecomLab")
st.sidebar.markdown("---")

opciones_modulos = [
    "🏠 Inicio",
    "🔌 GPON Planner",
    "📶 Mobile Planner",
    "⏳ Queue Simulator",
    "🏢 ICT Designer"
]

modulo_query = st.query_params.get("modulo")
if modulo_query not in opciones_modulos:
    modulo_query = None

if modulo_query:
    modulo = st.sidebar.selectbox(
        "Elige un módulo",
        opciones_modulos,
        index=opciones_modulos.index(modulo_query)
    )
else:
    modulo = st.sidebar.selectbox(
        "Elige un módulo",
        opciones_modulos
    )

if modulo != modulo_query:
    st.query_params["modulo"] = modulo
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Universidad de Granada · IRC")
st.sidebar.caption("Proyecto didáctico - 2026")

# --------------------------------------------------
# Nota: las funciones de cálculo (perdida_split, potencia_recibida,
# distancia_maxima, ci_omnidirectional, ci_sectorized_120/60, mm1_metrics)
# viven en calculations.py y se importan arriba. Así evitamos tener la
# misma fórmula escrita dos veces (una en calculations.py y otra aquí).
# --------------------------------------------------

# --------------------------------------------------
# Función para exportar a PDF
# --------------------------------------------------
def exportar_pdf(nombre_modulo, parametros, resultados, figura=None):
    try:
        from utils.pdf_export import generar_pdf
        return generar_pdf(nombre_modulo, parametros, resultados, figura)
    except ImportError as e:
        st.error(f"No se pudo generar el PDF: {e}. Revisa que pdf_export.py esté en la misma carpeta que app.py y que 'reportlab' esté instalado (pip install reportlab).")
        return None

# --------------------------------------------------
# MÓDULO: INICIO
# --------------------------------------------------
if modulo == "🏠 Inicio":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0d47a1, #1e88e5); padding: 1.5rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 1.5rem;">
            <h1 style="font-size: 2.8rem; margin: 0;">📡 TelecomLab</h1>
            <p style="font-size: 1.1rem; opacity: 0.9;">Plataforma educativa para Infraestructuras y Redes de Comunicación</p>
            <p style="font-size: 0.9rem; opacity: 0.7; margin-top: 0.2rem;">Universidad de Granada · GITT · Curso 2025/2026</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("""
    Con esta herramienta puedes experimentar con distintos conceptos de la asignatura. 
    Cambia los parámetros y mira cómo se comporta el sistema en tiempo real.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; border-top: 4px solid #1e88e5; height: 180px; display: flex; flex-direction: column; justify-content: center; color: black;">
            <div style="font-size: 2.5rem;">🔌</div>
            <h4 style="margin: 0.3rem 0; color: black;">GPON Planner</h4>
            <p style="font-size: 0.9rem; margin: 0; color: black;">Diseña redes ópticas pasivas: calcula potencia, distancia máxima y comprueba el enlace.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a GPON", key="btn_gpon", use_container_width=True):
            st.query_params["modulo"] = "🔌 GPON Planner"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; border-top: 4px solid #43a047; height: 180px; display: flex; flex-direction: column; justify-content: center; color: black;">
            <div style="font-size: 2.5rem;">📶</div>
            <h4 style="margin: 0.3rem 0; color: black;">Mobile Planner</h4>
            <p style="font-size: 0.9rem; margin: 0; color: black;">Analiza interferencia cocanal, calcula C/I y visualiza el patrón de reuso.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Mobile", key="btn_mobile", use_container_width=True):
            st.query_params["modulo"] = "📶 Mobile Planner"
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; border-top: 4px solid #f9a825; height: 180px; display: flex; flex-direction: column; justify-content: center; color: black;">
            <div style="font-size: 2.5rem;">⏳</div>
            <h4 style="margin: 0.3rem 0; color: black;">Queue Simulator</h4>
            <p style="font-size: 0.9rem; margin: 0; color: black;">Simula colas M/M/1: obtén utilización, tiempos de espera y distribución de estados.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Queue", key="btn_queue", use_container_width=True):
            st.query_params["modulo"] = "⏳ Queue Simulator"
            st.rerun()

    with col4:
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; border-top: 4px solid #e53935; height: 180px; display: flex; flex-direction: column; justify-content: center; color: black;">
            <div style="font-size: 2.5rem;">🏢</div>
            <h4 style="margin: 0.3rem 0; color: black;">ICT Designer</h4>
            <p style="font-size: 0.9rem; margin: 0; color: black;">Diseña red de TDT según normativa: calcula niveles y verifica el cumplimiento.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a ICT", key="btn_ict", use_container_width=True):
            st.query_params["modulo"] = "🏢 ICT Designer"
            st.rerun()

    st.markdown("---")
    st.info("💡 **Pista:** Juega con los deslizadores y selectores para ver cómo cambian los resultados.")
    st.caption("Desarrollado para la asignatura Infraestructuras y Redes de Comunicación · GITT · UGR")

# --------------------------------------------------
# MÓDULO: GPON PLANNER
# --------------------------------------------------
elif modulo == "🔌 GPON Planner":
    st.header("🔌 GPON Planner")
    st.markdown("Diseña una red GPON y comprueba si el enlace óptico funciona.")

    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.write("""
        Aquí metes los datos típicos de un enlace GPON: potencia de la OLT, sensibilidad del receptor, distancia, atenuación de la fibra, número de usuarios (split ratio) y pérdidas extras. La aplicación te dice la potencia que llega al receptor, la distancia máxima que se puede alcanzar y si el enlace es válido. También dibuja un esquema de la red.
        """)

    col1, col2 = st.columns(2)
    with col1:
        pot_tx = st.slider("Potencia de la OLT (dBm)", 0.0, 40.0, 30.0, 0.5)
        sensibilidad = st.slider("Sensibilidad del ONT (dBm)", -40.0, -10.0, -30.0, 0.5)
        distancia = st.slider("Distancia (km)", 0.0, 40.0, 8.0, 0.5)
    with col2:
        atenuacion = st.slider("Atenuación de la fibra (dB/km)", 0.1, 1.0, 0.5, 0.05)
        usuarios = st.selectbox("Número de usuarios (split)", [8, 16, 32, 64], index=3)
        perdidas_extra = st.slider("Pérdidas extra (conectores, empalmes) (dB)", 0.0, 10.0, 2.0, 0.5)

    split_loss = perdida_split(usuarios)
    perdida_total = atenuacion * distancia + split_loss + perdidas_extra
    rx_power = pot_tx - perdida_total
    max_dist = distancia_maxima(pot_tx, sensibilidad, atenuacion, usuarios, perdidas_extra)

    st.subheader("📊 Resultados")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔹 Potencia recibida", f"{rx_power:.2f} dBm")
    c2.metric("🔹 Distancia máxima", f"{max_dist:.2f} km")
    c3.metric("🔹 Pérdida del split", f"{split_loss:.2f} dB")
    c4.metric("🔹 Pérdidas totales", f"{perdida_total:.2f} dB")

    if rx_power >= sensibilidad:
        st.markdown('<div class="success-box">✅ Enlace válido: la potencia recibida es suficiente para el receptor.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">❌ Enlace NO válido: la potencia recibida es muy baja. Acorta la distancia o sube la potencia de la OLT.</div>', unsafe_allow_html=True)

    st.subheader("📈 Potencia recibida vs Distancia")
    d_range = np.linspace(0, max_dist + 5 if max_dist < 40 else 40, 100)
    powers = [potencia_recibida(pot_tx, d, atenuacion, usuarios, perdidas_extra) for d in d_range]

    fig1, ax = plt.subplots(figsize=(10, 4))
    ax.plot(d_range, powers, label="Potencia recibida", color='#1E88E5', linewidth=2)
    ax.axhline(y=sensibilidad, color='red', linestyle='--', label=f"Sensibilidad = {sensibilidad} dBm")
    ax.axvline(x=max_dist, color='green', linestyle=':', label=f"Distancia máxima = {max_dist:.2f} km")
    ax.set_xlabel("Distancia (km)")
    ax.set_ylabel("Potencia (dBm)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig1)

    st.subheader("🌐 Esquema de la red")
    fig_gpon, ax_gpon = plt.subplots(figsize=(10, 4))
    ax_gpon.set_xlim(-1, 10)
    ax_gpon.set_ylim(-1, 5)
    ax_gpon.axis('off')

    olt_pos = (0, 2.5)
    splitter_pos = (4, 2.5)
    onu_positions = []
    num_onus = min(usuarios, 8)
    for i in range(num_onus):
        x = 7.5
        y = 0.5 + (4.0 / (num_onus - 1)) * i if num_onus > 1 else 2.5
        onu_positions.append((x, y))

    ax_gpon.scatter(*olt_pos, s=1000, color='#1E88E5', zorder=5)
    ax_gpon.text(olt_pos[0]-0.5, olt_pos[1]-0.3, "OLT", fontsize=12, fontweight='bold', color='white')
    ax_gpon.scatter(*splitter_pos, s=800, color='#FFA000', zorder=5)
    ax_gpon.text(splitter_pos[0]-0.9, splitter_pos[1]-0.3, f"Splitter\n1:{usuarios}", fontsize=10, fontweight='bold', color='white', ha='center')
    for pos in onu_positions:
        ax_gpon.scatter(*pos, s=500, color='#43A047', zorder=5)
        ax_gpon.text(pos[0]-0.4, pos[1]-0.3, "ONU", fontsize=10, fontweight='bold', color='white')

    ax_gpon.plot([olt_pos[0], splitter_pos[0]], [olt_pos[1], splitter_pos[1]], color='black', linewidth=3, zorder=1)
    for pos in onu_positions:
        ax_gpon.plot([splitter_pos[0], pos[0]], [splitter_pos[1], pos[1]], color='black', linewidth=2, linestyle='--', zorder=1)

    ax_gpon.text(2, 2.8, f"Fibra: {distancia} km\nAten: {atenuacion} dB/km", fontsize=9, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    ax_gpon.text(5.5, 3.5, f"Pérdidas extra:\n{perdidas_extra} dB", fontsize=9, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    ax_gpon.set_title(f"Red GPON con {usuarios} usuarios")
    st.pyplot(fig_gpon)

    # --- Botones finales: PDF y Volver al inicio (uno al lado del otro) ---
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📄 Generar PDF con estos resultados (GPON)", use_container_width=True):
            parametros = {
                "Potencia OLT": f"{pot_tx} dBm",
                "Sensibilidad ONT": f"{sensibilidad} dBm",
                "Distancia": f"{distancia} km",
                "Atenuación": f"{atenuacion} dB/km",
                "Usuarios": usuarios,
                "Pérdidas extra": f"{perdidas_extra} dB"
            }
            resultados = {
                "Potencia recibida": f"{rx_power:.2f} dBm",
                "Distancia máxima": f"{max_dist:.2f} km",
                "Pérdida split": f"{split_loss:.2f} dB",
                "Pérdidas totales": f"{perdida_total:.2f} dB",
                "Enlace válido": "Sí" if rx_power >= sensibilidad else "No"
            }
            pdf_buffer = exportar_pdf("GPON Planner", parametros, resultados, fig1)
            if pdf_buffer:
                b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="TelecomLab_GPON.pdf">⬇️ Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
    with col_b2:
        if st.button("🏠 Volver al inicio", key="volver_inicio_gpon", use_container_width=True):
            st.query_params["modulo"] = "🏠 Inicio"
            st.rerun()

# --------------------------------------------------
# MÓDULO: MOBILE PLANNER
# --------------------------------------------------
elif modulo == "📶 Mobile Planner":
    st.header("📶 Mobile Planner")
    st.markdown("Calcula la interferencia cocanal en redes celulares.")

    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.write("""
        Aquí defines el factor de reuso N, la constante de propagación γ y el tipo de celda 
        (omnidireccional o sectorizada). Cada tipo tiene un número distinto de celdas 
        co-canal interferentes "dominantes" en la primera corona: 6 en omnidireccional, 
        2 en sectorización a 120° (3 sectores) y 1 en sectorización a 60° (6 sectores) — 
        sectorizar reduce la interferencia porque las antenas direccionales "tapan" a la 
        mayoría de las celdas que antes interferían. La herramienta calcula la C/I 
        resultante (lineal y en dB), la distancia de reuso D/R, y dibuja el patrón de celdas.
        """)

    col1, col2, col3 = st.columns(3)
    with col1:
        N = st.slider("Factor de reuso N", 1, 12, 7, 1)
    with col2:
        gamma = st.slider("Constante de propagación γ", 2.0, 5.0, 4.0, 0.1)
    with col3:
        tipo_celda = st.selectbox(
            "Tipo de celda",
            ["Omnidireccional (6 interferentes)", "Sectorizada 120° (2 interferentes)", "Sectorizada 60° (1 interferente)"]
        )

    if tipo_celda.startswith("Omnidireccional"):
        ci, ci_db = ci_omnidirectional(N, gamma)
        interferentes = 6
    elif tipo_celda.startswith("Sectorizada 120"):
        ci, ci_db = ci_sectorized_120(N, gamma)
        interferentes = 2
    else:
        ci, ci_db = ci_sectorized_60(N, gamma)
        interferentes = 1

    DR = math.sqrt(3 * N)

    st.subheader("📊 Resultados")
    c1, c2, c3 = st.columns(3)
    c1.metric("C/I (lineal)", f"{ci:.3f}")
    c2.metric("C/I (dB)", f"{ci_db:.2f} dB")
    c3.metric("D/R", f"{DR:.2f}")

    if ci_db >= 18:
        st.markdown('<div class="success-box">✅ Excelente calidad: C/I > 18 dB, ideal para modulaciones densas.</div>', unsafe_allow_html=True)
    elif ci_db >= 12:
        st.markdown('<div class="warning-box">⚠️ Calidad aceptable: C/I entre 12 y 18 dB, se pueden usar modulaciones robustas.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">❌ Calidad insuficiente: C/I < 12 dB, riesgo de errores.</div>', unsafe_allow_html=True)

    st.subheader("🔷 Patrón de celdas interferentes")
    fig, ax = plt.subplots(figsize=(8, 6))
    def hex_corners(cx, cy, r=1):
        angulos = np.linspace(0, 2*np.pi, 7)
        return [(cx + r*np.cos(a), cy + r*np.sin(a)) for a in angulos]

    r = 1.0
    cx, cy = 0, 0
    hex_central = hex_corners(cx, cy, r)
    ax.add_patch(plt.Polygon(hex_central, color='#1E88E5', alpha=0.7, label='Celda objetivo'))

    for angulo in np.linspace(0, 2*np.pi, interferentes, endpoint=False):
        dx = DR * r * np.cos(angulo)
        dy = DR * r * np.sin(angulo)
        hex_inter = hex_corners(dx, dy, r)
        ax.add_patch(plt.Polygon(hex_inter, color='#FF5252', alpha=0.5, label='Interferente' if angulo == 0 else ""))

    ax.set_xlim(-DR*r - 1.5, DR*r + 1.5)
    ax.set_ylim(-DR*r - 1.5, DR*r + 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"Reuso N={N} | D/R = {DR:.2f}")
    st.pyplot(fig)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📄 Generar PDF (Mobile)", use_container_width=True):
            parametros = {"N": N, "γ": gamma, "Interferentes": interferentes}
            resultados = {"C/I lineal": f"{ci:.3f}", "C/I dB": f"{ci_db:.2f}", "D/R": f"{DR:.2f}"}
            pdf_buffer = exportar_pdf("Mobile Planner", parametros, resultados, fig)
            if pdf_buffer:
                b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="TelecomLab_Mobile.pdf">⬇️ Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
    with col_b2:
        if st.button("🏠 Volver al inicio", key="volver_inicio_mobile", use_container_width=True):
            st.query_params["modulo"] = "🏠 Inicio"
            st.rerun()

# --------------------------------------------------
# MÓDULO: QUEUE SIMULATOR
# --------------------------------------------------
elif modulo == "⏳ Queue Simulator":
    st.header("⏳ Queue Simulator")
    st.markdown("Simula una cola M/M/1 y saca todas sus métricas.")

    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.write("""
        Metes la tasa de llegada λ y la de servicio μ. La aplicación calcula la utilización ρ, el número medio de clientes en el sistema L, el tiempo medio W, y también los de la cola (Lq y Wq). Además, dibuja la distribución de probabilidad de los estados.
        """)

    col1, col2 = st.columns(2)
    with col1:
        lam = st.slider("λ (llegadas/seg)", 0.1, 20.0, 4.0, 0.1)
    with col2:
        mu = st.slider("μ (servicios/seg)", 0.1, 20.0, 6.0, 0.1)

    if lam >= mu:
        st.markdown('<div class="error-box">⚠️ Cuidado: λ ≥ μ, el sistema es inestable. Aumenta μ o baja λ.</div>', unsafe_allow_html=True)
    else:
        rho = lam / mu
        W = 1 / (mu - lam)
        L = lam * W
        Wq = W - (1/mu)
        Lq = lam * Wq

        st.subheader("📊 Métricas")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("ρ (utilización)", f"{rho:.3f}")
        c2.metric("L (sistema)", f"{L:.3f}")
        c3.metric("W (sistema) s", f"{W:.3f}")
        c4.metric("Lq (cola)", f"{Lq:.3f}")
        c5.metric("Wq (cola) s", f"{Wq:.3f}")

        if rho < 0.5:
            st.markdown('<div class="success-box">🟢 Baja ocupación: todo va rápido.</div>', unsafe_allow_html=True)
        elif rho < 0.8:
            st.markdown('<div class="warning-box">🟡 Ocupación moderada: retrasos razonables.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">🔴 Sistema saturado: muchos retrasos, mejor aumentar μ.</div>', unsafe_allow_html=True)

        st.subheader("📈 Probabilidad de cada estado")
        max_n = 20
        probs = [(1-rho) * (rho**n) for n in range(max_n+1)]
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(range(max_n+1), probs, color='#1E88E5', alpha=0.7)
        ax.set_xlabel("Número de clientes (n)")
        ax.set_ylabel("Probabilidad πₙ")
        ax.grid(True, alpha=0.3)
        ax.set_title("Distribución estacionaria M/M/1")
        st.pyplot(fig)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("📄 Generar PDF (Queue)", use_container_width=True):
                parametros = {"λ": lam, "μ": mu}
                resultados = {"ρ": f"{rho:.3f}", "L": f"{L:.3f}", "W": f"{W:.3f} s", "Lq": f"{Lq:.3f}", "Wq": f"{Wq:.3f} s"}
                pdf_buffer = exportar_pdf("Queue Simulator", parametros, resultados, fig)
                if pdf_buffer:
                    b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="TelecomLab_Queue.pdf">⬇️ Descargar PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
        with col_b2:
            if st.button("🏠 Volver al inicio", key="volver_inicio_queue", use_container_width=True):
                st.query_params["modulo"] = "🏠 Inicio"
                st.rerun()

# --------------------------------------------------
# MÓDULO: ICT DESIGNER
# --------------------------------------------------
elif modulo == "🏢 ICT Designer":
    st.header("🏢 ICT Designer")
    st.markdown("Diseña la red de distribución de TDT de un edificio según el RD 346/2011.")

    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.write("""
        Aquí defines el número de plantas, viviendas por planta y distancia entre plantas, además del 
        nivel de salida del amplificador de cabecera, la atenuación del cable y el rango admitido en 
        toma. Luego eliges qué derivador poner en cada planta (cada uno tiene unas pérdidas de paso AP 
        y de derivación AD). Si hay más de una vivienda por planta, se añade además la pérdida de un 
        distribuidor ideal que reparte la señal entre ellas (10·log₁₀(viviendas)). La aplicación calcula 
        el nivel de señal en cada toma y te dice si cumple el rango que hayas definido. También dibuja 
        un esquema vertical de la red.

        **Simplificación asumida:** se modela una única toma "representativa" por planta (con la pérdida 
        de distribución ya incluida si hay varias viviendas), no cada BAT individual.
        """)

    st.subheader("Parámetros del edificio")
    col1, col2, col3 = st.columns(3)
    with col1:
        plantas = st.slider("Número de plantas", 1, 10, 5, 1)
    with col2:
        viviendas_planta = st.slider("Viviendas por planta", 1, 6, 4, 1)
    with col3:
        dist_entre_plantas = st.slider("Distancia entre plantas (m)", 2, 6, 4, 1)

    st.subheader("Parámetros de cabecera y normativa")
    col4, col5, col6 = st.columns(3)
    with col4:
        nivel_salida_amp = st.slider("Nivel de salida del amplificador (dBμV)", 80, 110, 90, 1)
    with col5:
        atenuacion_cable = st.slider("Atenuación del cable (dB/m)", 0.05, 0.30, 0.10, 0.01)
    with col6:
        rango_admitido = st.slider("Rango admitido en toma (dBμV)", 20, 90, (40, 70), 1)
    nivel_min, nivel_max = rango_admitido

    perdida_toma = 1.5
    perdida_pau = 1.0
    # Pérdida adicional de un distribuidor ideal si hay más de una vivienda
    # por planta (reparte la señal de la derivación entre las N viviendas).
    perdida_distribuidor = 10 * math.log10(viviendas_planta) if viviendas_planta > 1 else 0.0

    derivadores = [
        {"nombre": "Derivador 10/2", "AD": 10, "AP": 2.3},
        {"nombre": "Derivador 15/1.6", "AD": 15, "AP": 1.6},
        {"nombre": "Derivador 20/1.6", "AD": 20, "AP": 1.6},
        {"nombre": "Derivador 25/1.3", "AD": 25, "AP": 1.3}
    ]

    st.subheader("Elige el derivador para cada planta")
    derivador_por_planta = []
    for p in range(plantas):
        opciones = [f"{d['nombre']} (AD={d['AD']} dB, AP={d['AP']} dB)" for d in derivadores]
        idx = st.selectbox(f"Planta {p+1} (desde arriba)", options=range(len(opciones)), format_func=lambda i: opciones[i], key=f"deriv_{p}")
        derivador_por_planta.append(derivadores[idx])

    niveles = []
    perdida_acumulada = 0
    dist_cabecera_planta_alta = 5

    for i in range(plantas-1, -1, -1):
        if i == plantas-1:
            dist_cable = dist_cabecera_planta_alta
        else:
            dist_cable = dist_entre_plantas
        perdida_cable = dist_cable * atenuacion_cable
        deriv = derivador_por_planta[i]
        señal_entrada_deriv = nivel_salida_amp - perdida_acumulada - perdida_cable
        señal_toma = señal_entrada_deriv - deriv["AD"] - perdida_pau - perdida_toma - perdida_distribuidor
        niveles.append(señal_toma)
        perdida_acumulada += deriv["AP"] + perdida_cable

    niveles = list(reversed(niveles))

    st.subheader("📊 Niveles de señal por planta")
    df_niveles = pd.DataFrame({
        "Planta": [f"{i+1}" for i in range(plantas)],
        "Nivel en toma (dBμV)": [f"{n:.2f}" for n in niveles],
        "Cumple ({}-{})".format(nivel_min, nivel_max): ["✅" if nivel_min <= n <= nivel_max else "❌" for n in niveles]
    })
    st.table(df_niveles)

    if all(nivel_min <= n <= nivel_max for n in niveles):
        st.markdown('<div class="success-box">✅ ¡Todo correcto! Todos los niveles están dentro del rango permitido.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">❌ Alguna planta no cumple. Prueba a cambiar los derivadores o añadir un amplificador intermedio.</div>', unsafe_allow_html=True)

    st.subheader("🏗️ Esquema de la red de distribución")
    fig_ict, ax_ict = plt.subplots(figsize=(12, 6))
    ax_ict.set_xlim(-2, 8)
    ax_ict.set_ylim(-1, plantas + 1)
    ax_ict.axis('off')

    ax_ict.plot([0, 0], [0, plantas + 1], color='#333', linewidth=4, zorder=1)
    ax_ict.scatter(0, plantas + 0.5, s=400, color='#1E88E5', zorder=5, edgecolors='black', linewidth=2)
    ax_ict.text(0.2, plantas + 0.5, "AMP\n90 dBµV", fontsize=10, ha='left', va='center', fontweight='bold')

    for i in range(plantas):
        y_pos = i + 0.5
        nivel = niveles[i]
        deriv = derivador_por_planta[i]
        color = '#43A047' if nivel_min <= nivel <= nivel_max else '#E53935'

        ax_ict.plot([0, 2.5], [y_pos, y_pos], color='#555', linewidth=2, zorder=1)
        ax_ict.scatter(2.5, y_pos, s=250, color='#FFA000', zorder=5, edgecolors='black')
        ax_ict.text(2.7, y_pos, f"Planta {i+1}\nAD={deriv['AD']}dB", fontsize=9, ha='left', va='center', bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7))
        ax_ict.scatter(5.5, y_pos, s=150, color=color, zorder=5, edgecolors='black')
        ax_ict.text(5.7, y_pos, f"{nivel:.1f} dBµV", fontsize=10, ha='left', va='center', fontweight='bold', color=color)
        ax_ict.plot([2.5, 5.5], [y_pos, y_pos], color='#888', linewidth=1.5, linestyle=':', zorder=1)

        if i < plantas - 1:
            ax_ict.annotate('', xy=(0, i+1.5), xytext=(0, i+1), arrowprops=dict(arrowstyle='->', color='#333', lw=1))

    ax_ict.scatter([], [], s=150, color='#43A047', label='Cumple normativa')
    ax_ict.scatter([], [], s=150, color='#E53935', label='Fuera de rango')
    ax_ict.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=10)
    ax_ict.set_title("Topología de la red de distribución (ICT)", fontsize=14, fontweight='bold')
    ax_ict.set_ylim(-0.5, plantas + 1)
    st.pyplot(fig_ict)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📄 Generar PDF (ICT)", use_container_width=True):
            parametros = {
                "Plantas": plantas,
                "Viviendas/planta": viviendas_planta,
                "Distancia entre plantas": f"{dist_entre_plantas} m"
            }
            resultados = {f"Planta {i+1}": f"{n:.2f} dBμV" for i, n in enumerate(niveles)}
            resultados["Cumple normativa"] = "Sí" if all(nivel_min <= n <= nivel_max for n in niveles) else "No"
            pdf_buffer = exportar_pdf("ICT Designer", parametros, resultados, fig_ict)
            if pdf_buffer:
                b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="TelecomLab_ICT.pdf">⬇️ Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
    with col_b2:
        if st.button("🏠 Volver al inicio", key="volver_inicio_ict", use_container_width=True):
            st.query_params["modulo"] = "🏠 Inicio"
            st.rerun()

# --------------------------------------------------
# Pie de página (común a todos los módulos)
# --------------------------------------------------
st.markdown("---")
st.caption("TelecomLab · Versión 2.0 · Hecho con 💙 para la UGR")