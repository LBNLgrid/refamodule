from ..conductor import Conductor
import pandas as pd
from typing import Callable, Dict


def default_conductor() -> Conductor:
    return Conductor(
        type='ACSR',
        code='556.5_DOVE',
        area_mm2=329.0,
        diameter_mm=24.0,
        weight_n_per_m=11.17,
        conductor_rts_kn=100.53,
        dol_per_1000_ft=1252.0,
        inst_dol_per_1000_ft=1804.0,
        accessories_dol_per_1000_ft=263.0,
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.0001,
        res_low_ohm_per_m=0.0001,
        res_high_ohm_per_m=0.000123,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

# ----- Conductors from csv file

class ConductorDict(dict):
    """Dictionary that allows dot notation access to conductor functions.
    
    Usage:
        conductors = ConductorDict()
        conductors['acsr_795_0_drake'] = acsr_795_0_drake
        # Access as: conductors.acsr_795_0_drake()
    """
    def __getattr__(self, name):
        try:
            value = self[name]
            return value
        except KeyError:
            raise AttributeError(f"No conductor named '{name}'")
    
    def __setattr__(self, name, value):
        self[name] = value


def load_conductors_from_csv(csv_path: str) -> ConductorDict:
    """Dynamically load conductor functions from CSV.
    
    Returns a ConductorRegistry that allows dot notation access.
    Usage: conductors.acsr_795_0_drake()
    """
    df = pd.read_csv(csv_path)
    conductors = ConductorDict()
    
    for _, row in df.iterrows():
        func_name = row['code'].lower().replace('.', '_').replace(' ', '_')
        cond_type = row['type'].lower()
        
        # Create closure to capture row data
        def make_conductor(data):
            def conductor_func():
                return Conductor(
                    type=data['type'],
                    code=data['code'],
                    diameter_mm=float(data['diameter_mm']),
                    area_mm2=float(data['area_mm2']),
                    weight_n_per_m=float(data['weight_n_per_m']),
                    conductor_rts_kn=float(data['conductor_rts_kn']),
                    dol_per_1000_ft=float(data['dol_per_1000_ft']),
                    inst_dol_per_1000_ft=float(data['inst_dol_per_1000_ft']),
                    accessories_dol_per_1000_ft=float(data['accessories_dol_per_1000_ft']),
                    temp_dc_c=float(data['temp_dc_c']),
                    temp_low_c=float(data['temp_low_c']),
                    temp_high_c=float(data['temp_high_c']),
                    max_temperature_c=float(data['max_temperature_c']),
                    res_dc_ohm_per_m=float(data['res_dc_ohm_per_m']),
                    res_low_ohm_per_m=float(data['res_low_ohm_per_m']),
                    res_high_ohm_per_m=float(data['res_high_ohm_per_m']),
                    elastic_modulus_gpa=float(data['elastic_modulus_gpa']),
                    coeff_thermal_expan_per_cel=float(data['coeff_thermal_expan_per_cel']),
                    emissivity=float(data['emissivity']),
                    solar_absorptivity=float(data['solar_absorptivity'])
                )
            return conductor_func
        
        conductors[f'{cond_type}_{func_name}'] = make_conductor(row)
    
    return conductors


# ----- Database of conductors

def acsr_266_8_waxwing() -> Conductor:
    return Conductor(
        type='ACSR',
        code='266.8_WAXWING',
        area_mm2=143.0,
        diameter_mm=15.0,
        weight_n_per_m=4.22,
        conductor_rts_kn=30.6,
        dol_per_1000_ft=609.0,
        inst_dol_per_1000_ft=828.0,
        accessories_dol_per_1000_ft=263.0,
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000211,
        res_low_ohm_per_m=0.000211,
        res_high_ohm_per_m=0.000258,
        elastic_modulus_gpa=66.0,
        coeff_thermal_expan_per_cel=2.12e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_266_8_partridge() -> Conductor:
    return Conductor(
        type='ACSR',
        code='266.8_PARTRIDGE',
        area_mm2=157.0,
        diameter_mm=16.0,
        weight_n_per_m=5.36,
        conductor_rts_kn=50.26,
        dol_per_1000_ft=735.0,
        inst_dol_per_1000_ft=1027.0,
        accessories_dol_per_1000_ft=263.0,
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000209,
        res_low_ohm_per_m=0.000209,
        res_high_ohm_per_m=0.000256,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_336_4_merlin() -> Conductor:
    return Conductor(
        type='ACSR',
        code='336.4_MERLIN',
        area_mm2=180.0,
        diameter_mm=17.0,
        weight_n_per_m=5.33,
        conductor_rts_kn=38.61,
        dol_per_1000_ft=650.0,
        inst_dol_per_1000_ft=942.0,
        accessories_dol_per_1000_ft=263.0,
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000167,
        res_low_ohm_per_m=0.000167,
        res_high_ohm_per_m=0.000205,
        elastic_modulus_gpa=66.0,
        coeff_thermal_expan_per_cel=2.12e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_336_4_linnet() -> Conductor:
    return Conductor(
        type='ACSR',
        code='336.4_LINNET',
        area_mm2=198.0,
        diameter_mm=18.0,
        weight_n_per_m=6.74,
        conductor_rts_kn=62.72,
        dol_per_1000_ft=749.0,
        inst_dol_per_1000_ft=1106.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000166,
        res_low_ohm_per_m=0.000166,
        res_high_ohm_per_m=0.000203,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_336_4_oriole() -> Conductor:
    return Conductor(
        type='ACSR',
        code='336.4_ORIOLE',
        area_mm2=210.0,
        diameter_mm=19.0,
        weight_n_per_m=7.68,
        conductor_rts_kn=76.95,
        dol_per_1000_ft=934.0,
        inst_dol_per_1000_ft=1302.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000165,
        res_low_ohm_per_m=0.000165,
        res_high_ohm_per_m=0.000201,
        elastic_modulus_gpa=80.0,
        coeff_thermal_expan_per_cel=1.78e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_397_5_chickadee() -> Conductor:
    return Conductor(
        type='ACSR',
        code='397.5_CHICKADEE',
        area_mm2=212.0,
        diameter_mm=19.0,
        weight_n_per_m=6.29,
        conductor_rts_kn=44.22,
        dol_per_1000_ft=802.0,
        inst_dol_per_1000_ft=1130.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000142,
        res_low_ohm_per_m=0.000142,
        res_high_ohm_per_m=0.000174,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_397_5_ibis() -> Conductor:
    return Conductor(
        type='ACSR',
        code='397.5_IBIS',
        area_mm2=234.0,
        diameter_mm=20.0,
        weight_n_per_m=7.97,
        conductor_rts_kn=72.51,
        dol_per_1000_ft=963.0,
        inst_dol_per_1000_ft=1366.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.00014,
        res_low_ohm_per_m=0.00014,
        res_high_ohm_per_m=0.000172,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_397_5_lark() -> Conductor:
    return Conductor(
        type='ACSR',
        code='397.5_LARK',
        area_mm2=248.0,
        diameter_mm=20.0,
        weight_n_per_m=9.08,
        conductor_rts_kn=90.3,
        dol_per_1000_ft=951.0,
        inst_dol_per_1000_ft=1430.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000139,
        res_low_ohm_per_m=0.000139,
        res_high_ohm_per_m=0.00017,
        elastic_modulus_gpa=80.0,
        coeff_thermal_expan_per_cel=1.78e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_477_0_pelican() -> Conductor:
    return Conductor(
        type='ACSR',
        code='477.0_PELICAN',
        area_mm2=256.0,
        diameter_mm=21.0,
        weight_n_per_m=7.55,
        conductor_rts_kn=52.49,
        dol_per_1000_ft=940.0,
        inst_dol_per_1000_ft=1353.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000118,
        res_low_ohm_per_m=0.000118,
        res_high_ohm_per_m=0.000145,
        elastic_modulus_gpa=66.0,
        coeff_thermal_expan_per_cel=2.12e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_477_0_flicker() -> Conductor:
    return Conductor(
        type='ACSR',
        code='477.0_FLICKER',
        area_mm2=273.0,
        diameter_mm=21.0,
        weight_n_per_m=8.96,
        conductor_rts_kn=76.51,
        dol_per_1000_ft=902.0,
        inst_dol_per_1000_ft=1357.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000117,
        res_low_ohm_per_m=0.000121,
        res_high_ohm_per_m=0.000144,
        elastic_modulus_gpa=72.5,
        coeff_thermal_expan_per_cel=2e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_477_0_hawk() -> Conductor:
    return Conductor(
        type='ACSR',
        code='477.0_HAWK',
        area_mm2=281.0,
        diameter_mm=22.0,
        weight_n_per_m=9.58,
        conductor_rts_kn=86.74,
        dol_per_1000_ft=1123.0,
        inst_dol_per_1000_ft=1594.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000117,
        res_low_ohm_per_m=0.00012,
        res_high_ohm_per_m=0.000144,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_477_0_hen() -> Conductor:
    return Conductor(
        type='ACSR',
        code='477.0_HEN',
        area_mm2=298.0,
        diameter_mm=22.0,
        weight_n_per_m=10.89,
        conductor_rts_kn=105.87,
        dol_per_1000_ft=1251.0,
        inst_dol_per_1000_ft=1741.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000116,
        res_low_ohm_per_m=0.000119,
        res_high_ohm_per_m=0.000143,
        elastic_modulus_gpa=80.0,
        coeff_thermal_expan_per_cel=1.78e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_556_5_osprey() -> Conductor:
    return Conductor(
        type='ACSR',
        code='556.5_OSPREY',
        area_mm2=298.0,
        diameter_mm=22.0,
        weight_n_per_m=8.8,
        conductor_rts_kn=60.94,
        dol_per_1000_ft=1128.0,
        inst_dol_per_1000_ft=1559.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000101,
        res_low_ohm_per_m=0.000104,
        res_high_ohm_per_m=0.000125,
        elastic_modulus_gpa=66.0,
        coeff_thermal_expan_per_cel=2.12e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_556_5_parakeet() -> Conductor:
    return Conductor(
        type='ACSR',
        code='556.5_PARAKEET',
        area_mm2=319.0,
        diameter_mm=23.0,
        weight_n_per_m=10.45,
        conductor_rts_kn=88.07,
        dol_per_1000_ft=1324.0,
        inst_dol_per_1000_ft=1818.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000101,
        res_low_ohm_per_m=0.000104,
        res_high_ohm_per_m=0.000124,
        elastic_modulus_gpa=72.5,
        coeff_thermal_expan_per_cel=2e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_556_5_dove() -> Conductor:
    return Conductor(
        type='ACSR',
        code='556.5_DOVE',
        area_mm2=329.0,
        diameter_mm=24.0,
        weight_n_per_m=11.17,
        conductor_rts_kn=100.53,
        dol_per_1000_ft=1252.0,
        inst_dol_per_1000_ft=1804.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.0001,
        res_low_ohm_per_m=0.0001,
        res_high_ohm_per_m=0.000123,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_636_0_kingbird() -> Conductor:
    return Conductor(
        type='ACSR',
        code='636.0_KINGBIRD',
        area_mm2=341.0,
        diameter_mm=24.0,
        weight_n_per_m=10.07,
        conductor_rts_kn=69.84,
        dol_per_1000_ft=1090.0,
        inst_dol_per_1000_ft=1624.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=8.86e-05,
        res_low_ohm_per_m=8.86e-05,
        res_high_ohm_per_m=0.000109,
        elastic_modulus_gpa=66.0,
        coeff_thermal_expan_per_cel=2.12e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_636_0_rook() -> Conductor:
    return Conductor(
        type='ACSR',
        code='636.0_ROOK',
        area_mm2=365.0,
        diameter_mm=25.0,
        weight_n_per_m=11.94,
        conductor_rts_kn=100.53,
        dol_per_1000_ft=1236.0,
        inst_dol_per_1000_ft=1861.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=8.79e-05,
        res_low_ohm_per_m=8.79e-05,
        res_high_ohm_per_m=0.000108,
        elastic_modulus_gpa=72.5,
        coeff_thermal_expan_per_cel=2e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_636_0_grosbeak() -> Conductor:
    return Conductor(
        type='ACSR',
        code='636.0_GROSBEAK',
        area_mm2=374.0,
        diameter_mm=25.0,
        weight_n_per_m=12.76,
        conductor_rts_kn=112.1,
        dol_per_1000_ft=1416.0,
        inst_dol_per_1000_ft=2031.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=8.76e-05,
        res_low_ohm_per_m=8.76e-05,
        res_high_ohm_per_m=0.000108,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_666_6_flamingo() -> Conductor:
    return Conductor(
        type='ACSR',
        code='666.6_FLAMINGO',
        area_mm2=381.0,
        diameter_mm=25.0,
        weight_n_per_m=12.53,
        conductor_rts_kn=105.42,
        dol_per_1000_ft=1460.0,
        inst_dol_per_1000_ft=2146.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=8.4e-05,
        res_low_ohm_per_m=8.4e-05,
        res_high_ohm_per_m=0.000103,
        elastic_modulus_gpa=72.5,
        coeff_thermal_expan_per_cel=2e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_795_0_tern() -> Conductor:
    return Conductor(
        type='ACSR',
        code='795.0_TERN',
        area_mm2=432.0,
        diameter_mm=27.0,
        weight_n_per_m=13.07,
        conductor_rts_kn=98.31,
        dol_per_1000_ft=1366.0,
        inst_dol_per_1000_ft=2048.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=7.09e-05,
        res_low_ohm_per_m=7.09e-05,
        res_high_ohm_per_m=8.83e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_795_0_cuckoo() -> Conductor:
    return Conductor(
        type='ACSR',
        code='795.0_CUCKOO',
        area_mm2=455.0,
        diameter_mm=28.0,
        weight_n_per_m=14.93,
        conductor_rts_kn=125.44,
        dol_per_1000_ft=1521.0,
        inst_dol_per_1000_ft=2291.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=7.05e-05,
        res_low_ohm_per_m=7.05e-05,
        res_high_ohm_per_m=8.92e-05,
        elastic_modulus_gpa=72.5,
        coeff_thermal_expan_per_cel=2e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_795_0_drake() -> Conductor:
    return Conductor(
        type='ACSR',
        code='795.0_DRAKE',
        area_mm2=468.0,
        diameter_mm=28.0,
        weight_n_per_m=15.96,
        conductor_rts_kn=140.12,
        dol_per_1000_ft=1711.0,
        inst_dol_per_1000_ft=2359.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=7.02e-05,
        res_low_ohm_per_m=7.02e-05,
        res_high_ohm_per_m=8.63e-05,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_900_0_canary() -> Conductor:
    return Conductor(
        type='ACSR',
        code='900.0_CANARY',
        area_mm2=516.0,
        diameter_mm=30.0,
        weight_n_per_m=16.91,
        conductor_rts_kn=141.9,
        dol_per_1000_ft=1937.0,
        inst_dol_per_1000_ft=2632.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=6.23e-05,
        res_low_ohm_per_m=6.23e-05,
        res_high_ohm_per_m=7.91e-05,
        elastic_modulus_gpa=69.0,
        coeff_thermal_expan_per_cel=1.93e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_954_0_rail() -> Conductor:
    return Conductor(
        type='ACSR',
        code='954.0_RAIL',
        area_mm2=517.0,
        diameter_mm=30.0,
        weight_n_per_m=15.68,
        conductor_rts_kn=115.21,
        dol_per_1000_ft=1805.0,
        inst_dol_per_1000_ft=2502.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=5.91e-05,
        res_low_ohm_per_m=5.91e-05,
        res_high_ohm_per_m=7.38e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_954_0_cardinal() -> Conductor:
    return Conductor(
        type='ACSR',
        code='954.0_CARDINAL',
        area_mm2=547.0,
        diameter_mm=30.0,
        weight_n_per_m=17.91,
        conductor_rts_kn=150.35,
        dol_per_1000_ft=1977.0,
        inst_dol_per_1000_ft=2757.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=5.87e-05,
        res_low_ohm_per_m=5.87e-05,
        res_high_ohm_per_m=7.48e-05,
        elastic_modulus_gpa=69.0,
        coeff_thermal_expan_per_cel=1.93e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1033_5_ortolan() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1033.5_ORTOLAN',
        area_mm2=560.0,
        diameter_mm=31.0,
        weight_n_per_m=16.98,
        conductor_rts_kn=123.22,
        dol_per_1000_ft=1979.0,
        inst_dol_per_1000_ft=3026.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=5.48e-05,
        res_low_ohm_per_m=5.48e-05,
        res_high_ohm_per_m=6.86e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1033_5_curlew() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1033.5_CURLEW',
        area_mm2=594.0,
        diameter_mm=32.0,
        weight_n_per_m=19.42,
        conductor_rts_kn=162.8,
        dol_per_1000_ft=2182.0,
        inst_dol_per_1000_ft=2926.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=5.41e-05,
        res_low_ohm_per_m=5.41e-05,
        res_high_ohm_per_m=6.92e-05,
        elastic_modulus_gpa=69.0,
        coeff_thermal_expan_per_cel=1.93e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1113_0_bluejay() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1113.0_BLUEJAY',
        area_mm2=604.0,
        diameter_mm=32.0,
        weight_n_per_m=18.29,
        conductor_rts_kn=132.56,
        dol_per_1000_ft=2103.0,
        inst_dol_per_1000_ft=3231.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=5.09e-05,
        res_low_ohm_per_m=5.35e-05,
        res_high_ohm_per_m=6.37e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1192_5_bunting() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1192.5_BUNTING',
        area_mm2=648.0,
        diameter_mm=33.0,
        weight_n_per_m=19.61,
        conductor_rts_kn=142.34,
        dol_per_1000_ft=1961.0,
        inst_dol_per_1000_ft=2850.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=4.72e-05,
        res_low_ohm_per_m=4.72e-05,
        res_high_ohm_per_m=5.97e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1272_0_bittern() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1272.0_BITTERN',
        area_mm2=689.0,
        diameter_mm=34.0,
        weight_n_per_m=20.91,
        conductor_rts_kn=151.68,
        dol_per_1000_ft=2272.0,
        inst_dol_per_1000_ft=3176.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=4.43e-05,
        res_low_ohm_per_m=4.43e-05,
        res_high_ohm_per_m=5.61e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1272_0_pheasant() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1272.0_PHEASANT',
        area_mm2=727.0,
        diameter_mm=35.0,
        weight_n_per_m=23.84,
        conductor_rts_kn=193.94,
        dol_per_1000_ft=2483.0,
        inst_dol_per_1000_ft=3567.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=4.43e-05,
        res_low_ohm_per_m=4.43e-05,
        res_high_ohm_per_m=5.68e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=1.93e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1351_5_dipper() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1351.5_DIPPER',
        area_mm2=731.0,
        diameter_mm=35.0,
        weight_n_per_m=22.2,
        conductor_rts_kn=161.03,
        dol_per_1000_ft=2457.0,
        inst_dol_per_1000_ft=3719.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=4.17e-05,
        res_low_ohm_per_m=4.17e-05,
        res_high_ohm_per_m=5.31e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1351_5_martin() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1351.5_MARTIN',
        area_mm2=772.0,
        diameter_mm=36.0,
        weight_n_per_m=25.33,
        conductor_rts_kn=205.95,
        dol_per_1000_ft=3045.0,
        inst_dol_per_1000_ft=3929.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=4.17e-05,
        res_low_ohm_per_m=4.17e-05,
        res_high_ohm_per_m=5.35e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=1.93e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1431_0_bobolink() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1431.0_BOBOLINK',
        area_mm2=775.0,
        diameter_mm=36.0,
        weight_n_per_m=23.52,
        conductor_rts_kn=170.37,
        dol_per_1000_ft=2785.0,
        inst_dol_per_1000_ft=4034.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=3.94e-05,
        res_low_ohm_per_m=3.94e-05,
        res_high_ohm_per_m=5.02e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1590_0_lapwing() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1590.0_LAPWING',
        area_mm2=860.0,
        diameter_mm=38.0,
        weight_n_per_m=26.13,
        conductor_rts_kn=187.71,
        dol_per_1000_ft=2872.0,
        inst_dol_per_1000_ft=4059.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=3.54e-05,
        res_low_ohm_per_m=3.54e-05,
        res_high_ohm_per_m=4.56e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=2.08e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acsr_1590_0_falcon() -> Conductor:
    return Conductor(
        type='ACSR',
        code='1590.0_FALCON',
        area_mm2=909.0,
        diameter_mm=39.0,
        weight_n_per_m=29.8,
        conductor_rts_kn=242.43,
        dol_per_1000_ft=3390.0,
        inst_dol_per_1000_ft=4664.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=3.54e-05,
        res_low_ohm_per_m=3.54e-05,
        res_high_ohm_per_m=4.59e-05,
        elastic_modulus_gpa=62.7,
        coeff_thermal_expan_per_cel=1.93e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_266_8_partridge() -> Conductor:
    return Conductor(
        type='ACSS',
        code='266.8_PARTRIDGE',
        area_mm2=157.0,
        diameter_mm=16.0,
        weight_n_per_m=5.35,
        conductor_rts_kn=39.5,
        dol_per_1000_ft=760.0,
        inst_dol_per_1000_ft=1027.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000206,
        res_low_ohm_per_m=0.000208,
        res_high_ohm_per_m=0.000254,
        elastic_modulus_gpa=67.95,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_336_4_linnet() -> Conductor:
    return Conductor(
        type='ACSS',
        code='336.4_LINNET',
        area_mm2=198.0,
        diameter_mm=18.0,
        weight_n_per_m=6.76,
        conductor_rts_kn=49.82,
        dol_per_1000_ft=867.0,
        inst_dol_per_1000_ft=1106.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000164,
        res_low_ohm_per_m=0.000165,
        res_high_ohm_per_m=0.000201,
        elastic_modulus_gpa=67.95,
        coeff_thermal_expan_per_cel=1.73e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_336_4_oriole() -> Conductor:
    return Conductor(
        type='ACSS',
        code='336.4_ORIOLE',
        area_mm2=210.0,
        diameter_mm=19.0,
        weight_n_per_m=7.69,
        conductor_rts_kn=65.83,
        dol_per_1000_ft=962.0,
        inst_dol_per_1000_ft=1302.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000163,
        res_low_ohm_per_m=0.000164,
        res_high_ohm_per_m=0.0002,
        elastic_modulus_gpa=72.0,
        coeff_thermal_expan_per_cel=1.6e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_397_5_ibis() -> Conductor:
    return Conductor(
        type='ACSS',
        code='397.5_IBIS',
        area_mm2=234.0,
        diameter_mm=20.0,
        weight_n_per_m=7.97,
        conductor_rts_kn=57.83,
        dol_per_1000_ft=1028.0,
        inst_dol_per_1000_ft=1366.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000139,
        res_low_ohm_per_m=0.00014,
        res_high_ohm_per_m=0.000171,
        elastic_modulus_gpa=67.95,
        coeff_thermal_expan_per_cel=1.73e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_397_5_lark() -> Conductor:
    return Conductor(
        type='ACSS',
        code='397.5_LARK',
        area_mm2=248.0,
        diameter_mm=20.0,
        weight_n_per_m=9.07,
        conductor_rts_kn=77.84,
        dol_per_1000_ft=1141.0,
        inst_dol_per_1000_ft=1430.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000138,
        res_low_ohm_per_m=0.000139,
        res_high_ohm_per_m=0.000169,
        elastic_modulus_gpa=72.0,
        coeff_thermal_expan_per_cel=1.6e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_477_0_flicker() -> Conductor:
    return Conductor(
        type='ACSS',
        code='477.0_FLICKER',
        area_mm2=273.0,
        diameter_mm=21.0,
        weight_n_per_m=8.97,
        conductor_rts_kn=57.83,
        dol_per_1000_ft=1081.0,
        inst_dol_per_1000_ft=1357.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000115,
        res_low_ohm_per_m=0.000117,
        res_high_ohm_per_m=0.000143,
        elastic_modulus_gpa=65.25,
        coeff_thermal_expan_per_cel=1.8e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_477_0_hawk() -> Conductor:
    return Conductor(
        type='ACSS',
        code='477.0_HAWK',
        area_mm2=281.0,
        diameter_mm=22.0,
        weight_n_per_m=9.56,
        conductor_rts_kn=69.39,
        dol_per_1000_ft=1200.0,
        inst_dol_per_1000_ft=1594.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000116,
        res_low_ohm_per_m=0.000116,
        res_high_ohm_per_m=0.000142,
        elastic_modulus_gpa=67.95,
        coeff_thermal_expan_per_cel=1.73e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_477_0_hen() -> Conductor:
    return Conductor(
        type='ACSS',
        code='477.0_HEN',
        area_mm2=298.0,
        diameter_mm=22.0,
        weight_n_per_m=10.89,
        conductor_rts_kn=93.41,
        dol_per_1000_ft=1283.0,
        inst_dol_per_1000_ft=1741.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000115,
        res_low_ohm_per_m=0.000116,
        res_high_ohm_per_m=0.000141,
        elastic_modulus_gpa=72.0,
        coeff_thermal_expan_per_cel=1.6e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_556_5_parakeet() -> Conductor:
    return Conductor(
        type='ACSS',
        code='556.5_PARAKEET',
        area_mm2=319.0,
        diameter_mm=23.0,
        weight_n_per_m=10.46,
        conductor_rts_kn=67.61,
        dol_per_1000_ft=1318.0,
        inst_dol_per_1000_ft=1818.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=9.93e-05,
        res_low_ohm_per_m=0.0001,
        res_high_ohm_per_m=0.000123,
        elastic_modulus_gpa=65.25,
        coeff_thermal_expan_per_cel=1.8e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_556_5_dove() -> Conductor:
    return Conductor(
        type='ACSS',
        code='556.5_DOVE',
        area_mm2=329.0,
        diameter_mm=24.0,
        weight_n_per_m=11.17,
        conductor_rts_kn=80.96,
        dol_per_1000_ft=1378.0,
        inst_dol_per_1000_ft=1804.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=9.9e-05,
        res_low_ohm_per_m=0.0001,
        res_high_ohm_per_m=0.000122,
        elastic_modulus_gpa=67.95,
        coeff_thermal_expan_per_cel=1.73e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_636_0_grosbeak() -> Conductor:
    return Conductor(
        type='ACSS',
        code='636.0_GROSBEAK',
        area_mm2=374.0,
        diameter_mm=25.0,
        weight_n_per_m=12.77,
        conductor_rts_kn=92.08,
        dol_per_1000_ft=1545.0,
        inst_dol_per_1000_ft=2031.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.67e-05,
        res_low_ohm_per_m=8.77e-05,
        res_high_ohm_per_m=0.000107,
        elastic_modulus_gpa=67.95,
        coeff_thermal_expan_per_cel=1.73e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_666_6_flamingo() -> Conductor:
    return Conductor(
        type='ACSS',
        code='666.6_FLAMINGO',
        area_mm2=381.0,
        diameter_mm=25.0,
        weight_n_per_m=12.52,
        conductor_rts_kn=80.96,
        dol_per_1000_ft=1711.0,
        inst_dol_per_1000_ft=2146.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.3e-05,
        res_low_ohm_per_m=8.42e-05,
        res_high_ohm_per_m=0.000103,
        elastic_modulus_gpa=65.25,
        coeff_thermal_expan_per_cel=1.8e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_795_0_tern() -> Conductor:
    return Conductor(
        type='ACSS',
        code='795.0_TERN',
        area_mm2=432.0,
        diameter_mm=27.0,
        weight_n_per_m=13.07,
        conductor_rts_kn=63.16,
        dol_per_1000_ft=1627.0,
        inst_dol_per_1000_ft=2048.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=7e-05,
        res_low_ohm_per_m=7.2e-05,
        res_high_ohm_per_m=8.77e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_795_0_cuckoo() -> Conductor:
    return Conductor(
        type='ACSS',
        code='795.0_CUCKOO',
        area_mm2=455.0,
        diameter_mm=28.0,
        weight_n_per_m=14.93,
        conductor_rts_kn=96.53,
        dol_per_1000_ft=1830.0,
        inst_dol_per_1000_ft=2291.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.97e-05,
        res_low_ohm_per_m=7.09e-05,
        res_high_ohm_per_m=8.63e-05,
        elastic_modulus_gpa=65.25,
        coeff_thermal_expan_per_cel=1.8e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_795_0_drake() -> Conductor:
    return Conductor(
        type='ACSS',
        code='795.0_DRAKE',
        area_mm2=468.0,
        diameter_mm=28.0,
        weight_n_per_m=15.95,
        conductor_rts_kn=115.21,
        dol_per_1000_ft=1721.0,
        inst_dol_per_1000_ft=2359.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.97e-05,
        res_low_ohm_per_m=7.05e-05,
        res_high_ohm_per_m=8.57e-05,
        elastic_modulus_gpa=67.95,
        coeff_thermal_expan_per_cel=1.73e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_900_0_canary() -> Conductor:
    return Conductor(
        type='ACSS',
        code='900.0_CANARY',
        area_mm2=516.0,
        diameter_mm=30.0,
        weight_n_per_m=16.91,
        conductor_rts_kn=109.43,
        dol_per_1000_ft=1888.0,
        inst_dol_per_1000_ft=2632.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.13e-05,
        res_low_ohm_per_m=6.29e-05,
        res_high_ohm_per_m=7.87e-05,
        elastic_modulus_gpa=62.1,
        coeff_thermal_expan_per_cel=1.74e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_954_0_rail() -> Conductor:
    return Conductor(
        type='ACSS',
        code='954.0_RAIL',
        area_mm2=517.0,
        diameter_mm=30.0,
        weight_n_per_m=15.69,
        conductor_rts_kn=74.29,
        dol_per_1000_ft=1836.0,
        inst_dol_per_1000_ft=2502.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.83e-05,
        res_low_ohm_per_m=6.01e-05,
        res_high_ohm_per_m=7.33e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_954_0_cardinal() -> Conductor:
    return Conductor(
        type='ACSS',
        code='954.0_CARDINAL',
        area_mm2=547.0,
        diameter_mm=30.0,
        weight_n_per_m=17.93,
        conductor_rts_kn=115.65,
        dol_per_1000_ft=2036.0,
        inst_dol_per_1000_ft=2757.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.8e-05,
        res_low_ohm_per_m=5.94e-05,
        res_high_ohm_per_m=7.43e-05,
        elastic_modulus_gpa=62.1,
        coeff_thermal_expan_per_cel=1.74e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1033_5_ortolan() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1033.5_ORTOLAN',
        area_mm2=560.0,
        diameter_mm=31.0,
        weight_n_per_m=16.99,
        conductor_rts_kn=80.51,
        dol_per_1000_ft=2447.0,
        inst_dol_per_1000_ft=3026.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.4e-05,
        res_low_ohm_per_m=5.58e-05,
        res_high_ohm_per_m=6.8e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1033_5_curlew() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1033.5_CURLEW',
        area_mm2=594.0,
        diameter_mm=32.0,
        weight_n_per_m=19.4,
        conductor_rts_kn=125.44,
        dol_per_1000_ft=2067.0,
        inst_dol_per_1000_ft=2926.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.37e-05,
        res_low_ohm_per_m=5.51e-05,
        res_high_ohm_per_m=6.87e-05,
        elastic_modulus_gpa=62.1,
        coeff_thermal_expan_per_cel=1.74e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1113_0_bluejay() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1113.0_BLUEJAY',
        area_mm2=604.0,
        diameter_mm=32.0,
        weight_n_per_m=18.28,
        conductor_rts_kn=86.74,
        dol_per_1000_ft=2626.0,
        inst_dol_per_1000_ft=3231.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5e-05,
        res_low_ohm_per_m=5.22e-05,
        res_high_ohm_per_m=6.33e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1192_5_bunting() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1192.5_BUNTING',
        area_mm2=648.0,
        diameter_mm=33.0,
        weight_n_per_m=19.61,
        conductor_rts_kn=95.19,
        dol_per_1000_ft=2198.0,
        inst_dol_per_1000_ft=2850.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.67e-05,
        res_low_ohm_per_m=4.89e-05,
        res_high_ohm_per_m=5.93e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1272_0_bittern() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1272.0_BITTERN',
        area_mm2=689.0,
        diameter_mm=34.0,
        weight_n_per_m=20.91,
        conductor_rts_kn=99.2,
        dol_per_1000_ft=2352.0,
        inst_dol_per_1000_ft=3176.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.37e-05,
        res_low_ohm_per_m=4.59e-05,
        res_high_ohm_per_m=5.57e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1272_0_pheasant() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1272.0_PHEASANT',
        area_mm2=727.0,
        diameter_mm=35.0,
        weight_n_per_m=23.85,
        conductor_rts_kn=151.68,
        dol_per_1000_ft=2719.0,
        inst_dol_per_1000_ft=3567.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.37e-05,
        res_low_ohm_per_m=4e-05,
        res_high_ohm_per_m=5.63e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.74e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1351_5_dipper() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1351.5_DIPPER',
        area_mm2=731.0,
        diameter_mm=35.0,
        weight_n_per_m=22.19,
        conductor_rts_kn=105.42,
        dol_per_1000_ft=2982.0,
        inst_dol_per_1000_ft=3719.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.13e-05,
        res_low_ohm_per_m=4.52e-05,
        res_high_ohm_per_m=5.27e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1351_5_martin() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1351.5_MARTIN',
        area_mm2=772.0,
        diameter_mm=36.0,
        weight_n_per_m=25.32,
        conductor_rts_kn=161.03,
        dol_per_1000_ft=2649.0,
        inst_dol_per_1000_ft=3929.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.1e-05,
        res_low_ohm_per_m=4.3e-05,
        res_high_ohm_per_m=5.33e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.74e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1431_0_bobolink() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1431.0_BOBOLINK',
        area_mm2=775.0,
        diameter_mm=36.0,
        weight_n_per_m=23.52,
        conductor_rts_kn=111.65,
        dol_per_1000_ft=3100.0,
        inst_dol_per_1000_ft=4034.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.9e-05,
        res_low_ohm_per_m=4.13e-05,
        res_high_ohm_per_m=5e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1590_0_lapwing() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1590.0_LAPWING',
        area_mm2=860.0,
        diameter_mm=38.0,
        weight_n_per_m=26.12,
        conductor_rts_kn=124.11,
        dol_per_1000_ft=3042.0,
        inst_dol_per_1000_ft=4059.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.5e-05,
        res_low_ohm_per_m=3.77e-05,
        res_high_ohm_per_m=4.53e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.87e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def acss_1590_0_falcon() -> Conductor:
    return Conductor(
        type='ACSS',
        code='1590.0_FALCON',
        area_mm2=909.0,
        diameter_mm=39.0,
        weight_n_per_m=29.83,
        conductor_rts_kn=189.49,
        dol_per_1000_ft=3393.0,
        inst_dol_per_1000_ft=4664.0,
        accessories_dol_per_1000_ft=263.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.5e-05,
        res_low_ohm_per_m=3.7e-05,
        res_high_ohm_per_m=4.57e-05,
        elastic_modulus_gpa=56.43,
        coeff_thermal_expan_per_cel=1.74e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_297_helsinki() -> Conductor:
    return Conductor(
        type='ACCC',
        code='297_HELSINKI',
        area_mm2=151.0,
        diameter_mm=16.0,
        weight_n_per_m=4.62,
        conductor_rts_kn=68.9,
        dol_per_1000_ft=1837.5,
        inst_dol_per_1000_ft=2567.5,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000186,
        res_low_ohm_per_m=0.00019,
        res_high_ohm_per_m=0.000321,
        elastic_modulus_gpa=75.8,
        coeff_thermal_expan_per_cel=1.79e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_434_copenhagen() -> Conductor:
    return Conductor(
        type='ACCC',
        code='434_COPENHAGEN',
        area_mm2=220.0,
        diameter_mm=18.0,
        weight_n_per_m=6.48,
        conductor_rts_kn=72.8,
        dol_per_1000_ft=2005.0,
        inst_dol_per_1000_ft=2825.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000127,
        res_low_ohm_per_m=0.00013,
        res_high_ohm_per_m=0.00022,
        elastic_modulus_gpa=73.7,
        coeff_thermal_expan_per_cel=1.91e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_467_glasgow() -> Conductor:
    return Conductor(
        type='ACCC',
        code='467_GLASGOW',
        area_mm2=237.0,
        diameter_mm=20.0,
        weight_n_per_m=7.18,
        conductor_rts_kn=115.0,
        dol_per_1000_ft=2407.5,
        inst_dol_per_1000_ft=3415.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000119,
        res_low_ohm_per_m=0.000122,
        res_high_ohm_per_m=0.000204,
        elastic_modulus_gpa=76.4,
        coeff_thermal_expan_per_cel=1.75e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_540_casablanca() -> Conductor:
    return Conductor(
        type='ACCC',
        code='540_CASABLANCA',
        area_mm2=274.0,
        diameter_mm=21.0,
        weight_n_per_m=8.18,
        conductor_rts_kn=101.1,
        dol_per_1000_ft=2255.0,
        inst_dol_per_1000_ft=3392.5,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000102,
        res_low_ohm_per_m=0.000105,
        res_high_ohm_per_m=0.000177,
        elastic_modulus_gpa=74.5,
        coeff_thermal_expan_per_cel=1.86e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_619_oslo() -> Conductor:
    return Conductor(
        type='ACCC',
        code='619_OSLO',
        area_mm2=314.0,
        diameter_mm=22.0,
        weight_n_per_m=9.62,
        conductor_rts_kn=147.8,
        dol_per_1000_ft=3310.0,
        inst_dol_per_1000_ft=4545.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.93e-05,
        res_low_ohm_per_m=9.11e-05,
        res_high_ohm_per_m=0.000154,
        elastic_modulus_gpa=76.2,
        coeff_thermal_expan_per_cel=1.76e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_623_lisbon() -> Conductor:
    return Conductor(
        type='ACCC',
        code='623_LISBON',
        area_mm2=316.0,
        diameter_mm=22.0,
        weight_n_per_m=9.3,
        conductor_rts_kn=103.5,
        dol_per_1000_ft=3310.0,
        inst_dol_per_1000_ft=4545.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.87e-05,
        res_low_ohm_per_m=9.1e-05,
        res_high_ohm_per_m=0.000153,
        elastic_modulus_gpa=73.8,
        coeff_thermal_expan_per_cel=1.91e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_725_amsterdam() -> Conductor:
    return Conductor(
        type='ACCC',
        code='725_AMSTERDAM',
        area_mm2=367.0,
        diameter_mm=24.0,
        weight_n_per_m=10.8,
        conductor_rts_kn=122.4,
        dol_per_1000_ft=3090.0,
        inst_dol_per_1000_ft=4652.5,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=7.62e-05,
        res_low_ohm_per_m=7.84e-05,
        res_high_ohm_per_m=0.000132,
        elastic_modulus_gpa=73.8,
        coeff_thermal_expan_per_cel=1.91e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_832_brussels() -> Conductor:
    return Conductor(
        type='ACCC',
        code='832_BRUSSELS',
        area_mm2=421.0,
        diameter_mm=25.0,
        weight_n_per_m=12.41,
        conductor_rts_kn=135.7,
        dol_per_1000_ft=3415.0,
        inst_dol_per_1000_ft=5120.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.66e-05,
        res_low_ohm_per_m=6.87e-05,
        res_high_ohm_per_m=0.000115,
        elastic_modulus_gpa=73.6,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1002_warsaw() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1002_WARSAW',
        area_mm2=508.0,
        diameter_mm=28.0,
        weight_n_per_m=14.91,
        conductor_rts_kn=158.7,
        dol_per_1000_ft=4842.5,
        inst_dol_per_1000_ft=6580.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.53e-05,
        res_low_ohm_per_m=5.73e-05,
        res_high_ohm_per_m=9.58e-05,
        elastic_modulus_gpa=73.3,
        coeff_thermal_expan_per_cel=1.94e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1035_dublin() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1035_DUBLIN',
        area_mm2=525.0,
        diameter_mm=28.0,
        weight_n_per_m=15.53,
        conductor_rts_kn=183.3,
        dol_per_1000_ft=4512.5,
        inst_dol_per_1000_ft=6255.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.34e-05,
        res_low_ohm_per_m=5.53e-05,
        res_high_ohm_per_m=9.25e-05,
        elastic_modulus_gpa=74.1,
        coeff_thermal_expan_per_cel=1.89e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1078_hamburg() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1078_HAMBURG',
        area_mm2=546.0,
        diameter_mm=29.0,
        weight_n_per_m=15.96,
        conductor_rts_kn=160.9,
        dol_per_1000_ft=4942.5,
        inst_dol_per_1000_ft=6892.5,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.14e-05,
        res_low_ohm_per_m=5.34e-05,
        res_high_ohm_per_m=8.91e-05,
        elastic_modulus_gpa=73.1,
        coeff_thermal_expan_per_cel=1.95e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1120_milan() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1120_MILAN',
        area_mm2=568.0,
        diameter_mm=29.0,
        weight_n_per_m=16.54,
        conductor_rts_kn=162.1,
        dol_per_1000_ft=4947.5,
        inst_dol_per_1000_ft=7565.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.94e-05,
        res_low_ohm_per_m=5.14e-05,
        res_high_ohm_per_m=8.57e-05,
        elastic_modulus_gpa=72.9,
        coeff_thermal_expan_per_cel=1.96e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1169_rome() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1169_ROME',
        area_mm2=593.0,
        diameter_mm=30.0,
        weight_n_per_m=17.4,
        conductor_rts_kn=187.1,
        dol_per_1000_ft=5455.0,
        inst_dol_per_1000_ft=7315.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.74e-05,
        res_low_ohm_per_m=4.94e-05,
        res_high_ohm_per_m=8.22e-05,
        elastic_modulus_gpa=73.5,
        coeff_thermal_expan_per_cel=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1242_vienna() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1242_VIENNA',
        area_mm2=629.0,
        diameter_mm=30.0,
        weight_n_per_m=18.18,
        conductor_rts_kn=165.5,
        dol_per_1000_ft=4902.5,
        inst_dol_per_1000_ft=7125.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.45e-05,
        res_low_ohm_per_m=4.66e-05,
        res_high_ohm_per_m=7.73e-05,
        elastic_modulus_gpa=72.5,
        coeff_thermal_expan_per_cel=1.99e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1319_budapest() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1319_BUDAPEST',
        area_mm2=668.0,
        diameter_mm=32.0,
        weight_n_per_m=19.46,
        conductor_rts_kn=191.4,
        dol_per_1000_ft=4902.5,
        inst_dol_per_1000_ft=7125.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.2e-05,
        res_low_ohm_per_m=4.4e-05,
        res_high_ohm_per_m=7.3e-05,
        elastic_modulus_gpa=72.9,
        coeff_thermal_expan_per_cel=1.96e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1363_prague() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1363_PRAGUE',
        area_mm2=691.0,
        diameter_mm=32.0,
        weight_n_per_m=19.92,
        conductor_rts_kn=169.0,
        dol_per_1000_ft=5680.0,
        inst_dol_per_1000_ft=7940.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.07e-05,
        res_low_ohm_per_m=4.28e-05,
        res_high_ohm_per_m=7.08e-05,
        elastic_modulus_gpa=72.1,
        coeff_thermal_expan_per_cel=2.01e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1447_munich() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1447_MUNICH',
        area_mm2=733.0,
        diameter_mm=33.0,
        weight_n_per_m=21.29,
        conductor_rts_kn=195.0,
        dol_per_1000_ft=6142.5,
        inst_dol_per_1000_ft=9297.5,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.84e-05,
        res_low_ohm_per_m=4.05e-05,
        res_high_ohm_per_m=6.69e-05,
        elastic_modulus_gpa=72.6,
        coeff_thermal_expan_per_cel=1.99e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1498_london() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1498_LONDON',
        area_mm2=759.0,
        diameter_mm=33.0,
        weight_n_per_m=22.05,
        conductor_rts_kn=204.8,
        dol_per_1000_ft=7612.5,
        inst_dol_per_1000_ft=9822.5,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.7e-05,
        res_low_ohm_per_m=3.91e-05,
        res_high_ohm_per_m=6.44e-05,
        elastic_modulus_gpa=72.6,
        coeff_thermal_expan_per_cel=1.98e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1606_paris() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1606_PARIS',
        area_mm2=814.0,
        diameter_mm=34.0,
        weight_n_per_m=23.21,
        conductor_rts_kn=175.9,
        dol_per_1000_ft=6962.5,
        inst_dol_per_1000_ft=10085.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.45e-05,
        res_low_ohm_per_m=3.68e-05,
        res_high_ohm_per_m=6.03e-05,
        elastic_modulus_gpa=71.6,
        coeff_thermal_expan_per_cel=2.05e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1865_antwerp() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1865_ANTWERP',
        area_mm2=945.0,
        diameter_mm=37.0,
        weight_n_per_m=27.08,
        conductor_rts_kn=215.2,
        dol_per_1000_ft=8475.0,
        inst_dol_per_1000_ft=11660.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=2.97e-05,
        res_low_ohm_per_m=3.21e-05,
        res_high_ohm_per_m=5.21e-05,
        elastic_modulus_gpa=71.8,
        coeff_thermal_expan_per_cel=2.03e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accc_1999_madrid() -> Conductor:
    return Conductor(
        type='ACCC',
        code='1999_MADRID',
        area_mm2=1010.0,
        diameter_mm=38.0,
        weight_n_per_m=28.92,
        conductor_rts_kn=219.1,
        dol_per_1000_ft=8475.0,
        inst_dol_per_1000_ft=11660.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=200.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=2.76e-05,
        res_low_ohm_per_m=3.02e-05,
        res_high_ohm_per_m=4.85e-05,
        elastic_modulus_gpa=71.5,
        coeff_thermal_expan_per_cel=2.05e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_2715_sanford() -> Conductor:
    return Conductor(
        type='AECC',
        code='2715_SANFORD',
        area_mm2=1570.0,
        diameter_mm=44.8,
        weight_n_per_m=39.24,
        conductor_rts_kn=365.6,
        dol_per_1000_ft=10170.0,
        inst_dol_per_1000_ft=13992.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=2.05e-05,
        res_low_ohm_per_m=2.45e-05,
        res_high_ohm_per_m=2.82e-05,
        elastic_modulus_gpa=61.6,
        coeff_thermal_expan_per_cel=1.35e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_2609_killdeer() -> Conductor:
    return Conductor(
        type='AECC',
        code='2609_KILLDEER',
        area_mm2=1500.0,
        diameter_mm=45.7,
        weight_n_per_m=37.51,
        conductor_rts_kn=314.89,
        dol_per_1000_ft=10170.0,
        inst_dol_per_1000_ft=13992.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=2.13e-05,
        res_low_ohm_per_m=2.53e-05,
        res_high_ohm_per_m=2.92e-05,
        elastic_modulus_gpa=60.8,
        coeff_thermal_expan_per_cel=1.35e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_2117_blanca() -> Conductor:
    return Conductor(
        type='AECC',
        code='2117_BLANCA',
        area_mm2=1210.0,
        diameter_mm=39.2,
        weight_n_per_m=30.19,
        conductor_rts_kn=237.22,
        dol_per_1000_ft=10170.0,
        inst_dol_per_1000_ft=13992.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=2.61e-05,
        res_low_ohm_per_m=2.98e-05,
        res_high_ohm_per_m=3.47e-05,
        elastic_modulus_gpa=60.3,
        coeff_thermal_expan_per_cel=1.35e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_2093_williamson() -> Conductor:
    return Conductor(
        type='AECC',
        code='2093_WILLIAMSON',
        area_mm2=1210.0,
        diameter_mm=39.2,
        weight_n_per_m=30.1,
        conductor_rts_kn=277.97,
        dol_per_1000_ft=10170.0,
        inst_dol_per_1000_ft=13992.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=2.64e-05,
        res_low_ohm_per_m=2.99e-05,
        res_high_ohm_per_m=3.49e-05,
        elastic_modulus_gpa=61.6,
        coeff_thermal_expan_per_cel=1.35e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_2074_helvellyn() -> Conductor:
    return Conductor(
        type='AECC',
        code='2074_HELVELLYN',
        area_mm2=1210.0,
        diameter_mm=39.3,
        weight_n_per_m=30.25,
        conductor_rts_kn=347.32,
        dol_per_1000_ft=10170.0,
        inst_dol_per_1000_ft=13992.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=2.67e-05,
        res_low_ohm_per_m=2.91e-05,
        res_high_ohm_per_m=3.43e-05,
        elastic_modulus_gpa=63.7,
        coeff_thermal_expan_per_cel=1.35e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_1608_bersfort() -> Conductor:
    return Conductor(
        type='AECC',
        code='1608_BERSFORT',
        area_mm2=962.0,
        diameter_mm=35.0,
        weight_n_per_m=23.82,
        conductor_rts_kn=334.02,
        dol_per_1000_ft=10170.0,
        inst_dol_per_1000_ft=13992.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.43e-05,
        res_low_ohm_per_m=3.64e-05,
        res_high_ohm_per_m=4.32e-05,
        elastic_modulus_gpa=66.2,
        coeff_thermal_expan_per_cel=1.35e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_1494_altar() -> Conductor:
    return Conductor(
        type='AECC',
        code='1494_ALTAR',
        area_mm2=876.0,
        diameter_mm=33.4,
        weight_n_per_m=21.69,
        conductor_rts_kn=239.63,
        dol_per_1000_ft=8616.0,
        inst_dol_per_1000_ft=12177.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.7e-05,
        res_low_ohm_per_m=3.98e-05,
        res_high_ohm_per_m=4.7e-05,
        elastic_modulus_gpa=63.4,
        coeff_thermal_expan_per_cel=1.46e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_1360_sierra() -> Conductor:
    return Conductor(
        type='AECC',
        code='1360_SIERRA',
        area_mm2=803.0,
        diameter_mm=32.0,
        weight_n_per_m=19.8,
        conductor_rts_kn=235.8,
        dol_per_1000_ft=8355.0,
        inst_dol_per_1000_ft=12102.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.05e-05,
        res_low_ohm_per_m=4.32e-05,
        res_high_ohm_per_m=5.11e-05,
        elastic_modulus_gpa=64.3,
        coeff_thermal_expan_per_cel=1.46e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_1099_ruddy() -> Conductor:
    return Conductor(
        type='AECC',
        code='1099_RUDDY',
        area_mm2=648.0,
        diameter_mm=28.7,
        weight_n_per_m=15.98,
        conductor_rts_kn=189.09,
        dol_per_1000_ft=5883.0,
        inst_dol_per_1000_ft=8550.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.01e-05,
        res_low_ohm_per_m=5.26e-05,
        res_high_ohm_per_m=6.26e-05,
        elastic_modulus_gpa=64.2,
        coeff_thermal_expan_per_cel=1.46e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_1094_pennell() -> Conductor:
    return Conductor(
        type='AECC',
        code='1094_PENNELL',
        area_mm2=659.0,
        diameter_mm=29.0,
        weight_n_per_m=16.14,
        conductor_rts_kn=228.24,
        dol_per_1000_ft=5883.0,
        inst_dol_per_1000_ft=8550.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.02e-05,
        res_low_ohm_per_m=5.27e-05,
        res_high_ohm_per_m=6.27e-05,
        elastic_modulus_gpa=66.4,
        coeff_thermal_expan_per_cel=1.46e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_1039_fishers() -> Conductor:
    return Conductor(
        type='AECC',
        code='1039_FISHERS',
        area_mm2=622.0,
        diameter_mm=28.1,
        weight_n_per_m=15.28,
        conductor_rts_kn=206.49,
        dol_per_1000_ft=6309.0,
        inst_dol_per_1000_ft=9693.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.29e-05,
        res_low_ohm_per_m=5.53e-05,
        res_high_ohm_per_m=6.59e-05,
        elastic_modulus_gpa=65.9,
        coeff_thermal_expan_per_cel=1.46e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_1027_gould() -> Conductor:
    return Conductor(
        type='AECC',
        code='1027_GOULD',
        area_mm2=622.0,
        diameter_mm=28.1,
        weight_n_per_m=15.23,
        conductor_rts_kn=226.33,
        dol_per_1000_ft=6309.0,
        inst_dol_per_1000_ft=9693.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.35e-05,
        res_low_ohm_per_m=5.59e-05,
        res_high_ohm_per_m=6.66e-05,
        elastic_modulus_gpa=67.1,
        coeff_thermal_expan_per_cel=1.46e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_979_fernow() -> Conductor:
    return Conductor(
        type='AECC',
        code='979_FERNOW',
        area_mm2=573.0,
        diameter_mm=27.0,
        weight_n_per_m=14.22,
        conductor_rts_kn=167.74,
        dol_per_1000_ft=5937.0,
        inst_dol_per_1000_ft=9078.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.62e-05,
        res_low_ohm_per_m=5.87e-05,
        res_high_ohm_per_m=6.99e-05,
        elastic_modulus_gpa=64.2,
        coeff_thermal_expan_per_cel=1.46e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_817_tern() -> Conductor:
    return Conductor(
        type='AECC',
        code='817_TERN',
        area_mm2=509.0,
        diameter_mm=25.5,
        weight_n_per_m=12.34,
        conductor_rts_kn=219.96,
        dol_per_1000_ft=5811.0,
        inst_dol_per_1000_ft=7896.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.72e-05,
        res_low_ohm_per_m=6.95e-05,
        res_high_ohm_per_m=8.31e-05,
        elastic_modulus_gpa=69.7,
        coeff_thermal_expan_per_cel=1.35e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_738_martin() -> Conductor:
    return Conductor(
        type='AECC',
        code='738_MARTIN',
        area_mm2=374.0,
        diameter_mm=23.5,
        weight_n_per_m=10.73,
        conductor_rts_kn=128.15,
        dol_per_1000_ft=4248.0,
        inst_dol_per_1000_ft=6093.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=7.44e-05,
        res_low_ohm_per_m=7.7e-05,
        res_high_ohm_per_m=9.2e-05,
        elastic_modulus_gpa=64.4,
        coeff_thermal_expan_per_cel=1.34e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def aecc_632_hawk() -> Conductor:
    return Conductor(
        type='AECC',
        code='632_HAWK',
        area_mm2=632.0,
        diameter_mm=21.8,
        weight_n_per_m=9.2,
        conductor_rts_kn=110.54,
        dol_per_1000_ft=5883.0,
        inst_dol_per_1000_ft=8550.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.69e-05,
        res_low_ohm_per_m=8.92e-05,
        res_high_ohm_per_m=1.07e-05,
        elastic_modulus_gpa=64.6,
        coeff_thermal_expan_per_cel=1.46e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_300_ostrich() -> Conductor:
    return Conductor(
        type='ACCR',
        code='300_OSTRICH',
        area_mm2=175.0,
        diameter_mm=17.2,
        weight_n_per_m=4.916,
        conductor_rts_kn=53.823,
        dol_per_1000_ft=5200.0,
        inst_dol_per_1000_ft=7536.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=0.000183,
        res_low_ohm_per_m=0.000187,
        res_high_ohm_per_m=0.000324,
        elastic_modulus_gpa=78.0,
        coeff_thermal_expan_per_cel=1.67e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_336_linnet() -> Conductor:
    return Conductor(
        type='ACCR',
        code='336_LINNET',
        area_mm2=200.0,
        diameter_mm=18.4,
        weight_n_per_m=5.625,
        conductor_rts_kn=61.83,
        dol_per_1000_ft=5992.0,
        inst_dol_per_1000_ft=8848.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=0.00016,
        res_low_ohm_per_m=0.000163,
        res_high_ohm_per_m=0.000283,
        elastic_modulus_gpa=78.0,
        coeff_thermal_expan_per_cel=1.67e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_397_ibis() -> Conductor:
    return Conductor(
        type='ACCR',
        code='397_IBIS',
        area_mm2=239.0,
        diameter_mm=20.1,
        weight_n_per_m=6.707,
        conductor_rts_kn=73.396,
        dol_per_1000_ft=7704.0,
        inst_dol_per_1000_ft=10928.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=0.000134,
        res_low_ohm_per_m=0.000137,
        res_high_ohm_per_m=0.000237,
        elastic_modulus_gpa=78.0,
        coeff_thermal_expan_per_cel=1.67e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_477_hawk() -> Conductor:
    return Conductor(
        type='ACCR',
        code='477_HAWK',
        area_mm2=277.0,
        diameter_mm=21.6,
        weight_n_per_m=7.781,
        conductor_rts_kn=85.406,
        dol_per_1000_ft=7216.0,
        inst_dol_per_1000_ft=10856.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=0.000115,
        res_low_ohm_per_m=0.000118,
        res_high_ohm_per_m=0.000205,
        elastic_modulus_gpa=78.0,
        coeff_thermal_expan_per_cel=1.67e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_557_dove() -> Conductor:
    return Conductor(
        type='ACCR',
        code='557_DOVE',
        area_mm2=338.0,
        diameter_mm=23.9,
        weight_n_per_m=9.483,
        conductor_rts_kn=102.754,
        dol_per_1000_ft=8720.0,
        inst_dol_per_1000_ft=12992.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=9.45e-05,
        res_low_ohm_per_m=9.45e-05,
        res_high_ohm_per_m=0.000168,
        elastic_modulus_gpa=78.0,
        coeff_thermal_expan_per_cel=1.67e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_636_grosbeak() -> Conductor:
    return Conductor(
        type='ACCR',
        code='636_GROSBEAK',
        area_mm2=385.0,
        diameter_mm=25.5,
        weight_n_per_m=10.799,
        conductor_rts_kn=113.874,
        dol_per_1000_ft=11680.0,
        inst_dol_per_1000_ft=17168.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=8.28e-05,
        res_low_ohm_per_m=8.48e-05,
        res_high_ohm_per_m=0.000147,
        elastic_modulus_gpa=77.0,
        coeff_thermal_expan_per_cel=1.65e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_795_drake() -> Conductor:
    return Conductor(
        type='ACCR',
        code='795_DRAKE',
        area_mm2=484.0,
        diameter_mm=28.6,
        weight_n_per_m=13.576,
        conductor_rts_kn=143.233,
        dol_per_1000_ft=13688.0,
        inst_dol_per_1000_ft=18872.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=6.58e-05,
        res_low_ohm_per_m=6.74e-05,
        res_high_ohm_per_m=0.000117,
        elastic_modulus_gpa=74.0,
        coeff_thermal_expan_per_cel=1.65e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_954_cardinal() -> Conductor:
    return Conductor(
        type='ACCR',
        code='954_CARDINAL',
        area_mm2=552.0,
        diameter_mm=30.6,
        weight_n_per_m=15.455,
        conductor_rts_kn=147.681,
        dol_per_1000_ft=15816.0,
        inst_dol_per_1000_ft=22056.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=5.72e-05,
        res_low_ohm_per_m=5.85e-05,
        res_high_ohm_per_m=0.000101,
        elastic_modulus_gpa=73.0,
        coeff_thermal_expan_per_cel=1.71e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_1033_curlew() -> Conductor:
    return Conductor(
        type='ACCR',
        code='1033_CURLEW',
        area_mm2=591.0,
        diameter_mm=31.7,
        weight_n_per_m=16.55,
        conductor_rts_kn=158.357,
        dol_per_1000_ft=17456.0,
        inst_dol_per_1000_ft=23408.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=5.34e-05,
        res_low_ohm_per_m=5.46e-05,
        res_high_ohm_per_m=9.47e-05,
        elastic_modulus_gpa=73.0,
        coeff_thermal_expan_per_cel=1.71e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_1112_finch() -> Conductor:
    return Conductor(
        type='ACCR',
        code='1112_FINCH',
        area_mm2=638.0,
        diameter_mm=32.9,
        weight_n_per_m=17.848,
        conductor_rts_kn=170.812,
        dol_per_1000_ft=15688.0,
        inst_dol_per_1000_ft=22800.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=4.95e-05,
        res_low_ohm_per_m=5.07e-05,
        res_high_ohm_per_m=8.78e-05,
        elastic_modulus_gpa=73.0,
        coeff_thermal_expan_per_cel=1.71e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_1272_pheasant() -> Conductor:
    return Conductor(
        type='ACCR',
        code='1272_PHEASANT',
        area_mm2=723.0,
        diameter_mm=35.0,
        weight_n_per_m=20.236,
        conductor_rts_kn=191.273,
        dol_per_1000_ft=19864.0,
        inst_dol_per_1000_ft=28536.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=4.36e-05,
        res_low_ohm_per_m=4.47e-05,
        res_high_ohm_per_m=7.74e-05,
        elastic_modulus_gpa=73.0,
        coeff_thermal_expan_per_cel=1.71e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_1351_martin() -> Conductor:
    return Conductor(
        type='ACCR',
        code='1351_MARTIN',
        area_mm2=761.0,
        diameter_mm=35.9,
        weight_n_per_m=21.305,
        conductor_rts_kn=201.504,
        dol_per_1000_ft=24360.0,
        inst_dol_per_1000_ft=31432.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=4.14e-05,
        res_low_ohm_per_m=4.24e-05,
        res_high_ohm_per_m=7.35e-05,
        elastic_modulus_gpa=73.0,
        coeff_thermal_expan_per_cel=1.71e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accr_1590_falcon() -> Conductor:
    return Conductor(
        type='ACCR',
        code='1590_FALCON',
        area_mm2=910.0,
        diameter_mm=39.3,
        weight_n_per_m=25.462,
        conductor_rts_kn=238.425,
        dol_per_1000_ft=27120.0,
        inst_dol_per_1000_ft=37312.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=210.0,
        max_temperature_c=240.0,
        res_dc_ohm_per_m=3.47e-05,
        res_low_ohm_per_m=3.55e-05,
        res_high_ohm_per_m=6.15e-05,
        elastic_modulus_gpa=73.0,
        coeff_thermal_expan_per_cel=1.71e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_266_8_shenandoah() -> Conductor:
    return Conductor(
        type='ACCS',
        code='266.8_SHENANDOAH',
        area_mm2=163.0,
        diameter_mm=15.4,
        weight_n_per_m=4.115,
        conductor_rts_kn=66.7,
        dol_per_1000_ft=3675.0,
        inst_dol_per_1000_ft=5135.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000207707,
        res_low_ohm_per_m=0.000212,
        res_high_ohm_per_m=0.000346,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_325_0_olympic() -> Conductor:
    return Conductor(
        type='ACCS',
        code='325.0_OLYMPIC',
        area_mm2=193.0,
        diameter_mm=17.0,
        weight_n_per_m=4.901,
        conductor_rts_kn=68.5,
        dol_per_1000_ft=3745.0,
        inst_dol_per_1000_ft=5530.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000170044,
        res_low_ohm_per_m=0.000174,
        res_high_ohm_per_m=0.000283,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_336_4_wrangell() -> Conductor:
    return Conductor(
        type='ACCS',
        code='336.4_WRANGELL',
        area_mm2=199.0,
        diameter_mm=17.3,
        weight_n_per_m=5.059,
        conductor_rts_kn=68.9,
        dol_per_1000_ft=3745.0,
        inst_dol_per_1000_ft=5530.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000164264,
        res_low_ohm_per_m=0.000168,
        res_high_ohm_per_m=0.000274,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_336_4_badlands() -> Conductor:
    return Conductor(
        type='ACCS',
        code='336.4_BADLANDS',
        area_mm2=208.0,
        diameter_mm=17.4,
        weight_n_per_m=5.216,
        conductor_rts_kn=87.6,
        dol_per_1000_ft=4670.0,
        inst_dol_per_1000_ft=6510.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000164823,
        res_low_ohm_per_m=0.000169,
        res_high_ohm_per_m=0.000275,
        elastic_modulus_gpa=60.0,
        coeff_thermal_expan_per_cel=1.34e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_397_5_andes() -> Conductor:
    return Conductor(
        type='ACCS',
        code='397.5_ANDES',
        area_mm2=230.0,
        diameter_mm=18.0,
        weight_n_per_m=5.888,
        conductor_rts_kn=70.7,
        dol_per_1000_ft=4815.0,
        inst_dol_per_1000_ft=6830.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000138844,
        res_low_ohm_per_m=0.000142,
        res_high_ohm_per_m=0.000231,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_397_5_joshua_tree() -> Conductor:
    return Conductor(
        type='ACCS',
        code='397.5_JOSHUA_TREE',
        area_mm2=234.0,
        diameter_mm=18.2,
        weight_n_per_m=5.96,
        conductor_rts_kn=79.6,
        dol_per_1000_ft=4815.0,
        inst_dol_per_1000_ft=6830.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000138906,
        res_low_ohm_per_m=0.000142,
        res_high_ohm_per_m=0.000232,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_397_5_sequoia() -> Conductor:
    return Conductor(
        type='ACCS',
        code='397.5_SEQUOIA',
        area_mm2=246.0,
        diameter_mm=18.7,
        weight_n_per_m=6.167,
        conductor_rts_kn=104.1,
        dol_per_1000_ft=4755.0,
        inst_dol_per_1000_ft=7150.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000139466,
        res_low_ohm_per_m=0.000143,
        res_high_ohm_per_m=0.000233,
        elastic_modulus_gpa=60.0,
        coeff_thermal_expan_per_cel=1.34e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_477_0_rogers() -> Conductor:
    return Conductor(
        type='ACCS',
        code='477.0_ROGERS',
        area_mm2=274.0,
        diameter_mm=19.8,
        weight_n_per_m=7.041,
        conductor_rts_kn=81.8,
        dol_per_1000_ft=4510.0,
        inst_dol_per_1000_ft=6785.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000115662,
        res_low_ohm_per_m=0.000119,
        res_high_ohm_per_m=0.000193,
        elastic_modulus_gpa=54.375,
        coeff_thermal_expan_per_cel=1.5e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_477_0_yosemite() -> Conductor:
    return Conductor(
        type='ACCS',
        code='477.0_YOSEMITE',
        area_mm2=279.0,
        diameter_mm=20.0,
        weight_n_per_m=7.12,
        conductor_rts_kn=91.6,
        dol_per_1000_ft=5615.0,
        inst_dol_per_1000_ft=7970.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000115724,
        res_low_ohm_per_m=0.000119,
        res_high_ohm_per_m=0.000193,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_477_0_capitol_reef() -> Conductor:
    return Conductor(
        type='ACCS',
        code='477.0_CAPITOL_REEF',
        area_mm2=297.0,
        diameter_mm=20.8,
        weight_n_per_m=7.439,
        conductor_rts_kn=129.4,
        dol_per_1000_ft=6255.0,
        inst_dol_per_1000_ft=8705.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=0.000116346,
        res_low_ohm_per_m=0.000119,
        res_high_ohm_per_m=0.000194,
        elastic_modulus_gpa=60.0,
        coeff_thermal_expan_per_cel=1.34e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_636_0_tortugas() -> Conductor:
    return Conductor(
        type='ACCS',
        code='636.0_TORTUGAS',
        area_mm2=355.0,
        diameter_mm=22.4,
        weight_n_per_m=9.212,
        conductor_rts_kn=86.3,
        dol_per_1000_ft=6180.0,
        inst_dol_per_1000_ft=9305.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.67e-05,
        res_low_ohm_per_m=8.93e-05,
        res_high_ohm_per_m=0.000145,
        elastic_modulus_gpa=54.375,
        coeff_thermal_expan_per_cel=1.5e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_636_0_yellowstone() -> Conductor:
    return Conductor(
        type='ACCS',
        code='636.0_YELLOWSTONE',
        area_mm2=359.0,
        diameter_mm=22.5,
        weight_n_per_m=9.288,
        conductor_rts_kn=96.1,
        dol_per_1000_ft=6180.0,
        inst_dol_per_1000_ft=9305.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.68e-05,
        res_low_ohm_per_m=8.93e-05,
        res_high_ohm_per_m=0.000145,
        elastic_modulus_gpa=54.375,
        coeff_thermal_expan_per_cel=1.5e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_636_0_glacier() -> Conductor:
    return Conductor(
        type='ACCS',
        code='636.0_GLACIER',
        area_mm2=372.0,
        diameter_mm=23.0,
        weight_n_per_m=9.491,
        conductor_rts_kn=121.9,
        dol_per_1000_ft=7080.0,
        inst_dol_per_1000_ft=10155.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.68e-05,
        res_low_ohm_per_m=8.92e-05,
        res_high_ohm_per_m=0.000145,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_636_0_carlsbad() -> Conductor:
    return Conductor(
        type='ACCS',
        code='636.0_CARLSBAD',
        area_mm2=394.0,
        diameter_mm=24.1,
        weight_n_per_m=9.876,
        conductor_rts_kn=164.1,
        dol_per_1000_ft=7300.0,
        inst_dol_per_1000_ft=10730.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.72e-05,
        res_low_ohm_per_m=8.95e-05,
        res_high_ohm_per_m=0.000146,
        elastic_modulus_gpa=54.375,
        coeff_thermal_expan_per_cel=1.5e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_641_7_congaree() -> Conductor:
    return Conductor(
        type='ACCS',
        code='641.7_CONGAREE',
        area_mm2=362.0,
        diameter_mm=22.6,
        weight_n_per_m=9.365,
        conductor_rts_kn=96.1,
        dol_per_1000_ft=6180.0,
        inst_dol_per_1000_ft=9305.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=8.6e-05,
        res_low_ohm_per_m=8.85e-05,
        res_high_ohm_per_m=0.000144,
        elastic_modulus_gpa=54.375,
        coeff_thermal_expan_per_cel=1.5e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_714_0_vinson() -> Conductor:
    return Conductor(
        type='ACCS',
        code='714.0_VINSON',
        area_mm2=399.0,
        diameter_mm=23.7,
        weight_n_per_m=10.351,
        conductor_rts_kn=98.3,
        dol_per_1000_ft=7300.0,
        inst_dol_per_1000_ft=10730.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=7.73e-05,
        res_low_ohm_per_m=7.97e-05,
        res_high_ohm_per_m=0.000129,
        elastic_modulus_gpa=54.375,
        coeff_thermal_expan_per_cel=1.5e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_795_0_kilimanjaro() -> Conductor:
    return Conductor(
        type='ACCS',
        code='795.0_KILIMANJARO',
        area_mm2=431.0,
        diameter_mm=24.4,
        weight_n_per_m=11.306,
        conductor_rts_kn=81.8,
        dol_per_1000_ft=6830.0,
        inst_dol_per_1000_ft=10240.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.93e-05,
        res_low_ohm_per_m=7.18e-05,
        res_high_ohm_per_m=0.000116,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_795_0_alps() -> Conductor:
    return Conductor(
        type='ACCS',
        code='795.0_ALPS',
        area_mm2=440.0,
        diameter_mm=24.7,
        weight_n_per_m=11.455,
        conductor_rts_kn=100.5,
        dol_per_1000_ft=6830.0,
        inst_dol_per_1000_ft=10240.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.94e-05,
        res_low_ohm_per_m=7.18e-05,
        res_high_ohm_per_m=0.000116,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_795_0_wind_cave() -> Conductor:
    return Conductor(
        type='ACCS',
        code='795.0_WIND_CAVE',
        area_mm2=452.0,
        diameter_mm=25.1,
        weight_n_per_m=11.658,
        conductor_rts_kn=126.3,
        dol_per_1000_ft=7605.0,
        inst_dol_per_1000_ft=11455.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.94e-05,
        res_low_ohm_per_m=7.17e-05,
        res_high_ohm_per_m=0.000116,
        elastic_modulus_gpa=54.375,
        coeff_thermal_expan_per_cel=1.5e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_795_0_denali() -> Conductor:
    return Conductor(
        type='ACCS',
        code='795.0_DENALI',
        area_mm2=469.0,
        diameter_mm=25.7,
        weight_n_per_m=11.935,
        conductor_rts_kn=161.0,
        dol_per_1000_ft=8555.0,
        inst_dol_per_1000_ft=11795.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.95e-05,
        res_low_ohm_per_m=7.16e-05,
        res_high_ohm_per_m=0.000116,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_795_0_rocky() -> Conductor:
    return Conductor(
        type='ACCS',
        code='795.0_ROCKY',
        area_mm2=491.0,
        diameter_mm=26.5,
        weight_n_per_m=12.329,
        conductor_rts_kn=202.8,
        dol_per_1000_ft=8555.0,
        inst_dol_per_1000_ft=11795.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=6.97e-05,
        res_low_ohm_per_m=7.18e-05,
        res_high_ohm_per_m=0.000117,
        elastic_modulus_gpa=56.625,
        coeff_thermal_expan_per_cel=1.44e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_954_0_crater_lake() -> Conductor:
    return Conductor(
        type='ACCS',
        code='954.0_CRATER_LAKE',
        area_mm2=516.0,
        diameter_mm=26.9,
        weight_n_per_m=13.609,
        conductor_rts_kn=94.7,
        dol_per_1000_ft=9685.0,
        inst_dol_per_1000_ft=13160.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.8e-05,
        res_low_ohm_per_m=6.06e-05,
        res_high_ohm_per_m=9.75e-05,
        elastic_modulus_gpa=51.75,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_954_0_grand_canyon() -> Conductor:
    return Conductor(
        type='ACCS',
        code='954.0_GRAND_CANYON',
        area_mm2=533.0,
        diameter_mm=27.2,
        weight_n_per_m=13.892,
        conductor_rts_kn=130.3,
        dol_per_1000_ft=9885.0,
        inst_dol_per_1000_ft=13785.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.81e-05,
        res_low_ohm_per_m=6.05e-05,
        res_high_ohm_per_m=9.74e-05,
        elastic_modulus_gpa=51.75,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_954_0_fuji() -> Conductor:
    return Conductor(
        type='ACCS',
        code='954.0_FUJI',
        area_mm2=543.0,
        diameter_mm=27.4,
        weight_n_per_m=13.997,
        conductor_rts_kn=152.6,
        dol_per_1000_ft=9885.0,
        inst_dol_per_1000_ft=13785.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.78e-05,
        res_low_ohm_per_m=6.01e-05,
        res_high_ohm_per_m=9.69e-05,
        elastic_modulus_gpa=51.75,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_954_0_jasper() -> Conductor:
    return Conductor(
        type='ACCS',
        code='954.0_JASPER',
        area_mm2=560.0,
        diameter_mm=28.0,
        weight_n_per_m=14.28,
        conductor_rts_kn=184.2,
        dol_per_1000_ft=9895.0,
        inst_dol_per_1000_ft=15130.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.79e-05,
        res_low_ohm_per_m=6e-05,
        res_high_ohm_per_m=9.69e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_954_0_arches() -> Conductor:
    return Conductor(
        type='ACCS',
        code='954.0_ARCHES',
        area_mm2=579.0,
        diameter_mm=28.7,
        weight_n_per_m=14.615,
        conductor_rts_kn=222.9,
        dol_per_1000_ft=10910.0,
        inst_dol_per_1000_ft=14630.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.8e-05,
        res_low_ohm_per_m=6.01e-05,
        res_high_ohm_per_m=9.71e-05,
        elastic_modulus_gpa=51.75,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_973_1_everglades() -> Conductor:
    return Conductor(
        type='ACCS',
        code='973.1_EVERGLADES',
        area_mm2=564.0,
        diameter_mm=28.1,
        weight_n_per_m=14.445,
        conductor_rts_kn=173.5,
        dol_per_1000_ft=9895.0,
        inst_dol_per_1000_ft=15130.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.67e-05,
        res_low_ohm_per_m=5.89e-05,
        res_high_ohm_per_m=9.51e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1033_5_big_bend() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1033.5_BIG_BEND',
        area_mm2=552.0,
        diameter_mm=27.8,
        weight_n_per_m=14.618,
        conductor_rts_kn=88.1,
        dol_per_1000_ft=9885.0,
        inst_dol_per_1000_ft=13785.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.35e-05,
        res_low_ohm_per_m=5.62e-05,
        res_high_ohm_per_m=9.01e-05,
        elastic_modulus_gpa=51.75,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1033_5_lassen() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1033.5_LASSEN',
        area_mm2=561.0,
        diameter_mm=28.0,
        weight_n_per_m=14.773,
        conductor_rts_kn=106.8,
        dol_per_1000_ft=9895.0,
        inst_dol_per_1000_ft=15130.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.36e-05,
        res_low_ohm_per_m=5.61e-05,
        res_high_ohm_per_m=9.01e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1033_5_tahoe() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1033.5_TAHOE',
        area_mm2=579.0,
        diameter_mm=28.4,
        weight_n_per_m=15.08,
        conductor_rts_kn=144.6,
        dol_per_1000_ft=10910.0,
        inst_dol_per_1000_ft=14630.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.36e-05,
        res_low_ohm_per_m=5.6e-05,
        res_high_ohm_per_m=9.01e-05,
        elastic_modulus_gpa=51.75,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1033_5_samoa() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1033.5_SAMOA',
        area_mm2=590.0,
        diameter_mm=28.7,
        weight_n_per_m=15.185,
        conductor_rts_kn=168.1,
        dol_per_1000_ft=10910.0,
        inst_dol_per_1000_ft=14630.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=5.34e-05,
        res_low_ohm_per_m=5.56e-05,
        res_high_ohm_per_m=8.96e-05,
        elastic_modulus_gpa=51.75,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1113_0_cook() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1113.0_COOK',
        area_mm2=592.0,
        diameter_mm=28.6,
        weight_n_per_m=15.708,
        conductor_rts_kn=89.9,
        dol_per_1000_ft=10910.0,
        inst_dol_per_1000_ft=14630.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.97e-05,
        res_low_ohm_per_m=5.24e-05,
        res_high_ohm_per_m=8.38e-05,
        elastic_modulus_gpa=51.75,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1113_0_blanc() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1113.0_BLANC',
        area_mm2=601.0,
        diameter_mm=28.9,
        weight_n_per_m=15.865,
        conductor_rts_kn=109.0,
        dol_per_1000_ft=10515.0,
        inst_dol_per_1000_ft=16155.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.97e-05,
        res_low_ohm_per_m=5.24e-05,
        res_high_ohm_per_m=8.38e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1113_0_niagara() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1113.0_NIAGARA',
        area_mm2=619.0,
        diameter_mm=29.3,
        weight_n_per_m=16.166,
        conductor_rts_kn=146.3,
        dol_per_1000_ft=10515.0,
        inst_dol_per_1000_ft=16155.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.98e-05,
        res_low_ohm_per_m=5.22e-05,
        res_high_ohm_per_m=8.38e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1113_0_gannett() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1113.0_GANNETT',
        area_mm2=635.0,
        diameter_mm=30.0,
        weight_n_per_m=16.444,
        conductor_rts_kn=177.0,
        dol_per_1000_ft=9805.0,
        inst_dol_per_1000_ft=14250.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.98e-05,
        res_low_ohm_per_m=5.21e-05,
        res_high_ohm_per_m=8.38e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1192_5_washington() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1192.5_WASHINGTON',
        area_mm2=633.0,
        diameter_mm=29.6,
        weight_n_per_m=16.799,
        conductor_rts_kn=92.1,
        dol_per_1000_ft=9805.0,
        inst_dol_per_1000_ft=14250.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.64e-05,
        res_low_ohm_per_m=4.92e-05,
        res_high_ohm_per_m=7.84e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1192_5_elbert() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1192.5_ELBERT',
        area_mm2=648.0,
        diameter_mm=30.1,
        weight_n_per_m=17.066,
        conductor_rts_kn=125.4,
        dol_per_1000_ft=9805.0,
        inst_dol_per_1000_ft=14250.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.64e-05,
        res_low_ohm_per_m=4.9e-05,
        res_high_ohm_per_m=7.84e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1192_5_kings_canyon() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1192.5_KINGS_CANYON',
        area_mm2=664.0,
        diameter_mm=30.6,
        weight_n_per_m=17.333,
        conductor_rts_kn=158.8,
        dol_per_1000_ft=9805.0,
        inst_dol_per_1000_ft=14250.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.65e-05,
        res_low_ohm_per_m=4.89e-05,
        res_high_ohm_per_m=7.83e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1192_5_acadia() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1192.5_ACADIA',
        area_mm2=681.0,
        diameter_mm=31.1,
        weight_n_per_m=17.624,
        conductor_rts_kn=189.9,
        dol_per_1000_ft=11360.0,
        inst_dol_per_1000_ft=15880.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.66e-05,
        res_low_ohm_per_m=4.88e-05,
        res_high_ohm_per_m=7.83e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1233_6_redwood() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1233.6_REDWOOD',
        area_mm2=669.0,
        diameter_mm=30.6,
        weight_n_per_m=17.63,
        conductor_rts_kn=126.8,
        dol_per_1000_ft=11360.0,
        inst_dol_per_1000_ft=15880.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.49e-05,
        res_low_ohm_per_m=4.75e-05,
        res_high_ohm_per_m=7.58e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1233_6_mesa_verde() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1233.6_MESA_VERDE',
        area_mm2=685.0,
        diameter_mm=31.0,
        weight_n_per_m=17.898,
        conductor_rts_kn=159.7,
        dol_per_1000_ft=11360.0,
        inst_dol_per_1000_ft=15880.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.49e-05,
        res_low_ohm_per_m=4.74e-05,
        res_high_ohm_per_m=7.57e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1233_6_biscayne() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1233.6_BISCAYNE',
        area_mm2=707.0,
        diameter_mm=31.6,
        weight_n_per_m=18.277,
        conductor_rts_kn=202.8,
        dol_per_1000_ft=11360.0,
        inst_dol_per_1000_ft=15880.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.5e-05,
        res_low_ohm_per_m=4.72e-05,
        res_high_ohm_per_m=7.57e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1272_0_saguaro() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1272.0_SAGUARO',
        area_mm2=677.0,
        diameter_mm=30.8,
        weight_n_per_m=17.957,
        conductor_rts_kn=103.6,
        dol_per_1000_ft=11360.0,
        inst_dol_per_1000_ft=15880.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.35e-05,
        res_low_ohm_per_m=4.63e-05,
        res_high_ohm_per_m=7.36e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1272_0_sierra_nevada() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1272.0_SIERRA_NEVADA',
        area_mm2=689.0,
        diameter_mm=31.1,
        weight_n_per_m=18.158,
        conductor_rts_kn=127.7,
        dol_per_1000_ft=11360.0,
        inst_dol_per_1000_ft=15880.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.35e-05,
        res_low_ohm_per_m=4.62e-05,
        res_high_ohm_per_m=7.36e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1272_0_eldorado() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1272.0_ELDORADO',
        area_mm2=711.0,
        diameter_mm=31.6,
        weight_n_per_m=18.524,
        conductor_rts_kn=173.9,
        dol_per_1000_ft=12415.0,
        inst_dol_per_1000_ft=17835.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.36e-05,
        res_low_ohm_per_m=4.6e-05,
        res_high_ohm_per_m=7.35e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1272_0_voyageurs() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1272.0_VOYAGEURS',
        area_mm2=727.0,
        diameter_mm=32.0,
        weight_n_per_m=18.806,
        conductor_rts_kn=203.7,
        dol_per_1000_ft=12415.0,
        inst_dol_per_1000_ft=17835.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.36e-05,
        res_low_ohm_per_m=4.59e-05,
        res_high_ohm_per_m=7.35e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1351_5_cascades() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1351.5_CASCADES',
        area_mm2=734.0,
        diameter_mm=32.1,
        weight_n_per_m=19.333,
        conductor_rts_kn=141.5,
        dol_per_1000_ft=12285.0,
        inst_dol_per_1000_ft=18595.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.1e-05,
        res_low_ohm_per_m=4.37e-05,
        res_high_ohm_per_m=6.93e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1351_5_banff() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1351.5_BANFF',
        area_mm2=751.0,
        diameter_mm=32.5,
        weight_n_per_m=19.616,
        conductor_rts_kn=176.1,
        dol_per_1000_ft=12285.0,
        inst_dol_per_1000_ft=18595.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.1e-05,
        res_low_ohm_per_m=4.35e-05,
        res_high_ohm_per_m=6.93e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1351_5_elbrus() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1351.5_ELBRUS',
        area_mm2=773.0,
        diameter_mm=33.0,
        weight_n_per_m=19.992,
        conductor_rts_kn=218.0,
        dol_per_1000_ft=15225.0,
        inst_dol_per_1000_ft=19645.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=4.11e-05,
        res_low_ohm_per_m=4.34e-05,
        res_high_ohm_per_m=6.93e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1590_0_bryce_canyon() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1590.0_BRYCE_CANYON',
        area_mm2=861.0,
        diameter_mm=34.5,
        weight_n_per_m=22.696,
        conductor_rts_kn=159.7,
        dol_per_1000_ft=14360.0,
        inst_dol_per_1000_ft=20295.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.48e-05,
        res_low_ohm_per_m=3.77e-05,
        res_high_ohm_per_m=5.93e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.56e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1590_0_adirondack() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1590.0_ADIRONDACK',
        area_mm2=888.0,
        diameter_mm=35.2,
        weight_n_per_m=23.149,
        conductor_rts_kn=212.6,
        dol_per_1000_ft=16950.0,
        inst_dol_per_1000_ft=23320.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.49e-05,
        res_low_ohm_per_m=3.75e-05,
        res_high_ohm_per_m=5.92e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1590_0_zion() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1590.0_ZION',
        area_mm2=901.0,
        diameter_mm=35.6,
        weight_n_per_m=23.38,
        conductor_rts_kn=239.8,
        dol_per_1000_ft=16950.0,
        inst_dol_per_1000_ft=23320.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.49e-05,
        res_low_ohm_per_m=3.74e-05,
        res_high_ohm_per_m=5.92e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1780_0_teton() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1780.0_TETON',
        area_mm2=951.0,
        diameter_mm=36.1,
        weight_n_per_m=25.19,
        conductor_rts_kn=153.0,
        dol_per_1000_ft=16950.0,
        inst_dol_per_1000_ft=23320.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.11e-05,
        res_low_ohm_per_m=3.43e-05,
        res_high_ohm_per_m=5.34e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1780_0_everest() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1780.0_EVEREST',
        area_mm2=973.0,
        diameter_mm=36.6,
        weight_n_per_m=25.568,
        conductor_rts_kn=195.3,
        dol_per_1000_ft=16950.0,
        inst_dol_per_1000_ft=23320.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.11e-05,
        res_low_ohm_per_m=3.41e-05,
        res_high_ohm_per_m=5.33e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

def accs_1780_0_katmai() -> Conductor:
    return Conductor(
        type='ACCS',
        code='1780.0_KATMAI',
        area_mm2=990.0,
        diameter_mm=37.2,
        weight_n_per_m=25.851,
        conductor_rts_kn=229.5,
        dol_per_1000_ft=16950.0,
        inst_dol_per_1000_ft=23320.0,
        accessories_dol_per_1000_ft=750.0,
        
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=180.0,
        max_temperature_c=200.0,
        res_dc_ohm_per_m=3.11e-05,
        res_low_ohm_per_m=3.39e-05,
        res_high_ohm_per_m=5.32e-05,
        elastic_modulus_gpa=47.025,
        coeff_thermal_expan_per_cel=1.45e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )

