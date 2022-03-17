import csv


class MSNBCDataset:
    PATH = "msnbc-dataset/msnbc990928.seq"

    def __init__(self):
        self.sequences = self.load_msnbc_dataset()

    def get_sequences(self):
        return self.sequences

    def load_msnbc_dataset(self):
        sequences = []
        with open(MSNBCDataset.PATH, "r") as datafile:
            csv_reader = csv.reader(datafile, delimiter=" ")
            for line in csv_reader:
                if len(line) == 0:
                    continue
                if line[0] == "%":
                    continue
                line = line[:-1] if line[-1] == "" else line
                if "" in line or " " in line:
                    raise AssertionError("Failed to load file: format error.")
                sequences.append(line)
        if len(sequences) == 0:
            raise IOError("Failed to load file: format error.")

        # First line in sequences should be descriptors ['frontpage', 'news', ..., ]
        # so remove that
        sequences = sequences[1:]

        return sequences

    def print_stats(self, size=True, av_seq_len=True, seq_lengths=False):
        dataset = self.load_msnbc_dataset()

        if size:
            print(f"The dataset has {len(dataset):,} sequences.")

        # Calculate frequency distribution of sequence lengths
        # in the dataset
        distr = {}
        for seq in dataset:
            try:
                distr[len(seq)] += 1
            except KeyError:
                distr[len(seq)] = 1

        if seq_lengths:
            print("Here is the frequency distribution of the dataset")
            for i in range(min(distr.keys()), max(distr.keys())):
                if i in distr.keys():
                    print(f"Sequence length: {str(i).zfill(3)}   Frequency: {distr[i]:,}")

        if av_seq_len:
            mean_seq_len = 0
            for k in distr.keys():
                mean_seq_len += k * distr[k]
            mean_seq_len /= sum(distr.values())
            print(f"The average sequence length is {mean_seq_len:.2f}")
