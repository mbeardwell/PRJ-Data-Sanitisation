class Distribution:
    def __init__(self):
        self.hash_to_val = {}
        self.hash_to_hashname = {}

    @staticmethod
    def __hash_sequence(seq):
        string = "["
        for symbol in seq:
            string += str(symbol) + ","
        string += "]"
        return string

    def __getitem__(self, item):
        hash = Distribution.__hash_sequence(item)
        return self.hash_to_val[hash]

    def __setitem__(self, key, value):
        hash = Distribution.__hash_sequence(key)
        self.hash_to_val[hash] = value
        self.hash_to_hashname[hash] = key

    def get_events(self):
        return list(self.hash_to_hashname.values())

    def get_max_val(self):
        return max(self.hash_to_val.values())


class FrequencyDistribution(Distribution):
    def __init__(self, patterns: list, sequence):
        super().__init__()
        for pattern in patterns:
            self[pattern] = freq_of_pattern_in_seq(pattern, sequence)

    def sum(self):
        return sum(self.hash_to_val.values())


class ProbabilityDistribution(Distribution):
    def __init__(self, patterns: list, sequence):
        super().__init__()
        freq_distr = FrequencyDistribution(patterns, sequence)
        is_empty = freq_distr.get_max_val() == 0
        for pattern in patterns:
            self[pattern] = freq_distr[pattern] / freq_distr.sum() if not is_empty else 0


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
