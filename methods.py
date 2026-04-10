from datetime import datetime
import numpy as np
import pandas as pd

atm = {'Clear':
       {"A": -42.2391,
        "B": 63.8044,
        "C": -1.9220,
        "D": 3.46921e-2,
        "E": -3.61118e-4,
        "F": 1.94318e-6,
        "G": -4.07608e-9},
       'Industrial':
       {"A": 53.1821,
        "B": 14.2110,
        "C": 6.6138e-1,
        "D": -3.1658e-2,
        "E": 5.4654e-4,
        "F": -4.3446e-6,
        "G": 1.3236e-8}}


def _solar_heat_gain(conductor, environment):

    #  ### solar heat gain ###
    date = environment["date"]
    lat = environment["latitude"]
    at = environment["atmosphere"]
    alpha = conductor["solar_absorptivity"]
    elevation = environment["elevation_m"]
    area = conductor["diameter_mm"] / 1e3 # in m they are the same
    dir_angle = environment["cw_angle_direction_rel_to_north"]

    # solar angle and declination
    day_year = date.timetuple().tm_yday
    solar_dec = 23.45 * np.sin(np.radians((284 + day_year) * 360.0 / 365.0))
    hour_angle = 15.0 * (environment['hour'] - 12)

    # solar altitude
    h_c = np.degrees(np.arcsin(
        np.cos(np.radians(lat)) * np.cos(np.radians(solar_dec))
        * np.cos(np.radians(hour_angle))
        + np.sin(np.radians(lat)) * np.sin(np.radians(solar_dec))
    ))

    # heat flux
    solar_heat_flux = atm[at]["A"] + atm[at]["B"] * h_c + atm[at]["C"] * h_c ** 2 \
        + atm[at]["D"] * h_c ** 3 + atm[at]["E"] * h_c ** 4 \
        + atm[at]["F"] * h_c ** 5 + atm[at]["G"] * h_c ** 6
    k_solar = 1 + 1.148e-4 * elevation - 1.108e-8 * elevation ** 2
    solar_heat_flux_corrected = k_solar * solar_heat_flux

    # solar azimuth angle
    xi = np.sin(np.radians(hour_angle)) / (
            np.sin(np.radians(lat)) * np.cos(np.radians(hour_angle))
            - np.cos(np.radians(lat)) * np.tan(np.radians(solar_dec))
    )
    if -180 < hour_angle < 0:
        c = 0.0 if xi >= 0 else 180.0
    else:
        c = 180.0 if xi >= 0 else 360.0
    solar_azimuth_angle = c + np.degrees(np.arctan(xi))

    # angle of incidence
    theta = np.degrees(
        np.arccos(
            np.cos(np.radians(h_c))
            * np.cos(np.radians(solar_azimuth_angle - dir_angle))
        )
    )

    # solar heat gain
    q_s = alpha * solar_heat_flux_corrected * np.sin(np.radians(theta)) * area

    return q_s


def _current_at_temperature(t_test, q_s, k_angle, conductor, environment):

    # conductor inputs
    diameter = conductor["diameter_mm"] / 1e3
    res_low = conductor["res_low_ohm_per_m"]
    t_low = conductor["temp_low_c"]
    res_high = conductor["res_high_ohm_per_m"]
    t_high = conductor["temp_high_c"]
    emissivity = conductor["emissivity"]

    # environment inputs
    t_a = environment["ambient_temperature_c"]
    wind_speed = environment["wind_speed_m_per_s"]
    elevation = environment["elevation_m"]

    # temperature
    t_film = (t_test+t_a)/2.0

    # dynamic viscosity
    mu_f = 1.458e-6 * (t_film + 273) ** 1.5 / (t_film + 383.4)

    # air-density
    rho_f = (1.293 - 1.525e-4 * elevation + 6.379e-9 * elevation ** 2
             ) / (1 + 0.00367 * t_film)

    # thermal conductivity
    k_f = 2.424e-2 + 7.477e-5 * t_film - 4.407e-9 * t_film ** 2

    # reynolds number
    n_re = diameter * rho_f * wind_speed/mu_f

    # forced convection
    q_c1 = k_angle * (1.01 + 1.35 * n_re**0.52) * k_f * (t_test-t_a)
    q_c2 = k_angle * (0.754 * n_re**0.6) * k_f * (t_test-t_a)

    # natural convection
    q_cn = 3.645 * rho_f**0.5 * diameter**0.75 * (t_test-t_a)**1.25
    q_c = max(q_c1, q_c2, q_cn)

    # radiated heat loss
    q_r = 17.8 * diameter * emissivity \
        * (((t_test + 273) / 100) ** 4 - ((t_a + 273) / 100) ** 4)

    if not environment['DC']:
        r_tc = ((res_high - res_low) / (t_high - t_low)) * (t_test - t_low) + res_low
    else:
        r_tc = conductor['res_dc_ohm_per_m'] * (1 + environment['temp_coeff_resistivity'] * (t_test - conductor['temp_dc_c']))

    x = (q_c+q_r-q_s)/r_tc
    if x > 0:
        i = np.sqrt(x)
    else:
        i = 0

    return r_tc, i


