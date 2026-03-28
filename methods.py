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


def _solar_heat_gain(conductor, conditions):

    #  ### solar heat gain ###
    date = datetime.strptime(conditions["date"], "%Y-%m-%d")
    lat = conditions["latitude"]
    at = conditions["atmosphere"]
    alpha = conditions["solar_absorptivity"]
    elevation = conditions["elevation_m"]
    area = conductor["diameter_mm"] / 1e3 # in m they are the same
    dir_angle = conditions["cw_angle_direction_rel_to_north"]

    # solar angle and declination
    day_year = date.timetuple().tm_yday
    solar_dec = 23.45 * np.sin(np.radians((284 + day_year) * 360.0 / 365.0))
    hour_angle = 15.0 * (conditions['hour'] - 12)

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


def _current_at_temperature(t_test, q_s, k_angle, conductor, conditions):

    # conductor inputs
    diameter = conductor["diameter_mm"] / 1e3
    res_low = conductor["res_low_ohm_per_m"]
    t_low = conductor["temp_low_c"]
    res_high = conductor["res_high_ohm_per_m"]
    t_high = conductor["temp_high_c"]

    # conditions inputs
    t_a = conditions["ambient_temperature_c"]
    wind_speed = conditions["wind_speed_m_per_s"]
    emissivity = conditions["emissivity"]
    elevation = conditions["elevation_m"]

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

    if not conditions['DC']:
        r_tc = ((res_high - res_low) / (t_high - t_low)) * (t_test - t_low) + res_low
    else:
        r_tc = conductor['res_dc_ohm_per_m'] * (1 + conditions['temp_coeff_resistivity'] * (t_test - conductor['temp_dc_c']))

    x = (q_c+q_r-q_s)/r_tc
    if x > 0:
        i = np.sqrt(x)
    else:
        i = 0

    return r_tc, i


def ieee_738_steady_state_rating(conductor, conditions):

    wind_angle = conditions['wind_angle']
    t_c = conductor['max_temperature_c']

    # solar heat gain
    q_s = _solar_heat_gain(conductor, conditions)

    # wind direction factor
    k_angle = 1.194 - np.cos(np.radians(wind_angle)) \
        + 0.194 * np.cos(np.radians(2 * wind_angle)) \
        + 0.368 * np.sin(np.radians(2 * wind_angle))

    r_tc, i = _current_at_temperature(t_c, q_s, k_angle,
                                      conductor, conditions)

    return i


def ieee_738_steady_state_temperature(current_a, conductor, conditions):

    # Calculate initial(steady - state) conductor temperature
    # from the steady-state load current, using a binary search

    tc_min = conditions["ambient_temperature_c"]
    r_tc = conductor["res_low_ohm_per_m"]
    wind_angle = conditions["wind_angle"]

    i_ss_threshold = 0.01
    tc_max = 300
    i_ss_result = 0.0

    # solar heat gain
    q_s = _solar_heat_gain(conductor, conditions)

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
            conductor, conditions))

        if i_ss_result == current_a:
            break
        elif i_ss_result > current_a:
            tc_max = t_test
        else:
            tc_min = t_test
        counter += 1

    return t_test, r_tc


def get_feasible(current_a, cd, environment, include_unfeasible):

    cables = cd
    cables['env_ampacity_a'] = cables.apply(lambda c:
                                            ieee_738_steady_state_rating(conductor=c.to_dict(),
                                                                         conditions=environment),
                                            axis=1)
    cb = cables.loc[(cables['env_ampacity_a'] > current_a)
                    & (cables['env_ampacity_a'] < current_a*300.0)] if not include_unfeasible else cables.copy()
    x = cb.apply(
        lambda c: ieee_738_steady_state_temperature(
            current_a=current_a, conductor=c.to_dict(), conditions=environment), axis=1
    )

    x = pd.DataFrame(x.to_list()).rename(columns={
                                              0: 'temp_at_current_c',
                                              1: 'res_at_current_ohm_per_m'})

    cb = cb.reset_index(drop=True).join(x)

    return cb


def cigre_324_sag(loading, conductor, span_m):

    diameter = conductor["diameter_mm"] / 1e3
    A = conductor['area_mm2'] / 1e6
    W0 = conductor['weight_n_per_m']
    alpha = conductor['CoeffThermalExpan_per_Cel']
    E = conductor['ElasticModulus_GPa'] * 1e9
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


