# Setup problems
from genotype import Genome
import Logger
import stupid_problem_test
problem = stupid_problem_test.StupidProblem()
# Setup logging
logger = Logger.Logger("log.txt", ["CGPProgram image"])
# Setup CGP genome
# - define a counter
from HelperClasses import Counter, randchoice
counter = Counter()
neuron_internal_states = 3
dendrite_internal_states = 3
signal_dimensionality = 3
dimensions = 3
hox_variant_count = 1

# - define the function arities
# also define canonical order of functions - arbitrary, for compatibilitiy with 
# neuron code
# RFE move out this order to some single source of knowledge
neuron_function_order = [
    'axon_birth_program',
    'signal_axon_program',
    'recieve_axon_signal_program',
    'recieve_reward_program',
    'move_program',
    'die_program',
    'neuron_birth_program',
    'action_controller_program',
    'hox_variant_selection_program'
    'internal_state_variable_count', # not function but parameter comes here in the order
]
neuron_function_arities = [  # by order above
    [dimensions+neuron_internal_states+1, 3+signal_dimensionality], # axon birth
    [signal_dimensionality+dimensions+neuron_internal_states, 2 + signal_dimensionality + neuron_internal_states], # signal axon
    [signal_dimensionality + dimensions + neuron_internal_states, 3+neuron_internal_states+signal_dimensionality], # recieve signal axon
    [1 + dimensions + neuron_internal_states, 2 + neuron_internal_states], # reciee reward
    [neuron_internal_states + dimensions, 7+neuron_internal_states], # move
    [dimensions + neuron_internal_states, 2+neuron_internal_states], # die
    [dimensions + neuron_internal_states, 2+neuron_internal_states*2], # neuron birth
    [neuron_internal_states+dimensions, 9], # action controller
    [neuron_internal_states + dimensions, hox_variant_count] # hox selection
]

dendrite_function_order = [
    'recieve_signal_neuron_program',
    'recieve_signal_dendrite_program',
    'signal_dendrite_program',
    'signal_neuron_program',
    'accept_connection_program',
    'break_connection_program',
    'recieve_reward_program',
    'die_program',
    'action_controller_program'
]
dendrite_function_arities = [
    [dendrite_internal_states + signal_dimensionality + dimensions, 4+signal_dimensionality+dendrite_internal_states],
    [dendrite_internal_states + signal_dimensionality + dimensions, 4+signal_dimensionality+dendrite_internal_states],
    [dimensions + dendrite_internal_states + signal_dimensionality, 4+signal_dimensionality+dendrite_internal_states],
    [dimensions + dendrite_internal_states + dimensions + dendrite_internal_states, 2+dendrite_internal_states],
    [dimensions + dendrite_internal_states + dimensions + dendrite_internal_states, 1],
    [dimensions + dendrite_internal_states + 1, 2 + dendrite_internal_states],
    [dimensions + dendrite_internal_states, 1+signal_dimensionality],
    [dendrite_internal_states + dimensions, 9]
]

