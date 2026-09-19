# -*- coding: utf-8 -*-
"""
Helper interno para construir proceso BSM y opción en QuantLib.
Convierte inputs (tipo, S, K, T, r, sigma, div) a objetos QuantLib.
"""
import QuantLib as ql


def _build_european_option(tipo, S, K, T, r, sigma, div):
    """
    Construye VanillaOption europea y proceso BSM.
    Retorna (option, bsm_process).
    """
    if sigma <= 0 or T <= 0:
        raise ValueError("sigma y T deben ser positivos.")
    if tipo not in ("C", "P"):
        raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put).")

    calculation_date = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = calculation_date
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates(ql.UnitedStates.NYSE)

    # maturity_date = calculation_date + T años (aproximado con 365 días)
    days_to_maturity = int(round(T * 365))
    maturity_date = calculation_date + ql.Period(days_to_maturity, ql.Days)

    option_type = ql.Option.Call if tipo == "C" else ql.Option.Put
    payoff = ql.PlainVanillaPayoff(option_type, K)
    exercise = ql.EuropeanExercise(maturity_date)
    option = ql.VanillaOption(payoff, exercise)

    spot_obj = ql.QuoteHandle(ql.SimpleQuote(S))
    rate_obj = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, r, day_count)
    )
    dividend_obj = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, div, day_count)
    )
    vol_obj = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(calculation_date, calendar, sigma, day_count)
    )
    bsm_process = ql.BlackScholesMertonProcess(
        spot_obj, dividend_obj, rate_obj, vol_obj
    )

    return option, bsm_process


def _build_american_option(tipo, S, K, T, r, sigma, div):
    """
    Construye VanillaOption americana y proceso BSM.
    Retorna (option, bsm_process).
    """
    if sigma <= 0 or T <= 0:
        raise ValueError("sigma y T deben ser positivos.")
    if tipo not in ("C", "P"):
        raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put).")

    calculation_date = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = calculation_date
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates(ql.UnitedStates.NYSE)

    days_to_maturity = int(round(T * 365))
    maturity_date = calculation_date + ql.Period(days_to_maturity, ql.Days)

    option_type = ql.Option.Call if tipo == "C" else ql.Option.Put
    payoff = ql.PlainVanillaPayoff(option_type, K)
    exercise = ql.AmericanExercise(calculation_date, maturity_date)
    option = ql.VanillaOption(payoff, exercise)

    spot_obj = ql.QuoteHandle(ql.SimpleQuote(S))
    rate_obj = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, r, day_count)
    )
    dividend_obj = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, div, day_count)
    )
    vol_obj = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(calculation_date, calendar, sigma, day_count)
    )
    bsm_process = ql.BlackScholesMertonProcess(
        spot_obj, dividend_obj, rate_obj, vol_obj
    )

    return option, bsm_process
