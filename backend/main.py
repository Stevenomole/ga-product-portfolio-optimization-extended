# imports
from genetic_algorithm import GeneticAlgorithm
from data_processing import load_data, preprocess_data
import os

# Global variables to store preprocessed data
module_profile = None
dependencies = {}
feasible_set = {}

def preprocess_data_once():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '..', 'Data', 'data_bank.xlsx')
    
    cost_profile_inh, resource_util_inh, resource_avail_inh, crash_data_inh, crash_data_out, preced = load_data(file_path)
    return preprocess_data(cost_profile_inh, resource_util_inh, resource_avail_inh, crash_data_inh, crash_data_out, preced)

def run_genetic_algorithm(input_params):
    module_profile, dependencies, feasible_set = preprocess_data_once()

    ga = GeneticAlgorithm(module_profile, dependencies, feasible_set, None, None)
    population_size = int(input_params['population'])
    mutation_rate = float(input_params['mutationRate'])
    crossover_rate = float(input_params['crossoverRate'])
    generations = int(input_params['generations'])
    interaction_degree = input_params['interactionMatrix']
    information_flow = input_params['informationMatrix']
    adoption_rate = input_params['adoptionRate']

    ga.interaction_degree = interaction_degree
    ga.information_flow = information_flow

    # Run the update_module_duration function
    ga.update_module_duration()
    print("Updated module durations:")

    best_solution, best_fitness, best_product_selection = ga.run(population_size, crossover_rate, mutation_rate, generations)
    
    for key, value in best_solution.items():
        module_cost = 0
        if module_profile[key]['type'] == 'inhouse':
            module_cost += module_profile[key]['cost']
            module_cost += module_profile[key]['crash cost'][0] * (value[2] ** 2)
        else:
            module_cost += module_profile[key]['cost'][value[1] - 1]
            module_cost += module_profile[key]['crash cost'][value[1] - 1] * value[2]
        best_solution[key].append(module_cost)
    
    return {
        "best_solution": best_solution,
        "fitness": best_fitness,
        "product_selection": best_product_selection
    }

"""
# Example usage
import pandas as pd
if __name__ == "__main__":
    input_params = {
        "population": 100,
        "mutationRate": 0.1,
        "crossoverRate": 0.5,
        "generations": 10,
        "interactionMatrix": pd.DataFrame(20, index=[i+1 for i in range(12)], columns=[i+1 for i in range(12)]),
        "informationMatrix": pd.DataFrame(0, index=[i+1 for i in range(12)], columns=[i+1 for i in range(12)]),
        "adoptionRate": []
    }
    result = run_genetic_algorithm(input_params)
    print(f"Best fitness: {result['fitness']}")
    print(f"Best solution: {result['best_solution']}")
"""
