import copy
import math

import Treetools

from Distributions import ProbabilityDistribution
def sanitise_seq(seq: list, generalisation_strategies: dict) -> list:
    return [generalisation_strategies[symbol] for symbol in seq]


def sanitise_pats(sensitive_patterns, generalisation_strategies):
    return [sanitise_seq(pattern, generalisation_strategies) for pattern in sensitive_patterns]


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
    return ProbabilityDistribution(sens_pats, input_sequence).get_max_val() > 0


def shannon_entropy(prob_distr: ProbabilityDistribution):
    entropy_inner_sum = 0
    for event in prob_distr.get_events():
        prob_event = prob_distr[event]
        if prob_event != 0:
            entropy_inner_sum += prob_event * math.log(prob_event)
        else:
            continue
    return -entropy_inner_sum


def conditional_shannon_entropy(prob_distr_A: ProbabilityDistribution, prob_distr_B: ProbabilityDistribution):
    """
    Returns the shannon entropy of A conditioned on B (i.e. H(A|B))

    In the case of these algorithms, each joint probability P[A_i,B_i] is simplified to P[A_i] as they are equivalent.
    This is not true for the general case of conditional shannon entropy.
    """
    events_A, events_B = prob_distr_A.get_events(), prob_distr_B.get_events()
    if len(events_A) != len(events_B):
        raise ValueError("There must be an equal number of events in both sets.")
    entropy_inner_sum = 0
    num_events = len(events_A)
    for i in range(num_events):
        event_A, event_B = events_A[i], events_B[i]
        prob_event_A, prob_event_B = prob_distr_A[event_A], prob_distr_B[event_B]
        if prob_event_A != 0 and prob_event_B != 0:
            entropy_inner_sum += prob_event_A * math.log(prob_event_B / prob_event_A)
        else:
            continue

    return entropy_inner_sum


def mutual_information(prob_distr_A: ProbabilityDistribution, prob_distr_B: ProbabilityDistribution):
    # H(S) - H(S|G)
    return shannon_entropy(prob_distr_A) - conditional_shannon_entropy(prob_distr_A, prob_distr_B)


def inference_gain(input_sequence, sensitive_patterns, generalisation_strategies):
    generalised_patterns = sanitise_pats(sensitive_patterns, generalisation_strategies)
    sanitised_sequence = sanitise_seq(input_sequence, generalisation_strategies)
    # Sensitive pattern probability distribution
    S = ProbabilityDistribution(sensitive_patterns, input_sequence)
    # Generalised pattern probability distribution
    G = ProbabilityDistribution(generalised_patterns, sanitised_sequence)
    return mutual_information(S, G)


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


