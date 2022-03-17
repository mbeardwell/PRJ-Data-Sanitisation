import copy
import math

import Entropy
import Trees
from Distributions import ProbabilityDistribution, JointProbabilityDistribution
from Generalisation import GeneralisationFunction

SILENT = True


def printer(*args):
    global SILENT
    if not SILENT:
        print(*args)


def sanitise_seq_top_down(sens_pats: list, input_sequence: list, epsilon: float,
                          taxonomy_tree: Trees.TaxonomyTree) -> list:
    printer(f"--- BEGINNING EXECUTION OF TOP-DOWN ---\n"
            f"Sensitive patterns: {sens_pats}\n"
            f"User generated sequence: {input_sequence[:min(len(input_sequence), 10)]}...\n"
            f"Privacy level/Average information leakage upper bound (epsilon): {epsilon}\n"
            f"\tIf the value is low, lots of generalisation. If it's high, little generalisation.\n"
            f"Taxonomy tree: \n{str(taxonomy_tree)}\n")
    # Return the original sequence if no sensitive patterns occur in it
    if not do_sens_pats_occur(input_sequence, sens_pats):
        return input_sequence

    # e.g. [Cookies, Beer, Milk, …]
    working_alphabet = sort_alphabet_by_freq(taxonomy_tree.get_leaf_symbols(), input_sequence)
    # g_final = {Cookies:ALL, Beer:ALL, Milk: ALL, …}
    g_final = GeneralisationFunction(working_alphabet, taxonomy_tree.get_root().get_symbol())
    symbols_to_prune = []
    # At each iteration, look at all leaves. Choose the best one (+collateral) to refine based on
    # utility gained after refining.
    while len(working_alphabet) > 0:
        previous_working_alphabet = copy.deepcopy(working_alphabet)
        previous_g_final = copy.deepcopy(g_final)
        symbols_refined_w_min_util_loss = []
        # g_final stays the same if no refinement possible
        g_final_updated = copy.deepcopy(g_final)
        util_loss = math.inf
        # Choose a leaf, if it can be refined, what’s the utility loss after refining?
        # Update g_final with this best refinement option
        printer(f"Working alphabet {working_alphabet}")
        printer(f"Current generalisation function", g_final)
        printer(f"... Iterating over working alphabet")
        for a_i in working_alphabet:
            printer(f"\ta_i {a_i}")
            if a_i in symbols_to_prune:
                printer(f"\ta_i {a_i} in symbols_to_prune")
                continue  # don't look at pruned symbols

            # if symbol already fully refined, discard from working_alphabet
            if g_final[a_i] == a_i:
                symbols_to_prune.append(a_i)
                continue

            # symbol on layer l_i + 1 on path towards a_i (more refined than on l_i)
            level_of_gen_a_i = g_final.get_generalisation_level(a_i)
            printer(f"\t\tcurrent level of generalisation {level_of_gen_a_i} for {a_i}")
            more_refined_generalisation_symbol = taxonomy_tree.find_leaf_node(a_i).get_path_from_root()[
                level_of_gen_a_i + 1].get_symbol()
            printer(f"\t\tmore refined symbol: {more_refined_generalisation_symbol}")

            # get the (bottom level) leaves that have the
            # more refined generalisation symbol as an ancestor
            more_ref_gen_sym_leaves = Trees.TreeNode.leaves(
                taxonomy_tree.find_nodes(more_refined_generalisation_symbol)[0])

            g_temp = copy.deepcopy(g_final)
            # update leaves of subtree's g-mapping as well as current symbol
            for a_j in more_ref_gen_sym_leaves:
                g_temp[a_j.get_symbol()] = more_refined_generalisation_symbol
                g_temp.incr_generalisation_level(a_j.get_symbol())
                # if Trees.TreeNode.is_leaf(a_j):
                #     symbols_to_prune.append(a_j.get_symbol())
            printer(f"\t\tProposed new generalisation function {g_temp}")
            # If this g is worse than the previous, don't continue to the next 'if'
            # to update, just discard this g and move onto the next symbol
            printer(f"\t\tEvaluating utility loss of proposed generalisation function")
            utility_loss_of_g = utility_loss_by_generalising(input_sequence, g_temp, taxonomy_tree.get_cost_func())
            if utility_loss_of_g > util_loss:
                printer(f"\t\t\t{utility_loss_of_g} > {util_loss}'")
                printer(f"\t\tUtility loss worse, moving onto next a_i")
                continue  # TODO: does python 'continue' work in the same way as algo 1 pseudocode?

            else:
                printer(f"\t\t\t{utility_loss_of_g} <= {util_loss}'")
                printer(f"\t\t\tUtility loss same or better")
            printer(f"\t\tAssessing privacy")
            # if privacy is still satisfied -> update with new generalisation strategies g
            if inference_gain(input_sequence, sens_pats, g_temp) <= epsilon:
                printer(f"\t\t\tInference gain {inference_gain(input_sequence, sens_pats, g_temp):.2f} <= {epsilon}\n"
                        f"\t\t\t(privacy satisfied)")
                printer(f"\t\t\t==> Current proposed refinements are {more_ref_gen_sym_leaves}")
                util_loss = utility_loss_of_g
                g_final_updated = copy.deepcopy(g_temp)
                symbols_refined_w_min_util_loss = [node.get_symbol() for node in
                                                   more_ref_gen_sym_leaves]
            else:  # privacy no longer satisfied -> prune tree using pruning criteria
                # don’t update generalisation strategies g with this new strategy
                # AND remove these leaves – they can’t be generalised further
                printer(f"\t\t\tInference gain {inference_gain(input_sequence, sens_pats, g_temp):.2f} > {epsilon}\n"
                        f"\t\t\t(privacy not satisfied)\n"
                        f"\t\t\t==> pruning {[str(a_j) for a_j in more_ref_gen_sym_leaves]}")
                for a_j in more_ref_gen_sym_leaves:
                    symbols_to_prune.append(a_j.get_symbol())
        for a_i in symbols_to_prune:
            working_alphabet.remove(a_i)
        symbols_to_prune = []
        g_final = copy.deepcopy(g_final_updated)  # g' is g_final updated with best leaf(s) to refine
        if working_alphabet == previous_working_alphabet:
            printer("\tNo change made to working alphabet in this iteration")
        else:
            printer(f"\tworking_alphabet updated this iteration\n"
                    f"\t\tworking alphabet Old:\n"
                    f"\t\t\t{previous_working_alphabet}\n"
                    f"\t\tworking alphabet Updated:\n"
                    f"\t\t\t{working_alphabet}")
        if g_final == previous_g_final:
            printer("\tNo change made to g_final in this iteration")
        else:
            printer(f"\tg_final updated this iteration\n"
                    f"\t\tg_final Old:\n"
                    f"\t\t\t{previous_g_final}\n"
                    f"\t\tg_final Updated:\n"
                    f"\t\t\t{g_final}")
    printer(f"Final generalisation function given epsilon={epsilon}:\n\t{g_final}")
    return generalise_seq(input_sequence, g_final)