def ieee_738_steady_state_rating(conductor, environment):

    wind_angle = environment['wind_angle']
    t_c = conductor['max_temperature_c']

    # solar heat gain
    q_s = _solar_heat_gain(conductor, environment)

    # wind direction factor
    k_angle = 1.194 - np.cos(np.radians(wind_angle)) \
        + 0.194 * np.cos(np.radians(2 * wind_angle)) \
        + 0.368 * np.sin(np.radians(2 * wind_angle))

    r_tc, i = _current_at_temperature(t_c, q_s, k_angle,
                                      conductor, environment)

    return i


def ieee_738_steady_state_temperature(current_a, conductor, environment):

    # Calculate initial(steady - state) conductor temperature
    # from the steady-state load current, using a binary search

    tc_min = environment["ambient_temperature_c"]
    r_tc = conductor["res_low_ohm_per_m"]
    wind_angle = environment["wind_angle"]

    i_ss_threshold = 0.01
    tc_max = 300
    i_ss_result = 0.0

    # solar heat gain
    q_s = _solar_heat_gain(conductor, environment)

    # wind direction factor
    k_angle = 1.194 - np.cos(np.radians(wind_angle)) \
        + 0.194 * np.cos(np.radians(2 * wind_angle)) \
        + 0.368 * np.sin(np.radians(2 * wind_angle))

    t_test = tc_max
    counter = 0
    while ((i_ss_result > current_a + i_ss_threshold) \
            or (i_ss_result < current_a - i_ss_threshold)) and counter<50:

        t_test = (tc_max + tc_min) / 2

        r_tc, i_ss_result = np.real(_current_at_temperature(
            t_test, q_s, k_angle,
            conductor, environment))

        if i_ss_result == current_a:
            break
        elif i_ss_result > current_a:
            tc_max = t_test
        else:
            tc_min = t_test
        counter += 1

    return t_test, r_tc


def get_performance(current_a, cd, environment, include_unfeasible):

    cables = cd
    cables['env_ampacity_a'] = cables.apply(lambda c:
                                            ieee_738_steady_state_rating(conductor=c.to_dict(),
                                                                         environment=environment),
                                            axis=1)
    cb = cables.loc[(cables['env_ampacity_a'] > current_a)
                    & (cables['env_ampacity_a'] < current_a*3)] if not include_unfeasible else cables.copy()
    x = cb.apply(
        lambda c: ieee_738_steady_state_temperature(
            current_a=min(current_a, c['env_ampacity_a']), conductor=c.to_dict(), environment=environment), axis=1
    )

    x = pd.DataFrame(x.to_list()).rename(columns={
                                              0: 'temp_at_current_c',
                                              1: 'res_at_current_ohm_per_m'})

    cb = cb.reset_index(drop=True).join(x)

    return cb


