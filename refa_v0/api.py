from flask import Flask, request
from methods import get_technically_feasible, npv, npv_existing, benefits, file_to_project, part1_fetch_congestion_cost, part2_fetch_congestion_cost
import pandas as pd
import json
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/calculate-feasible-projects", methods=['POST'])
def calculate_feasible_projects():
    # process data
    content = request.json

    content = convert_to_float(content)
    content['specs'] = convert_to_int(content['specs'], ['replace_st_at', 'replace_cd_at'])
    content['economics'] = convert_to_int(content['economics'], 
                                          ['conductors_lifetime', 'structures_lifetime', 'conductors_life', 'structures_life'])

    conds_df = pd.DataFrame.from_records(content['conductors'])
    str_strength_df = pd.DataFrame.from_records(content['str_strength'])
    benefits_df = pd.DataFrame.from_records(content['social_benefits_params'])   
    

    feasibility = {}
    for inv_option in content['specs']:
        feasible = get_technically_feasible(conds_df, content['data'], content['environment'], 
                                            content['loading'], content['specs'][inv_option], str_strength_df, content['include_unfeasible']['value'])
        if not feasible['feasible'].empty:
            npv_result = npv(feasible['feasible'], content['economics'], content['specs'][inv_option], 
                             bool(content['data']['losses_check']), 100, not content['include_unfeasible']['value'])
            benefits_res = benefits(feasible['feasible'], content['data'], benefits_df, content['year_ref'], content['specs'][inv_option]['voltage'])['benefits'].reset_index(drop=True)
            npv_result['benefits'] = benefits_res.loc[benefits_res.year != content['year_ref']]
            npv_result['conductors'] = feasible['feasible']
            feasibility[inv_option] = {key: json.loads(df.to_json(orient='records')) for key, df in npv_result.items()}


    if ('existing' in content and content['existing']['area_mm2']):
        existing = pd.DataFrame.from_records([content['existing']])
        npv_result = npv_existing(existing, content['economics'], content['data'], content['existing']['structures'], content['environment'], content['loading'], benefits_df, content['year_ref'], bool(content['data']['losses_check']), 100)
        npv_result['benefits'] = npv_result['benefits'].loc[npv_result['benefits'].year != content['year_ref']]
        feasibility['Existing'] = {}
        feasibility['Existing'] = {key: json.loads(df.to_json(orient='records')) for key, df in npv_result.items()}

    return feasibility


@app.route("/import-pls-cadd-data", methods=['POST'])
def import_pls_cadd_data():
    # process data
    content = request.data # Get raw bytes

    # Save XML content to a file
    file_name = 'tmp/upload_' + datetime.now().strftime('%Y-%m-%d %Hh%Mmn%Ss') + '.xml'
    with open(file_name, 'wb') as f:
        f.write(content)
        f.close()

    output = {}

    data = file_to_project(file_name)
    
    output = {key: json.loads(df.to_json(orient='records')) for key, df in data.items()}

    # delete file
    os.remove(file_name)

    return output


@app.route("/part1-congestion-cost", methods=['POST'])
def part1_congestion_cost():
    # process data
    content = request.json

    output = part1_fetch_congestion_cost(content['line_segments'])

    return output

@app.route("/part2-congestion-cost", methods=['POST'])
def part2_congestion_cost():
    # process data
    content = request.json
    
    labels = content['inter_zone_labels']
    if '--' in content['select_zone']:
        zone = labels[content['select_zone']]
    else:
        zone = content['select_zone']

    output = part2_fetch_congestion_cost(zone, content['line_segments'])

    return output




def convert_to_float(data):
    if isinstance(data, dict):
        return {key: convert_to_float(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_float(value) for value in data]
    elif isinstance(data, str):
        try: # Attempt to convert string to float
            return float(data)
        except ValueError:
            return data  # Return unchanged if conversion fails
    return data  # Non-numeric data is returned unchanged


def convert_to_int(data, keys):
    if isinstance(data, dict):
        return {key: int(value) if key in keys else convert_to_int(value, keys) for key, value in data.items()}
    else: return data
