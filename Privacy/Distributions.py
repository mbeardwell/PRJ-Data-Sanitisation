class JointDistribution:
    def __init__(self):
        self.hash_to_val = {}

    @staticmethod
    def hash_sequence(seq):
        string = "["
        for symbol in seq:
            string += str(symbol) + ","
        string += "]"
        return string

    @staticmethod
    def hash_sequences(*sequences):
        hash = ""
        for seq in sequences:
            hash += JointDistribution.hash_sequence(seq)
            hash += "|"
        return hash

    def get(self, *sequences):
        hash = JointDistribution.hash_sequences(sequences)
        return self.hash_to_val[hash]

    def set(self, val, *sequences):
        hash = JointDistribution.hash_sequences(sequences)
        self.hash_to_val[hash] = val

    def values(self):
        return self.hash_to_val.values()

    def get_max_val(self):
        return max(self.values())

    def sum(self):
        return sum(self.values())


class Distribution(JointDistribution):
    def __init__(self):
        super().__init__()
        self.hash_to_hashname = {}

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(value, key)
        self.hash_to_hashname[JointDistribution.hash_sequence(key)] = key

    def __repr__(self):
        # out = "{"
        # for hash in self.hash_to_hashname.keys():
        #     out += str(self.hash_to_hashname[hash])
        #     out += ":"
        #     out += str(self.hash_to_val[hash])
        #     out += ","
        #
        # out = out[:-1] + "}"  # remove last comma and close list
        out = "["
        delimiter = ", "
        if len(self.values()) == 0:
            return "[Empty]"

        output_array_len = 0
        for val in self.values():
            if val != 0:  # ignore zero probabilities
                out += f"{val:.2f}" + delimiter
                output_array_len += 1

        if output_array_len > 0:
            return out[:-len(delimiter)] + "]"  # remove last comma and close list
        else:
            return "[Empty]"

    def get_events(self):
        return list(self.hash_to_hashname.values())


class FrequencyDistribution(Distribution):
    def __init__(self, sequence):
        super().__init__()
        possible_patterns = all_patterns(sequence)
        for pattern in possible_patterns:  # list(set(..)) returns all unique patterns
            try:
                self[pattern] += 1
            except KeyError:
                self[pattern] = 1

class ProbabilityDistribution(Distribution):
    # FIXME don't use the frequency distribution
    # P[p] = input_seq.count(p) / 2 ** len(input_seq)
    def __init__(self, sequence):
        super().__init__()
        freq_distr = FrequencyDistribution(sequence)
        is_empty = freq_distr.get_max_val() == 0
        for pattern in freq_distr.get_events():
            self[pattern] = freq_distr[pattern] / freq_distr.sum() if not is_empty else 0


class JointFrequencyDistribution(JointDistribution):
    def __init__(self, *sequences):
        super().__init__()
        possible_patterns = all_patterns_dual(*sequences[:2])
        for pattern in possible_patterns:
            try:
                self.set(self.get(pattern) + 1, pattern)
            except KeyError:
                self.set(0, pattern)


class JointProbabilityDistribution(JointFrequencyDistribution):
    def __init__(self, *sequences):
        super().__init__()
        total = self.sum()
        if total > 0:
            for hash in self.hash_to_val.keys():
                self.hash_to_val[hash] = self.hash_to_val[hash] / total


# TODO completely rewrite
# TODO https://www.geeksforgeeks.org/generating-all-possible-subsequences-using-recursion/
def all_patterns_rec_dual(input_sequence, generalised_sequence, i, input_seq_pats, output_seq_pats):
    if i == len(input_sequence):
        return [input_seq_pats]
    else:
        return all_patterns_rec(input_sequence, i + 1, input_seq_pats, output_seq_pats) + \
               all_patterns_rec(input_sequence, i + 1, input_seq_pats + [input_sequence[i]],
                                generalised_sequence + [generalised_sequence[i]])


def all_patterns_rec(input_sequence, i, input_seq_pats):
    if i == len(input_sequence):
        return [input_seq_pats]
    else:
        return all_patterns_rec(input_sequence, i + 1, input_seq_pats) + \
               all_patterns_rec(input_sequence, i + 1, input_seq_pats + [input_sequence[i]])


def all_patterns_dual(input_sequence, generalised_sequence):
    return all_patterns_rec_dual(input_sequence, generalised_sequence, 0, [], [])


def all_patterns(sequence):
    patterns = all_patterns_rec(sequence, 0, [])
    # # remove the empty pattern
    # if [] in patterns:
    #     patterns.remove([])
    return patterns
