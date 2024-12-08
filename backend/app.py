from flask import Flask, request, jsonify
from main import run_genetic_algorithm, preprocess_data_once
import os
import pandas as pd
from flask_cors import CORS # type: ignore

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for request size

# Use environment variable or config file for file path
file_path = os.environ.get('DATA_FILE_PATH', 'data_bank.xlsx')

# Global variables for preprocessed data (lazy loading)
preprocessed_data = {
    'module_profile': None,
    'dependencies': None,
    'feasible_set': None
}

# Ensure data is only preprocessed when required
def ensure_data_preprocessed():
    if preprocessed_data['module_profile'] is None or preprocessed_data['dependencies'] is None:
        module_profile, dependencies, feasible_set = preprocess_data_once()
        preprocessed_data['module_profile'] = module_profile
        preprocessed_data['dependencies'] = dependencies
        preprocessed_data['feasible_set'] = feasible_set
    return preprocessed_data


def prepare_matrix(matrix_dict, num_modules):
    # Create an empty DataFrame with the appropriate dimensions
    matrix = pd.DataFrame('-', index=[i+1 for i in range(num_modules)], columns=[i+1 for i in range(num_modules)])
    
    # Populate the DataFrame with the values from the matrix_dict
    for key, value in matrix_dict.items():
        predecessor, successor = key.split('-')
        predecessor = int(predecessor.split(' ')[1])
        successor = int(successor.split(' ')[1])
        matrix.loc[predecessor, successor] = value
    
    return matrix

@app.route('/run-ga', methods=['POST'])
def run_ga():
    try:
        print(request.headers)  # Log the headers to inspect them
        data = request.json
        
        # Ensure preprocessing is done before running GA
        ensure_data_preprocessed()

        # Prepare the interaction and information matrices
        num_modules = len(preprocessed_data['dependencies'])
        data['interactionMatrix'] = prepare_matrix(data['interactionMatrix'], num_modules=12)
        data['informationMatrix'] = prepare_matrix(data['informationMatrix'], num_modules=12)

        print(f"Received data: {data}")
        
        # Run the genetic algorithm with preprocessed data and input parameters
        result = run_genetic_algorithm(data)

        return jsonify(result)
    
    except Exception as e:
        # Return JSON even for errors
        return jsonify({'error': str(e)}), 500

@app.route('/get-preprocessed-data', methods=['GET'])
def get_preprocessed_data():
    try:
        # Preprocess data if it hasn't been done already
        processed_data = ensure_data_preprocessed()
        return jsonify({'dependencies': processed_data['dependencies']})
    
    except Exception as e:
        # Return JSON even for errors
        return jsonify({'error': str(e)}), 500
    
@app.route('/ws', methods=['GET'])
def websocket_dummy():
    return '', 200  # Return an empty response with a 200 OK status

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
