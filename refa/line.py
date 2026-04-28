from .line_design import LineDesign
from .conductor import Conductor
from pydantic import BaseModel, model_validator
from typing import Dict, Callable
import pandas as pd
import numpy as np
from inspect import signature
from operator import gt, ge, lt, le
# Map operator strings to Python operator functions
OPERATORS = {
    '>': gt,    # strictly greater than
    '>=': ge,   # greater than or equal
    '<': lt,    # strictly less than
    '<=': le,   # less than or equal
}


class Line(BaseModel):
    line_design: LineDesign
    conductor: Conductor

    @model_validator(mode="after")
    def _update_parameters(self):
        # ensure unique instances of objects
        self.line_design = self.line_design.model_copy(deep=True)
        self.conductor = self.conductor.model_copy(deep=True)
        return self

    def __getattr__(self, name):
        conductor = object.__getattribute__(self, "conductor")
        design = object.__getattribute__(self, "line_design")
        if hasattr(conductor, name):
            return getattr(conductor, name)
        if hasattr(design, name):
            return getattr(design, name)
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")
    
    def __setattr__(self, name, value):
        # If it's a defined field of LineDesign, use standard Pydantic setting
        if name in type(self).model_fields:
            super().__setattr__(name, value)
            return

        # If the line_design object has this attribute, set it there
        design = getattr(self, "line_design", None)
        env = getattr(self, "environment", None)
        if (design and hasattr(design, name)) and not hasattr(env, name):
            setattr(design, name, value)
            return

        # If the environment object has this attribute, set it there
        if env and hasattr(env, name):
            setattr(env, name, value)
            return
       
        # Fallback to default behavior
        super().__setattr__(name, value)


    # ----- validation decorator ensuring method args fall in correct value ranges.
    
    def _validate_args(arg_ranges: Dict[str, tuple]) -> Callable:
        """
        Flexible decorator supporting different operators per parameter.
        Usage example:
        @_validate_args({'load_factor': ('>=', 0, '<=', 1), 'voltage_kv': ('>', 0)})
        """
        def decorator(func: Callable) -> Callable:
            sig = signature(func)        
            def wrapper(*args, **kwargs):
                bound_args = sig.bind(*args, **kwargs)
                for arg_name, constraints in arg_ranges.items():
                    if arg_name in bound_args.arguments:
                        value = bound_args.arguments[arg_name]
                        # Skip validation if None
                        if value is None:
                            continue
                        # Parse and validate constraints tuple
                        i = 0
                        while i < len(constraints):
                            op_str = constraints[i]
                            threshold = constraints[i + 1]
                            if op_str not in OPERATORS:
                                raise ValueError(f"Unknown operator: {op_str}")
                            op_func = OPERATORS[op_str]
                            if not op_func(value, threshold):
                                raise ValueError(
                                    f"{arg_name} must be {op_str} {threshold}, got {value}"
                                )
                            i += 2
                return func(*args, **kwargs)
            return wrapper
        return decorator


    # ----- Internal calculation methods

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


    def _current_at_temperature(self, t_test, q_s, k_angle, is_hvdc=False):

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

        if not is_hvdc:
            r_tc = ((res_high - res_low) / (t_high - t_low)) * (t_test - t_low) + res_low
        else:
            r_tc = self.res_dc_ohm_per_m * (
                    1 + 0.0039 * (t_test - self.temp_dc_c) # assuming a typical temperature coefficient of resistivity 0.0039
            )

        x = (q_c + q_r - q_s) / r_tc
        if x > 0:
            i = np.sqrt(x)
        else:
            i = 0

        return r_tc, i


    def _ieee_738_steady_state_rating(self, is_hvdc=False):

        wind_angle = self.wind_angle
        t_c = self.max_temperature_c

        # solar heat gain
        q_s = self._solar_heat_gain()

        # wind direction factor
        k_angle = 1.194 - np.cos(np.radians(wind_angle)) \
                  + 0.194 * np.cos(np.radians(2 * wind_angle)) \
                  + 0.368 * np.sin(np.radians(2 * wind_angle))

        r_tc, i = self._current_at_temperature(t_c, q_s, k_angle, is_hvdc=is_hvdc)

        return i


    def _ieee_738_steady_state_temperature(self, current_a, is_hvdc=False):

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

            r_tc, i_ss_result = \
                self._current_at_temperature(t_test, q_s, k_angle,  is_hvdc=is_hvdc)

            if i_ss_result == current_a:
                break
            elif i_ss_result > current_a:
                tc_max = t_test
            else:
                tc_min = t_test
            counter += 1

        return t_test, r_tc


    def _cigre_324_sag(self, initial_tension_percentage, initial_temperature_c, temp_at_current_c, loading_conditions=None):

        diameter = self.diameter_mm / 1e3
        area = self.area_mm2 / 1e6
        initial_weight = self.weight_n_per_m
        alpha = self.coeff_thermal_expan_per_cel
        elastic_modulus = self.elastic_modulus_gpa * 1e9
        span = self.max_span_m
        initial_tension = initial_tension_percentage * self.conductor_rts_kn * 1e3
        initial_temp = initial_temperature_c

        temp_at_current = temp_at_current_c

        ice_density = 0 if loading_conditions is None else loading_conditions.ice_density_kg_per_m3
        ice_loading = 0 if loading_conditions is None else loading_conditions.ice_thickness_m
        wind_loading = 0 if loading_conditions is None else loading_conditions.pressure_pa
        additive_loading = 0 if loading_conditions is None else loading_conditions.additive_loading_n_per_m
        
        # calculate initial sag and length (without loading)
        initial_sag = initial_tension / initial_weight * (np.cosh(initial_weight * span / 2 / initial_tension) - 1)  
        initial_length = span + 8 * pow(initial_sag, 2) / 3 / span  # deduce initial length

        # calculate new weight with loading conditions
        ice_weight = ice_density * np.pi * (
                    pow(diameter + 2 * ice_loading, 2) - pow(diameter, 2)) / 4 * 9.81  # ice density*ice volume*g (N/m)
        wind_weight = wind_loading * (diameter + 2 * ice_loading)
        new_weight = np.sqrt(pow(initial_weight + ice_weight, 2) + pow(wind_weight, 2)) + additive_loading

        # reference length removes the mechanical elongation caused by the initial applied load
        reference_length = initial_length * (1 - initial_tension / elastic_modulus / area)
        
        # estimate of new length and sag based on temp. difference
        new_length = reference_length * (1 + alpha * (temp_at_current - initial_temp))  
        new_sag = np.sqrt(3 * span * abs(new_length - span) / 8)

        sag_holder = 0
        tension_min = 0
        tension_max = 500000
        # iteratively calculate new sag and tension until convergence (sag difference < 0.001 m)
        while abs(new_sag - sag_holder) > 0.001:
            new_tension = (tension_min + tension_max) / 2
            tension_holder = new_tension
            sag_holder = new_sag
            intermediate_length = new_length * (1 + new_tension / elastic_modulus / area)
            new_sag = np.sqrt(3 * span * abs(intermediate_length - span) / 8)
            new_tension = new_weight * pow(span, 2) / 8 / new_sag
            if new_tension > tension_holder:
                tension_min = tension_holder
            else:
                tension_max = tension_holder

        return new_sag

    
    def _sag(self, initial_tension_percentage,  initial_temperature_c=10,
                        current_a=None, power_mw=None, voltage_kv=None,
                        temp_at_current_c=None, loading_conditions=None, is_hvdc=False):

        if temp_at_current_c is not None:
            pass
        elif current_a is not None:
            temp = self._ieee_738_steady_state_temperature(current_a, is_hvdc=is_hvdc)
            temp_at_current_c = temp[0]
        elif current_a is None and power_mw is not None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when power_mw is specified.")
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)
            temp = self._ieee_738_steady_state_temperature(current_a, is_hvdc=is_hvdc)
            temp_at_current_c = temp[0]
        elif loading_conditions is not None:
            temp_at_current_c = loading_conditions.wind_ice_temperature_c
        else:
            raise ValueError("Either temp_at_current_c, current_a, (power_mw and voltage_kv) "
                            "or loading_conditions must be provided for sag calculations.")
        
        sag = self._cigre_324_sag(
            initial_tension_percentage=initial_tension_percentage, 
            initial_temperature_c=initial_temperature_c, 
            temp_at_current_c=temp_at_current_c, 
            loading_conditions=loading_conditions
        )
                                                  
        return sag


    @_validate_args({'current_a': ('>', 0), 'max_sag_m': ('>', 0),
        'voltage_kv': ('>', 0, '<', 1000), 'power_mw': ('>', 0, '<', 10000),
        'initial_tension_percentage': ('>=', 0.1, '<=', 0.6),
        'initial_temperature_c': ('>', 0, '<', '75')})
    def _is_feasible(self, current_a=None, voltage_kv=None, power_mw=None, max_sag_m=None, 
                    initial_tension_percentage=0.2, initial_temperature_c=10, 
                    loading_conditions=None, structure_config=None, is_hvdc=False):
        
        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when power_mw is specified")
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)
        
        amp_ok = True
        sag_ok = True
        corona_ok = True
        message = ""
        if current_a is not None:
            ampacity = self._ieee_738_steady_state_rating(is_hvdc=is_hvdc)
            amp_ok = True if ampacity > current_a and ampacity < current_a*3 else False
            message += f"Ampacity {ampacity} Amps is not sufficient for peak current {current_a} Amps. " if not amp_ok else ""
            
        if max_sag_m is not None:
            if initial_tension_percentage is None:
                raise ValueError(
                    "initial_tension_percentage must be provided "
                    "when a max_sag limit is defined."
                )
            sag = max(
                self._cigre_324_sag(
                    initial_tension_percentage, 
                    initial_temperature_c, 
                    temp_at_current_c=self._ieee_738_steady_state_temperature(current_a=current_a, is_hvdc=is_hvdc)[0]
                ),
                self._cigre_324_sag(
                    initial_tension_percentage, 
                    initial_temperature_c, 
                    loading_conditions=loading_conditions
                ) if loading_conditions is not None else 0
            )
            sag_ok = True if sag < max_sag_m else False
            message += f"Sag {sag} meters exceeds the limit {max_sag_m} meters. " if not sag_ok else ""

        if structure_config is not None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when structure_config is specified")
            corona_inception_voltage = self.corona_inception_voltage(structure_config, is_hvdc=is_hvdc)     
            corona_ok = True if  voltage_kv < corona_inception_voltage else False
            message += f"Corona inception voltage {corona_inception_voltage} kV is below the line voltage. " if not corona_ok else ""

        return amp_ok and sag_ok and corona_ok, message


    # ----- Main calculation methods -----

    def get_current(self, power_mw, voltage_kv, is_hvdc=False):
        return power_mw / (voltage_kv * np.sqrt(3) *
                    self.nbr_circuits * self.nbr_conds_per_bundle * 1e-3) if not is_hvdc \
                else power_mw / (voltage_kv * 
                    self.nbr_circuits * self.nbr_bundles * self.nbr_conds_per_bundle * 1e-3) 


    def get_power(self, current_a, voltage_kv, is_hvdc=False):
        return current_a * voltage_kv * np.sqrt(3) * \
                    self.nbr_circuits * self.nbr_conds_per_bundle * 1e-3 if not is_hvdc \
                else current_a * voltage_kv * self.nbr_conds_per_bundle * 1e-3

    
    @_validate_args({'load_factor': ('>=', 0, '<=', 1), 'current_a': ('>', 0),
        'voltage_kv': ('>', 0, '<', 1000), 'power_mw': ('>', 0, '<', 10000)})
    def temperature_at_current(self,  current_a=None, power_mw=None, voltage_kv=None, is_hvdc=False):
        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when power_mw is specified")
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)
        
        ampacity = self.ampacity_at_environment(is_hvdc=is_hvdc)
        
        temp_at_current_c, _ = self._ieee_738_steady_state_temperature(
                current_a=min(current_a, ampacity), is_hvdc=is_hvdc
        )

        return temp_at_current_c
   
    
    @_validate_args({'load_factor': ('>=', 0, '<=', 1), 'current_a': ('>', 0),
        'voltage_kv': ('>', 0, '<', 1000), 'power_mw': ('>', 0, '<', 10000)})
    def resistance_at_current(self,  current_a=None, power_mw=None, voltage_kv=None, is_hvdc=False):
        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when power_mw is specified")
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)
        
        ampacity = self.ampacity_at_environment(is_hvdc=is_hvdc)
        
        _ , res_at_current_ohm_per_m = self._ieee_738_steady_state_temperature(
                current_a=min(current_a, ampacity), is_hvdc=is_hvdc
        )

        return res_at_current_ohm_per_m
    
    
    def ampacity_at_environment(self, is_hvdc=False):

        ampacity = self._ieee_738_steady_state_rating(is_hvdc=is_hvdc)

        return ampacity


    @_validate_args({'current_a': ('>', 0),
            'initial_tension_percentage': ('>=', 0.1, '<=', 0.6),
            'initial_temperature_c': ('>', 0, '<', '75')})
    def sag_at_current(self, current_a, initial_tension_percentage, 
                         initial_temperature_c=10, is_hvdc=False):
        
        temp = self._ieee_738_steady_state_temperature(current_a, is_hvdc=is_hvdc)
        temp_at_current_c = temp[0]
        sag = self._cigre_324_sag(
            initial_tension_percentage=initial_tension_percentage, 
            initial_temperature_c=initial_temperature_c, 
            temp_at_current_c=temp_at_current_c
        )
                                                  
        return sag


    @_validate_args({'voltage_kv': ('>', 0, '<', 1000), 'power_mw': ('>', 0, '<', 10000),
            'initial_tension_percentage': ('>=', 0.1, '<=', 0.6),
            'initial_temperature_c': ('>', 0, '<', '75')})
    def sag_at_power_and_voltage(self, power_mw, voltage_kv,
                initial_tension_percentage,  initial_temperature_c=10, is_hvdc=False):

        current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)
        temp = self._ieee_738_steady_state_temperature(current_a, is_hvdc=is_hvdc)
        temp_at_current_c = temp[0]     
        sag = self._cigre_324_sag(
            initial_tension_percentage=initial_tension_percentage, 
            initial_temperature_c=initial_temperature_c, 
            temp_at_current_c=temp_at_current_c,
        )
                                                  
        return sag
    

    @_validate_args({'temp_at_current_c': ('>', -60, '<', 300), 
            'initial_tension_percentage': ('>=', 0.1, '<=', 0.6),
            'initial_temperature_c': ('>', 0, '<', '75')})
    def sag_at_temperature(self, temp_at_current_c, initial_tension_percentage,  
                             initial_temperature_c=10):

        sag = self._cigre_324_sag(
            initial_tension_percentage=initial_tension_percentage, 
            initial_temperature_c=initial_temperature_c, 
            temp_at_current_c=temp_at_current_c
        )
                                                  
        return sag


    @_validate_args({'initial_tension_percentage': ('>=', 0.1, '<=', 0.6),
                     'initial_temperature_c': ('>', 0, '<', '75')})
    def sag_at_loading(self, loading_conditions, initial_tension_percentage,  
                         initial_temperature_c=10):
        
        sag = self._cigre_324_sag(
            initial_tension_percentage=initial_tension_percentage, 
            initial_temperature_c=initial_temperature_c, 
            temp_at_current_c=loading_conditions.wind_ice_temperature_c, 
            loading_conditions=loading_conditions
        )
                                                  
        return sag


    def corona_inception_voltage(self, structure_config, is_hvdc=False):
            
        # Air correction factor
        delta = 293 / (273 + self.ambient_temperature_c) * np.exp(-0.00012 * self.elevation_m)
        radius = self.diameter_mm / 2 * 0.1

        if not is_hvdc:
            # Geometrical mean distance (GMD) between phases, in centimeter
            gmd = pow(structure_config.distance_a_b_m * structure_config.distance_b_c_m * structure_config.distance_a_c_m, 1 / 3) * 1e2
            d = radius * np.log(gmd / radius)
            inception_voltage = np.sqrt(3) * 29.8 / np.sqrt(2) * self.weather_correction_factor * self.rugosity_coefficient * delta * \
                    self.nbr_conds_per_bundle * d
        else:
            d = radius * np.log(structure_config.distance_pos_neg_poles_m * 1e2 / radius)
            inception_voltage = 30 * self.weather_correction_factor * self.rugosity_coefficient * delta * \
                                self.nbr_conds_per_bundle * (1 + 0.301 / np.sqrt(delta * radius)) * d
        
        return inception_voltage
    

    def corona_voltage_gradient(self, structure_config, is_hvdc=False):
            
        # Air correction factor
        delta = 293 / (273 + self.ambient_temperature_c) * np.exp(-0.00012 * self.elevation_m)
        radius = self.diameter_mm / 2 * 0.1

        if not is_hvdc:
            # Geometrical mean distance (GMD) between phases, in centimeter
            gmd = pow(structure_config.distance_a_b_m * structure_config.distance_b_c_m * structure_config.distance_a_c_m, 1 / 3) * 1e2
            d = radius * np.log(gmd / radius)
            inception_voltage = np.sqrt(3) * 29.8 / np.sqrt(2) * self.weather_correction_factor * self.rugosity_coefficient * delta * \
                    self.nbr_conds_per_bundle * d
        else:
            d = radius * np.log(structure_config.distance_pos_neg_poles_m * 1e2 / radius)
            inception_voltage = 30 * self.weather_correction_factor * self.rugosity_coefficient * delta * \
                                self.nbr_conds_per_bundle * (1 + 0.301 / np.sqrt(delta * radius)) * d
        
        voltage_gradient_kv_per_cm = inception_voltage / d

        return voltage_gradient_kv_per_cm


    # evaluate losses and congestion 
     
    @_validate_args({'load_factor': ('>=', 0, '<=', 1), 'current_a': ('>', 0),
        'voltage_kv': ('>', 0, '<', 1000), 'power_mw': ('>', 0, '<', 10000)})
    def resistive_line_losses(self, load_factor, current_a=None, voltage_kv=None, power_mw=None, is_hvdc=False):
        
        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when power_mw is specified")
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)
                
        loss_factor = 0.3 * load_factor + 0.7 * load_factor ** 2  # coeffs set to 0.15 and 0.85 in case of distribution

        res_at_current_ohm_per_m = self._ieee_738_steady_state_temperature(current_a=current_a, is_hvdc=is_hvdc)[1]
        nbr_conds = self.nbr_conds_per_bundle * self.nbr_bundles * self.nbr_circuits
        
        losses_at_peak_mwh_per_m = \
            res_at_current_ohm_per_m * current_a ** 2 * loss_factor * nbr_conds * 8760 * 1e-6
 
        return losses_at_peak_mwh_per_m

  
    @_validate_args({'load_factor': ('>=', 0, '<=', 1), 'current_a': ('>', 0),
        'voltage_kv': ('>', 0, '<', 1000), 'power_mw': ('>', 0, '<', 10000)})
    def resistive_line_losses_considering_congestion(self, load_factor, voltage_kv, power_mw=None, current_a=None, is_hvdc=False):
        
        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is not None:
            power_mw = self.get_power(current_a, voltage_kv, is_hvdc=is_hvdc)
        else:
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)
        
        I_E = self._ieee_738_steady_state_rating(is_hvdc=is_hvdc) # current in one conductor per phase/pole of the existing line
        P_E = self.get_power(I_E, voltage_kv, is_hvdc=is_hvdc)
        
        t_E = (power_mw - P_E) / power_mw
        loss_factor = 0.3 * load_factor + 0.7 * load_factor ** 2  # coeffs set to 0.15 and 0.85 in case of distribution

        res_at_current_ohm_per_m = self._ieee_738_steady_state_temperature(current_a=current_a, is_hvdc=is_hvdc)[1]
        nbr_conds = self.nbr_conds_per_bundle * self.nbr_bundles * self.nbr_circuits
        if (power_mw - P_E) > 0:
            # loss factor at the congested line
            load_factor_1 = (1 + t_E) / 2
            loss_factor_1 = 0.3 * load_factor_1 + 0.7 * load_factor_1 ** 2

            # line resistance and loss factor at the neighboring line which takes on the congestion power from existing line
            R = 8.63 * 1e-5  # ACSR DRAKE at 75 deg. Cel

            losses_at_peak_mwh_per_m = (
                res_at_current_ohm_per_m * I_E**2 * loss_factor_1 + R * (current_a - I_E)**2 * loss_factor
                ) * nbr_conds * 8760 * 1e-6
        else:
            losses_at_peak_mwh_per_m = \
                res_at_current_ohm_per_m * current_a ** 2 * loss_factor * nbr_conds * 8760 * 1e-6
 
        return losses_at_peak_mwh_per_m


    @_validate_args({'load_factor': ('>=', 0, '<=', 1),
                     'voltage_kv': ('>', 0, '<', 1000)})
    def corona_discharge_losses(self, voltage_kv, structure_config, load_factor, is_hvdc=False):
        loss_factor = 0.3 * load_factor + 0.7 * load_factor ** 2  # coeffs set to 0.15 and 0.85 in case of distribution
        delta = 293 / (273 + self.ambient_temperature_c) * np.exp(
            -0.00012 * self.elevation_m) # Air correction factor
        inception_voltage_kv = \
            self.corona_inception_voltage(structure_config, is_hvdc=is_hvdc)
        voltage_gradient_kv_per_cm = \
            self.corona_voltage_gradient(structure_config, is_hvdc=is_hvdc)
        if inception_voltage_kv < voltage_kv:
            if not is_hvdc:
                gmd = pow(
                    structure_config.distance_a_b_m * structure_config.distance_b_c_m *
                           structure_config.distance_a_c_m, 
                    1 / 3) * 1e2  
                corona_losses_mwh_per_m = \
                    (241 / delta * (60 + 25) * np.sqrt(self.diameter_mm / 2 * 0.1 / gmd) *
                    pow((max(voltage_kv - inception_voltage_kv, 0)) / np.sqrt(3), 2) * 1e-5 *
                    self.nbr_circuits * self.nbr_bundles * self.nbr_conds_per_bundle * loss_factor * 8760 * 1e-6)
            else:
                corona_losses_mwh_per_m = \
                    pow(10, (11 + 40 * np.log10(voltage_gradient_kv_per_cm / 25) +
                            20 * np.log10(self.diameter_mm / 2 * 0.1 / 3.05) +
                            15 * np.log10(self.nbr_conds_per_bundle / 3) -
                            10 * np.log10(structure_config.structure_height_m * 
                                          structure_config.distance_pos_neg_poles_m / 15 / 15)) / 10) * \
                    self.nbr_circuits * self.nbr_bundles * self.nbr_conds_per_bundle * loss_factor * 8760 * 1e-6

            return corona_losses_mwh_per_m
        
        else:
            return 0


    @_validate_args({'current_a': ('>', 0), 'voltage_kv': ('>', 0, '<', 1000),
                     'power_mw': ('>', 0, '<', 10000)})
    def congestion(self, voltage_kv, power_mw=None, current_a=None, is_hvdc=False):
        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is not None:
            power_mw = self.get_power(current_a, voltage_kv, is_hvdc=is_hvdc)
        
        I_E = self._ieee_738_steady_state_rating(is_hvdc=is_hvdc) # current in one conductor per phase of the existing line
        P_E = self.get_power(I_E, voltage_kv, is_hvdc=is_hvdc)
        
        t_E = (power_mw - P_E) / power_mw
        if (power_mw - P_E) > 0:
            congestion_mw = (power_mw - P_E) * t_E / 2
        else:
            congestion_mw = 0

        return congestion_mw


    # overall technical performance

    @_validate_args({'load_factor': ('>=', 0, '<=', 1), 'current_a': ('>', 0),
        'voltage_kv': ('>', 0, '<', 1000), 'power_mw': ('>', 0, '<', 10000),
        'initial_tension_percentage': ('>=', 0.1, '<=', 0.6),
        'initial_temperature_c': ('>', 0, '<', '75')})
    def overall_technical_performance(self, current_a=None, power_mw=None, voltage_kv=None, 
                                        initial_tension_percentage=0.2, initial_temperature_c=10, loading_conditions=None, 
                                        load_factor=None, structure_config=None, is_hvdc=False):

        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when power_mw is specified")
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)

        result = {}
        result['ampacity_a'] = self.ampacity_at_environment(is_hvdc=False)
        
        result['sag_m'] = max(
            self._sag(
                initial_tension_percentage,
                initial_temperature_c,
                temp_at_current_c=self._ieee_738_steady_state_temperature(current_a=current_a, is_hvdc=is_hvdc)[0]
            ), 
            self._sag(
                initial_tension_percentage,
                initial_temperature_c,
                loading_conditions=loading_conditions
            ) if loading_conditions is not None else 0
        )    
    
        if load_factor is not None:
            result['resistive_losses_mwh_per_m'] = self.resistive_line_losses(
                load_factor, current_a=current_a
            )

        if voltage_kv is not None:
            result['congestion_mw'] = self.congestion(voltage_kv, current_a=current_a, is_hvdc=is_hvdc)    

            if structure_config is not None:
                result['corona_inception_voltage_kv'] = \
                            self.corona_inception_voltage(structure_config, is_hvdc=is_hvdc)
                result['corona_voltage_gradient_kv_per_cm'] = \
                            self.corona_voltage_gradient(structure_config, is_hvdc=is_hvdc)
                result['corona_losses_mwh_per_m'] = self.corona_discharge_losses(
                                            voltage_kv, structure_config, load_factor, is_hvdc=is_hvdc)       
        else:
            print("voltage_kv required to calculate losses and congestion.")
               
        return result


    @_validate_args({'current_a': ('>', 0), 'voltage_kv': ('>', 0, '<', 1000),
                     'power_mw': ('>', 0, '<', 10000)})
    def is_ampacity_feasible(self, current_a=None, voltage_kv=None, power_mw=None, is_hvdc=False):
        
        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when power_mw is specified")
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)

        amp_ok = True
        message = ""
        ampacity = self._ieee_738_steady_state_rating(is_hvdc=is_hvdc)
        amp_ok = True if ampacity > current_a and ampacity < current_a*3 else False
        message += f"Ampacity {ampacity} Amps is not sufficient for peak current {current_a} Amps. " if not amp_ok else ""
        
        return amp_ok, message


    @_validate_args({'current_a': ('>', 0), 'max_sag_m': ('>', 0),
            'voltage_kv': ('>', 0, '<', 1000), 'power_mw': ('>', 0, '<', 10000),
            'initial_tension_percentage': ('>=', 0.1, '<=', 0.6),
            'initial_temperature_c': ('>', 0, '<', '75')})
    def is_sag_feasible(self, max_sag_m, initial_tension_percentage, 
                    current_a=None, voltage_kv=None, power_mw=None, 
                    initial_temperature_c=10, loading_conditions=None, is_hvdc=False):
        
        if (current_a is None) == (power_mw is None):
            raise ValueError("Either current_a or power_mw must be provided.")
        if current_a is None:
            if voltage_kv is None:
                raise ValueError("voltage_kv required when power_mw is specified")
            current_a = self.get_current(power_mw, voltage_kv, is_hvdc=is_hvdc)
        
        sag_ok = True
        message = ""
        if max_sag_m is not None:
            if initial_tension_percentage is None:
                raise ValueError(
                    "initial_tension_percentage must be provided "
                    "when a max_sag limit is defined."
                )
            sag = max(
                self._cigre_324_sag(
                    initial_tension_percentage, 
                    initial_temperature_c, 
                    temp_at_current_c=self._ieee_738_steady_state_temperature(current_a=current_a, is_hvdc=is_hvdc)[0]
                ),
                self._cigre_324_sag(
                    initial_tension_percentage, 
                    initial_temperature_c, 
                    loading_conditions=loading_conditions
                ) if loading_conditions is not None else 0
            )
            sag_ok = True if sag < max_sag_m else False
            message += f"Sag {sag} meters exceeds the limit {max_sag_m} meters. " if not sag_ok else ""

        return sag_ok, message


    @_validate_args({'voltage_kv': ('>', 0, '<', 1000)})
    def is_corona_feasible(self, voltage_kv, structure_config, is_hvdc=False):   
        
        corona_ok = True
        message = ""
        corona_inception_voltage = self.corona_inception_voltage(structure_config, is_hvdc=is_hvdc)     
        corona_ok = True if  voltage_kv < corona_inception_voltage else False
        message += f"Corona inception voltage {corona_inception_voltage} kV is below the line voltage. " if not corona_ok else ""

        return corona_ok, message

