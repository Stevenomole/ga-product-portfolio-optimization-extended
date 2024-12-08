#imports
import pandas as pd
import numpy as np

def load_data(file_path):
    # read the necessary data from csv
    cost_profile_inh = pd.read_excel(file_path, sheet_name='cost_profile_inhouse')
    resource_util_inh = pd.read_excel(file_path, sheet_name='resource_util_inhouse')
    resource_avail_inh = pd.read_excel(file_path, sheet_name='resource_avail_inhouse')
    crash_data_inh = pd.read_excel(file_path, sheet_name='crash_data_inhouse')
    crash_data_out = pd.read_excel(file_path, sheet_name='crash_data_outsourced')
    preced = pd.read_excel(file_path, sheet_name='precedence_constraints', index_col=0)

    return cost_profile_inh, resource_util_inh, resource_avail_inh, crash_data_inh, crash_data_out, preced

def preprocess_data(cost_profile_inh, resource_util_inh, resource_avail_inh, crash_data_inh, crash_data_out, preced):
    # initialize dictionary to hold the modules profiles
    module_profile = {
        i: {
            'type': None,
            'supplier': None,
            'duration': [],
            'cost': [],
            'resource util': None,
            'resource avail': None,
            'max crash': [],
            'crash cost': []
        } for i in range(1, 13)
    }

    # populate the dictionary for inhouse and outsourced modules
    for module in module_profile.keys():
        if module <= 6:  # inhouse modules
            module_profile[module]['type'] = 'inhouse'
            data = crash_data_inh[crash_data_inh['module'] == module].iloc[0]
            module_profile[module]['max crash'].append(data['allowable_crash'])
            module_profile[module]['crash cost'].append(data['cost_per_crash_period'])
            module_profile[module]['duration'].append(data['ideal_duration'])
            module_profile[module]['cost'] = cost_profile_inh.iloc[module-1, 1].tolist()
            module_profile[module]['resource util'] = resource_util_inh.iloc[module-1, 1:].tolist()
            module_profile[module]['resource avail'] = resource_avail_inh.iloc[module-1, 1:].tolist()
        else:  # outsourced modules
            module_profile[module]['type'] = 'outsourced'

    # populate the outsourced modules profiles
    outsource_profile = {}
    for index, row in crash_data_out.iterrows():
        module = int(row['module'])
        supplier = int(row['supplier'])
        exped_cost = row['cost_per_crash_period']
        actual_cost = row['cost']
        lead_time = row['lead_time']
        allowable_expediting_time = row['allowable_expediting_time']
        
        if module not in outsource_profile:
            outsource_profile[module] = [{'supplier': supplier, 'cost': actual_cost, 'lead time': lead_time, 'exped cost': exped_cost, 'max exped': allowable_expediting_time}]
        else:
            supplier_exists = False
            for supplier_info in outsource_profile[module]:
                if supplier_info['supplier'] == supplier:
                    supplier_info['exped cost'] = exped_cost
                    supplier_info['cost'] = actual_cost
                    supplier_info['lead time'] = lead_time
                    supplier_info['max exped'] =allowable_expediting_time
                    supplier_exists = True
                    break
            if not supplier_exists:
                outsource_profile[module].append({'supplier': supplier, 'cost': actual_cost, 'lead time': lead_time, 'exped cost': exped_cost, 'max exped': allowable_expediting_time})

    # merge outsource_profile data back into module_profile
    for module in outsource_profile:
        module_profile[module]['supplier'] = [s['supplier'] for s in outsource_profile[module]]
        module_profile[module]['duration'] = [s['lead time'] for s in outsource_profile[module]]
        module_profile[module]['cost'] = [s['cost'] for s in outsource_profile[module]]
        module_profile[module]['max crash'] = [s['max exped'] for s in outsource_profile[module]]
        module_profile[module]['crash cost'] = [s['exped cost'] for s in outsource_profile[module]]

    # create dictionary to store feasibility periods
    feasible_set = {}  
    for module in module_profile:
        feasible_set[module] = []
        if module_profile[module]['type'] == 'inhouse':
            num_periods = len(module_profile[module]['resource avail'])
            for period in range(num_periods):
                if module_profile[module]['resource avail'][period] >= module_profile[module]['resource util'][period]:
                    feasible_set[module].append(1)
                else:
                    feasible_set[module].append(0)
        else:
            feasible_set[module] = [1]*156

    # convert matrix to list of dependencies
    dependencies = {i: [] for i in range(1, len(preced.columns) + 1)} 
    for i, row in preced.iterrows(): 
        row_index = int(i.strip('M'))  
        for j, val in enumerate(row):
            if val == 1:
                dependencies[j+1].append(row_index)
    
    return module_profile, dependencies, feasible_set

import os
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '..', 'Data', 'data_bank.xlsx')
    cost_profile_inh, resource_util_inh, resource_avail_inh, crash_data_inh, crash_data_out, preced = load_data(file_path)
    module_profile, dependencies, feasible_set = preprocess_data(cost_profile_inh, resource_util_inh, resource_avail_inh, crash_data_inh, crash_data_out, preced)
    print(module_profile[1]['cost'])