# TODO add support for homeobox variant selection, currently just uses one
# Knowledge duplication thooo
def genome_to_init_data(genome):
    neuron_init_data = {
        'axon_birth_program' : genome.function_chromosomes[0].hex_variants[0].program,
        'signal_axon_program' : genome.function_chromosomes[1].hex_variants[0].program,
        'recieve_axon_signal_program': genome.function_chromosomes[2].hex_variants[0].program,
        'recieve_reward_program': genome.function_chromosomes[3].hex_variants[0].program,
        'move_program': genome.function_chromosomes[4].hex_variants[0].program,
        'die_program': genome.function_chromosomes[5].hex_variants[0].program,
        'neuron_birth_program': genome.function_chromosomes[6].hex_variants[0].program,
        'action_controller_program': genome.function_chromosomes[7].hex_variants[0].program,
        'hox_variant_selection_program': genome.hex_selector_genome.program,
        'internal_state_variable_count': neuron_internal_states
    }
    axon_init_data = {
        'recieve_signal_neuron_program' : genome.function_chromosomes[8].hex_variants[0].program,
        'recieve_signal_dendrite_program' : genome.function_chromosomes[9].hex_variants[0].program,
        'signal_dendrite_program' : genome.function_chromosomes[10].hex_variants[0].program,
        'signal_neuron_program' : genome.function_chromosomes[11].hex_variants[0].program,
        'accept_connection_program' : genome.function_chromosomes[12].hex_variants[0].program,
        'break_connection_program' : genome.function_chromosomes[13].hex_variants[0].program,
        'recieve_reward_program' : genome.function_chromosomes[14].hex_variants[0].program,
        'die_program' : genome.function_chromosomes[15].hex_variants[0].program,
        'action_controller_program' : genome.function_chromosomes[16].hex_variants[0].program,
    }
    return neuron_init_data, axon_init_data

import CGPEngine
# initialize the genome(s)
all_function_arities = neuron_function_arities + dendrite_function_arities
genome_count = 8
genomes = []
for num in range(genome_count):
    genomes.append(Genome(
        hox_variant_count,
        2,
        all_function_arities,
        counter,
        neuron_internal_states,
        neuron_function_order[:-1] + dendrite_function_order,
        logger)) # TODO RN assumes equal amount of axon and neuron internal state variables


from engine import NeuronEngine
# learning loop
learning_iterations = 1000000000000
genome_results = []
neuron_init, axon_init = genome_to_init_data(genomes[0])
for genome in genomes:
    engine = NeuronEngine(
        input_arity = problem.input_arity,
        output_arity = problem.output_arity,
        grid_count = 6,
        grid_size = 10,
        actions_max = 60,
        neuron_initialization_data = neuron_init,
        axon_initialization_data = axon_init,
        signal_arity = signal_dimensionality,
        hox_variant_count = hox_variant_count,
        counter = counter,
        instances_per_iteration = 50
    )
    result = engine.run(problem)
    genome_results.append(result)
genomes = list(zip(genomes, genome_results))
# TODO Crossover breaks function chromosome in genome
for num in range(learning_iterations):    
    new_genomes = []
    egligable_bachelors = [x[0] for x in genomes]
    while len(egligable_bachelors) > 0:
        choice1 = randchoice(egligable_bachelors)
        choice2 = randchoice(egligable_bachelors)
        indexes = [egligable_bachelors.index(choice1), egligable_bachelors.index(choice2)]
        egligable_bachelors.remove(choice1)  # Currently possible to do crossover with self, which does make some sense with subgraph extraction
        if choice2 in egligable_bachelors:
            egligable_bachelors.remove(choice2)
        new_genomes = choice1.crossover(choice2)
        genome_results = []
        # Could run this in parallell
        for genome in new_genomes:
            engine = NeuronEngine(
                input_arity = problem.input_arity,
                output_arity = problem.output_arity,
                grid_count = 6,
                grid_size = 10,
                actions_max = 60,
                neuron_initialization_data = neuron_init,
                axon_initialization_data = axon_init,
                signal_arity = signal_dimensionality,
                hox_variant_count = hox_variant_count,
                counter = counter,
                instances_per_iteration = 50
            )
            result = engine.run(problem)
            genome_results.append(result)
        
        # all children of a parent compete for the parents spots
        parent1score = genomes[indexes[0]][1]
        parent2score = genomes[indexes[1]][1]
        for num in range(len(new_genomes)):
            if genome_results[num] >= parent1score:
                genomes[indexes[0]] = (new_genomes[num], genome_results[num])
                parent1score = genome_results[num] 
            elif genome_results[num] >= parent2score:
                genomes[indexes[1]] = (new_genomes[num], genome_results[num])
                parent2score = genome_results[num]
    print([x[1] for x in genomes])
    