def cigre_324_sag(conductor, loading, span_m):

    diameter = conductor["diameter_mm"] / 1e3
    A = conductor['area_mm2'] / 1e6
    W0 = conductor['weight_n_per_m']
    alpha = conductor['coeff_thermal_expan_per_cel']
    E = conductor['elastic_modulus_gpa'] * 1e9
    S = span_m
    H0 = loading['initial_tension_percentage'] * conductor['conductor_rts_kn'] * 1e3
    T0 = loading['initial_temperature_c']

    T1 = conductor['temp_at_current_c']

    ice_density = loading['ice_density_kg_per_m3']
    Ice_Ld = loading['ice_thickness_m']
    Wind_Ld = loading['pressure_pa']
    Additive_Ld = loading['additive_loading_n_per_m']

    sag0 = H0 / W0 * (np.cosh(W0 * S / 2 / H0)-1) # calculate initial sag (without loading)
    L0 = S + 8 * pow(sag0, 2) / 3 / S # deduce initial length

    W_ice = ice_density * np.pi * (pow(diameter + 2*Ice_Ld, 2) - pow(diameter, 2)) / 4 * 9.81 # ice density*ice volume*g (N/m)
    W_wind = Wind_Ld * (diameter + 2*Ice_Ld)
    W1 = np.sqrt(pow(W0+W_ice, 2) + pow(W_wind, 2)) + Additive_Ld

    Lref = L0 * (1 - H0 / E / A)
    L1 = Lref * (1 + alpha * (T1 - T0)) # estimate of new length based on temp. difference

    sag1 = np.sqrt(3 * S * abs(L1 - S) / 8)

    sag1_temp = 0
    counter = 0
    H1_min = 0
    H1_max = 500000
    while abs(sag1 - sag1_temp) > 0.001:
        H1 = (H1_min + H1_max) / 2
        H1_temp = H1
        sag1_temp = sag1
        Li = L1 * (1 + H1 / E / A)
        sag1 = np.sqrt(3 * S * abs(Li - S) / 8)
        H1 = W1 * pow(S, 2) / 8 / sag1
        if H1 > H1_temp:
            H1_min = H1_temp
        else:
            H1_max = H1_temp

        counter += 1

    return sag1, H1, {'W0': W0, 'W1': W1, 'H0':H0, 'H1': H1, 'W_ice': W_ice, 'W_wind': W_wind, 'T1': T1}


def get_performance_sag(conductors, sag_max_m, span_m, loading, include_unfeasible):

    conductors[['sag_m', 'tension_n', 'extra']] = conductors.apply(lambda c:
                                   cigre_324_sag(conductor=c.to_dict(), loading=loading, span_m= span_m),
                                   axis=1, result_type='expand')

    df = conductors.loc[conductors['sag_m'] < sag_max_m] if not include_unfeasible else conductors.copy()
    return df


def corona(radius, structure, environment):

    # Air correction factor
    delta = 293 / (273 + environment['ambient_temperature_c']) * np.exp(-0.00012 * environment['elevation_m'])

    if not environment['DC']:
        # Geometrical mean distance (GMD) between phases, in centimeter
        gmd = pow(structure['dist_a_b_m'] * structure['dist_b_c_m'] * structure['dist_a_c_m'], 1 / 3) * 1e2
        d = radius * np.log(gmd / radius)
        inception_voltage = np.sqrt(3) * 29.8 / np.sqrt(2) * structure['weather_corr_factor'] * structure['rigosity_coeff'] * delta * \
                structure['nbr_conductors'] * d
    else:
        d = radius * np.log(structure['dist_pos_neg_m'] * 1e2 / radius)
        inception_voltage = 30 * structure['weather_corr_factor'] * structure['rigosity_coeff'] * delta * \
                            structure['nbr_conductors'] * (1 + 0.301 / np.sqrt(delta * radius)) * d

    return inception_voltage, inception_voltage / d


def get_performance_corona(conductors, structure, environment, voltage, include_unfeasible):

    conductors[['inception_voltage_kv', 'voltage_gradient_kv_per_cm']] = (
        conductors.apply(lambda r: corona(r['diameter_mm'] / 2 * 0.1, structure, environment),
                         axis=1,
                         result_type='expand')) # radius is needed in centimeter
    df = conductors.loc[conductors['inception_voltage_kv'] > voltage] if not include_unfeasible else conductors.copy()

    return df


def RUS_bulletin_200_loading(cond, angle, span, tot_nbr_conds, material_structure, str_strength):

    # Transverse force (N)
    F_t = cond['extra']['W_wind'] * span * np.cos(angle) + cond['str_tension_n'] * np.sin(angle)

    # Longitudinal force (N)
    F_l = cond['str_tension_n'] * np.cos(angle)

    # Horizontal force a vector summation of F_t and F_l (N)
    F_h = np.sqrt(pow(F_t, 2) + pow(F_l, 2)) * tot_nbr_conds

    structure = str_strength[(str_strength.horiz_load_2f_from_top_n > F_h) & (str_strength.line_type == 'HVAC') &
                             ((str_strength.material+'_'+str_strength.structure) == material_structure)]
    structure['diff'] = (structure['horiz_load_2f_from_top_n'] - F_h)
    min_diff = structure['diff'].min()
    structure = pd.DataFrame(structure[structure['diff'] == min_diff]).reset_index()

    type = (structure.iloc[0]['material'] + '_' + structure.iloc[0]['structure'] + '_' +
            structure.iloc[0]['structure_code']) if not structure.empty else ''

    return F_h, type


