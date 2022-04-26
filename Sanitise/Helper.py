from Privacy.Distributions import ProbabilityDistribution
from Sanitise.Generalisation import GeneralisationFunction


def printer(*args, SILENT=True):
    if not SILENT:
        print(*args)


class Alphabet:
    def __init__(self, elements: list = None):
        self.elements = elements

    # Returns an alphabet, sorted by the symbols' frequency of occurrence in sequence 'seq'
    def sort_by_freq_in_sequence(self, sequence):
        symbol_frequencies = {a: sequence.count(a) for a in self.elements}
        self.elements = sorted(self.elements, key=lambda a: symbol_frequencies[a], reverse=True)  # descending order

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

    def __eq__(self, x):
        return self.elements.__eq__(x)

    @staticmethod
    def alphabet_of(*some_lists) -> set:
        elements = set()
        for list_i in some_lists:
            elements = elements.union(set(list_i))
        return Alphabet(elements)


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

def do_sens_pats_occur(input_sequence, sens_pats):
    """
    Returns whether any sensitive pattern occurs in the input sequence
    """
    return ProbabilityDistribution(input_sequence).sum() > 0


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
