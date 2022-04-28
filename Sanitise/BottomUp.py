import math

from Sanitise import Helper, Trees
from Sanitise.Helper import GeneralisationFunction
from Sanitise.Trees import TaxonomyTree


class Cluster:
    def __init__(self, centroid, samples=None):
        self.__centroid = centroid
        self.__samples = samples if samples is not None else []

    def get_samples(self):
        return self.__samples

    def get_centroid(self):
        return self.__centroid

    @staticmethod
    def generalisation_distance(centroid_a, centroid_b, taxonomy_tree, input_seq):
        dist = 0
        alphabet = Helper.alphabet_of(centroid_a, centroid_b)
        for symbol in alphabet:
            node_a, node_b = taxonomy_tree.find_node(centroid_a), taxonomy_tree.find_node(centroid_b)
            cost_func = taxonomy_tree.get_cost_func()
            least_common_ancestor = None  # TODO = LCA p1 p2 (a)
            generalisation_cost = cost_func[(symbol, least_common_ancestor)]
            dist += generalisation_cost * input_seq.count(symbol)

        return dist


class ClusterList:
    def __init__(self, tax_tree, input_seq):
        self.clusters = []
        self.tax_tree = tax_tree
        self.input_seq = input_seq

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

    def remove_clusters(self, *centroids):
        for centroid in centroids:
            self.__remove_cluster(self.get(centroid))

    @staticmethod
    def __centroid_distances(centroids, taxonomy_tree, input_seq):
        distances = {}
        for centroid_a in centroids:
            for centroid_b in centroids:
                if centroid_a != centroid_b:
                    distances[(centroid_a, centroid_b)] = Cluster.generalisation_distance(centroid_a,
                                                                                          centroid_b,
                                                                                          taxonomy_tree,
                                                                                          input_seq)
        return distances

    def closest_centroid_pair(self, centroids):
        cluster_dists = ClusterList.__centroid_distances(centroids, self.tax_tree, self.input_seq)
        smallest_dist = 0
        closest_pair = None
        for pair in cluster_dists.keys():
            dist = cluster_dists[pair]
            if dist <= smallest_dist:
                smallest_dist = dist
                closest_pair = pair
        return closest_pair

    # C[p3] = C(p1) Union C(p2)
    def merge_two_clusters(self, centroid_a, centroid_b, new_centroid):
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
    # line 2
    unique_symbols = Helper.alphabet_of(pattern_1, pattern_2)
    generalisation_funcs.append(GeneralisationFunction(unique_symbols))
    for sym in unique_symbols:
        generalisation_funcs[0][sym] = sym

    # lines 3-13
    for generalisation_func_iteration in range(1, pattern_len + 1):
        curr_gen_func = generalisation_funcs[generalisation_func_iteration]
        for pattern_index in range(1, pattern_len + 1):
            a_i, b_i = pattern_1[pattern_index], pattern_2[pattern_index]
            node_a = taxonomy_tree.find_leaf_node(curr_gen_func[a_i])
            node_b = taxonomy_tree.find_leaf_node(curr_gen_func[b_i])
            curr_gen_func[b_i] = TaxonomyTree.lowest_common_ancestor(node_a, node_b)
            curr_gen_func[a_i] = curr_gen_func[b_i]

        next_gen_func = GeneralisationFunction(unique_symbols)
        for sym in unique_symbols:
            next_gen_func[sym] = curr_gen_func[sym]
        generalisation_funcs.append(next_gen_func)

    # lines 14-15
    final_gen_func = generalisation_funcs[-1]  # last iteration of generalisation functions
    return Helper.generalise_seq(pattern_1, final_gen_func.generalisation_strategies)


def init_centroids(sensitive_patterns):
    # TODO comments - returns a set of centroids, one centroid
    #  is assigned to each sensitive pattern

    # TODO check if this is correct
    return [Cluster(sens_pat) for sens_pat in sensitive_patterns]


def sanitise_seq_bottom_up(sens_pats: list, input_sequence: list, epsilon: float,
                           taxonomy_tree: Trees.TaxonomyTree) -> list:
    #  lines 2-3
    clusters = ClusterList(taxonomy_tree, input_sequence)
    for centroid in init_centroids(sens_pats):
        clusters.append(centroid)
    alphabet = taxonomy_tree.get_leaf_symbols()
    root = taxonomy_tree.get_root().get_symbol()
    # TODO i don't think they are all generalised to the root
    # TODO what is g_final, what is a (i.e. for â_i = a_i)
    g_final = GeneralisationFunction(alphabet, default_generalisation=root)

    inf_gain = math.inf
    # repeat until the privacy level is met
    while not (inf_gain <= epsilon):
        #  lines 5-7
        if len(clusters) == 1:
            pass  # TODO greedily generalise the symbols in g_final

        # lines 8-10
        sens_pat_1, sens_pat_2 = clusters.closest_centroid_pair()
        clusters.remove_clusters(sens_pat_1, sens_pat_2)

        #  lines 11-13
        new_sens_pat = least_common_generalised_pattern(sens_pat_1, sens_pat_2, taxonomy_tree)
        clusters.merge_two_clusters(sens_pat_1, sens_pat_2, new_sens_pat)

        #  line 14
        # TODO update g_final according to LCGP(p1,p2) >> updates the centroids accordingly

        inf_gain = Helper.inference_gain(input_sequence, sens_pats, g_final)

    #  lines 16-17
    return Helper.generalise_seq(input_sequence, g_final)
