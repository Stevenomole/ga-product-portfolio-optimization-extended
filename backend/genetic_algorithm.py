import math 
import random
import numpy as np
import pandas as pd
from collections import deque

class GeneticAlgorithm:
    def __init__(self, module_profile, dependencies, feasible_set, interaction_degree, information_flow):
        self.module_profile = module_profile
        self.dependencies = dependencies
        self.feasible_set = feasible_set
        self.interaction_degree = interaction_degree
        self.information_flow = information_flow

    def generate_individual(self):
        while True:  # keep trying until a valid individual is generated
            individual = {}
            periods = {module: [] for module in self.module_profile.keys()}
            module_sequence = self.topological_sort(self.dependencies)
            valid_schedule = True

            for module in module_sequence:
                # handle in-house modules with non-preemptive scheduling
                if self.module_profile[module]['type'] == 'inhouse':
                    duration = self.module_profile[module]['duration'][0]
                    max_crash = int(self.module_profile[module]['max crash'][0])
                    crash_period = random.randint(0, max_crash) if max_crash > 0 else 0
                    duration -= crash_period
                    is_allocated = False
                    available_periods = list(range(1, int(156 - duration + 1)))
                    random.shuffle(available_periods)  # randomize the order of period selection

                    for start_period in available_periods:
                        if self.check_precedence(start_period, module, periods):
                            if self.check_resource_availability(start_period, duration, module):
                                is_allocated = True
                                periods[module] = [start_period, None, crash_period, int(start_period + duration)]
                                break
                    if not is_allocated:
                        valid_schedule = False
                        break

                # handle outsourced modules
                if self.module_profile[module]['type'] == 'outsourced':
                    supplier = random.choice(self.module_profile[module]['supplier'])
                    duration = self.module_profile[module]['duration'][supplier - 1]
                    max_crash = int(self.module_profile[module]['max crash'][supplier - 1])
                    crash_period = random.randint(0, max_crash) if max_crash > 0 else 0
                    duration -= crash_period
                    is_allocated = False
                    available_periods = list(range(1, int(156 - duration + 1)))
                    random.shuffle(available_periods)  # randomize the order of period selection

                    for start_period in available_periods:
                        if self.check_precedence(start_period, module, periods):
                            periods[module] = [start_period, supplier, crash_period, int(start_period + duration)]
                            is_allocated = True
                            break

                    if not is_allocated:
                        valid_schedule = False
                        break 

            if valid_schedule:
                individual = periods
                return individual 
    
    def check_resource_availability(self, start_period, duration, module):
        end_period = int(start_period + duration)
        for period in range(start_period, end_period+1):
            if self.feasible_set[module][period-1] == 0:
                return False
        return True
    

    def check_precedence(self, start_period, module, periods):
        # Check if all predecessors have completed before the proposed start period
        if self.dependencies[module]:
            for predecessor in self.dependencies[module]:
                if self.interaction_degree[predecessor][module] > 0:
                    if self.module_profile[predecessor]['type'] == 'inhouse':
                        predecessor_end_period = periods[predecessor][0] + self.interaction_degree[predecessor][module]/100*(self.module_profile[predecessor]['duration'][0] - periods[predecessor][2])                
                        if int(predecessor_end_period) > start_period:
                            return False
                    else:
                        predecessor_end_period = periods[predecessor][0] + self.interaction_degree[predecessor][module]/100*(self.module_profile[predecessor]['duration'][periods[predecessor][1] - 1] - periods[predecessor][2])
                        if int(predecessor_end_period) > start_period:
                            return False
        return True

    def topological_sort(self, dependencies):
        in_degree = {i: 0 for i in range(1, len(dependencies) + 1)}
        for node, preds in dependencies.items():
            for pred in preds:
                in_degree[node] += 1

        queue = deque([node for node, deg in in_degree.items() if deg == 0])
        order = [] 
        
        while queue:
            node = queue.popleft()
            order.append(node)
            for successor in [succ for succ, preds in dependencies.items() if node in preds]:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    queue.append(successor)

        if len(order) == len(dependencies):
            return order
        else:
            return "Cycle Detected!!!"
            
    def initialize_population(self, pop_size):
        return [self.generate_individual() for _ in range(pop_size)]

    def fitness_function(self, individual):
        
        # Product definitions and ILT
        products = {
            'P11': {'name': 'P11', 'ILT': 53, 'product_rev':2000000, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 1, 7: 1, 8: 0, 9: 0, 10: 0, 11: 0, 12: 1},
            'P21': {'name': 'P21', 'ILT': 53, 'product_rev':2000000, 1: 1, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1, 8: 0, 9: 0, 10: 1, 11: 0, 12: 0},
            'P31': {'name': 'P31', 'ILT': 53, 'product_rev':2000000, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 1, 7: 1, 8: 0, 9: 0, 10: 0, 11: 1, 12: 0},
            'P12': {'name': 'P12', 'ILT': 53, 'product_rev':3000000, 1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1, 7: 0, 8: 1, 9: 0, 10: 1, 11: 0, 12: 0},
            'P22': {'name': 'P22', 'ILT': 53, 'product_rev':3000000, 1: 0, 2: 1, 3: 0, 4: 0, 5: 1, 6: 1, 7: 0, 8: 1, 9: 0, 10: 0, 11: 1, 12: 0},
            'P32': {'name': 'P32', 'ILT': 53, 'product_rev':3000000, 1: 0, 2: 1, 3: 0, 4: 0, 5: 1, 6: 1, 7: 0, 8: 1, 9: 0, 10: 0, 11: 0, 12: 1},
            'P13': {'name': 'P13', 'ILT': 53, 'product_rev':4000000, 1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 1, 7: 0, 8: 0, 9: 1, 10: 0, 11: 1, 12: 0},
            'P23': {'name': 'P23', 'ILT': 53, 'product_rev':4000000, 1: 0, 2: 0, 3: 1, 4: 0, 5: 1, 6: 1, 7: 0, 8: 0, 9: 1, 10: 1, 11: 0, 12: 0}
        }
        
        families = {
            'K1': ['P11', 'P21', 'P31'],
            'K2': ['P12', 'P22', 'P32'],
            'K3': ['P13', 'P23'],
        }
        
        total_profit = 0
        family_product_profit = {}
        for family, products_list in families.items():
            product_profit_and_times = {prod: self.calculate_product_profit(products[prod], individual) for prod in products_list}
            product_profit = {prod: cost for prod, (cost, _) in product_profit_and_times.items()}
            launch_time_by_product = {prod: time for prod, (_, time) in product_profit_and_times.items()}

            selected_product = max(product_profit, key=product_profit.get)
            family_profit = product_profit[selected_product]
            family_launch = launch_time_by_product[selected_product]
            total_profit += family_profit
            family_product_profit[family] = {selected_product: [family_profit, family_launch]}

        return total_profit, family_product_profit

    def calculate_product_profit(self, product, individual):
        product_cost_fv_at_launch = 0
        max_period = 0  # track the latest module completion time for the product
        interest_rate = 0.002

        # sum the future costs of the modules at product completion
        for module in product:
            if product[module] == 1:  # check if the module is required for the product
                start_period = individual[module][0]
                duration = self.module_profile[module]['duration'][0] if self.module_profile[module]['type'] == 'inhouse' else self.module_profile[module]['duration'][individual[module][1] - 1]
                completion_time = start_period + duration - individual[module][2]
                max_period = max(max_period, completion_time)
        product_completion_period = max_period + 1

        for module in product:
            if product[module] == 1:  # check if the module is required for the product
                start_period = individual[module][0]
                duration = self.module_profile[module]['duration'][0] if self.module_profile[module]['type'] == 'inhouse' else self.module_profile[module]['duration'][individual[module][1] - 1]
                completion_time = start_period + duration - individual[module][2]
                
                # add base cost for all periods and crashing cost
                if self.module_profile[module]['type'] == 'inhouse':
                    module_cal_cost = self.module_profile[module]['cost'] + self.module_profile[module]['crash cost'][0] * (individual[module][2] ** 2)
                else:
                    module_cal_cost = self.module_profile[module]['cost'][individual[module][1] - 1] + self.module_profile[module]['crash cost'][individual[module][1] - 1] * (individual[module][2] ** 2)
                
                product_cost_fv_at_launch += module_cal_cost * (1+interest_rate)**(product_completion_period - completion_time - 1)

        # calculate present value of revenue and future value of the cost 
        product_cost_fv = product_cost_fv_at_launch * (1+interest_rate)**(max(0, (product['ILT'] - product_completion_period)))      
        
        product_rev_pv = product['product_rev']*(1-((1+interest_rate)**-(156-max(product_completion_period, product['ILT']))))*(1+interest_rate)/(interest_rate)
               
        return product_rev_pv-product_cost_fv, max(product_completion_period, product['ILT'])

    def select_parents(self, population, fitness_scores):
        # select parents based on their fitness probabilities
        elite_size = int(len(population)/2)
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population), key=lambda pair: pair[0], reverse=True)]
        elite_parents = sorted_population[:elite_size]
        
        return elite_parents

    def contest_select(self, population, fitness_scores, contest_size=3):
        selected_indices = random.sample(range(len(population)), contest_size)
        selected_fitness = [fitness_scores[i] for i in selected_indices]
        best_index = selected_indices[selected_fitness.index(min(selected_fitness))]
        
        return population[best_index]

    def uniform_crossover(self, parent1, parent2):
        swap_count = 0
        modules_to_swap = list(parent1.keys())
        half_modules = math.ceil(len(modules_to_swap) / 2)
        offspring1, offspring2 = parent1.copy(), parent2.copy()
        
        while swap_count < half_modules and modules_to_swap:
            module = random.choice(modules_to_swap)
            # tentatively swap the modules
            offspring1[module], offspring2[module] = offspring2[module], offspring1[module]
            check_passed = True
            
            for i in list(parent1.keys()):
                start_period1, start_period2 = offspring1[i][0], offspring2[i][0]
                
                # check if swapping the target module maintains the precedence constraints
                if not (self.check_precedence(start_period1, i, offspring1) and 
                        self.check_precedence(start_period2, i, offspring2)):
                    check_passed = False
                    break

            if check_passed:
                swap_count += 1
            else:
                # revert the swap if it violates constraints
                offspring1[module], offspring2[module] = offspring2[module], offspring1[module]

            # remove the module from the list to avoid repetitive checks
            modules_to_swap.remove(module)

        # if less than 6 swaps were made, discard the offspring by returning None
        if swap_count < 6:
            return None, None

        return offspring1, offspring2

    def crossover(self, parents, fitness_scores, crossover_rate):
        offs_size = int(len(parents)/2)
        offspring = []

        for _ in range(len(parents)):
            parent1 = self.contest_select(parents, fitness_scores, 3)
            parent2 = self.contest_select(parents, fitness_scores, 3)
            if random.random() < crossover_rate:
                offspring1, offspring2 = self.uniform_crossover(parent1, parent2)
                if offspring1 is not None and offspring2 is not None:
                    offspring.append(offspring1)
                    offspring.append(offspring2)

        offspring = offspring[:offs_size] if len(offspring) > offs_size else offspring
        
        return offspring

    def mutation(self, offspring, mutation_rate):
        for individual in offspring:
            if random.random() < mutation_rate:
                # randomly select a module to mutate
                module = random.choice(list(individual.keys()))
                
                # mutating the in-house modules
                if self.module_profile[module]['type'] == 'inhouse':
                    max_crash = int(self.module_profile[module]['max crash'][0])
                    crash_period = random.choice([x for x in range(0, max_crash + 1) if x != individual[module][2]]) if max_crash > 0 else 0
                    duration = self.module_profile[module]['duration'][0] - crash_period
                    
                    # attempt to find a valid new start period
                    available_periods = list(range(1, int(156 - duration + 1)))
                    random.shuffle(available_periods)
                    valid_mutation = False
                    
                    for new_start_period in available_periods:
                        if self.check_precedence(new_start_period, module, individual) and \
                        self.check_resource_availability(new_start_period, duration, module):
                            
                            individual[module] = [new_start_period, None, crash_period, new_start_period + duration]
                            check_passed = True
                            # check if mutation does not make successors invalid
                            for i in list(individual.keys()):
                                start_period = individual[i][0]
                
                                if not self.check_precedence(start_period, i, individual):
                                    check_passed = False
                                    break
                            if check_passed:
                                valid_mutation = True
                                break
                    
                    if not valid_mutation:
                        # if no valid mutation is found, do not change the individual
                        continue
                    
                # mutating outsourced modules
                else:
                    new_supplier = random.choice(self.module_profile[module]['supplier'])
                    lead_time = self.module_profile[module]['duration'][new_supplier - 1]
                    max_crash = int(self.module_profile[module]['max crash'][new_supplier - 1])
                    crash_period = random.choice([x for x in range(0, max_crash + 1) if x != individual[module][2]]) if max_crash > 0 else 0
                    lead_time -= crash_period
                    
                    # Attempt to find a valid new start period
                    available_periods = list(range(1, int(156 - lead_time + 1)))
                    random.shuffle(available_periods)
                    valid_mutation = False
                    
                    for new_start_period in available_periods:
                        if self.check_precedence(new_start_period, module, individual):
                            individual[module] = [new_start_period, new_supplier, crash_period, new_start_period + lead_time]
                            check_passed = True
                            # check if mutation does not make successors invalid
                            for i in list(individual.keys()):
                                start_period = individual[i][0]
                
                                if not self.check_precedence(start_period, i, individual):
                                    check_passed = False
                                    break
                            if check_passed:
                                valid_mutation = True
                                break
                    
                    if not valid_mutation:
                        # if no valid mutation is found, do not change the individual
                        continue

        return offspring
    
    def run(self, pop_size, crossover_rate, mutation_rate, num_generations):
        # initialize population
        population = self.initialize_population(pop_size)

        # initialize best individual tracking
        global_best_fitness = -float('inf')
        global_best_individual = None
        global_best_product_selection = None

        for generation in range(num_generations):
            # evaluate fitness for each individual
            fitness_results = [self.fitness_function(individual) for individual in population]
            fitness_scores = [result[0] for result in fitness_results]
            product_selections = [result[1] for result in fitness_results]

            # check and update the best individual and fitness
            for ind, (fitness, product_selection) in enumerate(zip(fitness_scores, product_selections)):
                if fitness > global_best_fitness:
                    global_best_fitness = fitness
                    global_best_individual = population[ind]
                    global_best_product_selection = product_selection

            # selection
            elite_parents = self.select_parents(population, fitness_scores)
            
            # crossover
            offspring = self.crossover(population, fitness_scores, crossover_rate)
            
            # mutation
            offspring = self.mutation(offspring, mutation_rate)
            
            population = elite_parents + offspring

            # Print generation number and best fitness
            print(f"Generation {generation}: Best fitness = {max(fitness_scores)}")

        return global_best_individual, global_best_fitness, global_best_product_selection

    def update_module_duration(self):
        self.information_flow = self.information_flow.replace('-', np.nan).astype(float)

        for module in self.module_profile.keys():
            # Get the column for the current module (successor)
            flow_values = self.information_flow.loc[module]

            # Find the maximum flow affecting the module (ignoring NaN values)
            max_flow = flow_values.max()

            # Update the durations if max flow is valid
            if not np.isnan(max_flow):
                updated_durations = []
                for duration in self.module_profile[module]['duration']:
                    updated_duration = int(duration + (max_flow / 100) * duration)
                    updated_durations.append(updated_duration)

                # Update the module's duration with the new calculated values
                self.module_profile[module]['duration'] = updated_durations
            