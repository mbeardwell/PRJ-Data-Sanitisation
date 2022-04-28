import math


def printer(*args, SILENT=True):
    if not SILENT:
        print(*args)


class Alphabet:
    def __init__(self, elements: list = None):
        self.elements = self.__unique(elements)

    # Returns an alphabet, sorted by the symbols' frequency of occurrence in sequence 'seq'
    def sort_by_freq_in_sequence(self, sequence):
        symbol_frequencies = {a: sequence.count(a) for a in self.elements}
        self.elements = sorted(self.elements, key=lambda a: symbol_frequencies[a], reverse=True)  # descending order

    def __unique(self, some_list):
        return list(set(some_list))

    def __iter__(self):
        return self.elements

    def __repr__(self):
        return self.elements.__repr__()

    def __len__(self):
        return self.elements.__len__()

    def remove(self, x):
        return self.elements.remove(x)

    def __contains__(self, x):
        return self.elements.__contains__(x)

    def __iter__(self):
        return self.elements.__iter__()

    def __eq__(self, x):
        return self.elements.__eq__(x)

    def __getitem__(self, x):
        return self.elements.__getitem__(x)

    @staticmethod
    def alphabet_of(*some_lists) -> set:
        elements = set()
        for list_i in some_lists:
            elements = elements.union(set(list_i))
        return Alphabet(elements)


class GeneralisationFunction:
    def __init__(self, alphabet: Alphabet, default_generalisation=None):
        self.default_generalisation = default_generalisation
        self.generalisation_strategies = {s: default_generalisation for s in alphabet}
        self.generalisation_level = {s: 0 for s in alphabet}

    def __repr__(self):
        default_strat = []
        not_default_strat = []
        for symbol in self.generalisation_strategies.keys():
            if self[symbol] == self.default_generalisation:
                default_strat.append(symbol)
            else:
                not_default_strat.append(symbol)
        maps = {symbol: self[symbol] for symbol in not_default_strat}
        if len(default_strat) > 0:
            maps["(all other symbols)"] = self.default_generalisation
        return str(maps)

    def __getitem__(self, symbol):
        return self.generalisation_strategies[symbol]

    def __setitem__(self, symbol, generalisation_symbol):
        self.generalisation_strategies[symbol] = generalisation_symbol

    def unique_strategies(self):
        return set(self.generalisation_strategies.values())

    def get_generalisation_level(self, symbol):
        return self.generalisation_level[symbol]

    def incr_generalisation_level(self, symbol):
        self.generalisation_level[symbol] += 1


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
#     unique_general_symbols = alphabet_of(sanitised_sequence)
#     used_general_symbols = []
#     for node in tax_tree.get_internal_nodes():
#         if node.get_symbol() in unique_general_symbols:
#             used_general_symbols.append(node.get_symbol())
#     return used_general_symbols

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


class CostFunction:
    def __init__(self, alphabet_extended: Alphabet):
        self.alphabet_extended = alphabet_extended
        self.map = {}
        self.root_sym = None

        for a_i in self.alphabet_extended:
            for a_j in self.alphabet_extended:
                self[(a_i, a_j)] = math.inf if a_i != a_j else 0

    def __repr__(self):
        inf_keys = []
        self_keys = []
        root_keys = []
        useful_keys = []
        for k in self.map.keys():
            if self[k] == math.inf:
                inf_keys.append(k)
            elif k[0] == k[1]:
                self_keys.append(k)
            elif self.root_sym is not None and k[1] == self.root_sym:
                root_keys.append(k[0])
            else:
                useful_keys.append(k)

        repr_dict = {k: self[k] for k in useful_keys}

        other = []
        if len(inf_keys) > 0:
            other.append("inf")
        if len(root_keys) > 0:
            other.append("root")
        if len(self_keys) > 0:
            other.append("self")

        if len(other) > 0:
            repr_dict["[other]"] = other

        return repr_dict.__repr__()

    def __getitem__(self, item):
        return self.map[item]

    def __setitem__(self, item, val):
        self.map[item] = val

    def set_gen_to_root_cost(self, root_sym, val):
        for a_i in self.alphabet_extended:
            if a_i != root_sym:
                self[(a_i, root_sym)] = val
        self.root_sym = root_sym
