from .line_structure import LineStructure
from .conductor import Conductor
from pydantic import BaseModel
import pandas as pd
import numpy as np


class Line(BaseModel):
    structure: LineStructure
    conductor: Conductor

    def __getattr__(self, name):
        conductor = object.__getattribute__(self, "conductor")
        structure = object.__getattribute__(self, "structure")
        if hasattr(conductor, name):
            return getattr(conductor, name)
        if hasattr(structure, name):
            return getattr(structure, name)
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    #######
    # Ampacity Calculation
    #######
    def _solar_heat_gain(self):

        #  ### solar heat gain ###
        date = self.date
        lat = self.latitude
        atm = self.atmosphere
        alpha = self.solar_absorptivity
        elevation = self.elevation_m
        area = self.diameter_mm / 1e3  # in m they are the same
        dir_angle = self.cw_angle_direction_rel_to_north

        # solar angle and declination
        day_year = date.timetuple().tm_yday
        solar_dec = 23.45 * np.sin(np.radians((284 + day_year) * 360.0 / 365.0))
        hour_angle = 15.0 * (self.hour - 12)

        # solar altitude
        h_c = np.degrees(np.arcsin(
            np.cos(np.radians(lat)) * np.cos(np.radians(solar_dec))
            * np.cos(np.radians(hour_angle))
            + np.sin(np.radians(lat)) * np.sin(np.radians(solar_dec))
        ))

        # heat flux
        solar_heat_flux = atm["A"] + atm["B"] * h_c + atm["C"] * h_c ** 2 \
                          + atm["D"] * h_c ** 3 + atm["E"] * h_c ** 4 \
                          + atm["F"] * h_c ** 5 + atm["G"] * h_c ** 6
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


    def _current_at_temperature(self, t_test, q_s, k_angle, is_dc=False):

        # conductor inputs
        diameter = self.diameter_mm / 1e3
        res_low = self.res_low_ohm_per_m
        t_low = self.temp_low_c
        res_high = self.res_high_ohm_per_m
        t_high = self.temp_high_c
        emissivity = self.emissivity

        # environment inputs
        t_a = self.ambient_temperature_c
        wind_speed = self.wind_speed_m_per_s
        elevation = self.elevation_m

        # temperature
        t_film = (t_test + t_a) / 2.0

        # dynamic viscosity
        mu_f = 1.458e-6 * (t_film + 273) ** 1.5 / (t_film + 383.4)

        # air-density
        rho_f = (1.293 - 1.525e-4 * elevation + 6.379e-9 * elevation ** 2
                 ) / (1 + 0.00367 * t_film)

        # thermal conductivity
        k_f = 2.424e-2 + 7.477e-5 * t_film - 4.407e-9 * t_film ** 2

        # reynolds number
        n_re = diameter * rho_f * wind_speed / mu_f

        # forced convection
        q_c1 = k_angle * (1.01 + 1.35 * n_re ** 0.52) * k_f * (t_test - t_a)
        q_c2 = k_angle * (0.754 * n_re ** 0.6) * k_f * (t_test - t_a)

        # natural convection
        q_cn = 3.645 * rho_f ** 0.5 * diameter ** 0.75 * (t_test - t_a) ** 1.25
        q_c = max(q_c1, q_c2, q_cn)

        # radiated heat loss
        q_r = 17.8 * diameter * emissivity \
              * (((t_test + 273) / 100) ** 4 - ((t_a + 273) / 100) ** 4)

        if not is_dc:
            r_tc = ((res_high - res_low) / (t_high - t_low)) * (t_test - t_low) + res_low
        else:
            r_tc = self.res_dc_ohm_per_m * (
                    1 + self.temp_coeff_resistivity * (t_test - self.temp_dc_c)
            )

        x = (q_c + q_r - q_s) / r_tc
        if x > 0:
            i = np.sqrt(x)
        else:
            i = 0

        return r_tc, i


    def _ieee_738_steady_state_rating(self, is_dc=False):

        wind_angle = self.wind_angle
        t_c = self.max_temperature_c

        # solar heat gain
        q_s = self._solar_heat_gain()

        # wind direction factor
        k_angle = 1.194 - np.cos(np.radians(wind_angle)) \
                  + 0.194 * np.cos(np.radians(2 * wind_angle)) \
                  + 0.368 * np.sin(np.radians(2 * wind_angle))

        r_tc, i = self._current_at_temperature(t_c, q_s, k_angle, is_dc=is_dc)

        return i

    def _ieee_738_steady_state_temperature(self, current_a, is_dc=False):

        # Calculate initial(steady - state) conductor temperature
        # from the steady-state load current, using a binary search

        tc_min = self.ambient_temperature_c
        r_tc = self.res_low_ohm_per_m
        wind_angle = self.wind_angle

        i_ss_threshold = 0.01
        tc_max = 300
        i_ss_result = 0.0

        # solar heat gain
        q_s = self._solar_heat_gain()

        # wind direction factor
        k_angle = 1.194 - np.cos(np.radians(wind_angle)) \
            + 0.194 * np.cos(np.radians(2 * wind_angle)) \
            + 0.368 * np.sin(np.radians(2 * wind_angle))

        t_test = tc_max
        counter = 0
        while ((i_ss_result > current_a + i_ss_threshold)
                or (i_ss_result < current_a - i_ss_threshold)) and counter<50:

            t_test = (tc_max + tc_min) / 2

            r_tc, i_ss_result = np.real(
                self._current_at_temperature(t_test, q_s, k_angle,  is_dc=is_dc)
            )

            if i_ss_result == current_a:
                break
            elif i_ss_result > current_a:
                tc_max = t_test
            else:
                tc_min = t_test
            counter += 1

        return t_test, r_tc

    def _cigre_324_sag(self, loading_conditions, initial_tension_percentage, temp_at_current_c):

        diameter = self.diameter_mm / 1e3
        A = self.area_mm2 / 1e6
        W0 = self.weight_n_per_m
        alpha = self.coeff_thermal_expan_per_cel
        E = self.elastic_modulus_gpa * 1e9
        S = self.span_m
        H0 = initial_tension_percentage * self.conductor_rts_kn * 1e3
        T0 = loading_conditions.initial_temperature_c

        T1 = temp_at_current_c

        ice_density = loading_conditions.ice_density_kg_per_m3
        Ice_Ld = loading_conditions.ice_thickness_m
        Wind_Ld = loading_conditions.pressure_pa
        Additive_Ld = loading_conditions.additive_loading_n_per_m

        sag0 = H0 / W0 * (np.cosh(W0 * S / 2 / H0) - 1)  # calculate initial sag (without loading)
        L0 = S + 8 * pow(sag0, 2) / 3 / S  # deduce initial length

        W_ice = ice_density * np.pi * (
                    pow(diameter + 2 * Ice_Ld, 2) - pow(diameter, 2)) / 4 * 9.81  # ice density*ice volume*g (N/m)
        W_wind = Wind_Ld * (diameter + 2 * Ice_Ld)
        W1 = np.sqrt(pow(W0 + W_ice, 2) + pow(W_wind, 2)) + Additive_Ld

        Lref = L0 * (1 - H0 / E / A)
        L1 = Lref * (1 + alpha * (T1 - T0))  # estimate of new length based on temp. difference

        sag1 = np.sqrt(3 * S * abs(L1 - S) / 8)

        sag1_temp = 0

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

        return sag1, H1, {'W0': W0, 'W1': W1, 'H0': H0, 'H1': H1,
                          'W_ice': W_ice, 'W_wind': W_wind, 'T1': T1}

    def calculate_sag(self, loading_conditions, initial_tension_percentage,
                       current_a=None, temp_at_current_c=None, is_dc=False):

        if temp_at_current_c is not None:
            pass
        elif current_a is not None:
            temp = self._ieee_738_steady_state_temperature(current_a, is_dc=is_dc)
            temp_at_current_c = temp[0]
        else:
            raise ValueError("Either temp_at_current_c or current_a "
                             "must be provided for sag calculations")

        sag, tension, extra = self._cigre_324_sag(
            loading_conditions, initial_tension_percentage, temp_at_current_c
        )

        return sag