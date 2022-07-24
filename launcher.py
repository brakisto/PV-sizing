import pandas as pd
from pv_dim.clases.pv import PVProduction, BatterySizing
from utils.constants import fresnel_fixed
from utils.pv_utils import init_inv

# Leemos los datos de la carga del lugar de estudio y
# los datos de irradiancia, temperatura, viento para la localidad escogida.

ll = pd.read_csv('pv_dim/data/lalaguna.csv', header=6, skipfooter=12, engine='python', index_col='time')
load = pd.read_csv('pv_dim/data/load.csv', sep=';', decimal=',')

if __name__ == '__main__':
    for np in range(5,15):
        print(F'### NÚMERO DE PANELES: {np} ###')
        days_auto = 0.5
        num_panel = np
        price_panel = 260
        price_inverter = 1300
        add_cost = 500
        coste_instalacion = 0.15

        inversion_inicial = init_inversion = init_inv(num_panel=num_panel, price_panel=price_panel,
                                                      costes_adicionales=add_cost, coste_instalacion=coste_instalacion,
                                                      price_inverter=price_inverter)

        pv = PVProduction(irr_data=ll, load=load, tnoct=42, gamma=-0.36, panel_power=450, num_panel=num_panel,
                          fresnel_eff=fresnel_fixed)

        bat = BatterySizing(irr_data=ll, load=load, tnoct=42, gamma=-0.36, panel_power=450, num_panel=num_panel,
                            fresnel_eff=fresnel_fixed, amb_temp_multiplier=1.163,
                            days_auto=days_auto,
                            dod=0.95,
                            amp_hour_rating=2400 / 48,
                            nominal_voltage=48,
                            batt_volt=48, inversor_eff=0.85)

        total_battery_capacity, n_bat_paralell, n_bat_series = bat.battery_sizing()
        daily_load_Wh = pv.mean_hourly_load_data().AE_kWh.sum() * 1000  # pasamos a Wh

        coste_energia_actual, coste_energia_pv, compensacion_pv, ahorro = pv.savings_from_pv(sell_price=0.06,
                                                                                             buy_price=0.32)
        cashflow, van, tir = pv.economic_analysis(inversion_inicial)

        print(f'Energía media diaria consumida: {daily_load_Wh} [Wh]')
        print(f'Capacidad necesaria para {days_auto} días de autonomía: {total_battery_capacity} [Ah]')

        print(f'Coste energía sin PV: {coste_energia_actual} €/año')
        print(f'Coste energía con PV: {coste_energia_pv} €/año')
        print(f'Compensación PV: {compensacion_pv} €/año')
        print(f'Ahorro: {ahorro} €/año')

        print(f'Iversión inicial: {inversion_inicial} €')
        print(f'VAN: {van} €')
        print(f'TIR {tir * 100} %')
        print()
    # pv.plot(cashflow['Cashflow acumulado'])
