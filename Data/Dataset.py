import csv
import os


class MSNBCDataset:
    PATH = "Data/Datasets/msnbc-dataset/msnbc990928.seq"

    def __init__(self, relative_path: str = None):
        if relative_path is None:
            absolute_path = MSNBCDataset.PATH
        else:
            absolute_path = f"{relative_path}/{MSNBCDataset.PATH}"

        sequences = []
        try:
            with open(absolute_path, "r") as datafile:
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
        except FileNotFoundError:
            msg = f"""
            The file containing the MSNBC dataset could not be located.
            Relative path given: {absolute_path}
            Current working dir: {os.getcwd()}
            """

            raise FileNotFoundError(msg)

        # First line in sequences should be descriptors ['frontpage', 'news', ..., ]
        self.descriptors, self.sequences = sequences[0], sequences[1:]

    def print_stats(self, size=True, av_seq_len=True, seq_lengths=False, top_10=True, seq_len_bin_width=10):
        if size:
            print(f"The dataset has {len(self.sequences):,} sequences.")

        # Calculate frequency distribution of sequence lengths
        # in the dataset
        distr = {}
        calc_bin = lambda index: (index // int(seq_len_bin_width)) * int(seq_len_bin_width)
        for seq in self.sequences:
            try:
                distr[calc_bin(len(seq))] += 1
            except KeyError:
                distr[calc_bin(len(seq))] = 1

        if seq_lengths:
            print("Here is the frequency distribution of the dataset")

            can_print_gap_next = False
            num_printed = 0
            for i in range(min(distr.keys()), max(distr.keys()), seq_len_bin_width):
                if num_printed >= 10:
                    print("[rest omitted]")
                    break
                if i in distr.keys():
                    can_print_gap_next = True
                    lower_bound = str(i).zfill(3)
                    upper_bound = str(i + seq_len_bin_width - 1).zfill(3)
                    print(f"Sequence length: {lower_bound}-{upper_bound}   Frequency: {distr[i]:,}")
                    num_printed += 1
                elif can_print_gap_next:
                    print("...")
                    can_print_gap_next = False

        if av_seq_len:
            total_seq_lens = 0
            for seq in self.sequences:
                total_seq_lens += len(seq)
            mean_seq_len = total_seq_lens / len(self.sequences)
            print(f"The average sequence length is {mean_seq_len:.2f}")
