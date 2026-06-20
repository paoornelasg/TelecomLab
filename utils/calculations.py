import math

def db_to_linear(db):
    return 10 ** (db / 10)

def linear_to_db(value):
    if value <= 0:
        raise ValueError(
            "El valor lineal debe ser mayor que cero."
        )
    return 10 * math.log10(value)

def splitter_loss(users):
    if users <= 0:
        raise ValueError(
            "El número de usuarios debe ser mayor que cero."
        )
    return 10 * math.log10(users)

def received_power(
        tx_power,
        distance,
        attenuation,
        users,
        extra_losses
):

    split_loss = splitter_loss(users)
    losses = (
        attenuation * distance
        + split_loss
        + extra_losses
    )

    return tx_power - losses

def max_distance(
        tx_power,
        sensitivity,
        attenuation,
        users,
        extra_losses
):
    if attenuation <= 0:
        raise ValueError(
            "La atenuación debe ser mayor que cero."
        )

    split_loss = splitter_loss(users)
    budget = (
        tx_power
        - sensitivity
        - split_loss
        - extra_losses
    )

    return budget / attenuation

def ci_omnidirectional(
        N,
        gamma
):
    ci = (
        (math.sqrt(3 * N))
        ** gamma
    ) / 6

    return ci, 10 * math.log10(ci)

def ci_sectorized_120(
        N,
        gamma
):
    ci = (
        0.5 *
        ((math.sqrt(3 * N))
        ** gamma)
    )

    return ci, 10 * math.log10(ci)

def ci_sectorized_60(
        N,
        gamma
):
    ci = (
        (math.sqrt(3 * N))
        ** gamma
    )

    return ci, 10 * math.log10(ci)

def mm1_metrics(
        lam,
        mu
):
    if lam <= 0:
        raise ValueError(
            "λ debe ser mayor que cero."
        )

    if mu <= 0:
        raise ValueError(
            "μ debe ser mayor que cero."
        )

    if lam >= mu:
        raise ValueError(
            "Sistema inestable: λ debe ser menor que μ."
        )

    rho = lam / mu
    W = 1 / (mu - lam)
    L = lam * W
    Wq = W - (1 / mu)
    Lq = lam * Wq

    return rho, W, L, Wq, Lq