def get_feasible_sag(conductors, sag_max_m, span_m, loading, include_unfeasible):
    conductors[['sag_m', 'tension_n', 'extra']] = conductors.apply(lambda c:
                                   cigre_324_sag(loading=loading, conductor=c.to_dict(), span_m= span_m),
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


def get_feasible_corona(conductors, structure, environment, voltage, include_unfeasible):
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


def get_feasible_mechanical_loading(conductors, structure, nbr_phases, span, strength):
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
def losses_including_unfeasible(cond, data, current_a, voltage, environment, support_str, nbr_ph):
    nbr_conds = 1 if 'nbr_conductors' not in support_str else support_str['nbr_conductors']
    I_E = cond['env_ampacity_a']  # current in one conductor per phase of the existing line
    P_E = I_E * voltage * np.sqrt(3) * data['nbr_ckts'] * nbr_conds * 1e-3 if not environment['DC'] \
            else I_E * voltage * nbr_ph * data['nbr_ckts'] * nbr_conds * 1e-3
    
    t_E = (data['power_mw'] - P_E) / data['power_mw']
    loss_factor = 0.3 * data['load_factor'] + 0.7 * data['load_factor'] ** 2  # coeffs set to 0.15 and 0.85 in case of distribution
    if (data['power_mw'] - P_E) > 0:
        # loss factor at the congested line
        load_factor_1 = (1 + t_E) / 2
        loss_factor_1 = 0.3 * load_factor_1 + 0.7 * load_factor_1 ** 2

        # line resistance and loss factor at the neighboring line which takes on the congestion power from existing line
        R = 8.63 * 1e-5  # ACSR DRAKE at 75 deg. Cel

        cond['losses_at_peak_mwh_per_m'] = (I_E ** 2 * cond['res_at_current_ohm_per_m'] * loss_factor_1 + \
                                            (current_a - I_E) ** 2 * R * loss_factor) \
                                           * data['nbr_ckts'] * nbr_ph * nbr_conds * 8760 * 1e-6
        cond['congestion_mw'] = (data['power_mw'] - P_E) * t_E / 2
    else:
        cond['losses_at_peak_mwh_per_m'] = cond['res_at_current_ohm_per_m'] * current_a ** 2 \
                                                 * loss_factor * data['nbr_ckts'] * nbr_ph * nbr_conds * 8760 * 1e-6
        cond['congestion_mw'] = 0

    if data['consider_corona']:
        # Air correction factor
        delta = 293 / (273 + environment['ambient_temperature_c']) * np.exp(
            -0.00012 * environment['elevation_m'])
        if not environment['DC']:
            gmd = pow(support_str['dist_a_b_m'] * support_str['dist_b_c_m'] * support_str['dist_a_c_m'],
                      1 / 3) * 1e2
            cond['corona_losses_mwh_per_m'] = \
                (241 / delta * (60 + 25) * np.sqrt(cond['diameter_mm'] / 2 * 0.1 / gmd) *
                pow((max(voltage - cond['inception_voltage_kv'], 0)) / np.sqrt(3), 2) * 1e-5 *
                data['nbr_ckts'] * nbr_ph * nbr_conds * loss_factor * 8760 * 1e-6)
        else:
            cond['corona_losses_mwh_per_m'] = \
                pow(10, (11 + 40 * np.log10(cond['voltage_gradient_kv_per_cm'] / 25) +
                        20 * np.log10(cond['diameter_mm'] / 2 * 0.1 / 3.05) +
                        15 * np.log10(support_str['nbr_conductors'] / 3) -
                        10 * np.log10(support_str['str_height_m'] * support_str['dist_pos_neg_m'] / 15 / 15)) / 10) * \
                data['nbr_ckts'] * nbr_ph * nbr_conds * loss_factor * 8760 * 1e-6
    else:
        cond['corona_losses_mwh_per_m'] = 0

    return cond


def get_technically_feasible(conductors, data, environment, ld, specs, str_strength, include_unfeasible):

    environment['DC'] = True if specs['option'] == 'HVDC' else False
    nbr_conds = 1 if 'nbr_conductors' not in specs['structures'] else specs['structures']['nbr_conductors']

    current_a = data['power_mw'] * 1e3 / (specs['voltage'] * np.sqrt(3)) / data['nbr_ckts'] / nbr_conds if not environment['DC'] \
        else data['power_mw'] * 1e3 / specs['voltage'] / specs['nbr_phases'] / data['nbr_ckts'] / nbr_conds

    conductors = get_feasible(current_a, conductors, environment, include_unfeasible)

    # get losses
    if not conductors.empty:
        feasible = get_feasible_sag(conductors, data['max_sag_m'], data['span_m'], ld, include_unfeasible)
        if data['consider_corona']:
            feasible = get_feasible_corona(feasible, specs['structures'], environment, specs['voltage'], include_unfeasible) \
                if not feasible.empty else pd.DataFrame()
        if data['consider_str_type']:
            feasible = get_feasible_mechanical_loading(feasible, specs['structures'], specs['nbr_phases'], data['span_m'], str_strength) \
                                                if not feasible.empty else pd.DataFrame()

        feasible = feasible.apply(
            lambda r: losses_including_unfeasible(r, data, current_a, specs['voltage'], environment, specs['structures'], specs['nbr_phases']),
            axis=1
        )
        
        feasible['project'] = specs['option']
        feasible['peak_current'] = current_a

        return {'feasible': feasible}
    else:
        return {'feasible': pd.DataFrame()}



def npv(conductors, ec, specs, include_losses=True, years=100, filter_type=False):

    if not conductors.empty:
        nbr_conds = 1 if 'nbr_conductors' not in specs['structures'] else specs['structures']['nbr_conductors']
        str_data = specs['structures']
        if str_data and 'line_angle' in str_data:
            ec['cost_of_structures_unit'] = (str_data['str_tgt'] * str_data['str_tgt_cost']
                                          + str_data['str_ra'] * str_data['str_ra_cost']
                                          + str_data['str_nade'] * str_data['str_nade_cost']
                                          + str_data['str_ade'] * str_data['str_ade_cost']) / str_data['nbr_structures']
            ec['nbr_structures'] = str_data['nbr_structures']

        c = conductors.reset_index(drop=True)
        desired_cols = ['conductor', 'type', 'dol_per_1000_ft', 'inst_dol_per_1000_ft', 'str_costs_dol',
               'acess_dol_per_1000_ft', 'env_ampacity_a', 'peak_current', 'temp_at_current_c', 'max_temperature_c',
               'sag_m', 'tension_n', 'losses_at_peak_mwh_per_m', 'inception_voltage_kv', 'structure_type', 'total_force',
               'congestion_mw', 'corona_losses_mwh_per_m']
        existing_cols = c.columns.intersection(desired_cols)
        c = c[existing_cols].copy()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(years))
        npv['inflation'] = npv.year.apply(lambda x: (1+ec['inflation'])**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(specs['replace_st_at'], years, ec['structures_lifetime'])), 'structures_inv'] = 1
        npv.loc[npv.year.isin(range(specs['replace_cd_at'], years, ec['conductors_lifetime'])), 'conductors_inv'] = 1
        npv['cost_capital'] = npv['year'].apply(lambda x: 1/(1+ec['wacc'])**x)

        length_kft = ec['length_miles'] * 5.28
        conductor_inv = c.dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                    * length_kft * ec['number_ckts'] * specs['nbr_phases'] * nbr_conds
        conductor_inst = c.inst_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                    * length_kft * ec['number_ckts'] * specs['nbr_phases'] * nbr_conds
        conductor_access = c.acess_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                           * length_kft * ec['number_ckts'] * specs['nbr_phases'] * nbr_conds

        length_m = ec['length_miles'] * 1609.34

        if not ec['customize_inv_options']:
            # structures = npv['inflation'] * ec['cost_of_structures_unit'] * npv['structures_inv'] * ec['nbr_structures']
            structures = c.str_costs_dol.apply(lambda r: npv['inflation'] * ec['cost_of_structures_unit'] * npv['structures_inv'] * ec['nbr_structures'])
        else:
            structures = c.str_costs_dol.apply(lambda r: r * npv['inflation'] * npv['structures_inv'])

        if specs['option'] == 'Voltage Upgrade':
            npv['structures_upgd_inv'] = 0
            npv.at[0, 'structures_upgd_inv'] = 1
            # costs of structure upgrade (if any) are added to structures costs
            structures[0] = ec['cost_of_structures_upgd_unit'] * ec['nbr_structures'] \
                                    if specs['structure_upgrade'] else structures[0]
            # costs of substations and transformers modifications are also considered
            ss_transfo = ec['cost_of_ss_transfo'] * npv['inflation'] * npv['structures_upgd_inv']
            converters = npv['inflation'] * 0

        elif specs['option'] == 'HVDC':
            npv['structures_upgd_inv'] = 0
            npv.at[0, 'structures_upgd_inv'] = 1
            # costs of structure upgrade (if any) are added to structures costs
            structures[0] = ec['cost_of_structures_hvdc_unit'] * ec['nbr_structures'] \
                if specs['structure_upgrade'] else structures[0]
            # costs of converters are also considered
            converters = ec['cost_of_converters'] * npv['inflation'] * npv['structures_upgd_inv']
            ss_transfo = npv['inflation'] * 0

        else:
            ss_transfo = npv['inflation'] * 0
            converters = npv['inflation'] * 0

        if include_losses:
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

        c['project'] = specs['option']
        prj = c.join(prj)
        prj = prj.reset_index(drop=True).sort_values(by=[prj.columns[-1]])

        cost_st = structures * npv['cost_capital'] / 1e6
        # cost_st = cost_st.cumsum()
        # cost_st['project'] = specs['option']
        cost_st = prj[['conductor', 'type', 'project']].join(cost_st.cumsum(axis=1))
        cost_cd = (conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'] / 1e6
        cost_cd = prj[['conductor', 'type', 'project']].join(cost_cd.cumsum(axis=1))
        losses = losses * npv['cost_capital'] / 1e6
        losses = prj[['conductor', 'type', 'project']].join(losses.cumsum(axis=1))
        congestion = congestion * npv['cost_capital'] / 1e6
        congestion = prj[['conductor', 'type', 'project']].join(congestion.cumsum(axis=1))
        ss_transfo = ss_transfo * npv['cost_capital'] / 1e6
        ss_transfo = ss_transfo.cumsum()
        ss_transfo['project'] = specs['option']
        converters = converters * npv['cost_capital'] / 1e6
        converters = converters.cumsum()
        converters['project'] = specs['option']

        if filter_type:
            df = pd.DataFrame(columns=prj.columns)
            for t in prj.type.unique():
                df = pd.concat([df, prj.loc[prj.type == t].iloc[0].to_frame().T])
            prj = df

        cost_cd = cost_cd.loc[cost_cd.index.isin(prj.index)]
        losses = losses.loc[losses.index.isin(prj.index)]

        return {'projects': prj, 'cost_st': pd.DataFrame(cost_st), 'cost_cd': cost_cd, 'losses': losses,
                'cost_ss_tr': pd.DataFrame(ss_transfo), 'cost_cv': pd.DataFrame(converters), 'congestion': congestion}
    else:
        return {'projects': pd.DataFrame(), 'cost_st': pd.DataFrame(), 'cost_cd': pd.DataFrame(), 'losses': pd.DataFrame(),
                'cost_ss_tr': pd.DataFrame(), 'cost_cv': pd.DataFrame(), 'congestion': pd.DataFrame()}


def npv_existing(cond, ec, data, support_str, environment, loading, benefit_params, year_ref,
                 include_losses=True, years=100):

    nbr_conds = 1 if 'nbr_conductors' not in support_str else support_str['nbr_conductors']

    if support_str and 'line_angle' in support_str:
        ec['cost_of_structures_unit'] = (support_str['str_tgt'] * support_str['str_tgt_cost']
                                         + support_str['str_ra'] * support_str['str_ra_cost']
                                         + support_str['str_nade'] * support_str['str_nade_cost']
                                         + support_str['str_ade'] * support_str['str_ade_cost']) / support_str['nbr_structures']
        ec['nbr_structures'] = support_str['nbr_structures']

    current_a = data['power_mw'] / (data['voltage_kv'] * np.sqrt(3)) * 1e3 / ec['number_ckts'] / nbr_conds

    cond['env_ampacity_a'] = ieee_738_steady_state_rating(conductor=cond.loc[0], conditions=environment)
    cond['peak_current'] = current_a

    I_E = cond.loc[0]['env_ampacity_a'] # current in one conductor per phase of the existing line
    P_E = I_E * data['voltage_kv'] * np.sqrt(3) * data['nbr_ckts'] * nbr_conds * 1e-3

    t_E = (data['power_mw'] - P_E) / data['power_mw']

    x = ieee_738_steady_state_temperature(min(I_E, current_a), conductor=cond.loc[0], conditions=environment)
    x = pd.DataFrame(x).T.rename(columns={0: 'temp_at_current_c',
                                          1: 'res_at_current_ohm_per_m'})
    cond = cond.reset_index(drop=True).join(x)
    cond['sag_m'], cond['tension_n'], extra = cigre_324_sag(loading, conductor=cond.loc[0], span_m=data['span_m'])

    c = cond.reset_index(drop=True)
    desired_cols = ['conductor', 'type', 'dol_per_1000_ft', 'inst_dol_per_1000_ft', 'acess_dol_per_1000_ft',
           'env_ampacity_a', 'peak_current', 'temp_at_current_c', 'max_temperature_c', 'sag_m',
           'inception_voltage_kv', 'tension_n', 'structure_type', 'total_force']
    existing_cols = c.columns.intersection(desired_cols)
    c = c[existing_cols].copy()

    npv = pd.DataFrame(columns=['year'])
    npv['year'] = list(range(years))
    npv['inflation'] = npv.year.apply(lambda x: (1+ec['inflation'])**x)

    npv[['structures_inv', 'conductors_inv']] = 0
    npv.loc[npv.year.isin(range(ec['structures_life'], years, ec['structures_lifetime'])), 'structures_inv'] = 1
    npv.loc[npv.year.isin(range(ec['conductors_life'], years, ec['conductors_lifetime'])), 'conductors_inv'] = 1
    npv['cost_capital'] = npv['year'].apply(lambda x: 1/(1+ec['wacc'])**x)

    length_kft = ec['length_miles'] * 5.28
    conductor_inv = c.dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                        * length_kft * ec['number_ckts'] * 3 * nbr_conds
    conductor_inst = c.inst_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                        * length_kft * ec['number_ckts'] * 3 * nbr_conds
    conductor_access = c.acess_dol_per_1000_ft.apply(lambda  r: r * npv['inflation'] * npv['conductors_inv']) \
                                                        * length_kft * ec['number_ckts'] * 3 * nbr_conds

    length_m = ec['length_miles'] * 1609.34
    structures = c.dol_per_1000_ft.apply(
            lambda r: npv['inflation'] * ec['cost_of_structures_unit'] * npv['structures_inv'] * ec['nbr_structures'])

    # losses and congestion costs
    loss_factor = 0.3 * data['load_factor'] + 0.7 * data['load_factor'] ** 2  # coeffs set to 0.15 and 0.85 in case of distribution
    if (data['power_mw'] - P_E) > 0:
        # loss factor at the congested line
        load_factor_1 = (1 + t_E) / 2
        loss_factor_1 = 0.3 * load_factor_1 + 0.7 * load_factor_1 ** 2

        # line resistance and loss factor at the neighboring line which takes on the congestion power from existing line
        R = 8.63 * 1e-5 # ACSR DRAKE at 75 deg. Cel

        c['losses_at_peak_mwh_per_m'] = (I_E**2 * cond['res_at_current_ohm_per_m'] * loss_factor_1 + \
                                            (current_a - I_E)**2 * R * loss_factor) \
                                        * ec['number_ckts'] * 3 * nbr_conds * 8760 * 1e-6
        congestion = npv['inflation'] * (data['power_mw'] - P_E) * t_E / 2 * ec['cost_congestion'] * 8760
    else:
        c['losses_at_peak_mwh_per_m'] = cond['res_at_current_ohm_per_m'] * current_a ** 2 \
                                             * loss_factor * ec['number_ckts'] * 3 * nbr_conds * 8760 * 1e-6
        congestion = npv['inflation'] * 0

    if data['consider_corona']:
        environment['DC'] = False
        c['inception_voltage_kv'], c['voltage_gradient_kv_cm'] = corona(cond['diameter_mm'] / 2 * 0.1, support_str, environment)

        # Geometrical mean distanche (GMD) between phases, in centimeter
        gmd = pow(support_str['dist_a_b_m'] * support_str['dist_b_c_m'] * support_str['dist_a_c_m'], 1 / 3) * 1e2
        # Air correction factor
        delta = 293 / (273 + environment['ambient_temperature_c']) * np.exp(-0.00012 * environment['elevation_m'])
        c['corona_losses_mwh_per_m'] = \
            241 / delta * (60 + 25) * np.sqrt(cond['diameter_mm'] / 2 * 0.1 / gmd) \
                * pow((max(data['voltage_kv'] - c['inception_voltage_kv'].iloc[0], 0)) / np.sqrt(3), 2) * 1e-5 \
                    * ec['number_ckts'] * 3 * nbr_conds * loss_factor * 8760 * 1e-6
    else:
        c['corona_losses_mwh_per_m'] = 0

    if include_losses:
        losses = c.losses_at_peak_mwh_per_m.apply(lambda r: (r + c['corona_losses_mwh_per_m'].iloc[0]) * npv['inflation']
                                                            * ec['cost_of_losses_dol_per_mwh'] * length_m)
    else:
        losses = c.losses_at_peak_mwh_per_m.apply(lambda r: r * npv['inflation'] * 0)

    prj = (structures + conductor_inv + conductor_inst + conductor_access + losses + congestion) * npv['cost_capital']

    # get cumulative sum in millions
    prj = prj.cumsum(axis=1) / 1e6
    prj['project'] = 'Existing'
    prj = c.join(prj)
    prj['type'] = 'Existing'
    prj['conductor'] = 'Conductor'

    cost_st = structures * npv['cost_capital'] / 1e6
    cost_st = prj[['conductor', 'type', 'project']].join(cost_st.cumsum(axis=1))
    cost_cd = (conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'] / 1e6
    cost_cd = prj[['conductor', 'type', 'project']].join(cost_cd.cumsum(axis=1))
    losses = losses * npv['cost_capital'] / 1e6
    losses = prj[['conductor', 'type', 'project']].join(losses.cumsum(axis=1))
    congestion = congestion * npv['cost_capital'] / 1e6
    congestion = pd.DataFrame({0: congestion}).T
    congestion = prj[['conductor', 'type', 'project']].join(congestion.cumsum(axis=1))

    cond['project'] = 'Existing'
    benefit = benefits(cond, data, benefit_params, year_ref, data['voltage_kv'])['benefits']

    return {'projects': prj, 'cost_st': pd.DataFrame(cost_st), 'cost_cd': cost_cd,
            'losses': losses, 'congestion': congestion, 'benefits': benefit}


def benefits(conductors, data, benefit_params, year_ref, voltage):
    if not conductors.empty:
        benefit_params['delta_capacity_mw'] = (benefit_params['load_ratio'] - 1) * data['power_mw']
        conductors['delta_ampacity_mw'] = conductors['env_ampacity_a'] * voltage * 1e-3 \
                                                            * np.sqrt(3) * data['nbr_ckts'] - data['power_mw']
        benefits = pd.merge(benefit_params, conductors, how='cross')

        benefits['res_integration_gwh'] = benefits.apply(lambda r:
             min(r['delta_ampacity_mw'], max(r['delta_capacity_mw'], 0)) * r['load_factor'] * 8760 * 1e-3 * \
                (r['res_fraction'] - benefits.loc[benefits.year == year_ref].iloc[0]['res_fraction']) / 100,
             axis=1)
        benefits['co2_emissions_ton'] = benefits.apply(lambda r:
             min(r['delta_ampacity_mw'], max(r['delta_capacity_mw'], 0)) * r['load_factor'] * 8760 * 1e-3 * \
                (r['load_co2e_kg_per_mwh'] - benefits.loc[benefits.year == year_ref].iloc[0]['load_co2e_kg_per_mwh']) / 100,
             axis=1)

        return {'benefits': benefits}

    else:
        return {'benefits': pd.DataFrame()}


import sys
sys.path.append('./plsxml_')
from plsxml_ import PLSXML

def get_unit_conversion():
    return pd.read_csv('unit_conversion.csv',
                       index_col='Quantity', encoding='latin-1')

def file_to_project(file_location):
    data_dict = {
        'power_mw': 250.0,
        'nbr_ckts': 1,
        'load_factor': 0.63,
    }
    # Imports from TVA's new templates

    # if import_prj_data is not None:
    tables = ['cable_data_report',
              'combined_bill_of_material_of_new_items_for_structure',
              'construction_staking_report',
              'stringing_chart_summary'
              ]
    # tables = ['cable_data_report',
    #           'circuit_and_phase_definitions_and_labels',
    #           'combined_bill_of_material_of_new_items_for_structure',
    #           'construction_staking_report',
    #           'detailed_pole_loading_data',
    #           'overturning_moment_summary_for_all_load_cases',
    #           'overturning_moments_for_user_input_concentrated_loads',
    #           'pole_steel_properties',
    #           'relative_attachment_labels_for',
    #           'sag_tension_report_for_all_sections',
    #           'section_geometry_data',
    #           'section_sagging_data',
    #           'stringing_chart_summary'
    #           ]

    # xml = PLSXML(import_prj_data.name, tables=tables)
    print(file_location)
    xml = PLSXML(file_location, tables=tables)

    general_data = xml['stringing_chart_summary']

    general_data = general_data.loc[(general_data['temp_deg F'] == 70)].drop_duplicates(
        subset=['span_from_str', 'span_to_str', 'temp_deg F'],
        keep='first'
    )

    staking_table = xml['construction_staking_report']
    staking_table = staking_table.loc[staking_table['stake_description'] == 'Structure Hub']

    data_dict.update({
        'voltage_kv': general_data['sec_voltage_kV'].max(),
        'length_km': general_data['span_length_ft'].sum() * 3.048 * 1e-4,
        'avg_span_m': general_data['span_length_ft'].mean() * 0.3048,
        'span_m': general_data['span_length_ft'].max() * 0.3048,
        'nbr_structures': len(general_data['span_from_str']),
        'max_sag_m': general_data['mid_span_sag_ft'].max() * 0.3048,
        'str_height_m': (staking_table['structure_height_or_pole_length_ft'] - staking_table[
            'actual_embedded_depth_ft']).max() * 0.3048,
        'elevation_m': staking_table['z_elevation_ft'].mean() * 0.3048,
        'latitude': staking_table['latitude_deg'].mean(),
        'longitude': staking_table['longitude_deg'].mean(),
        'latitude1': staking_table['latitude_deg'].max(),
        'longitude1': staking_table['longitude_deg'].max()
    })

    conds_table = xml['cable_data_report'][
        ['description',
         'cable_name',
         'stock_number',
         'cross_section_area_in^2',
         'outside_diameter_in',
         'unit_weight_lbs/ft',
         'ultimate_tension_lbs',
         'temp_1_deg F',
         'temp_2_deg F',
         'dc_temp_deg F',
         'resistance_1_Ohm/mile',
         'resistance_2_Ohm/mile',
         'dc_resistance_Ohm/mile',
         'outer_mod_of_elast_psi/100',
         'outer_thermal_expansion_coeff_/100 deg',
         'emissivity_coeff',
         'solar_absorption_coeff'
         ]
    ]
    data_dict.update({
        'emissivity': conds_table['emissivity_coeff'].iloc[0],
        'solar_absorptivity': conds_table['solar_absorption_coeff'].iloc[0]
    })

    conds_cost_table = xml['combined_bill_of_material_of_new_items_for_structure'][
        ['stock_number', 'material_unit_cost']].drop_duplicates()
    conds_table = pd.merge(conds_table, conds_cost_table, how='left', on='stock_number').fillna(0)

    units = get_unit_conversion()
    non_numeric_cols = ['description', 'cable_name', 'stock_number', 'emissivity_coeff', 'solar_absorption_coeff']
    unit_conversion_factors = pd.Series(
        [645.16,
         25.4,
         1 / units.loc['n_lbs']['to_Imperial'] * 1 / units.loc['m_ft']['to_Imperial'],
         1 / units.loc['n_lbs']['to_Imperial'] * 1e-3,
         5 / 9,
         5 / 9,
         5 / 9,
         1 / 1609.34,
         1 / 1609.34,
         1 / 1609.34,
         6894.76 * 1e-7,
         1e-2 * 1.8,
         1e3],
        index=[elem for elem in conds_table.columns if elem not in non_numeric_cols]
    )

    conversion_table = conds_table.loc[:, ~conds_table.columns.isin(non_numeric_cols)].copy()
    conversion_table[
        ['temp_1_deg F', 'temp_2_deg F', 'dc_temp_deg F']] -= 32  # prepare conversion from deg F to deg C
    conversion_table = conversion_table.mul(unit_conversion_factors)
    conds_table = conds_table[['description', 'cable_name']].join(conversion_table)

    conds_table = conds_table.rename(columns={
        'description': 'type',
        'cable_name': 'conductor',
        'cross_section_area_in^2': 'area_mm2',
        'outside_diameter_in': 'diameter_mm',
        'unit_weight_lbs/ft': 'weight_n_per_m',
        'ultimate_tension_lbs': 'conductor_rts_kn',
        'temp_1_deg F': 'temp_low_c',
        'temp_2_deg F': 'temp_high_c',
        'dc_temp_deg F': 'temp_dc_c',
        'dc_resistance_Ohm/mile': 'res_dc_ohm_per_m',
        'resistance_1_Ohm/mile': 'res_low_ohm_per_m',
        'resistance_2_Ohm/mile': 'res_high_ohm_per_m',
        'outer_mod_of_elast_psi/100': 'ElasticModulus_GPa',
        'outer_thermal_expansion_coeff_/100 deg': 'CoeffThermalExpan_per_Cel',
        'material_unit_cost': 'dol_per_1000_ft'
    })
    conds_table['max_temperature_c'] = conds_table['temp_high_c'] + 25
    conds_table[['inst_dol_per_1000_ft', 'acess_dol_per_1000_ft', 'str_costs_dol']] = 0

    # data_dict['conductors'] = conds_table

    data = pd.DataFrame(data_dict, index=[0])

    return {'data': data, 'conductors': conds_table}


from shapely.geometry import Point
import geopandas as gpd

def get_iso_rto():
    return gpd.read_file('input_data_raw/Independent_System_Operator.geojson')

def iso_rto_zone(zones, point_coords):
    # Define the point you want to check
    point = Point(point_coords)

    zones = zones[zones.geometry.type == 'MultiPolygon']
    matches = list(zones[zones.contains(point)]['NAME_abbr'])

    # Report results
    if not matches:
        print(f"The point {point_coords} is not inside any multipolygon.")
    else:
        print(f"The point is contained in multipolygons with indices: {matches}")

    return matches

def part1_fetch_congestion_cost(ln):
    zones = get_iso_rto()

    zones['geometry'] = zones['geometry'].buffer(0)
    zones['NAME_abbr'] = ['MISO', 'SPP', 'PJM', 'ERCOT', 'CAISO', 'ISONE', 'NYISO']

    fr_zones = iso_rto_zone(zones, (ln['long_fr'], ln['lat_fr']))
    to_zones = iso_rto_zone(zones, (ln['long_to'], ln['lat_to']))

    inter_zone = {tuple(sorted((x, y))) for x in fr_zones for y in to_zones if x != y}
    inter_zone_labels = {f'{z[0]}--{z[1]}': z for z in inter_zone}

    list_zones = ["Non-ISO"] + list(set(fr_zones + to_zones)) + list(inter_zone_labels.keys())

    return {'list_zones': list_zones, 'inter_zone_labels': inter_zone_labels}


from scipy.spatial import KDTree
def congestion_cost_iso_rto(df, ln):
    # Find link entries having one cood (x1,y1) closest to starting point of the line
    coordinates = df[['y1', 'x1']].to_numpy()
    tree = KDTree(coordinates)

    lat_fr = ln['lat_fr']
    long_fr = ln['long_fr']
    fr_point = np.array([lat_fr, long_fr])

    distance, index = tree.query(fr_point)

    closest_location = df.iloc[index]
    temp = dict(closest_location[['x1', 'y1']])
    temp1 = df.loc[(df.x1 == temp['x1']) & (df.y1 == temp['y1'])]

    # Among the resulting links, select the link with the closest other end (x2,y2) to the ending point of the line
    tree1 = KDTree(temp1[['x2', 'y2']].to_numpy())

    lat_to = ln['lat_to']
    long_to = ln['long_to']
    to_point = np.array([lat_to, long_to])

    distance1, index = tree1.query(to_point)

    closest_location1 = temp1.iloc[index]

    from geopy.distance import geodesic
    # Calculate distances
    distance = geodesic((closest_location['y1'], closest_location['x1']), (lat_fr, long_fr)).km
    distance1 = geodesic((lat_to, long_to), (closest_location1['y2'], closest_location1['x2'])).km

    return closest_location1['mean_abs_price_diff'] if distance <= 50 and distance1 <= 50 else 1.0

def part2_fetch_congestion_cost(zone, ln):
    if not isinstance(zone, str):
        df = pd.read_csv(f'input_data_raw/mean_price_diff_interRegional_2019-2023_in_$2023_SJ_20250715.csv')
        mask = ((df['from_zone'] == zone[0]) & (df['to_zone'] == zone[1])) | \
               ((df['from_zone'] == zone[1]) & (df['to_zone'] == zone[0]))
        congestion_cost = df.loc[mask, 'abs_mean_price_diff'].values[0] if mask.any() else 10
    else:
        congestion_cost = congestion_cost_iso_rto(pd.read_csv(
            f"input_data_raw/multi_year_ave_{zone}_2019_2023_in_$2023_SJ_20250122.csv"),
            ln) if zone != 'Non-ISO' and (20 <= ln['length_km'] <= 80) else 1.0

    return {'congestion_cost': congestion_cost if congestion_cost != None else 1.0}