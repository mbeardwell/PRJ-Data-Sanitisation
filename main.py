import copy
import math

import Treetools


def sanitise_seq(seq: list, generalisation_strategies: dict) -> list:
    return [generalisation_strategies[symbol] for symbol in seq]


def sanitise_pats(sensitive_patterns, generalisation_strategies):
    return [sanitise_seq(pattern, generalisation_strategies) for pattern in sensitive_patterns]


# Returns the number of times a pattern (subsequence) appears in a sequence
def freq_of_pattern_in_seq(pattern: list, sequence: list):
    # This function is taken in its entirety from
    # https://www.geeksforgeeks.org/find-number-times-string-occurs-given-string/
    # TODO rewrite this as it is plagiarism as it is
    def count(a, b):
        m = len(a)
        n = len(b)

        # Create a table to store results of sub-problems
        lookup = [[0] * (n + 1) for i in range(m + 1)]

        # If first string is empty
        for i in range(n + 1):
            lookup[0][i] = 0

        # If second string is empty
        for i in range(m + 1):
            lookup[i][0] = 1

        # Fill lookup[][] in bottom up manner
        for i in range(1, m + 1):
            for j in range(1, n + 1):

                # If last characters are same,
                # we have two options -
                # 1. consider last characters of
                # both strings in solution
                # 2. ignore last character of first string
                if a[i - 1] == b[j - 1]:
                    lookup[i][j] = lookup[i - 1][j - 1] + lookup[i - 1][j]

                else:
                    # If last character are different, ignore
                    # last character of first string
                    lookup[i][j] = lookup[i - 1][j]

        return lookup[m][n]

    return count(sequence, pattern)


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

def freq_distr_of_patterns(patterns: list, sequence):
    return [freq_of_pattern_in_seq(pattern, sequence) for pattern in patterns]


def do_sens_pats_occur(user_generated_seq, sens_pats):
    """
    Returns whether any sensitive pattern occurs in the input sequence
    """
    return max(freq_distr_of_patterns(sens_pats, user_generated_seq)) > 0


def inference_gain(input_sequence, sensitive_patterns, generalisation_strategies):
    generalised_patterns = sanitise_pats(sensitive_patterns, generalisation_strategies)
    sanitised_sequence = sanitise_seq(input_sequence, generalisation_strategies)
    # Sensitive pattern frequency distribution and respective probability distribution
    # \mathbbm{S} in the notation of the paper
    sens_pat_freq_distr = freq_distr_of_patterns(sensitive_patterns, input_sequence)
    if sum(sens_pat_freq_distr) == 0:
        sens_pat_prob_distr = [0 for freq in sens_pat_freq_distr]
    else:
        sens_pat_prob_distr = [freq / sum(sens_pat_freq_distr) for freq in sens_pat_freq_distr]
    # Generalised pattern frequency distribution and respective probability distribution
    # \mathbbm{G} in the notation of the paper
    gen_pat_freq_distr = freq_distr_of_patterns(generalised_patterns, sanitised_sequence)
    if sum(gen_pat_freq_distr) == 0:
        gen_pat_prob_distr = [0 for freq in sens_pat_freq_distr]
    else:
        gen_pat_prob_distr = [freq / sum(gen_pat_freq_distr) for freq in gen_pat_freq_distr]

    mutual_information_sum = 0
    for sens_pat_index in range(len(sensitive_patterns)):
        for gen_pat_index in range(len(generalised_patterns)):
            prob_sens_pat = sens_pat_prob_distr[sens_pat_index]
            prob_gen_pat = gen_pat_prob_distr[gen_pat_index]
            # Swap following equivalent equations in case of zero probabilities which result in infinite/undefined sums
            if prob_sens_pat == 0 and not prob_gen_pat == 0:
                mutual_information_sum += prob_sens_pat * math.log(prob_gen_pat)
            elif not prob_gen_pat == 0 and prob_gen_pat == 0:
                mutual_information_sum += prob_gen_pat * math.log(prob_sens_pat)
            else:
                # inference gain about is zero if the sensitive patterns don't exist in the input pattern
                # TODO: is this the correct value to return?
                return 0
    return -mutual_information_sum


# Represented by UL(S,g,[c]) in pseudocode
def utility_loss_by_generalising(user_generated_sequence, g, c):
    sanitised_sequence = generalise_seq(user_generated_sequence, g)
    utility_loss_sum = 0
    for i in range(len(user_generated_sequence)):
        utility_loss_sum += c[(user_generated_sequence[i], sanitised_sequence[i])]
    return utility_loss_sum


