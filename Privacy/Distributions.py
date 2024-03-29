from Sanitise.Helper import sequences_to_hash, sequence_to_hash


class JointDistribution:
    def __init__(self):
        self.hash_to_val = {}

    def __contains__(self, *items):
        return self.get(items) is not None

    def get(self, *sequences):
        hash = sequences_to_hash(sequences)
        # print("hash", hash)
        # print("hash_to_val", self.hash_to_val.keys())
        if hash in self.hash_to_val.keys():
            return self.hash_to_val[hash]
        else:
            return None

    def set(self, val, *sequences):
        hash = sequences_to_hash(sequences)
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
        self.hash_to_hashname[sequence_to_hash(key)] = key


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

        # enumerate all subsequences of 'sequence'
        possible_patterns = []
        for index_array in enum_all_subsequence_indices(len(sequence)):
            possible_patterns.append(get_subsequence(sequence, index_array))

        for pattern in possible_patterns:  # list(set(..)) returns all unique patterns
            if pattern in self:
                self[pattern] += 1
            else:
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
    def __init__(self, sequence1, sequence2):
        if len(sequence1) != len(sequence2):
            raise ValueError("Sequences must have the same length")

        super().__init__()
        print(f"x = JointFrequencyDistribution({sequence1},{sequence2})")

        for indices in enum_all_subsequence_indices(len(sequence1)):
            subsequence1 = get_subsequence(sequence1, indices)
            subsequence2 = get_subsequence(sequence2, indices)
            if super().__contains__(subsequence1, subsequence2):
                self.set(self.get(subsequence1, subsequence2) + 1, subsequence1, subsequence2)
            else:
                self.set(1, subsequence1, subsequence2)


class JointProbabilityDistribution(JointFrequencyDistribution):
    def __init__(self, sequence1, sequence2):
        super().__init__(sequence1, sequence2)
        total = self.sum()
        if total > 0:
            for hash in self.hash_to_val.keys():
                self.hash_to_val[hash] = self.hash_to_val[hash] / total


# returns all subsequence indices of a sequence
# e.g. for a sequence of length 3: [[0],[1],[2],[0,1],[0,2],[1,2],[0,1,2]]
# uses binary numbers where each number says whether each index is to be included in the output array
# i.e. '0b101' means index array [0,2]
def enum_all_subsequence_indices(array_len):
    subseq_indices = []
    counter = bin(1)  # don't start from 0 otherwise empty array [] will be included

    def incr_counter(c):
        return bin(int(c, 2) + 1)

    # e.g. '0b101' --> [0,2] or '0b111' --> [0,1,2]
    def bin_to_indices(num_bin: bin):
        indices = []
        num_bin = num_bin[2:]  # remove '0b' from beginning of string
        for i in range(len(num_bin)):
            digit = num_bin[i]
            if digit == '1':
                indices.append(i)
        return indices

    for i in range(2 ** array_len):
        subseq_indices.append(bin_to_indices(counter))
        counter = incr_counter(counter)

    return subseq_indices


# e.g. indices = [1,4,7] returns [sequence[1], sequence[4], sequence[7]]
def get_subsequence(sequence, indices):
    return [sequence[i] for i in indices]