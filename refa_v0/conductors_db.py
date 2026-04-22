import pandas as pd
import re

def generate_conductor_functions(csv_path, output_path):
    """Generate conductor functions from CSV file."""
    df = pd.read_csv(csv_path)
    
    # Generate function code
    functions = []
    for _, row in df.iterrows():
        # Convert code to valid Python function name
        func_name = row['code'].lower().replace('.', '_').replace(' ', '_')
        cond_type = row['type'].lower()
        
        # Build parameter string
        params = params = [
            f"        type='{row['type']}',",
            f"        code='{row['code']}',",
            f"        area_mm2={float(row['area_mm2'])},",
            f"        diameter_mm={float(row['diameter_mm'])},",
            f"        weight_n_per_m={float(row['weight_n_per_m'])},",
            f"        conductor_rts_kn={float(row['conductor_rts_kn'])},",
            f"        dol_per_1000_ft={float(row['dol_per_1000_ft'])},",
            f"        inst_dol_per_1000_ft={float(row['inst_dol_per_1000_ft'])},",
            f"        accessories_dol_per_1000_ft={float(row['accessories_dol_per_1000_ft'])},",
            f"        str_costs_dol={float(row['str_costs_dol'])},",
            f"        temp_dc_c={float(row['temp_dc_c'])},",
            f"        temp_low_c={float(row['temp_low_c'])},",
            f"        temp_high_c={float(row['temp_high_c'])},",
            f"        max_temperature_c={float(row['max_temperature_c'])},",
            f"        res_dc_ohm_per_m={float(row['res_dc_ohm_per_m'])},",
            f"        res_low_ohm_per_m={float(row['res_low_ohm_per_m'])},",
            f"        res_high_ohm_per_m={float(row['res_high_ohm_per_m'])},",
            f"        elastic_modulus_gpa={float(row['elastic_modulus_gpa'])},",
            f"        coeff_thermal_expan_per_cel={float(row['coeff_thermal_expan_per_cel'])},",
            f"        emissivity={float(row['emissivity'])},",
            f"        solar_absorptivity={float(row['solar_absorptivity'])},",
        ]
        
        func = f"""def {cond_type}_{func_name}() -> Conductor:
    return Conductor(
{chr(10).join(params)}
    )

"""
        functions.append(func)
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write("from conductor import Conductor\nfrom typing import Any\n\n")
        f.writelines(functions)

# Usage
generate_conductor_functions(
    'input_data_raw/conductors.csv',
    'conductors_.py'
)