def sanitise_seq_top_down(sens_pats: list, input_sequence: list, epsilon: float,
                          taxonomy_tree: Treetools.TaxonomyTree) -> list:
    print(f"--- BEGINNING EXECUTION OF TOP-DOWN ---\n"
          f"Sensitive patterns: {sens_pats}\n"
          f"User generated sequence: {input_sequence[:min(len(input_sequence), 10)]}...\n"
          f"Privacy level/Average information leakage upper bound (epsilon): {epsilon}\n"
          f"\tIf the value is low, lots of generalisation. If it's high, little generalisation.\n"
          f"Taxonomy tree: {str(taxonomy_tree)}\n")
    # Return the original sequence if no sensitive patterns occur in it
    if not do_sens_pats_occur(input_sequence, sens_pats):
        return input_sequence

    working_alphabet = sort_alphabet_by_freq(taxonomy_tree.get_leaf_symbols(),
                                             input_sequence)  # e.g. [Cookies, Beer, Milk, …]
    g_final = {a_i: taxonomy_tree.get_root().get_symbol() for a_i in
               working_alphabet}  # g_f={Cookies:ALL, Beer:ALL, Milk: ALL, …}
    level_of_generalisation = {a_i: 0 for a_i in
                               working_alphabet}  # current level of gen. for a_i, initially 1 = root = ALL
    symbols_to_prune = []
    # At each iteration, look at all leaves. Choose the best one (+collateral) to refine based on
    # utility gained after refining.
    while len(working_alphabet) > 0:
        previous_working_alphabet = copy.deepcopy(working_alphabet)
        symbols_refined_w_min_util_loss = []
        g_final_updated = copy.deepcopy(
            g_final)  # if no refinement possible, just keep most general everything=All (g_f)
        util_loss = math.inf
        # Choose a leaf, if it can be refined, what’s the utility loss after refining?
        # Update g_f with this best refinement option
        print(f"Working alphabet {working_alphabet}")
        print(f"Current generalisation function {g_final}")
        print(f"... Iterating over working alphabet")
        for a_i in working_alphabet:
            print(f"\ta_i {a_i}")
            if a_i in symbols_to_prune:
                print(f"\ta_i {a_i} in symbols_to_prune")
                continue  # don't look at pruned symbols

            # symbol on layer l_i + 1 on path towards a_i (more refined than on l_i)
            level_of_gen_a_i = copy.deepcopy(level_of_generalisation[a_i])
            print(f"\t\tcurrent level of generalisation {level_of_gen_a_i}")
            more_refined_generalisation_symbol = taxonomy_tree.find_leaf_node(a_i).get_path_from_root()[
                level_of_gen_a_i + 1].get_symbol()
            print(f"\t\tmore refined symbol: {more_refined_generalisation_symbol}")

            # get the (bottom level) leaves that have the
            # more refined generalisation symbol as an ancestor
            more_ref_gen_sym_leaves = Treetools.TreeNode.leaves(
                taxonomy_tree.find_nodes(more_refined_generalisation_symbol)[0])

            g_temp = copy.deepcopy(g_final)
            # update leaves of subtree's g-mapping as well as current symbol
            for a_j in more_ref_gen_sym_leaves:
                g_temp[a_j.get_symbol()] = more_refined_generalisation_symbol
                # if Treetools.TreeNode.is_leaf(a_j):
                #     symbols_to_prune.append(a_j.get_symbol())
            print(f"\t\tProposed new generalisation function {g_temp}")
            # If this g is worse than the previous, don't continue to the next 'if'
            # to update, just discard this g and move onto the next symbol
            print(f"\t\tEvaluating utility loss")
            utility_loss_of_g = utility_loss_by_generalising(input_sequence, g_temp, taxonomy_tree.get_cost_func())
            if utility_loss_of_g > util_loss:
                print("\t\t\tUtility loss worse, moving onto next a_i")
                continue  # TODO: does python 'continue' work in the same way as algo 1 pseudocode?
            else:
                print(f"\t\t\tUtility loss same or better")

            print(f"\t\tAssessing inference gain")
            # if privacy is still satisfied -> update with new generalisation strategies g
            if inference_gain(input_sequence, sens_pats, g_temp) <= epsilon:
                print(f"\t\t\tInference gain {inference_gain(input_sequence, sens_pats, g_temp):.2f} <= {epsilon}"
                      f"\n\t\t\t(privacy satisfied)"
                      f"\n\t\t\t==> symbol(s) {more_ref_gen_sym_leaves} have smallest utility loss so far for this "
                      f"parse of working_alphabet")
                util_loss = utility_loss_of_g
                g_final_updated = copy.deepcopy(g_temp)
                symbols_refined_w_min_util_loss = [node.get_symbol() for node in
                                                   more_ref_gen_sym_leaves]
            else:  # privacy no longer satisfied -> prune tree using pruning criteria
                # don’t update generalisation strategies g with this new strategy
                # AND remove these leaves – they can’t be generalised further
                print(f"\t\t\tInference gain {inference_gain(input_sequence, sens_pats, g_temp):.2f} > {epsilon}"
                      f"\n\t\t\t- pruning {[str(a_j) for a_j in more_ref_gen_sym_leaves]}")
                for a_j in more_ref_gen_sym_leaves:
                    symbols_to_prune.append(a_j.get_symbol())
        for a_i in symbols_to_prune:
            level_of_generalisation[a_i] += 1
            working_alphabet.remove(a_i)
        symbols_to_prune = []
        g_final = copy.deepcopy(g_final_updated)  # g' is g_f updated with best leaf(s) to refine
        if working_alphabet == previous_working_alphabet:
            print("No change made to working alphabet in this iteration")
            import sys
            sys.exit()
        print(f"Final generalisation function given epsilon={epsilon}:\n\t{g_final}")
        print(f"- of which unique symbols:\n\t{set(g_final.values())}")
    return generalise_seq(input_sequence, g_final)