def get_performance_mechanical_loading(conductors, structure, nbr_phases, span, strength):
    conds = conductors.copy()
    angle = structure['line_angle'] / 2 * np.pi / 180
    tot_nbr_conds = nbr_phases if 'nbr_conductors' not in structure else nbr_phases * structure['nbr_conductors']

    # Tension at the point of attachment on structure (N)
    conds['str_tension_n'] = conds.apply(lambda r:
                                         r['extra']['H1'] + (r['extra']['W0'] + r['extra']['W_ice']) * r['sag_m'] / 2,
                                         axis=1)

    # Horizontal force (N)
    conds[['total_force', 'structure_type']] = conds.apply(lambda r:
                         RUS_bulletin_200_loading(cond=r.to_dict(), angle=angle, span=span, tot_nbr_conds=tot_nbr_conds,
                                                  material_structure=structure['mat_str'], str_strength=strength),
                         axis=1,
                         result_type='expand'
                         )

    return conds


# evaluate losses and congestion
def losses_including_unfeasible(cond, prj_info, current_a, voltage, environment, support_str, nbr_ph):
    nbr_conds = 1 if 'nbr_conductors' not in support_str else support_str['nbr_conductors']
    I_E = cond['env_ampacity_a']  # current in one conductor per phase of the existing line
    P_E = I_E * voltage * np.sqrt(3) * prj_info['nbr_ckts'] * nbr_conds * 1e-3 if not environment['DC'] \
            else I_E * voltage * nbr_ph * prj_info['nbr_ckts'] * nbr_conds * 1e-3
    
    t_E = (prj_info['power_mw'] - P_E) / prj_info['power_mw']
    loss_factor = 0.3 * prj_info['load_factor'] + 0.7 * prj_info['load_factor'] ** 2  # coeffs set to 0.15 and 0.85 in case of distribution
    if (prj_info['power_mw'] - P_E) > 0:
        # loss factor at the congested line
        load_factor_1 = (1 + t_E) / 2
        loss_factor_1 = 0.3 * load_factor_1 + 0.7 * load_factor_1 ** 2

        # line resistance and loss factor at the neighboring line which takes on the congestion power from existing line
        R = 8.63 * 1e-5  # ACSR DRAKE at 75 deg. Cel

        cond['losses_at_peak_mwh_per_m'] = (cond['res_at_current_ohm_per_m'] * I_E ** 2 * loss_factor_1 + \
                                            (current_a - I_E) ** 2 * R * loss_factor) \
                                           * prj_info['nbr_ckts'] * nbr_ph * nbr_conds * 8760 * 1e-6
        cond['congestion_mw'] = (prj_info['power_mw'] - P_E) * t_E / 2
    else:
        cond['losses_at_peak_mwh_per_m'] = cond['res_at_current_ohm_per_m'] * current_a ** 2 \
                                                 * loss_factor * prj_info['nbr_ckts'] * nbr_ph * nbr_conds * 8760 * 1e-6
        cond['congestion_mw'] = 0

    if prj_info['consider_corona']:
        delta = 293 / (273 + environment['ambient_temperature_c']) * np.exp(
            -0.00012 * environment['elevation_m']) # Air correction factor
        if not environment['DC']:
            gmd = pow(support_str['dist_a_b_m'] * support_str['dist_b_c_m'] * support_str['dist_a_c_m'],
                      1 / 3) * 1e2
            cond['corona_losses_mwh_per_m'] = \
                (241 / delta * (60 + 25) * np.sqrt(cond['diameter_mm'] / 2 * 0.1 / gmd) *
                pow((max(voltage - cond['inception_voltage_kv'], 0)) / np.sqrt(3), 2) * 1e-5 *
                prj_info['nbr_ckts'] * nbr_ph * nbr_conds * loss_factor * 8760 * 1e-6)
        else:
            cond['corona_losses_mwh_per_m'] = \
                pow(10, (11 + 40 * np.log10(cond['voltage_gradient_kv_per_cm'] / 25) +
                        20 * np.log10(cond['diameter_mm'] / 2 * 0.1 / 3.05) +
                        15 * np.log10(support_str['nbr_conductors'] / 3) -
                        10 * np.log10(support_str['str_height_m'] * support_str['dist_pos_neg_m'] / 15 / 15)) / 10) * \
                prj_info['nbr_ckts'] * nbr_ph * nbr_conds * loss_factor * 8760 * 1e-6
    else:
        cond['corona_losses_mwh_per_m'] = 0

    return cond