def init_centroids(sensitive_patterns):
    # TODO returns a set of centroids, one centroid
    #  is assigned to each sensitive pattern
    pass


def least_common_generalised_pattern(pattern_1, pattern_2, taxonomy_tree):
    return  # TODO returns LCGP(p_1, p_2); look at algorithm 2


def sanitise_seq_bottom_up(sens_pats: list, input_sequence: list, epsilon: float,
                           taxonomy_tree: Trees.TaxonomyTree) -> list:
    centroids = init_centroids(sens_pats)
    alphabet = taxonomy_tree.get_leaf_symbols()
    root = taxonomy_tree.get_root().get_symbol()
    g_final = GeneralisationFunction(alphabet, root)

    inference_gain = epsilon

    # repeat until the privacy level is met
    while not (inference_gain <= epsilon):
        if len(centroids) == 1:
            pass  # TODO greeidly generalise the symbols in g_final

        # TODO compute distance between pair of centroids
        centroid_distances = {}
        # TODO compute closest pair of centroids
        sens_pat_1, sens_pat_2 = None, None  # TODO = closest pair of centroids

        centroids.remove(sens_pat_1)
        centroids.remove(sens_pat_2)

        sens_pat_3 = least_common_generalised_pattern(sens_pat_1, sens_pat_2, taxonomy_tree)
        centroids[sens_pat_3] = None  # TODO  C[p3] = C(p1) Union C(p2)

        # TODO add p3 to centroids

        # TODO update g_final according to LCGP(p1,p2) >> updates the centroids accordingly

    return generalise_seq(input_sequence, g_final)


def sanitise_seq(seq: list, generalisation_strategies: GeneralisationFunction) -> list:
    return [generalisation_strategies[symbol] for symbol in seq]


def sanitise_pats(sensitive_patterns, generalisation_strategies: GeneralisationFunction):
    sanitised_patterns = []
    for pattern in sensitive_patterns:
        sanitised_pattern = sanitise_seq(pattern, generalisation_strategies)
        if sanitised_pattern not in sanitised_patterns:
            sanitised_patterns.append(sanitised_pattern)
    return sanitised_patterns


# returns a list of the occurrences of each pattern, in the pattern set, in the sequence
# the order of the list is the same order as the pattern set list


# # returns the general symbols used in the sanitised sequence
# def get_used_general_symbols(sanitised_sequence, tax_tree):
#     unique_general_symbols = list(set(sanitised_sequence))
#     used_general_symbols = []
#     for node in tax_tree.get_internal_nodes():
#         if node.get_symbol() in unique_general_symbols:
#             used_general_symbols.append(node.get_symbol())
#     return used_general_symbols

def do_sens_pats_occur(input_sequence, sens_pats):
    """
    Returns whether any sensitive pattern occurs in the input sequence
    """
    return ProbabilityDistribution(input_sequence).sum() > 0


def inference_gain(input_sequence, sensitive_patterns, generalisation_strategies: GeneralisationFunction):
    generalised_patterns = sanitise_pats(sensitive_patterns, generalisation_strategies)
    sanitised_sequence = sanitise_seq(input_sequence, generalisation_strategies)
    # Sensitive pattern probability distribution
    S = ProbabilityDistribution(input_sequence)
    # Generalised pattern probability distribution
    G = ProbabilityDistribution(sanitised_sequence)
    joint_S_G = JointProbabilityDistribution(input_sequence, sanitised_sequence)
    return Entropy.mutual_information(S, G, joint_S_G)


# Represented by UL(S,g,[c]) in pseudocode
def utility_loss_by_generalising(input_sequence, g, c):
    sanitised_sequence = generalise_seq(input_sequence, g)
    utility_loss_sum = 0
    for i in range(len(input_sequence)):
        utility_loss_sum += c[(input_sequence[i], sanitised_sequence[i])]
    return utility_loss_sum


# pseudocode would be S_hat(S,g)
# Returns sanitised sequence - S sanitised by g mappings
def generalise_seq(input_sequence: list, g: dict) -> list:
    return [g[a_i] for a_i in input_sequence]


# Returns an alphabet, sorted by the symbols' frequency of occurrence in sequence 'seq'
def sort_alphabet_by_freq(alphabet: list, seq: list) -> list:
    symbol_frequencies = {a: seq.count(a) for a in alphabet}
    alphabet_new = sorted(alphabet, key=lambda a: symbol_frequencies[a], reverse=True)  # descending order
    return alphabet_new
