import numpy as np
import datetime as dt
from pathlib import Path
from typing import Literal, Optional, List, Dict
import pandas as pd
from pydantic import BaseModel, Field, root_validator, validator
from conductor import Conductor
from utils import load_conductors


# ----------------------------------------------------------------------
# 1️ - Low‑level building blocks (one model per tab or logical parameter group)
# ----------------------------------------------------------------------
class GeneralData(BaseModel):
    """Data‑tab – basic project requirements."""
    power_mw: float = Field(..., ge=50, le=10_000, description="MW capacity")
    voltage_kv: float = Field(..., ge=60, le=1_000, description="Operating voltage")
    nbr_ckts: int = Field(..., ge=1, le=3, description="Number of circuits")
    length_km: float = Field(..., gt=0, description="Line length (km)")
    nbr_structures: int = Field(..., ge=1, description="Number of structures (auto‑calculated)")
    avg_span_m: float = Field(..., gt=0, description="Ruling span (m)")
    span_m: float = Field(..., gt=0, description="Maximum span (m)")
    max_sag_m: float = Field(..., gt=0, description="Maximum sag (m)")
    consider_losses: bool = False
    load_factor: float = Field(..., ge=0, le=1, description="Load factor")
    consider_corona: bool = False
    consider_str_type: bool = False

    # @model_validator(mode="after")
    # def _validate_spans_and_length(cls, values):
    #     avg = values.avg_span_m
    #     max_span = values.span_m
    #     length = values.length_km

    #     if max_span < avg:
    #         raise ValueError('Max span must be greater than or equal to average span.')
    #     if length <= max_span / 1_000:
    #         raise ValueError('Length must be greater than the specified span (km).')
    #     return values
        


class Environment(BaseModel):
    """Env‑tab – weather & geographic data."""
    date: dt.date = Field(default_factory=dt.date.today)
    latitude: float = Field(..., ge=-90, le=90)
    elevation_m: float = Field(..., ge=0)
    wind_speed_m_per_s: float = Field(..., ge=0)
    wind_angle: int = Field(..., ge=0, le=90)
    cw_angle_direction_rel_to_north: int = Field(..., ge=0, le=90)
    hour: int = Field(..., ge=0, le=24)
    atmosphere: Literal["Clear", "Industrial"] = "Clear"
    ambient_temperature_c: float = Field(...)


class Loading(BaseModel):
    """Loading‑tab – mechanical loading profile."""
    initial_tension_percentage: float = Field(..., ge=0.1, le=0.50)  # stored as fraction
    initial_temperature_c: float = Field(..., ge=-60, le=60)
    wind_ice_temperature_c: Optional[float] = None
    pressure_pa: float = 0
    ice_thickness_m: float = 0
    ice_density_kg_per_m3: float = 0
    additive_loading_n_per_m: float = 0
    # … add any other fields you need (e.g. cost_of_losses, etc.) …


class AdvancedOptions(BaseModel):
    """Advanced‑tab – corona & custom structure options."""
    consider_corona: bool = False
    dist_a_b_m: Optional[float] = None  # Phase‑to‑Phase A‑B (m)
    nbr_conductors: Optional[int] = None
    dist_b_c_m: Optional[float] = None
    weather_corr_factor: Optional[float] = None
    dist_a_c_m: Optional[float] = None
    rigosity_coeff: Optional[float] = None
    # If the user checks “different structure types”, we later attach a list of StructureSpec objects.
    structures: Optional[List[Dict]] = None  # free‑form – you can replace with a proper sub‑model