def get_technical_performance(conductors, prj_info, environment, loading, prj_option, str_strength, include_unfeasible):

    environment['DC'] = True if prj_option['hvdc'] else False
    nbr_conds = 1 if 'nbr_conductors' not in prj_option['structures'] else prj_option['structures']['nbr_conductors']

    current_a = prj_info['power_mw'] * 1e3 / (prj_option['voltage_kv'] * np.sqrt(3)) / prj_info['nbr_ckts'] / nbr_conds if not environment['DC'] \
        else prj_info['power_mw'] * 1e3 / prj_option['voltage_kv'] / prj_option['nbr_phases'] / prj_info['nbr_ckts'] / nbr_conds

    curr_result = get_performance(current_a, conductors, environment, include_unfeasible)

    # get losses
    if not curr_result.empty:
        techn_result = get_performance_sag(curr_result, prj_info['max_sag_m'], prj_info['span_m'], loading, include_unfeasible)
        if prj_info['consider_corona']:
            techn_result = get_performance_corona(techn_result, prj_option['structures'], environment, prj_option['voltage_kv'], include_unfeasible) \
                if not techn_result.empty else pd.DataFrame()
        if prj_info['consider_str_type']:
            techn_result = get_performance_mechanical_loading(techn_result, prj_option['structures'], prj_option['nbr_phases'], prj_info['span_m'], str_strength) \
                                                if not techn_result.empty else pd.DataFrame()

        techn_result = techn_result.apply(
            lambda r: losses_including_unfeasible(r, prj_info, current_a, prj_option['voltage_kv'], environment, prj_option['structures'], prj_option['nbr_phases']),
            axis=1
        )
        
        techn_result['prj_option'] = prj_option['option']
        techn_result['peak_current'] = current_a

        return {'performance': techn_result}
    else:
        return {'performance': pd.DataFrame()}


