# -------------------------------------------------------------------
# TelecomLab - Aplicación principal (versión final)
# -------------------------------------------------------------------
# Asignatura: Infraestructuras y Redes de Comunicación
# Universidad de Granada
# -------------------------------------------------------------------

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
    ci_custom_distances,
    mm1_metrics,
    erlang_b,
    canales_para_erlang,
    modulacion_minima,
    mejor_modulacion,
)

# ------------------------------------------------------------
# Configuración de la página (modo ancho)
# ------------------------------------------------------------
st.set_page_config(
    page_title="TelecomLab · IRC",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# Estilos CSS (para que la interfaz se vea bonita)
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# Barra lateral
# ------------------------------------------------------------
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

# Control de la navegación con query params
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

# ------------------------------------------------------------
# Función para exportar a PDF
# ------------------------------------------------------------
def exportar_pdf(nombre_modulo, parametros, resultados, figura=None):
    try:
        from utils.pdf_export import generar_pdf
        return generar_pdf(nombre_modulo, parametros, resultados, figura)
    except ImportError as e:
        st.markdown(
            f'<div class="warning-box" style="color: #b26a00;">⚠️ No se pudo generar el PDF: {e}.</div>',
            unsafe_allow_html=True
        )
        return None

# ------------------------------------------------------------
# Página de inicio
# ------------------------------------------------------------
if modulo == "🏠 Inicio":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0d47a1, #1e88e5); padding: 1.5rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 1.5rem;">
            <h1 style="font-size: 2.8rem; margin: 0;">📡 TelecomLab</h1>
            <p style="font-size: 1.1rem; opacity: 0.9;">Plataforma educativa para Infraestructuras y Redes de Comunicación</p>
            <p style="font-size: 0.9rem; opacity: 0.7; margin-top: 0.2rem;">Universidad de Granada · Curso 2025/2026</p>
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
    st.info("💡 **Consejo:** Juega con los deslizadores y selectores para ver cómo cambian los resultados.")
    st.caption("Desarrollado para la asignatura Infraestructuras y Redes de Comunicación · Universidad de Granada")


# ------------------------------------------------------------
# Módulo GPON Planner
# ------------------------------------------------------------
elif modulo == "🔌 GPON Planner":
    st.header("🔌 GPON Planner")
    st.markdown("Diseña una red GPON y comprueba si el enlace óptico funciona.")

    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.write("""
        **Parámetros:** potencia y sensibilidad de OLT y ONT, atenuación, split ratio, pérdidas extra.
        - **Distancia máxima:** se calcula para ambos enlaces (descendente y ascendente) y se muestra la más restrictiva.
        - **Potencia mínima:** para alcanzar una velocidad objetivo, se elige la modulación que minimiza el ancho de banda (máxima modulación posible, hasta 16-QAM).
        """)

    # --- Parámetros de entrada ---
    col1, col2 = st.columns(2)
    with col1:
        pot_olt = st.slider("Potencia de la OLT (dBm)", 0.0, 40.0, 30.0, 0.5)
        sens_ont = st.slider("Sensibilidad del ONT (dBm)", -40.0, -10.0, -25.0, 0.5)
        pot_ont = st.slider("Potencia de la ONT (dBm)", 0.0, 30.0, 22.0, 0.5)
        sens_olt = st.slider("Sensibilidad de la OLT (dBm)", -40.0, -10.0, -30.0, 0.5)
    with col2:
        atenuacion = st.slider("Atenuación de la fibra (dB/km)", 0.1, 1.0, 0.5, 0.05)
        usuarios = st.selectbox("Número de usuarios (split)", [8, 16, 32, 64], index=3)
        perdidas_extra = st.slider("Pérdidas extra (conectores, empalmes) (dB)", 0.0, 10.0, 2.0, 0.5)
        distancia = st.slider("Distancia (km)", 0.0, 100.0, 8.0, 0.5)

    # Cálculo de pérdidas
    split_loss = perdida_split(usuarios)
    perdida_total_dl = atenuacion * distancia + split_loss + perdidas_extra
    perdida_total_ul = atenuacion * distancia + perdidas_extra

    # Potencias recibidas
    rx_ont = pot_olt - perdida_total_dl
    rx_olt = pot_ont - perdida_total_ul

    # Distancias máximas
    dmax_dl = distancia_maxima(pot_olt, sens_ont, atenuacion, usuarios, perdidas_extra)
    # En ascendente no se cuenta la pérdida de splitter (criterio del enunciado/examen);
    # se reutiliza la misma función con users=1 para no duplicar la fórmula.
    dmax_ul = distancia_maxima(pot_ont, sens_olt, atenuacion, 1, perdidas_extra)
    dmax_sistema = min(dmax_dl, dmax_ul)

    # Mostrar resultados de sensibilidad
    st.subheader("📊 Resultados de sensibilidad")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔹 Potencia recibida ONT", f"{rx_ont:.2f} dBm")
    c2.metric("🔹 Potencia recibida OLT", f"{rx_olt:.2f} dBm")
    c3.metric("🔹 Distancia máx. DL", f"{dmax_dl:.2f} km")
    c4.metric("🔹 Distancia máx. UL", f"{dmax_ul:.2f} km")
    st.metric("📏 Distancia máxima del sistema (la menor)", f"{dmax_sistema:.2f} km")

    if rx_ont >= sens_ont and rx_olt >= sens_olt:
        st.markdown('<div class="success-box">✅ Enlace válido: ambos receptores reciben señal suficiente.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box" style="color: #b71c1c;">❌ Enlace NO válido: alguna potencia recibida es inferior a la sensibilidad.</div>', unsafe_allow_html=True)

    # ---- Potencia mínima OLT para velocidad objetivo (DL) ----
    st.subheader("🔽 Potencia mínima de OLT para velocidad objetivo (downlink)")
    velocidad_dl = st.number_input("Velocidad objetivo por usuario (Mbps)", min_value=1, max_value=100, value=40, step=1)
    velocidad_total_dl = velocidad_dl * usuarios  # Mbps totales
    # Modulaciones permitidas: máxima 16-QAM (según enunciado)
    modulaciones_dl = [("16-QAM", 16, 21.5), ("8-QAM", 8, 18), ("4-QAM", 4, 14.5)]
    psd_ruido_dl_dbm = -100.0  # dBm/Hz (solo ruido; el enunciado dice que la interferencia solo afecta al ascendente)
    resultado_dl = mejor_modulacion(modulaciones_dl, velocidad_total_dl, perdida_total_dl, psd_ruido_dl_dbm, pot_olt)
    if resultado_dl is not None:
        st.success(f"✅ Modulación elegida: **{resultado_dl['nombre']}** con ancho de banda **{resultado_dl['bw_mhz']:.2f} MHz**")
        st.metric("Potencia mínima OLT necesaria", f"{resultado_dl['potencia_dbm']:.2f} dBm")
    else:
        st.markdown('<div class="error-box" style="color: #b71c1c;">❌ No se puede alcanzar la velocidad objetivo con ninguna modulación (potencia necesaria > máxima).</div>', unsafe_allow_html=True)

    # ---- Potencia mínima ONT para velocidad objetivo (UL) con ruido+interferencia ----
    st.subheader("🔽 Potencia mínima de ONT para velocidad objetivo (uplink)")
    psd_ruido = db_to_linear(-100)   # mW/Hz
    psd_interf = db_to_linear(-95)   # mW/Hz
    psd_total = (math.sqrt(psd_ruido) + math.sqrt(psd_interf))**2
    psd_total_dbm = linear_to_db(psd_total)   # dBm/Hz

    velocidad_ul = st.number_input("Velocidad objetivo por usuario (Mbps) (uplink)", min_value=1, max_value=100, value=20, step=1)
    velocidad_total_ul = velocidad_ul * usuarios
    modulaciones_ul = [("16-QAM", 16, 21.5), ("8-QAM", 8, 18), ("4-QAM", 4, 14.5)]
    resultado_ul = mejor_modulacion(modulaciones_ul, velocidad_total_ul, perdida_total_ul, psd_total_dbm, pot_ont)
    if resultado_ul is not None:
        st.success(f"✅ Modulación elegida: **{resultado_ul['nombre']}** con ancho de banda **{resultado_ul['bw_mhz']:.2f} MHz**")
        st.metric("Potencia mínima ONT necesaria", f"{resultado_ul['potencia_dbm']:.2f} dBm")
    else:
        st.markdown('<div class="error-box" style="color: #b71c1c;">❌ No se puede alcanzar la velocidad en uplink con ninguna modulación.</div>', unsafe_allow_html=True)

    # ---- Gráfica de potencia vs distancia ----
    st.subheader("📈 Potencia recibida vs Distancia")
    d_range = np.linspace(0, max(dmax_dl, dmax_ul) + 5, 100)
    powers_dl = [potencia_recibida(pot_olt, d, atenuacion, usuarios, perdidas_extra) for d in d_range]
    powers_ul = [potencia_recibida(pot_ont, d, atenuacion, 1, perdidas_extra) for d in d_range]  # sin splitter en UL

    fig1, ax = plt.subplots(figsize=(18, 8))
    fig1.patch.set_facecolor('#2d2d2d')
    ax.set_facecolor('#2d2d2d')
    ax.plot(d_range, powers_dl, color="#1E88E5", linewidth=3, label="Downlink (OLT→ONT)")
    ax.plot(d_range, powers_ul, color="#FF9800", linewidth=3, linestyle='--', label="Uplink (ONT→OLT)")
    ax.axhline(y=sens_ont, color="red", linestyle="--", linewidth=2, label=f"Sens. ONT = {sens_ont} dBm")
    ax.axhline(y=sens_olt, color="purple", linestyle="-.", linewidth=2, label=f"Sens. OLT = {sens_olt} dBm")
    ax.axvline(x=dmax_dl, color="green", linestyle=":", linewidth=2, label=f"Dmax DL = {dmax_dl:.1f} km")
    ax.axvline(x=dmax_ul, color="orange", linestyle=":", linewidth=2, label=f"Dmax UL = {dmax_ul:.1f} km")
    ax.set_xlabel("Distancia (km)", fontsize=14, color='white')
    ax.set_ylabel("Potencia recibida (dBm)", fontsize=14, color='white')
    ax.set_title("Evolución de la potencia en ambos enlaces", fontsize=16, color='white')
    ax.grid(True, linestyle=":", alpha=0.5, color='gray')
    ax.legend(fontsize=12, facecolor='#2d2d2d', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')
    fig1.tight_layout()
    st.pyplot(fig1, use_container_width=True)

    # ---- Esquema de la red ----
    st.subheader("🌐 Esquema de la red")
    enlace_ok = rx_ont >= sens_ont and rx_olt >= sens_olt
    color_enlace = '#43A047' if enlace_ok else '#E53935'

    fig_gpon, ax_gpon = plt.subplots(figsize=(18, 8))
    fig_gpon.patch.set_facecolor('#2d2d2d')
    ax_gpon.set_facecolor('#2d2d2d')
    ax_gpon.set_xlim(-1, 10.5)
    ax_gpon.set_ylim(-1.3, 5)
    ax_gpon.axis('off')

    olt_pos = (0, 2.5)
    splitter_pos = (4, 2.5)
    num_onus_dibujadas = min(usuarios, 8)
    onu_positions = []
    for i in range(num_onus_dibujadas):
        x = 7.5
        y = 0.5 + (4.0 / (num_onus_dibujadas - 1)) * i if num_onus_dibujadas > 1 else 2.5
        onu_positions.append((x, y))

    ax_gpon.scatter(*olt_pos, s=1200, color='#1E88E5', zorder=5)
    ax_gpon.text(olt_pos[0]-0.5, olt_pos[1]-0.35, "OLT", fontsize=14, fontweight='bold', color='white')
    ax_gpon.text(olt_pos[0], olt_pos[1]+0.7, f"P_TX = {pot_olt:.1f} dBm", fontsize=12, ha='center', color='white')

    ax_gpon.plot([olt_pos[0], splitter_pos[0]], [olt_pos[1], splitter_pos[1]], color=color_enlace, linewidth=3, zorder=1)
    ax_gpon.annotate('', xy=(splitter_pos[0], olt_pos[1]-0.55), xytext=(olt_pos[0], olt_pos[1]-0.55),
                     arrowprops=dict(arrowstyle='<->', color='white'))
    ax_gpon.text((olt_pos[0]+splitter_pos[0])/2, olt_pos[1]-0.9,
                 f"{distancia:.1f} km · {atenuacion:.2f} dB/km", fontsize=12, ha='center', color='white')

    ax_gpon.scatter(*splitter_pos, s=1000, color='#FFA000', zorder=5)
    ax_gpon.text(splitter_pos[0], splitter_pos[1]-0.1, f"Splitter\n1:{usuarios}", fontsize=12, fontweight='bold', color='white', ha='center', va='center')
    ax_gpon.text(splitter_pos[0], splitter_pos[1]+0.9,
                 f"Split: {split_loss:.2f} dB\nExtra: {perdidas_extra:.1f} dB",
                 fontsize=12, ha='center', color='white',
                 bbox=dict(boxstyle="round,pad=0.25", facecolor='#2d2d2d', alpha=0.85, edgecolor='white'))

    for pos in onu_positions:
        ax_gpon.scatter(*pos, s=700, color='#43A047', zorder=5)
        ax_gpon.text(pos[0]-0.4, pos[1]-0.3, "ONU", fontsize=14, fontweight='bold', color='white')
        ax_gpon.plot([splitter_pos[0], pos[0]], [splitter_pos[1], pos[1]], color=color_enlace, linewidth=2, linestyle='--', zorder=1)

    if usuarios > num_onus_dibujadas:
        ax_gpon.text(8.7, -0.2, f"(+{usuarios - num_onus_dibujadas} ONUs\nmás, no dibujadas)",
                     fontsize=11, style='italic', ha='center', color='lightgray')

    ax_gpon.text(9.7, 2.5, f"P_RX ONT ≈\n{rx_ont:.2f} dBm\nP_RX OLT ≈\n{rx_olt:.2f} dBm",
                 fontsize=12, ha='center', fontweight='bold', color='white',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=color_enlace, alpha=0.25, edgecolor='white'))

    icono_estado = "✅" if enlace_ok else "❌"
    ax_gpon.set_title(f"Red GPON con {usuarios} usuarios — enlace {icono_estado}", fontsize=16, color='white')
    fig_gpon.tight_layout()
    st.pyplot(fig_gpon, use_container_width=True)

    # Botones finales
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📄 Generar PDF con estos resultados (GPON)", use_container_width=True):
            parametros = {
                "Potencia OLT": f"{pot_olt} dBm",
                "Sensibilidad ONT": f"{sens_ont} dBm",
                "Potencia ONT": f"{pot_ont} dBm",
                "Sensibilidad OLT": f"{sens_olt} dBm",
                "Distancia": f"{distancia} km",
                "Atenuación": f"{atenuacion} dB/km",
                "Usuarios": usuarios,
                "Pérdidas extra": f"{perdidas_extra} dB"
            }
            resultados = {
                "Potencia recibida ONT": f"{rx_ont:.2f} dBm",
                "Potencia recibida OLT": f"{rx_olt:.2f} dBm",
                "Distancia máx. DL": f"{dmax_dl:.2f} km",
                "Distancia máx. UL": f"{dmax_ul:.2f} km",
                "Distancia máx. sistema": f"{dmax_sistema:.2f} km",
                "Enlace válido": "Sí" if enlace_ok else "No"
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


# ------------------------------------------------------------
# Módulo Mobile Planner
# ------------------------------------------------------------
elif modulo == "📶 Mobile Planner":
    st.header("📶 Mobile Planner")
    st.markdown("Calcula la interferencia cocanal en redes celulares.")

    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.write("""
        **Modo estándar:** Define el factor de reuso N, la constante de propagación γ y el tipo de celda
        (omnidireccional o sectorizada). La herramienta calcula la C/I resultante y dibuja el patrón de celdas.

        **Nuevo:**
        - **Distancias personalizadas:** introduce manualmente las distancias a los interferentes (como en el inciso a del examen) y obtén la C/I exacta.
        - **Erlang B:** calcula la probabilidad de bloqueo y el número de canales necesarios para un tráfico dado (útil para los incisos b y c).
        """)

    pestaña = st.radio("Selecciona una opción", ["Modo estándar (N, γ)", "Distancias personalizadas", "Calculadora Erlang B"])

    # ---- Modo estándar ----
    if pestaña == "Modo estándar (N, γ)":
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
            st.markdown('<div class="warning-box" style="color: #b26a00;">⚠️ Calidad aceptable: C/I entre 12 y 18 dB, se pueden usar modulaciones robustas.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box" style="color: #b71c1c;">❌ Calidad insuficiente: C/I < 12 dB, riesgo de errores.</div>', unsafe_allow_html=True)

        st.subheader("🔷 Patrón de celdas interferentes")
        fig, ax = plt.subplots(figsize=(18, 8))
        fig.patch.set_facecolor('#2d2d2d')
        ax.set_facecolor('#2d2d2d')

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
        ax.set_title(f"Reuso N={N} | D/R = {DR:.2f}", fontsize=16, color='white')
        ax.legend(loc='upper right', fontsize=12, facecolor='#2d2d2d', edgecolor='white', labelcolor='white')
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

        st.subheader("📈 Evolución de C/I con el factor de reutilización")
        Ns = [1, 3, 4, 7, 12, 19]
        ci_db_values = []
        for n in Ns:
            if tipo_celda.startswith("Omnidireccional"):
                _, value = ci_omnidirectional(n, gamma)
            elif tipo_celda.startswith("Sectorizada 120"):
                _, value = ci_sectorized_120(n, gamma)
            else:
                _, value = ci_sectorized_60(n, gamma)
            ci_db_values.append(value)

        fig_ci, ax_ci = plt.subplots(figsize=(18, 8))
        fig_ci.patch.set_facecolor('#2d2d2d')
        ax_ci.set_facecolor('#2d2d2d')
        ax_ci.plot(Ns, ci_db_values, marker="o", linewidth=3, markersize=8, color='#FFA000')
        ax_ci.axhline(18, linestyle="--", color="red", label="18 dB")
        ax_ci.set_xlabel("Factor de reutilización N", fontsize=14, color='white')
        ax_ci.set_ylabel("C/I (dB)", fontsize=14, color='white')
        ax_ci.set_title("Calidad de señal según N", fontsize=16, color='white')
        ax_ci.grid(True, linestyle=":", color='gray')
        ax_ci.legend(loc='best', fontsize=12, facecolor='#2d2d2d', edgecolor='white', labelcolor='white')
        ax_ci.tick_params(colors='white')
        for spine in ax_ci.spines.values():
            spine.set_color('white')
        fig_ci.tight_layout()
        st.pyplot(fig_ci, use_container_width=True)

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

    # ---- Distancias personalizadas ----
    elif pestaña == "Distancias personalizadas":
        st.subheader("🔍 Cálculo de C/I con distancias a los interferentes")
        st.markdown("Introduce las distancias (en múltiplos de R) a cada interferente que consideres en el peor caso.")
        gamma = st.slider("Constante de propagación γ", 2.0, 5.0, 2.0, 0.1, key="gamma_custom")
        num_interf = st.number_input("Número de interferentes", min_value=1, max_value=10, value=3, step=1)
        distancias = []
        for i in range(num_interf):
            d = st.number_input(f"D{i+1} (·R)", min_value=0.1, max_value=20.0, value=2.0 if i==0 else (3.0 if i==1 else 4.0), step=0.1, key=f"d_{i}")
            distancias.append(d)

        if st.button("Calcular C/I", use_container_width=True):
            ci, ci_db = ci_custom_distances(distancias, gamma)
            st.metric("C/I (lineal)", f"{ci:.4f}")
            st.metric("C/I (dB)", f"{ci_db:.2f} dB")
            formula = f"$C/I = \\frac{{1}}{{\\sum 1/D_i^{gamma}}} = \\frac{{1}}{{\\sum 1/({', '.join([str(d) for d in distancias])})^{gamma}}} = {ci:.4f}$"
            st.markdown(formula)
            if ci_db >= 18:
                st.success("Excelente calidad (> 18 dB)")
            elif ci_db >= 12:
                st.markdown('<div class="warning-box" style="color: #b26a00;">⚠️ Calidad aceptable (12-18 dB)</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box" style="color: #b71c1c;">❌ Calidad insuficiente (< 12 dB)</div>', unsafe_allow_html=True)

    # ---- Calculadora Erlang B ----
    elif pestaña == "Calculadora Erlang B":
        st.subheader("📊 Erlang B Calculator")
        st.markdown("Calcula la probabilidad de bloqueo o el número de canales necesarios para un tráfico dado.")

        col1, col2 = st.columns(2)
        with col1:
            trafico = st.slider("Tráfico ofrecido (Erlangs)", 0.1, 50.0, 8.0, 0.1)
            canales = st.slider("Número de canales", 1, 50, 15, 1)
            pb = erlang_b(trafico, canales)
            st.metric("Probabilidad de bloqueo", f"{pb*100:.4f}%")
        with col2:
            pb_objetivo = st.slider("Pb objetivo (%)", 0.1, 20.0, 1.0, 0.1) / 100
            C_min = canales_para_erlang(trafico, pb_objetivo)
            if C_min:
                st.metric("Canales mínimos necesarios", C_min)
            else:
                st.markdown('<div class="warning-box" style="color: #b26a00;">⚠️ No se encontró solución en el rango (máx 50 canales).</div>', unsafe_allow_html=True)

        st.subheader("📋 Tabla de Erlang B (Pb vs canales)")
        canales_lista = list(range(1, 21))
        pbs = [erlang_b(trafico, C) for C in canales_lista]
        df = pd.DataFrame({"Canales": canales_lista, "Pb": [f"{p*100:.4f}%" for p in pbs]})
        st.dataframe(df)


# ------------------------------------------------------------
# Módulo Queue Simulator
# ------------------------------------------------------------
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
        st.markdown('<div class="error-box" style="color: #b71c1c;">⚠️ Cuidado: λ ≥ μ, el sistema es inestable. Aumenta μ o baja λ.</div>', unsafe_allow_html=True)
        st.stop()
    else:
        rho, W, L, Wq, Lq = mm1_metrics(lam, mu)

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
            st.markdown('<div class="warning-box" style="color: #b26a00;">🟡 Ocupación moderada: retrasos razonables.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box" style="color: #b26a00;">🔴 Sistema saturado: muchos retrasos, mejor aumentar μ.</div>', unsafe_allow_html=True)

        st.subheader("📈 Probabilidad de cada estado")
        max_n = 20
        probs = [(1-rho) * (rho**n) for n in range(max_n+1)]
        fig, ax = plt.subplots(figsize=(18, 8))
        fig.patch.set_facecolor('#2d2d2d')
        ax.set_facecolor('#2d2d2d')
        ax.bar(range(max_n+1), probs, color='#1E88E5', alpha=0.7)
        ax.set_xlabel("Número de clientes (n)", fontsize=14, color='white')
        ax.set_ylabel("Probabilidad πₙ", fontsize=14, color='white')
        ax.grid(True, alpha=0.3, color='gray')
        ax.set_title("Distribución estacionaria M/M/1", fontsize=16, color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

        st.subheader("📈 Sensibilidad del sistema frente a λ")
        arrival_rates = np.linspace(0.1, mu - 0.1, 150)
        waiting_times = [1 / (mu - l) for l in arrival_rates]

        fig_wait, ax_wait = plt.subplots(figsize=(18, 8))
        fig_wait.patch.set_facecolor('#2d2d2d')
        ax_wait.set_facecolor('#2d2d2d')
        ax_wait.plot(arrival_rates, waiting_times, linewidth=3, color="#FF9800")
        ax_wait.axvline(lam, linestyle="--", color="red", label=f"λ actual = {lam}")
        ax_wait.set_xlabel("Tasa de llegada λ", fontsize=14, color='white')
        ax_wait.set_ylabel("Tiempo medio W (s)", fontsize=14, color='white')
        ax_wait.set_title("Crecimiento del retardo al acercarse a saturación", fontsize=16, color='white')
        ax_wait.grid(True, linestyle=":", color='gray')
        ax_wait.legend(loc='best', fontsize=12, facecolor='#2d2d2d', edgecolor='white', labelcolor='white')
        ax_wait.tick_params(colors='white')
        for spine in ax_wait.spines.values():
            spine.set_color('white')
        fig_wait.tight_layout()
        st.pyplot(fig_wait, use_container_width=True)

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


# ------------------------------------------------------------
# Módulo ICT Designer (revisado y con comentarios clarificadores)
# ------------------------------------------------------------
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

        **Importante:** la cabecera está en la parte superior del edificio. La planta 1 es la más baja.
        El cálculo empieza desde la planta más alta (la última) y va bajando, acumulando pérdidas de
        cable y de paso de los derivadores.
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

    # --- Cálculo de niveles (de arriba hacia abajo) ---
    niveles = []
    perdida_acumulada = 0
    dist_cabecera_planta_alta = 5   # distancia desde la cabecera hasta la planta más alta

    # Recorremos las plantas en orden inverso: desde la más alta (índice plantas-1) hasta la baja (índice 0)
    for i in range(plantas-1, -1, -1):
        if i == plantas-1:
            # Primera planta que se calcula (la más alta): el cable viene directamente de la cabecera
            dist_cable = dist_cabecera_planta_alta
        else:
            # Para el resto: el cable viene de la planta superior (distancia entre plantas)
            dist_cable = dist_entre_plantas

        perdida_cable = dist_cable * atenuacion_cable
        deriv = derivador_por_planta[i]

        # Señal que llega al derivador de esta planta
        señal_entrada_deriv = nivel_salida_amp - perdida_acumulada - perdida_cable

        # Señal en la toma (restando derivación, PAU, toma y distribuidor)
        señal_toma = señal_entrada_deriv - deriv["AD"] - perdida_pau - perdida_toma - perdida_distribuidor

        niveles.append(señal_toma)

        # Acumulamos pérdidas para la siguiente planta (la de más abajo):
        # la pérdida de paso del derivador actual + el cable que hemos recorrido.
        perdida_acumulada += deriv["AP"] + perdida_cable

    # Los niveles están de la planta más alta a la más baja; los invertimos para que
    # el índice 0 corresponda a la planta 1 (la más baja).
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
        st.markdown('<div class="error-box" style="color: #b71c1c;">❌ Alguna planta no cumple. Prueba a cambiar los derivadores o añadir un amplificador intermedio.</div>', unsafe_allow_html=True)

    # --- Esquema gráfico (planta 1 abajo, planta N arriba) ---
    st.subheader("🏗️ Esquema de la red de distribución")
    fig_ict, ax_ict = plt.subplots(figsize=(18, 8))
    fig_ict.patch.set_facecolor('#2d2d2d')
    ax_ict.set_facecolor('#2d2d2d')
    ax_ict.set_xlim(-2, 8)
    ax_ict.set_ylim(-1, plantas + 1)
    ax_ict.axis('off')

    # Línea vertical del cable principal (desde la cabecera hasta la planta baja)
    ax_ict.plot([0, 0], [0, plantas + 1], color='white', linewidth=4, zorder=1)

    # Cabecera (amplificador) en la parte superior
    ax_ict.scatter(0, plantas + 0.5, s=400, color='#1E88E5', zorder=5, edgecolors='white', linewidth=2)
    ax_ict.text(0.2, plantas + 0.5, f"AMP\n{nivel_salida_amp} dBµV", fontsize=10, ha='left', va='center', fontweight='bold', color='white')

    # Dibujar cada planta: la planta 1 (i=0) se coloca en la parte inferior (y=0.5),
    # la planta N (i=plantas-1) en la parte superior (y=plantas-0.5)
    for i in range(plantas):
        # Índice i=0 corresponde a la planta 1 (la más baja)
        y_pos = i + 0.5   # Planta 1 abajo, planta N arriba
        nivel = niveles[i]
        deriv = derivador_por_planta[i]
        color = '#43A047' if nivel_min <= nivel <= nivel_max else '#E53935'

        # Conexión desde el cable principal hasta el derivador
        ax_ict.plot([0, 2.5], [y_pos, y_pos], color='gray', linewidth=2, zorder=1)

        # Derivador
        ax_ict.scatter(2.5, y_pos, s=250, color='#FFA000', zorder=5, edgecolors='white')
        ax_ict.text(2.7, y_pos, f"Planta {i+1}\nAD={deriv['AD']}dB", fontsize=9, ha='left', va='center', color='white', bbox=dict(boxstyle="round,pad=0.2", facecolor='#2d2d2d', alpha=0.7, edgecolor='white'))

        # Toma de usuario
        ax_ict.scatter(5.5, y_pos, s=150, color=color, zorder=5, edgecolors='white')
        ax_ict.text(5.7, y_pos, f"{nivel:.1f} dBµV", fontsize=10, ha='left', va='center', fontweight='bold', color='white')

        # Conexión derivador -> toma
        ax_ict.plot([2.5, 5.5], [y_pos, y_pos], color='gray', linewidth=1.5, linestyle=':', zorder=1)

        # Flecha hacia la siguiente planta (solo si no es la última)
        if i < plantas - 1:
            ax_ict.annotate('', xy=(0, y_pos + 1), xytext=(0, y_pos + 0.5), arrowprops=dict(arrowstyle='->', color='white', lw=1))

    # Leyenda
    ax_ict.scatter([], [], s=150, color='#43A047', label='Cumple normativa')
    ax_ict.scatter([], [], s=150, color='#E53935', label='Fuera de rango')
    ax_ict.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=10, facecolor='#2d2d2d', edgecolor='white', labelcolor='white')
    ax_ict.set_title("Topología de la red de distribución (ICT)", fontsize=14, fontweight='bold', color='white')
    ax_ict.set_ylim(-0.5, plantas + 1)
    fig_ict.tight_layout()
    st.pyplot(fig_ict, use_container_width=True)

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


# ------------------------------------------------------------
# Pie de página (común)
# ------------------------------------------------------------
st.markdown("---")
st.caption("TelecomLab · Versión 2.0 · Universidad de Granada")