# ----------------------------------------------------------------------
# 2️ - Top‑level “master” config that glues everything together
# ----------------------------------------------------------------------
class Line(Conductor, GeneralData, Environment, Loading):
    """All parameters that the REFA core logic needs."""
    # existing_conductor: Optional[Conductor] = None
    # advanced: AdvancedOptions = Field(default_factory=AdvancedOptions)
    dc: bool = False
    nbr_phases: int = 3
    conductors_list: Optional[List[Conductor]] = None
    
    # @root_validator(pre=True)
    # def _unwrap(cls, values):
    #     # automatically strip a single top‑level wrapper key
    #     if len(values) == 1:
    #         (only_key,) = values.keys()
    #         inner = values[only_key]
    #         if isinstance(inner, dict):
    #             return inner
    #     return values

    # ----- Helper methods for calculations (called by the main calculation methods) -----    
    
    def _solar_heat_gain(self,cond):

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
                    "G": 1.3236e-8}
        }

        #  ### solar heat gain ###
        date = self.date
        lat = self.latitude
        at = self.atmosphere
        alpha = cond["solar_absorptivity"]
        elevation = self.elevation_m
        area = cond["diameter_mm"] / 1e3 # in m they are the same
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


    def _current_at_temperature(self, t_test, q_s, k_angle, cond):

        # conductor inputs
        diameter = cond["diameter_mm"] / 1e3
        res_low = cond["res_low_ohm_per_m"]
        t_low = cond["temp_low_c"]
        res_high = cond["res_high_ohm_per_m"]
        t_high = cond["temp_high_c"]
        emissivity = cond["emissivity"]

        # environment inputs
        t_a = self.ambient_temperature_c
        wind_speed = self.wind_speed_m_per_s
        elevation = self.elevation_m

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

        if not self.dc:
            r_tc = ((res_high - res_low) / (t_high - t_low)) * (t_test - t_low) + res_low
        else:
            r_tc = cond['res_dc_ohm_per_m'] * (1 + self.temp_coeff_resistivity * (t_test - cond['temp_dc_c']))

        x = (q_c+q_r-q_s)/r_tc
        if x > 0:
            i = np.sqrt(x)
        else:
            i = 0

        return r_tc, i


    def _ieee_738_steady_state_rating(self, cond):

        wind_angle = self.wind_angle
        t_c = cond['max_temperature_c']

        # solar heat gain
        q_s = self._solar_heat_gain(cond)

        # wind direction factor
        k_angle = 1.194 - np.cos(np.radians(wind_angle)) \
            + 0.194 * np.cos(np.radians(2 * wind_angle)) \
            + 0.368 * np.sin(np.radians(2 * wind_angle))

        r_tc, i = self._current_at_temperature(t_c, q_s, k_angle, cond)

        return i


    def _ieee_738_steady_state_temperature(self, current_a, cond):

        # Calculate initial(steady - state) conductor temperature
        # from the steady-state load current, using a binary search

        tc_min = self.ambient_temperature_c
        r_tc = cond["res_low_ohm_per_m"]
        wind_angle = self.wind_angle

        i_ss_threshold = 0.01
        tc_max = 300
        i_ss_result = 0.0

        # solar heat gain
        q_s = self._solar_heat_gain(cond)

        # wind direction factor
        k_angle = 1.194 - np.cos(np.radians(wind_angle)) \
            + 0.194 * np.cos(np.radians(2 * wind_angle)) \
            + 0.368 * np.sin(np.radians(2 * wind_angle))

        t_test = tc_max
        counter = 0
        while ((i_ss_result > current_a + i_ss_threshold) \
                or (i_ss_result < current_a - i_ss_threshold)) and counter<50:

            t_test = (tc_max + tc_min) / 2

            r_tc, i_ss_result = np.real(self._current_at_temperature(t_test, q_s, k_angle, cond))

            if i_ss_result == current_a:
                break
            elif i_ss_result > current_a:
                tc_max = t_test
            else:
                tc_min = t_test
            counter += 1

        return t_test, r_tc
    
        
    def _cigre_324_sag(self, cond):

        diameter = cond["diameter_mm"] / 1e3
        A = cond['area_mm2'] / 1e6
        W0 = cond['weight_n_per_m']
        alpha = cond['coeff_thermal_expan_per_cel']
        E = cond['elastic_modulus_gpa'] * 1e9
        S = self.span_m
        H0 = self.initial_tension_percentage * cond['conductor_rts_kn'] * 1e3
        T0 = self.initial_temperature_c

        T1 = cond['temp_at_current_c']

        ice_density = self.ice_density_kg_per_m3
        Ice_Ld = self.ice_thickness_m
        Wind_Ld = self.pressure_pa
        Additive_Ld = self.additive_loading_n_per_m

        sag0 = H0 / W0 * (np.cosh(W0 * S / 2 / H0)-1) # calculate initial sag (without loading)
        L0 = S + 8 * pow(sag0, 2) / 3 / S # deduce initial length

        W_ice = ice_density * np.pi * (pow(diameter + 2*Ice_Ld, 2) - pow(diameter, 2)) / 4 * 9.81 # ice density*ice volume*g (N/m)
        W_wind = Wind_Ld * (diameter + 2*Ice_Ld)
        W1 = np.sqrt(pow(W0+W_ice, 2) + pow(W_wind, 2)) + Additive_Ld

        Lref = L0 * (1 - H0 / E / A)
        L1 = Lref * (1 + alpha * (T1 - T0)) # estimate of new length based on temp. difference

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

        return sag1, H1, {'W0': W0, 'W1': W1, 'H0':H0, 'H1': H1, 'W_ice': W_ice, 'W_wind': W_wind, 'T1': T1}


    # evaluate losses and congestion
    def _resistive_line_losses(self, cond, current_a, voltage, load_factor, nbr_ckts=1, nbr_ph=3, support_str={}):
        
        nbr_conds = 1 if 'nbr_conductors' not in support_str else support_str['nbr_conductors']
        self.power_mw = current_a * voltage * np.sqrt(3) * nbr_ckts * nbr_conds * 1e-3 if not self.dc \
                else current_a * voltage * nbr_ph * nbr_ckts * nbr_conds * 1e-3

        I_E = cond['env_ampacity_a'] if 'env_ampacity_a' in cond else self._ieee_738_steady_state_rating(cond=cond) # current in one conductor per phase of the existing line
        P_E = I_E * voltage * np.sqrt(3) * nbr_ckts * nbr_conds * 1e-3 if not self.dc \
                else I_E * voltage * nbr_ph * nbr_ckts * nbr_conds * 1e-3
        
        t_E = (self.power_mw - P_E) / self.power_mw
        loss_factor = 0.3 * load_factor + 0.7 * load_factor ** 2  # coeffs set to 0.15 and 0.85 in case of distribution

        res_at_current_ohm_per_m = cond['res_at_current_ohm_per_m'] if 'res_at_current_ohm_per_m' in cond else self._ieee_738_steady_state_temperature(current_a=current_a, cond=cond)[1]
        if (self.power_mw - P_E) > 0:
            # loss factor at the congested line
            load_factor_1 = (1 + t_E) / 2
            loss_factor_1 = 0.3 * load_factor_1 + 0.7 * load_factor_1 ** 2

            # line resistance and loss factor at the neighboring line which takes on the congestion power from existing line
            R = 8.63 * 1e-5  # ACSR DRAKE at 75 deg. Cel

            losses_at_peak_mwh_per_m = (res_at_current_ohm_per_m * I_E ** 2 * loss_factor_1 + \
                                                (current_a - I_E) ** 2 * R * loss_factor) \
                                            * nbr_ckts * nbr_ph * nbr_conds * 8760 * 1e-6
        else:
            losses_at_peak_mwh_per_m = res_at_current_ohm_per_m * current_a ** 2 \
                                                    * loss_factor * nbr_ckts * nbr_ph * nbr_conds * 8760 * 1e-6
 
        return losses_at_peak_mwh_per_m


    def _congestion(self, cond, current_a, voltage, nbr_ckts=1, nbr_ph=3, support_str={}):
            
        nbr_conds = 1 if 'nbr_conductors' not in support_str else support_str['nbr_conductors']
        self.power_mw = current_a * voltage * np.sqrt(3) * nbr_ckts * nbr_conds * 1e-3 if not self.dc \
                else current_a * voltage * nbr_ph * nbr_ckts * nbr_conds * 1e-3
        
        I_E = cond['env_ampacity_a'] if 'env_ampacity_a' in cond else self._ieee_738_steady_state_rating(cond=cond) # current in one conductor per phase of the existing line
        P_E = I_E * voltage * np.sqrt(3) * nbr_ckts * nbr_conds * 1e-3 if not self.dc \
                else I_E * voltage * nbr_ph * nbr_ckts * nbr_conds * 1e-3
        
        t_E = (self.power_mw - P_E) / self.power_mw
        if (self.power_mw - P_E) > 0:
            congestion_mw = (self.power_mw - P_E) * t_E / 2
        else:
            congestion_mw = 0

        return congestion_mw



    # ----- Main calculation methods -----
    
    def calculate_ampacity(self, current_a, only_feasible_conds=False, conds_subset=pd.DataFrame()):

        conductors = conds_subset if not conds_subset.empty else \
                        pd.DataFrame.from_records([cond.dict() for cond in self.conductors_list])

        conductors['env_ampacity_a'] = conductors.apply(
            lambda c: self._ieee_738_steady_state_rating(cond=c.to_dict()),
            axis=1
        )
        cb = conductors.loc[(conductors['env_ampacity_a'] > current_a)
                            & (conductors['env_ampacity_a'] < current_a*3)] if only_feasible_conds else conductors.copy()
    
        return cb
    

    def calculate_temperature_and_resistance_at_current(self, current_a):
  
        conductors = pd.DataFrame.from_records([cond.dict() for cond in self.conductors_list])
        if 'env_ampacity_a' not in conductors.columns:
            conductors['env_ampacity_a'] = conductors.apply(
                lambda c: self._ieee_738_steady_state_rating(cond=c.to_dict()),
                axis=1
            )
        
        conductors[['temp_at_current_c', 'res_at_current_ohm_per_m']] = conductors.apply(
            lambda c: self._ieee_738_steady_state_temperature(
                current_a=min(current_a, c['env_ampacity_a']), cond=c.to_dict()), 
            axis=1,
            result_type='expand'
        )

        return conductors
    

    def calculate_sag(self, current_a, only_feasible_conds=False, conds_subset=pd.DataFrame()):

        conductors = conds_subset if not conds_subset.empty else \
                        pd.DataFrame.from_records([cond.dict() for cond in self.conductors_list])

        if 'temp_at_current_c' not in conductors.columns:
            conductors['temp_at_current_c'] = conductors.apply(
                lambda c: self._ieee_738_steady_state_temperature(current_a=current_a, cond=c.to_dict())[0],
                axis=1
            )

        conductors[['sag_m', 'tension_n', 'extra']] = conductors.apply(
            lambda c: self._cigre_324_sag(cond=c.to_dict()), 
            axis=1, 
            result_type='expand'
        )

        df = conductors.loc[conductors['sag_m'] < self.max_sag_m] if only_feasible_conds else conductors.copy()

        return df


    def calculate_resistive_line_losses(self, current_a, load_factor):
        
        conductors = pd.DataFrame.from_records([cond.dict() for cond in self.conductors_list])
        conductors['losses_at_peak_mwh_per_m'] = conductors.apply(
            lambda c: self._resistive_line_losses(
                c.to_dict(), current_a, self.voltage_kv, load_factor),
            axis=1
        )

        return conductors
    

    def calculate_congestion(self, current_a):

        conductors = pd.DataFrame.from_records([cond.dict() for cond in self.conductors_list])
        conductors['congestion_mw'] = conductors.apply(
            lambda c: self._congestion(c.to_dict(), current_a, self.voltage_kv),
            axis=1
        )

        return conductors


    def calculate_overall_technical_performance(self, current_a, only_feasible_conds=False, st={}):

        nbr_conds = 1 if 'nbr_conductors' not in st else st['nbr_conductors']

        current_a = self.power_mw * 1e3 / (self.voltage_kv * np.sqrt(3)) / self.nbr_ckts / nbr_conds if not self.dc \
            else self.power_mw * 1e3 / self.voltage_kv / self.nbr_phases / self.nbr_ckts / nbr_conds

        curr_result = self.calculate_ampacity(current_a, only_feasible_conds=False)
        
        if not curr_result.empty:
            techn_result = self.calculate_sag(
                current_a,
                only_feasible_conds=only_feasible_conds,
                conds_subset=curr_result.copy()
            )
            techn_result = self.calculate_resistive_line_losses(current_a, self.load_factor)

            if not only_feasible_conds:
                techn_result = self.calculate_congestion(current_a)
            
            techn_result['peak_current'] = current_a
            
            return techn_result
        else:
            return pd.DataFrame()