# pseudocode would be S_hat(S,g)
# Returns sanitised sequence - S sanitised by g mappings
def generalise_seq(user_generated_sequence: list, g: dict) -> list:
    return [g[a_i] for a_i in user_generated_sequence]


# Returns an alphabet, sorted by the symbols' frequency of occurrence in sequence 'seq'
def sort_alphabet_by_freq(alphabet: list, seq: list) -> list:
    symbol_frequencies = {a: seq.count(a) for a in alphabet}
    alphabet_new = sorted(alphabet, key=lambda a: symbol_frequencies[a], reverse=True)  # descending order
    return alphabet_new


def sanitise_seq_top_down(sens_pats: list, user_generated_seq: list, epsilon: float,
                          taxonomy_tree: Treetools.TaxonomyTree) -> list:
    # Return the original sequence if no sensitive patterns occur in it
    if not do_sens_pats_occur(user_generated_seq, sens_pats):
        return user_generated_seq

    print(max(freq_distr_of_patterns(user_generated_seq,sens_pats))==0)
    working_alphabet = sort_alphabet_by_freq(taxonomy_tree.get_leaf_symbols(),
                                             user_generated_seq)  # e.g. [Cookies, Beer, Milk, …]
    g_f = {a_i: taxonomy_tree.get_root().get_symbol() for a_i in
           working_alphabet}  # g_f={Cookies:ALL, Beer:ALL, Milk: ALL, …}
    level_of_generalisation = {a_i: 0 for a_i in
                               working_alphabet}  # current level of gen. for a_i, initially 1 = root = ALL
    symbols_to_prune = []
    # At each iteration, look at all leaves. Choose the best one (+collateral) to refine based on
    # utility gained after refining.
    while len(working_alphabet) > 0:
        symbols_refined_w_min_util_loss = []
        g_new = copy.deepcopy(g_f)  # if no refinement possible, just keep most general everything=All (g_f)
        util_loss = math.inf
        # Choose a leaf, if it can be refined, what’s the utility loss after refining?
        # Update g_f with this best refinement option
        for a_i in working_alphabet:
            if a_i in symbols_to_prune:
                continue  # don't look at pruned symbols

            # symbol on layer l_i + 1 on path towards a_i (more refined than on l_i)
            l_i = copy.deepcopy(level_of_generalisation[a_i])
            more_refined_generalisation_symbol = taxonomy_tree.find_leaf_node(a_i).get_path_from_root()[
                l_i + 1].get_symbol()

            # get the (bottom level) leaves that have the
            # more refined generalisation symbol as an ancestor
            leaves_of_tree_of_more_refined_generalisation_symbol = Treetools.TreeNode.leaves(
                taxonomy_tree.find_nodes(more_refined_generalisation_symbol)[0])

            g = copy.deepcopy(g_f)
            # update leaves of subtree's g-mapping as well as current symbol
            for a_j in leaves_of_tree_of_more_refined_generalisation_symbol:
                g[a_j.get_symbol()] = more_refined_generalisation_symbol
                # if Treetools.TreeNode.is_leaf(a_j):
                #     symbols_to_prune.append(a_j.get_symbol())

            # If this g is worse than the previous, don't continue to the next 'if'
            # to update, just discard this g and move onto the next symbol
            utility_loss_of_g = utility_loss_by_generalising(user_generated_seq, g, taxonomy_tree.get_cost_func())
            if utility_loss_of_g > util_loss:
                continue  # TODO: does python 'continue' work in the same way as algo 1 pseudocode?

            # if privacy is still satisfied -> update with new generalisation strategies g
            if inference_gain(user_generated_seq, sens_pats, g) <= epsilon:
                util_loss = utility_loss_of_g
                g_new = copy.deepcopy(g)
                symbols_refined_w_min_util_loss = [node.get_symbol() for node in
                                                   leaves_of_tree_of_more_refined_generalisation_symbol]
            else:  # privacy no longer satisfied -> prune tree using pruning criteria
                # don’t update generalisation strategies g with this new strategy
                # AND remove these leaves – they can’t be generalised further
                for a_j in leaves_of_tree_of_more_refined_generalisation_symbol:
                    symbols_to_prune.append(a_j.get_symbol())
        for a_i in symbols_to_prune:
            level_of_generalisation[a_i] += 1
            working_alphabet.remove(a_i)
        symbols_to_prune = []
        g_f = copy.deepcopy(g_new)  # g' is g_f updated with best leaf(s) to refine
    return generalise_seq(user_generated_seq, g_f)
