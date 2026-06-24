# ------------------------------------------------------------
# Pruebas unitarias para utils/calculations.py
# ------------------------------------------------------------
# Se pueden ejecutar con:  python test_calculations.py
# O con pytest:           pytest test_calculations.py -v
# ------------------------------------------------------------

import math
from utils.calculations import (
    db_to_linear,
    linear_to_db,
    splitter_loss,
    received_power,
    max_distance,
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


def assert_close(actual, expected, tol=0.01, msg=""):
    """Comprueba que dos números son aproximadamente iguales."""
    assert abs(actual - expected) <= tol, (
        f"{msg}: se esperaba {expected}, se obtuvo {actual} "
        f"(diferencia {abs(actual - expected)} > tolerancia {tol})"
    )


# ------------------------------------------------------------
# Conversiones dB <-> lineal
# ------------------------------------------------------------

def test_db_to_linear_y_linear_to_db_son_inversas():
    # 20 dB = factor 100 en lineal
    assert_close(db_to_linear(20), 100.0, msg="db_to_linear(20)")
    # Inversa: 10*log10(100) = 20 dB
    assert_close(linear_to_db(100.0), 20.0, msg="linear_to_db(100)")


def test_linear_to_db_rechaza_valores_no_positivos():
    try:
        linear_to_db(0)
        raise AssertionError("Debería haber lanzado ValueError para valor <= 0")
    except ValueError:
        pass


# ------------------------------------------------------------
# Splitter óptico
# ------------------------------------------------------------

def test_splitter_loss_64_usuarios():
    # Splitter 1:64 -> 10*log10(64) = 18.0618 dB
    assert_close(splitter_loss(64), 18.0618, tol=0.001, msg="splitter_loss(64)")


def test_splitter_loss_rechaza_cero_usuarios():
    try:
        splitter_loss(0)
        raise AssertionError("Debería haber lanzado ValueError para users<=0")
    except ValueError:
        pass


# ------------------------------------------------------------
# Presupuesto de enlace GPON (ejemplo del examen)
# ------------------------------------------------------------

def test_max_distance_caso_examen_gpon():
    # Datos: P_TX=22 dBm, sensibilidad=-30 dBm, fibra 0.5 dB/km,
    # splitter 1:64 (18.06 dB), pérdidas extra 2 dB.
    # Presupuesto = 22 - (-30) - 18.0618 - 2 = 31.9382 dB
    # Distancia = 31.9382 / 0.5 = 63.876 km
    d = max_distance(
        tx_power=22, sensitivity=-30, attenuation=0.5, users=64, extra_losses=2
    )
    assert_close(d, 63.876, tol=0.01, msg="max_distance (caso examen GPON)")


def test_received_power_en_la_distancia_maxima_iguala_la_sensibilidad():
    # En el límite, la potencia recibida debe ser igual a la sensibilidad.
    sensitivity = -30
    d = max_distance(
        tx_power=22, sensitivity=sensitivity, attenuation=0.5, users=64, extra_losses=2
    )
    p_rx = received_power(
        tx_power=22, distance=d, attenuation=0.5, users=64, extra_losses=2
    )
    assert_close(p_rx, sensitivity, tol=0.01, msg="potencia recibida en distancia máxima")


def test_max_distance_rechaza_atenuacion_no_positiva():
    try:
        max_distance(tx_power=22, sensitivity=-30, attenuation=0, users=64, extra_losses=2)
        raise AssertionError("Debería haber lanzado ValueError para attenuation<=0")
    except ValueError:
        pass


# ------------------------------------------------------------
# C/I estándar (omnidireccional, sectorizada 120°, 60°)
# ------------------------------------------------------------

def test_ci_omnidireccional_N7_gamma4():
    # Para N=7, gamma=4: (√(3*7))^4 / 6 = 441/6 = 73.5 -> 18.66 dB
    ci, ci_db = ci_omnidirectional(7, 4)
    assert_close(ci, 73.5, tol=0.1, msg="ci_omnidirectional lineal")
    assert_close(ci_db, 18.66, tol=0.05, msg="ci_omnidirectional dB")


def test_ci_sectorizado_120_N7_gamma4():
    # (√(3*7))^4 / 2 = 441/2 = 220.5 -> 23.43 dB
    ci, ci_db = ci_sectorized_120(7, 4)
    assert_close(ci, 220.5, tol=0.1, msg="ci_sectorized_120 lineal")
    assert_close(ci_db, 23.43, tol=0.05, msg="ci_sectorized_120 dB")


def test_ci_sectorizado_60_N7_gamma4():
    # (√(3*7))^4 = 441 -> 26.44 dB
    ci, ci_db = ci_sectorized_60(7, 4)
    assert_close(ci, 441.0, tol=0.1, msg="ci_sectorized_60 lineal")
    assert_close(ci_db, 26.44, tol=0.05, msg="ci_sectorized_60 dB")


def test_sectorizar_siempre_mejora_la_ci():
    # Con menos interferentes, la C/I no debe empeorar.
    ci_omni, _ = ci_omnidirectional(7, 4)
    ci_120, _ = ci_sectorized_120(7, 4)
    ci_60, _ = ci_sectorized_60(7, 4)
    assert ci_60 >= ci_120 >= ci_omni, "Sectorizar más debería dar igual o mejor C/I"


# ------------------------------------------------------------
# C/I con distancias personalizadas (inciso a del examen móvil)
# ------------------------------------------------------------

def test_ci_custom_distances_examen_gamma2():
    # D1 = 2R, D2 = √37 R, gamma=2
    # C/I = 1 / (1/4 + 1/37) = 3.6097 -> 5.574 dB
    ci, ci_db = ci_custom_distances([2, math.sqrt(37)], gamma=2)
    assert_close(ci, 3.6097, tol=0.001, msg="ci_custom_distances lineal (examen)")
    assert_close(ci_db, 5.574, tol=0.01, msg="ci_custom_distances dB (examen)")


def test_ci_custom_distances_con_gamma4():
    # Con gamma=4: 1 / (1/16 + 1/37^2) = 15.815 -> 11.99 dB
    ci, ci_db = ci_custom_distances([2, math.sqrt(37)], gamma=4)
    assert_close(ci, 15.815, tol=0.01, msg="ci_custom_distances gamma=4")
    assert_close(ci_db, 11.99, tol=0.02, msg="ci_custom_distances dB gamma=4")


def test_ci_custom_distances_con_un_solo_interferente():
    # Con un solo interferente a distancia 3R: C/I = 3^2 = 9
    ci, ci_db = ci_custom_distances([3], gamma=2)
    assert_close(ci, 9.0, msg="ci_custom_distances un interferente")
    assert_close(ci_db, 10 * math.log10(9), tol=0.01, msg="ci_custom_distances dB un interferente")


# ------------------------------------------------------------
# Erlang B (valores calculados con la recursión exacta)
# ------------------------------------------------------------

def test_erlang_b_caso_examen_C1_A8():
    # A=8 Erlangs
    assert_close(erlang_b(8, 10), 0.1217, tol=0.001, msg="Erlang B(8,10)")
    assert_close(erlang_b(8, 11), 0.0813, tol=0.001, msg="Erlang B(8,11)")
    assert_close(erlang_b(8, 12), 0.0514, tol=0.001, msg="Erlang B(8,12)")
    assert_close(erlang_b(8, 13), 0.0307, tol=0.001, msg="Erlang B(8,13)")
    assert_close(erlang_b(8, 14), 0.0172, tol=0.001, msg="Erlang B(8,14)")   # ≤2%
    assert_close(erlang_b(8, 15), 0.0091, tol=0.001, msg="Erlang B(8,15)")   # ≤1%
    assert_close(erlang_b(8, 16), 0.0045, tol=0.001, msg="Erlang B(8,16)")   # ≤0.5%


def test_erlang_b_caso_examen_C2_A4():
    # A=4 Erlangs
    assert_close(erlang_b(4, 5), 0.1991, tol=0.001, msg="Erlang B(4,5)")
    assert_close(erlang_b(4, 6), 0.1172, tol=0.001, msg="Erlang B(4,6)")
    assert_close(erlang_b(4, 7), 0.0628, tol=0.001, msg="Erlang B(4,7)")
    assert_close(erlang_b(4, 8), 0.0304, tol=0.001, msg="Erlang B(4,8)")
    assert_close(erlang_b(4, 9), 0.0133, tol=0.001, msg="Erlang B(4,9)")
    assert_close(erlang_b(4, 10), 0.0053, tol=0.001, msg="Erlang B(4,10)")


def test_erlang_b_caso_examen_C3_A2():
    # A=2 Erlangs
    assert_close(erlang_b(2, 4), 0.0952, tol=0.001, msg="Erlang B(2,4)")
    assert_close(erlang_b(2, 5), 0.0367, tol=0.001, msg="Erlang B(2,5)")
    assert_close(erlang_b(2, 6), 0.0121, tol=0.001, msg="Erlang B(2,6)")
    assert_close(erlang_b(2, 7), 0.0034, tol=0.001, msg="Erlang B(2,7)")
    assert_close(erlang_b(2, 8), 0.00086, tol=0.001, msg="Erlang B(2,8)")
    assert_close(erlang_b(2, 9), 0.00019, tol=0.001, msg="Erlang B(2,9)")


# ------------------------------------------------------------
# canales_para_erlang
# ------------------------------------------------------------

def test_canales_para_erlang_A8():
    assert canales_para_erlang(8, 0.02) == 14, "A=8, Pb≤2% -> 14 canales"
    assert canales_para_erlang(8, 0.01) == 15, "A=8, Pb≤1% -> 15 canales"
    assert canales_para_erlang(8, 0.005) == 16, "A=8, Pb≤0.5% -> 16 canales"
    assert canales_para_erlang(8, 0.15) == 10, "A=8, Pb≤15% -> 10 canales"


def test_canales_para_erlang_A4():
    # B(9)=0.0133 ≤0.02, B(10)=0.0053 >0.005, B(11)=0.00192 ≤0.005
    assert canales_para_erlang(4, 0.02) == 9, "A=4, Pb≤2% -> 9 canales"
    assert canales_para_erlang(4, 0.005) == 11, "A=4, Pb≤0.5% -> 11 canales"


def test_canales_para_erlang_A2():
    # B(6)=0.0121 ≤0.02, B(5)=0.0367 >0.02 -> para 2% mínimo 6
    # B(6)=0.0121 >0.005, B(7)=0.0034 ≤0.005 -> para 0.5% mínimo 7
    assert canales_para_erlang(2, 0.02) == 6, "A=2, Pb≤2% -> 6 canales"
    assert canales_para_erlang(2, 0.005) == 7, "A=2, Pb≤0.5% -> 7 canales"


# ------------------------------------------------------------
# Cola M/M/1
# ------------------------------------------------------------

def test_mm1_metrics_lambda4_mu6():
    # λ=4, μ=6
    rho, W, L, Wq, Lq = mm1_metrics(4, 6)
    assert_close(rho, 0.6667, tol=0.001, msg="rho")
    assert_close(W, 0.5, tol=0.001, msg="W")
    assert_close(L, 2.0, tol=0.001, msg="L")
    assert_close(Wq, 0.3333, tol=0.001, msg="Wq")
    assert_close(Lq, 1.3333, tol=0.001, msg="Lq")


def test_mm1_metrics_little_law_se_cumple():
    # Comprobación de la ley de Little: L = λ·W, Lq = λ·Wq
    lam, mu = 3, 5
    rho, W, L, Wq, Lq = mm1_metrics(lam, mu)
    assert_close(L, lam * W, tol=1e-9, msg="Ley de Little: L = lambda*W")
    assert_close(Lq, lam * Wq, tol=1e-9, msg="Ley de Little en cola: Lq = lambda*Wq")


def test_mm1_metrics_rechaza_sistema_inestable():
    # λ >= μ debe lanzar ValueError
    try:
        mm1_metrics(6, 6)
        raise AssertionError("Debería haber lanzado ValueError para lambda >= mu")
    except ValueError:
        pass

    try:
        mm1_metrics(8, 6)
        raise AssertionError("Debería haber lanzado ValueError para lambda > mu")
    except ValueError:
        pass


# ------------------------------------------------------------
# Ejercicio examen GPON
# ------------------------------------------------------------

def test_examen_gpon_apartado_a_distancia_maxima():
    # Downlink: P_OLT=30dBm, S_ONT=-25dBm, splitter 1:64, 2dB extra, 0.5dB/km
    # -> 69.87 km (valor exacto del examen)
    d_dl = max_distance(tx_power=30, sensitivity=-25, attenuation=0.5, users=64, extra_losses=2)
    assert_close(d_dl, 69.87, tol=0.01, msg="GPON examen a) D_max downlink")

    # Uplink: P_ONT=22dBm, S_OLT=-30dBm, SIN splitter (TDMA), 2dB extra -> 100 km
    # Se reutiliza max_distance con users=1 (splitter_loss(1) = 0 dB).
    d_ul = max_distance(tx_power=22, sensitivity=-30, attenuation=0.5, users=1, extra_losses=2)
    assert_close(d_ul, 100.0, tol=0.01, msg="GPON examen a) D_max uplink")

    # La distancia máxima del sistema es la más restrictiva (el downlink)
    assert_close(min(d_dl, d_ul), 69.87, tol=0.01, msg="GPON examen a) D_max sistema")


def test_examen_gpon_apartado_b_modulacion_downlink():
    # d=8km, 40 Mbps/usuario, 64 usuarios -> 2.56 Gbps totales
    # L_DL = 10*log10(64) + 2 + 0.5*8 = 24.06 dB ; solo ruido (-100 dBm/Hz)
    perdidas_dl = splitter_loss(64) + 2 + 0.5 * 8
    modulaciones = [("16-QAM", 16, 21.5), ("8-QAM", 8, 18), ("4-QAM", 4, 14.5)]
    resultado = mejor_modulacion(modulaciones, 40 * 64, perdidas_dl, -100.0, potencia_max=30)

    # Se descartan 16-QAM (33.62 dBm) y 8-QAM (31.36 dBm) por exceder
    # los 30 dBm máximos de la OLT, y elige 4-QAM con 29.63 dBm.
    assert resultado is not None, "Debería existir una modulación válida (4-QAM)"
    assert resultado["nombre"] == "4-QAM", "El examen elige 4-QAM para minimizar BW dentro del presupuesto"
    assert_close(resultado["bw_mhz"], 1280.0, tol=0.5, msg="GPON examen b) BW de 4-QAM")
    assert_close(resultado["potencia_dbm"], 29.63, tol=0.05, msg="GPON examen b) potencia mínima OLT")

    # Comprobamos también que 16-QAM y 8-QAM efectivamente superan el máximo
    todas = modulacion_minima(modulaciones, 40 * 64, perdidas_dl, -100.0)
    pot_por_nombre = {r["nombre"]: r["potencia_dbm"] for r in todas}
    assert_close(pot_por_nombre["16-QAM"], 33.62, tol=0.05, msg="GPON examen b) 16-QAM (no válida)")
    assert_close(pot_por_nombre["8-QAM"], 31.36, tol=0.1, msg="GPON examen b) 8-QAM (no válida)")


def test_examen_gpon_apartado_c_modulacion_uplink():
    # d=8km, 20 Mbps/usuario, 64 usuarios -> 1.28 Gbps totales
    # L_UL = 2 + 0.5*8 = 6 dB ; ruido + interferencia combinados
    perdidas_ul = 2 + 0.5 * 8
    psd_ruido = db_to_linear(-100)
    psd_interf = db_to_linear(-95)
    psd_total_dbm = linear_to_db((math.sqrt(psd_ruido) + math.sqrt(psd_interf)) ** 2)
    assert_close(psd_total_dbm, -91.12, tol=0.01, msg="GPON examen c) PSD ruido+interferencia")

    modulaciones = [("16-QAM", 16, 21.5), ("8-QAM", 8, 18), ("4-QAM", 4, 14.5)]
    resultado = mejor_modulacion(modulaciones, 20 * 64, perdidas_ul, psd_total_dbm, potencia_max=22)

    # El examen elige 16-QAM (la de mayor orden) porque ya cumple con 21.43 dBm
    assert resultado is not None, "Debería existir una modulación válida (16-QAM)"
    assert resultado["nombre"] == "16-QAM", "El examen elige 16-QAM para minimizar BW en el uplink"
    assert_close(resultado["bw_mhz"], 320.0, tol=0.1, msg="GPON examen c) BW de 16-QAM")
    assert_close(resultado["potencia_dbm"], 21.43, tol=0.05, msg="GPON examen c) potencia mínima ONT")


# ------------------------------------------------------------
# Ejercicio de telefonía móvil celular
# ------------------------------------------------------------

def test_examen_movil_apartado_a_ci_sistema_original():
    # D1=2R, D2=√13·R, D3=4·R, gamma=2 -> C/I = 1/(1/4+1/13+1/16) ≈ 2.57 (4.1 dB)
    ci, ci_db = ci_custom_distances([2, math.sqrt(13), 4], gamma=2)
    assert_close(ci, 2.57, tol=0.01, msg="Móvil examen a) C/I lineal sistema original")
    assert_close(ci_db, 4.1, tol=0.05, msg="Móvil examen a) C/I en dB sistema original")


def test_examen_movil_apartado_c_ci_sistema_mejorado():
    # D1=2R, D2=√37·R, gamma=2 -> C/I = 1/(1/4+1/37) ≈ 3.61 (5.57 dB)
    ci, ci_db = ci_custom_distances([2, math.sqrt(37)], gamma=2)
    assert_close(ci, 3.61, tol=0.01, msg="Móvil examen c) C/I lineal sistema mejorado")
    assert_close(ci_db, 5.57, tol=0.02, msg="Móvil examen c) C/I en dB sistema mejorado")
    # El diseño propuesto debe mejorar la C/I del sistema original
    ci_original, _ = ci_custom_distances([2, math.sqrt(13), 4], gamma=2)
    assert ci > ci_original, "El sistema mejorado debe tener mejor C/I que el original"


def test_examen_movil_apartado_b_canales_por_grupo():
    # Demanda de canales según la tabla de Erlang B del examen, apartado b)
    # C1: 8E omnidireccional (3 grupos), C2: 4E sectorial (5 grupos), C3: 2E (6 grupos)
    casos_examen = {
        0.15: (10, 6, 4),
        0.10: (11, 7, 4),
        0.05: (13, 8, 5),
        0.02: (14, 9, 6),
        0.01: (15, 10, 7),
    }
    for pb, (c1_esperado, c2_esperado, c3_esperado) in casos_examen.items():
        assert canales_para_erlang(8, pb) == c1_esperado, f"C1 (A=8E) Pb<={pb}"
        assert canales_para_erlang(4, pb) == c2_esperado, f"C2 (A=4E) Pb<={pb}"
        assert canales_para_erlang(2, pb) == c3_esperado, f"C3 (A=2E) Pb<={pb}"


# ------------------------------------------------------------
# modulacion_minima / mejor_modulacion (validaciones generales)
# ------------------------------------------------------------

def test_modulacion_minima_rechaza_bitrate_no_positivo():
    try:
        modulacion_minima([("4-QAM", 4, 14.5)], 0, 10, -100)
        raise AssertionError("Debería haber lanzado ValueError para bitrate<=0")
    except ValueError:
        pass


def test_mejor_modulacion_devuelve_none_si_ninguna_cumple():
    # Pedimos una potencia máxima absurdamente baja: ninguna modulación cumplirá.
    modulaciones = [("16-QAM", 16, 21.5), ("8-QAM", 8, 18), ("4-QAM", 4, 14.5)]
    resultado = mejor_modulacion(modulaciones, 2560, 24.06, -100.0, potencia_max=-50)
    assert resultado is None, "No debería haber solución con una potencia máxima tan baja"


# ------------------------------------------------------------
# Validaciones adicionales (robustez)
# ------------------------------------------------------------

def test_erlang_b_rechaza_trafico_no_positivo():
    try:
        erlang_b(0, 10)
        raise AssertionError("Debería haber lanzado ValueError para A<=0")
    except ValueError:
        pass
    try:
        erlang_b(-3, 10)
        raise AssertionError("Debería haber lanzado ValueError para A<0")
    except ValueError:
        pass


def test_ci_custom_distances_rechaza_distancia_no_positiva():
    try:
        ci_custom_distances([2, 0, 4], gamma=2)
        raise AssertionError("Debería haber lanzado ValueError para una distancia=0")
    except ValueError:
        pass
    try:
        ci_custom_distances([2, -1], gamma=2)
        raise AssertionError("Debería haber lanzado ValueError para una distancia negativa")
    except ValueError:
        pass


# ------------------------------------------------------------
# Ejecución como script
# ------------------------------------------------------------

if __name__ == "__main__":
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    ok, fallos = 0, []
    for t in tests:
        try:
            t()
            ok += 1
            print(f"OK   - {t.__name__}")
        except AssertionError as e:
            fallos.append((t.__name__, str(e)))
            print(f"FAIL - {t.__name__}: {e}")

    print(f"\n{ok}/{len(tests)} tests superados.")
    if fallos:
        raise SystemExit(1)