def npv(conductors, ec, length_km, prj_option, consider_losses=True, time_horizon=100, filter_type=False):

    if not conductors.empty:
        nbr_conds = 1 if 'nbr_conductors' not in prj_option['structures'] else prj_option['structures']['nbr_conductors']
        str_data = prj_option['structures']
        if str_data and 'line_angle' in str_data:
            ec['cost_of_structures_unit'] = (str_data['str_tgt'] * str_data['str_tgt_cost']
                                          + str_data['str_ra'] * str_data['str_ra_cost']
                                          + str_data['str_nade'] * str_data['str_nade_cost']
                                          + str_data['str_ade'] * str_data['str_ade_cost']) / str_data['nbr_structures']
            ec['nbr_structures'] = str_data['nbr_structures']

        c = conductors.reset_index(drop=True)
        desired_cols = ['code', 'type', 'dol_per_1000_ft', 'inst_dol_per_1000_ft', 'str_costs_dol',
               'accessories_dol_per_1000_ft', 'env_ampacity_a', 'peak_current', 'temp_at_current_c', 'max_temperature_c',
               'sag_m', 'tension_n', 'losses_at_peak_mwh_per_m', 'inception_voltage_kv', 'structure_type', 'total_force',
               'congestion_mw', 'corona_losses_mwh_per_m']
        existing_cols = c.columns.intersection(desired_cols)
        c = c[existing_cols].copy()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1+ec['inflation'])**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(prj_option['replace_st_at'], time_horizon, ec['structures_lifetime'])), 'structures_inv'] = 1
        npv.loc[npv.year.isin(range(prj_option['replace_cd_at'], time_horizon, ec['conductors_lifetime'])), 'conductors_inv'] = 1
        npv['cost_capital'] = npv['year'].apply(lambda x: 1/(1+ec['wacc'])**x)

        length_kft = length_km * 3.28
        conductor_inv = c.dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                    * length_kft * ec['nbr_ckts'] * prj_option['nbr_phases'] * nbr_conds
        conductor_inst = c.inst_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                    * length_kft * ec['nbr_ckts'] * prj_option['nbr_phases'] * nbr_conds
        conductor_access = c.accessories_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                           * length_kft * ec['nbr_ckts'] * prj_option['nbr_phases'] * nbr_conds

        length_m = length_km * 1e3

        if not ec['customize_inv_options']:
            structures = c.str_costs_dol.apply(lambda r: npv['inflation'] * ec['cost_of_structures_unit'] * npv['structures_inv'] * ec['nbr_structures'])
        else:
            structures = c.str_costs_dol.apply(lambda r: r * npv['inflation'] * npv['structures_inv'])

        if prj_option['voltage_upgrade']:
            npv['structures_upgd_inv'] = 0
            npv.at[0, 'structures_upgd_inv'] = 1
            # costs of structure upgrade (if any) are added to structures costs
            structures[0] = ec['cost_of_structures_upgd_unit'] * ec['nbr_structures'] \
                                    if prj_option['structure_upgrade'] else structures[0]
            # costs of substations and transformers modifications are also considered
            ss_transfo = ec['cost_of_ss_transfo'] * npv['inflation'] * npv['structures_upgd_inv']
            converters = npv['inflation'] * 0

        elif prj_option['hvdc']:
            npv['structures_upgd_inv'] = 0
            npv.at[0, 'structures_upgd_inv'] = 1
            # costs of structure upgrade (if any) are added to structures costs
            structures[0] = ec['cost_of_structures_hvdc_unit'] * ec['nbr_structures'] \
                if prj_option['structure_upgrade'] else structures[0]
            # costs of converters are also considered
            converters = ec['cost_of_converters'] * npv['inflation'] * npv['structures_upgd_inv']
            ss_transfo = npv['inflation'] * 0

        else:
            ss_transfo = npv['inflation'] * 0
            converters = npv['inflation'] * 0

        if consider_losses:
            losses = c.losses_at_peak_mwh_per_m.apply(
                lambda r: (r + c['corona_losses_mwh_per_m'].iloc[0]) * npv['inflation']
                          * ec['cost_of_losses_dol_per_mwh'] * length_m)
        else:
            losses = c.losses_at_peak_mwh_per_m.apply(lambda r: r * npv['inflation'] * 0)

        congestion = c.congestion_mw.apply(lambda r: r * npv['inflation'] * 8760 * ec['cost_congestion'])

        prj = ((structures + conductor_inv + conductor_inst + conductor_access + losses + ss_transfo + converters + congestion)
               * npv['cost_capital'])

        # get cumulative sum in millions
        prj = prj.cumsum(axis=1)/1e6

        c['prj_option'] = prj_option['option']
        prj = c.join(prj)
        prj = prj.reset_index(drop=True).sort_values(by=[prj.columns[-1]])

        cost_st = structures * npv['cost_capital'] / 1e6
        cost_st = prj[['code', 'type', 'prj_option']].join(cost_st.cumsum(axis=1))
        cost_cd = (conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'] / 1e6
        cost_cd = prj[['code', 'type', 'prj_option']].join(cost_cd.cumsum(axis=1))
        losses = losses * npv['cost_capital'] / 1e6
        losses = prj[['code', 'type', 'prj_option']].join(losses.cumsum(axis=1))
        congestion = congestion * npv['cost_capital'] / 1e6
        congestion = prj[['code', 'type', 'prj_option']].join(congestion.cumsum(axis=1))
        ss_transfo = ss_transfo * npv['cost_capital'] / 1e6
        ss_transfo = ss_transfo.cumsum()
        ss_transfo['prj_option'] = prj_option['option']
        converters = converters * npv['cost_capital'] / 1e6
        converters = converters.cumsum()
        converters['prj_option'] = prj_option['option']

        if filter_type:
            df = pd.DataFrame(columns=prj.columns)
            for t in prj.type.unique():
                df = pd.concat([df, prj.loc[prj.type == t].iloc[0].to_frame().T])
            prj = df

        cost_cd = cost_cd.loc[cost_cd.index.isin(prj.index)]
        losses = losses.loc[losses.index.isin(prj.index)]

        return {'total_prj_perf': prj, 'cost_st': pd.DataFrame(cost_st), 'cost_cd': cost_cd, 'losses': losses,
                'cost_ss_tr': pd.DataFrame(ss_transfo), 'cost_cv': pd.DataFrame(converters), 'congestion': congestion}
    else:
        return {'total_prj_perf': pd.DataFrame(), 'cost_st': pd.DataFrame(), 'cost_cd': pd.DataFrame(), 'losses': pd.DataFrame(),
                'cost_ss_tr': pd.DataFrame(), 'cost_cv': pd.DataFrame(), 'congestion': pd.DataFrame()}

