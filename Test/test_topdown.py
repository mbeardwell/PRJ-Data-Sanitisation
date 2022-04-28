import random
from unittest import TestCase

from Data.Dataset import MSNBCDataset
from Privacy import Entropy
from Privacy.Distributions import ProbabilityDistribution
from Sanitise import TopDown
from Sanitise.Helper import Alphabet
from Test import Setup


class TestMain(TestCase):
    def setUp(self) -> None:
        self.__test_parameters = Setup.Groceries()
        self.__root_sym = self.__test_parameters.get_tax_tree().get_root().get_symbol()
        self.__sequences = generate_random_sequences(self.__test_parameters.get_alphabet_leaves(), 1)
        self.__sens_pats_set = [gen_rand_sens_pats(self.__test_parameters.get_alphabet_leaves(), seq) for seq in
                                self.__sequences]

    def test_sanitise_seq_top_down(self):
        def top_down(self, epsilon):
            return TopDown.sanitise_seq_top_down(sens_pats, self.input_seq, epsilon,
                                                 self.__test_parameters.get_tax_tree())

        for i in range(len(self.__sequences)):
            input_seq, sens_pats = self.__sequences[i], self.__sens_pats_set[i]

            sens_pat_prob_distr = ProbabilityDistribution(input_seq)
            print("Input seq:", input_seq)
            print("Prob distr: ", sens_pat_prob_distr)
            print(TopDown.do_sens_pats_occur(input_seq, sens_pats))
            inference_gain_upper_bound = Entropy.shannon_entropy(sens_pat_prob_distr)
            if TopDown.do_sens_pats_occur(input_seq, sens_pats):
                most_general_seq = [self.__root_sym] * len(input_seq)
            else:
                most_general_seq = input_seq

            epsilon = 0
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, most_general_seq,
                             msg=f"Privacy level {epsilon} should return the most generalised sequence")

            epsilon = inference_gain_upper_bound + 0.001
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, input_seq,
                             msg=f"Privacy level {epsilon} should return the same sequence - no generalisation needed due to loose privacy requirements")

            epsilon = inference_gain_upper_bound / 2
            sanitised_sequence = top_down(self, epsilon)
            self.assertNotEqual(sanitised_sequence, input_seq,
                                msg=f"Privacy level {epsilon} should not be totally refined")
            self.assertNotEqual(sanitised_sequence, most_general_seq,
                                msg=f"Privacy level {epsilon} should not be totally generalised")

        # print("---    Taxonomy tree    ---")
        # Trees.TaxonomyTree.print_tree(TAX_TREE)
        # def print_seq_short(seq):
        #     print([string[:3] for string in seq])
        # print(
        #     f"The user-generated event sequence has been sanitised satisfying ",
        #     f"ϵ-mutual information privacy, choosing ϵ = {EPSILON}.")
        # print_seq_short(USER_GEN_SEQUENCE)
        # print_seq_short(sanitised_sequence)

    # noinspection PyPep8Naming
    def tearDown(self) -> None:
        pass


class TestMSNBC(TestCase):
    def setUp(self) -> None:
        self.__test_parameters = Setup.MSNBC()
        self.__root_sym = self.__test_parameters.get_tax_tree().get_root().get_symbol()
        self.__sequences = MSNBCDataset(relative_path="..").sequences
        self.__sens_pats_set = [gen_rand_sens_pats(Alphabet(seq)) for seq in self.__sequences]

    def test_sanitise_seq_top_down(self):
        # for seq in self.__sequences:
        #     if len(seq) == 20:
        #         break
        # print()
        # print("len(seq):\t", len(seq))
        # print("seq:\t\t", seq)
        # print("Test:\t\t", TopDown.sanitise_seq_top_down([["1", "1"]], seq, 1, self.__test_parameters.get_tax_tree()))

        def top_down(self, epsilon):
            return TopDown.sanitise_seq_top_down(sens_pats, self.input_seq, epsilon,
                                                 self.__test_parameters.get_tax_tree())

        for i in range(len(self.__sequences)):
            input_seq, sens_pats = self.__sequences[i], self.__sens_pats_set[i]

            sens_pat_prob_distr = ProbabilityDistribution(input_seq)

            print(TopDown.do_sens_pats_occur(input_seq, sens_pats))
            inference_gain_upper_bound = Entropy.shannon_entropy(sens_pat_prob_distr)
            if TopDown.do_sens_pats_occur(input_seq, sens_pats):
                most_general_seq = [self.__root_sym] * len(input_seq)
            else:
                most_general_seq = input_seq

            epsilon = 0
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, most_general_seq,
                             msg=f"Privacy level {epsilon} should return the most generalised sequence")

            epsilon = inference_gain_upper_bound + 0.001
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, input_seq,
                             msg=f"Privacy level {epsilon} should return the same sequence - no generalisation needed due to loose privacy requirements")

            epsilon = inference_gain_upper_bound / 2
            sanitised_sequence = top_down(self, epsilon)
            self.assertNotEqual(sanitised_sequence, input_seq,
                                msg=f"Privacy level {epsilon} should not be totally refined")
            self.assertNotEqual(sanitised_sequence, most_general_seq,
                                msg=f"Privacy level {epsilon} should not be totally generalised")

    def tearDown(self) -> None:
        pass  # TODO


def gen_rand_seq(alpha_leaves: Alphabet, seq_len_range=(10, 20)):
    len_seq = random.randint(seq_len_range[0], seq_len_range[1])
    return [random.choice(alpha_leaves) for i in range(len_seq)]


def gen_rand_sens_pats(alpha_leaves, input_seq, sens_pat_len_range=(2, 2), num_sens_pats_range=(2, 5)):
    num_sens_patterns = random.randint(num_sens_pats_range[0], num_sens_pats_range[1])
    sensitive_patterns = []
    for i in range(num_sens_patterns):
        x = 0
        while True:
            sens_pat = gen_rand_seq(alpha_leaves, seq_len_range=sens_pat_len_range)
            print(f"for {i}, while {x}")
            print("\t", input_seq)
            print("\t", sens_pat)
            if TopDown.does_sens_pat_occur(input_seq, sens_pat):
                print("Sens pat occurs")
                break
            else:
                print("Sens pat NOT occurs")
            x += 1
        sensitive_patterns.append(sens_pat)
    return sensitive_patterns


# Set of random user generated sequences
def generate_random_sequences(alpha_leaves: Alphabet, num_sequences: int):
    return [gen_rand_seq(alpha_leaves) for i in range(num_sequences)]
