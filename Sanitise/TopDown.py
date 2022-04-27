import copy
import math

from Privacy.Distributions import ProbabilityDistribution
from Sanitise import Helper, Trees
from Sanitise.Helper import GeneralisationFunction


def do_sens_pats_occur(input_sequence, sens_pats):
    """
    Returns whether any sensitive pattern occurs in the input sequence
    """
    return ProbabilityDistribution(input_sequence).sum() > 0


def sanitise_seq_top_down(sens_pats: list, input_sequence: list, epsilon: float,
                          taxonomy_tree: Trees.TaxonomyTree) -> list:
    Helper.printer(f"--- BEGINNING EXECUTION OF TOP-DOWN ---\n"
                   f"Sensitive patterns: {sens_pats}\n"
                   f"User generated sequence: {input_sequence[:min(len(input_sequence), 10)]}...\n"
                   f"Privacy level/Average information leakage upper bound (epsilon): {epsilon}\n"
                   f"\tIf the value is low, lots of generalisation. If it's high, little generalisation.\n"
                   f"Taxonomy tree: \n{str(taxonomy_tree)}\n")
    # Return the original sequence if no sensitive patterns occur in it
    if not do_sens_pats_occur(input_sequence, sens_pats):
        return input_sequence

    # e.g. [Cookies, Beer, Milk, …]
    working_alphabet = Helper.Alphabet(taxonomy_tree.get_leaf_symbols())
    working_alphabet.sort_by_freq_in_sequence(input_sequence)

    # g_final = {Cookies:ALL, Beer:ALL, Milk: ALL, …}
    g_final = GeneralisationFunction(working_alphabet, default_generalisation=taxonomy_tree.get_root().get_symbol())
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
        Helper.printer(f"Working alphabet {working_alphabet}")
        Helper.printer(f"Current generalisation function", g_final)
        Helper.printer(f"... Iterating over working alphabet")
        for a_i in working_alphabet:
            Helper.printer(f"\ta_i {a_i}")
            if a_i in symbols_to_prune:
                Helper.printer(f"\ta_i {a_i} in symbols_to_prune")
                continue  # don't look at pruned symbols

            # if symbol already fully refined, discard from working_alphabet
            if g_final[a_i] == a_i:
                symbols_to_prune.append(a_i)
                continue

            # symbol on layer l_i + 1 on path towards a_i (more refined than on l_i)
            level_of_gen_a_i = g_final.get_generalisation_level(a_i)
            Helper.printer(f"\t\tcurrent level of generalisation {level_of_gen_a_i} for {a_i}")
            more_refined_generalisation_symbol = taxonomy_tree.find_leaf_node(a_i).get_path_from_root()[
                level_of_gen_a_i + 1].get_symbol()
            Helper.printer(f"\t\tmore refined symbol: {more_refined_generalisation_symbol}")

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
            Helper.printer(f"\t\tProposed new generalisation function {g_temp}")
            # If this g is worse than the previous, don't continue to the next 'if'
            # to update, just discard this g and move onto the next symbol
            Helper.printer(f"\t\tEvaluating utility loss of proposed generalisation function")
            utility_loss_of_g = Helper.utility_loss_by_generalising(input_sequence, g_temp,
                                                                    taxonomy_tree.get_cost_func())
            if utility_loss_of_g > util_loss:
                Helper.printer(f"\t\t\t{utility_loss_of_g} > {util_loss}'")
                Helper.printer(f"\t\tUtility loss worse, moving onto next a_i")
                continue  # TODO: does python 'continue' work in the same way as algo 1 pseudocode?

            else:
                Helper.printer(f"\t\t\t{utility_loss_of_g} <= {util_loss}'")
                Helper.printer(f"\t\t\tUtility loss same or better")
            Helper.printer(f"\t\tAssessing privacy")
            # if privacy is still satisfied -> update with new generalisation strategies g
            if Helper.inference_gain(input_sequence, sens_pats, g_temp) <= epsilon:
                Helper.printer(
                    f"\t\t\tInference gain {Helper.inference_gain(input_sequence, sens_pats, g_temp):.2f} <= {epsilon}\n"
                    f"\t\t\t(privacy satisfied)")
                Helper.printer(f"\t\t\t==> Current proposed refinements are {more_ref_gen_sym_leaves}")
                util_loss = utility_loss_of_g
                g_final_updated = copy.deepcopy(g_temp)
                symbols_refined_w_min_util_loss = [node.get_symbol() for node in
                                                   more_ref_gen_sym_leaves]
            else:  # privacy no longer satisfied -> prune tree using pruning criteria
                # don’t update generalisation strategies g with this new strategy
                # AND remove these leaves – they can’t be generalised further
                Helper.printer(
                    f"\t\t\tInference gain {Helper.inference_gain(input_sequence, sens_pats, g_temp):.2f} > {epsilon}\n"
                    f"\t\t\t(privacy not satisfied)\n"
                    f"\t\t\t==> pruning {[str(a_j) for a_j in more_ref_gen_sym_leaves]}")
                for a_j in more_ref_gen_sym_leaves:
                    symbols_to_prune.append(a_j.get_symbol())
        for a_i in symbols_to_prune:
            working_alphabet.remove(a_i)
        symbols_to_prune = []
        g_final = copy.deepcopy(g_final_updated)  # g' is g_final updated with best leaf(s) to refine
        if working_alphabet == previous_working_alphabet:
            Helper.printer("\tNo change made to working alphabet in this iteration")
        else:
            Helper.printer(f"\tworking_alphabet updated this iteration\n"
                           f"\t\tworking alphabet Old:\n"
                           f"\t\t\t{previous_working_alphabet}\n"
                           f"\t\tworking alphabet Updated:\n"
                           f"\t\t\t{working_alphabet}")
        if g_final == previous_g_final:
            Helper.printer("\tNo change made to g_final in this iteration")
        else:
            Helper.printer(f"\tg_final updated this iteration\n"
                           f"\t\tg_final Old:\n"
                           f"\t\t\t{previous_g_final}\n"
                           f"\t\tg_final Updated:\n"
                           f"\t\t\t{g_final}")
    Helper.printer(f"Final generalisation function given epsilon={epsilon}:\n\t{g_final}")
    return Helper.generalise_seq(input_sequence, g_final)
