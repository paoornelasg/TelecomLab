# ------------------------------------------------------------
# Funciones de cálculo para TelecomLab
# ------------------------------------------------------------

import math


def db_to_linear(db):
    """Convierte dB a factor lineal (10^(dB/10))"""
    return 10 ** (db / 10)


def linear_to_db(value):
    """Convierte un factor lineal a dB (10*log10(value))"""
    if value <= 0:
        raise ValueError("El valor lineal debe ser mayor que cero.")
    return 10 * math.log10(value)


def splitter_loss(users):
    """Pérdida de un splitter óptico ideal (1:N) en dB"""
    if users <= 0:
        raise ValueError("El número de usuarios debe ser mayor que cero.")
    return 10 * math.log10(users)


def received_power(tx_power, distance, attenuation, users, extra_losses):
    """
    Calcula la potencia recibida en un enlace GPON.
    - tx_power: potencia transmitida (dBm)
    - distance: longitud de fibra (km)
    - attenuation: atenuación de la fibra (dB/km)
    - users: número de usuarios (split)
    - extra_losses: pérdidas adicionales (conectores, empalmes...)
    """
    split_loss = splitter_loss(users)
    losses = attenuation * distance + split_loss + extra_losses
    return tx_power - losses


def max_distance(tx_power, sensitivity, attenuation, users, extra_losses):
    """
    Distancia máxima que permite el presupuesto de potencia.
    Se asume que la potencia recibida no debe ser inferior a la sensibilidad.
    """
    if attenuation <= 0:
        raise ValueError("La atenuación debe ser mayor que cero.")
    split_loss = splitter_loss(users)
    budget = tx_power - sensitivity - split_loss - extra_losses
    return budget / attenuation


# ------------------------------------------------------------
# Cálculo de C/I en redes celulares
# ------------------------------------------------------------

def ci_omnidirectional(N, gamma):
    """C/I para celdas omnidireccionales (6 interferentes)"""
    ci = ((math.sqrt(3 * N)) ** gamma) / 6
    return ci, 10 * math.log10(ci)


def ci_sectorized_120(N, gamma):
    """C/I con sectorización de 120° (2 interferentes)"""
    ci = 0.5 * ((math.sqrt(3 * N)) ** gamma)
    return ci, 10 * math.log10(ci)


def ci_sectorized_60(N, gamma):
    """C/I con sectorización de 60° (1 interferente)"""
    ci = (math.sqrt(3 * N)) ** gamma
    return ci, 10 * math.log10(ci)


def ci_custom_distances(distances, gamma=2):
    """
    C/I con distancias arbitrarias a los interferentes.
    - distances: lista de distancias normalizadas (D_i / R)
    - gamma: exponente de propagación
    """
    if not distances:
        raise ValueError("Debe haber al menos un interferente.")
    if any(d <= 0 for d in distances):
        raise ValueError("Todas las distancias deben ser mayores que cero.")
    interference = sum(1 / (d ** gamma) for d in distances)
    ci = 1 / interference
    return ci, 10 * math.log10(ci)


# ------------------------------------------------------------
# Selección de modulación / potencia mínima de transmisión
# ------------------------------------------------------------

def modulacion_minima(modulaciones, bitrate_total_mbps, perdidas_db, psd_ruido_dbm_hz):
    """
    Calcula, para cada modulación de la lista, el ancho de banda necesario y la
    potencia de transmisión mínima requerida para alcanzar 'bitrate_total_mbps'
    Mbps con unas pérdidas de enlace 'perdidas_db' y una densidad espectral de
    ruido (o ruido+interferencia) 'psd_ruido_dbm_hz' (dBm/Hz, constante en la
    banda usada).

    - modulaciones: lista de tuplas (nombre, M, snr_min_dB), p.ej.
      [("16-QAM", 16, 21.5), ("8-QAM", 8, 18), ("4-QAM", 4, 14.5)]

    Devuelve una lista de dicts (mismo orden de entrada) con 'nombre', 'M',
    'bw_mhz' y 'potencia_dbm' (potencia de Tx necesaria, en dBm).

    Fórmula: P_tx = SNR_min + Pérdidas + N, con N = PSD + 10*log10(BW).
    """
    if bitrate_total_mbps <= 0:
        raise ValueError("El bitrate total debe ser mayor que cero.")
    resultados = []
    for nombre, M, snr_min in modulaciones:
        bw_hz = (bitrate_total_mbps * 1e6) / math.log2(M)
        ruido_dbm = psd_ruido_dbm_hz + 10 * math.log10(bw_hz)
        potencia_dbm = snr_min + perdidas_db + ruido_dbm
        resultados.append({
            "nombre": nombre,
            "M": M,
            "bw_mhz": bw_hz / 1e6,
            "potencia_dbm": potencia_dbm,
        })
    return resultados


def mejor_modulacion(modulaciones, bitrate_total_mbps, perdidas_db, psd_ruido_dbm_hz, potencia_max):
    """
    Recorre 'modulaciones' (debe ir de mayor a menor orden M, para minimizar
    el ancho de banda) y devuelve el primer resultado cuya potencia requerida
    no supere 'potencia_max'. Si ninguna modulación cumple, devuelve None.
    """
    for r in modulacion_minima(modulaciones, bitrate_total_mbps, perdidas_db, psd_ruido_dbm_hz):
        if r["potencia_dbm"] <= potencia_max:
            return r
    return None


# ------------------------------------------------------------
# Cola M/M/1
# ------------------------------------------------------------

def mm1_metrics(lam, mu):
    """
    Métricas de una cola M/M/1.
    - lam: tasa de llegadas (clientes/segundo)
    - mu: tasa de servicio (clientes/segundo)
    Devuelve: (rho, W, L, Wq, Lq)
    """
    if lam <= 0:
        raise ValueError("λ debe ser mayor que cero.")
    if mu <= 0:
        raise ValueError("μ debe ser mayor que cero.")
    if lam >= mu:
        raise ValueError("Sistema inestable: λ debe ser menor que μ.")

    rho = lam / mu
    W = 1 / (mu - lam)
    L = lam * W
    Wq = W - (1 / mu)
    Lq = lam * Wq
    return rho, W, L, Wq, Lq


# ------------------------------------------------------------
# Fórmula de Erlang B (con recurrencia)
# ------------------------------------------------------------

def erlang_b(A, C):
    """
    Probabilidad de bloqueo para un sistema con C canales
    y tráfico ofrecido A (Erlangs).
    """
    if A <= 0:
        raise ValueError("El tráfico ofrecido A debe ser mayor que cero.")
    if C == 0:
        return 1.0
    inv = 1.0
    for i in range(1, C + 1):
        inv = 1.0 + (i / A) * inv
    return 1.0 / inv


def canales_para_erlang(A, pb_objetivo, max_canales=50):
    """
    Devuelve el número mínimo de canales necesarios para que
    la probabilidad de bloqueo sea <= pb_objetivo.
    """
    for C in range(1, max_canales + 1):
        if erlang_b(A, C) <= pb_objetivo:
            return C
    return None