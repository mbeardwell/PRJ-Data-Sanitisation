import copy
import math

import Entropy
import Trees
from Distributions import ProbabilityDistribution, JointProbabilityDistribution
from Generalisation import GeneralisationFunction
from Trees import TaxonomyTree

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
    # TODO comments - returns a set of centroids, one centroid
    #  is assigned to each sensitive pattern

    # TODO check if this is correct
    return [Cluster(sens_pat) for sens_pat in sensitive_patterns]


def alphabet_of_pattern(pattern):
    return list(set(pattern))


class Cluster:
    def __init__(self, centroid, samples=None):
        self.__centroid = centroid
        self.__samples = samples if samples is not None else []

    def get_samples(self):
        return self.__samples

    def get_centroid(self):
        return self.__centroid

    @staticmethod
    def generalisation_distance(cluster_a, cluster_b, taxonomy_tree):
        centroid_a = cluster_a.get_centroid()
        centroid_b = cluster_b.get_centroid()
        total = 0
        alphabet = alphabet_of_pattern(centroid_a) + alphabet_of_pattern(centroid_b)
        for symbol in alphabet:
            node_a, node_b = taxonomy_tree.find_node(centroid_a), taxonomy_tree.find_node(centroid_b)
            cost_func = taxonomy_tree.get_cost_func()
            generalisation_cost = cost_func(symbol, TaxonomyTree.lowest_common_ancestor(node_a, node_b, symbol))
            total += generalisation_cost * input_seq.count(symbol)
            pass  # TODO
        pass  # TODO


class ClusterList:
    def __init__(self):
        self.clusters = []

    def __len__(self):
        return len(self.clusters)

    def append(self, cluster):
        self.clusters.append(cluster)

    def get(self, centroid):
        for cluster in self.clusters:
            if cluster.__centroid == centroid:
                return cluster
        return None

    def __remove_cluster(self, cluster):
        self.clusters.remove(cluster)

    def remove(self, centroids):
        for centroid in centroids:
            self.__remove_cluster(self.get(centroid))

    def __centroid_distances(self, centroids, taxonomy_tree):
        distances = {}
        for centroid_a in centroids:
            for centroid_b in centroids:
                if centroid_a != centroid_b:
                    distances[(centroid_a, centroid_b)] = Cluster.generalisation_distance(centroid_a, centroid_b,
                                                                                          taxonomy_tree)
        return distances

    def closest_centroid_pair(self, centroids, taxonomy_tree):
        cluster_dists = self.__centroid_distances(centroids, taxonomy_tree)
        smallest_dist = 0
        closest_pair = None
        for pair in cluster_dists.keys():
            dist = cluster_dists[pair]
            if dist <= smallest_dist:
                smallest_dist = dist
                closest_pair = pair
        return closest_pair

    # C[p3] = C(p1) Union C(p2)
    def merge2clusters(self, centroid_a, centroid_b, new_centroid):
        cluster_a = self.get(centroid_a)
        cluster_b = self.get(centroid_b)
        if cluster_a is None:
            raise Exception("There is no cluster with centroid", centroid_a)
        if cluster_b is None:
            raise Exception("There is no cluster with centroid", centroid_b)

        merged_samples = cluster_a.get_samples() + cluster_b.get_samples()
        new_cluster = Cluster(new_centroid, samples=merged_samples)
        for cluster in [cluster_a, cluster_b]:
            self.__remove_cluster(cluster)
        self.append(new_cluster)


def least_common_generalised_pattern(pattern_1, pattern_2, taxonomy_tree):
    if len(pattern_1) != len(pattern_2):
        raise ValueError("Both patterns must have the same length")
    pattern_len = len(pattern_1)  # == len(pattern_2)
    generalisation_funcs = []

    # TODO - change comment below
    #  for each unique symbol a in p1, p2, set h0(a) = a
    unique_symbols = list(set(pattern_1).union(set(pattern_2)))
    generalisation_funcs.append(GeneralisationFunction(unique_symbols, ""))
    for sym in unique_symbols:
        generalisation_funcs[0][sym] = sym

    for gen_map_iter in range(1, pattern_len + 1):
        curr_gen_func = generalisation_funcs[gen_map_iter]
        for pattern_index in range(1, pattern_len + 1):
            a_i, b_i = pattern_1[pattern_index], pattern_2[pattern_index]
            node_a = taxonomy_tree.find_leaf_node(curr_gen_func[a_i])
            node_b = taxonomy_tree.find_leaf_node(curr_gen_func[b_i])
            curr_gen_func[b_i] = TaxonomyTree.lowest_common_ancestor(node_a, node_b)
            curr_gen_func[a_i] = curr_gen_func[b_i]

        next_gen_func = GeneralisationFunction(unique_symbols, "")
        for sym in unique_symbols:
            next_gen_func[sym] = curr_gen_func[sym]
        generalisation_funcs.append(next_gen_func)

    final_gen_func = generalisation_funcs[-1]
    return generalise_seq(pattern_1, final_gen_func.generalisation_strategies)


def sanitise_seq_bottom_up(sens_pats: list, input_sequence: list, epsilon: float,
                           taxonomy_tree: Trees.TaxonomyTree) -> list:
    #  lines 2-3
    clusters = ClusterList()
    for centroid in init_centroids(sens_pats):
        clusters.append(centroid)
    alphabet = taxonomy_tree.get_leaf_symbols()
    root = taxonomy_tree.get_root().get_symbol()
    # TODO i don't think they are all generalised to the root
    # TODO what is g_final, what is a (i.e. for â_i = a_i)
    g_final = GeneralisationFunction(alphabet, root)

    inf_gain = math.inf
    # repeat until the privacy level is met
    while not (inf_gain <= epsilon):
        #  lines 5-7
        if len(clusters) == 1:
            pass  # TODO greedily generalise the symbols in g_final

        # lines 8-10
        sens_pat_1, sens_pat_2 = clusters.closest_centroid_pair(taxonomy_tree)
        clusters.remove([sens_pat_1, sens_pat_2])

        #  lines 11-13
        new_sens_pat = least_common_generalised_pattern(sens_pat_1, sens_pat_2, taxonomy_tree)
        clusters.merge2clusters(sens_pat_1, sens_pat_2, new_sens_pat)

        #  line 14
        # TODO update g_final according to LCGP(p1,p2) >> updates the centroids accordingly

        inf_gain = inference_gain(input_sequence, sens_pats, g_final)

    #  lines 16-17
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
