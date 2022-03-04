import math
import random
from unittest import TestCase

import Entropy
import Trees
import main
from Distributions import ProbabilityDistribution


class TestMain(TestCase):
    def setUp(self) -> None:
        # Other parameters
        self.ALPHABET_LEAVES: list[str] = ["Wine", "Beer", "Cookies", "Chips", "Milk", "Cheese"]  # ie. leaves
        ALPHABET_GENERAL: list[str] = ["Alcohol", "Snack", "Dairy", "ALL"]  # i.e. Σ_g
        ALPHABET_EXTENDED: list[str] = self.ALPHABET_LEAVES + ALPHABET_GENERAL  # i.e. Σ_e

        # Create cost function
        self.COST_FUNC = {}
        for a_i in ALPHABET_EXTENDED:
            for a_j in ALPHABET_EXTENDED:
                self.COST_FUNC[(a_i, a_j)] = math.inf if a_i != a_j else 0

        self.COST_FUNC[("Wine", "Alcohol")] = 0.2
        self.COST_FUNC[("Beer", "Alcohol")] = 0.5
        self.COST_FUNC[("Cookies", "Snack")] = 0.8
        self.COST_FUNC[("Chips", "Snack")] = 0.3
        self.COST_FUNC[("Milk", "Dairy")] = 0.5
        self.COST_FUNC[("Cheese", "Dairy")] = 0.5
        for a_i in ALPHABET_EXTENDED:
            if a_i != "ALL":
                self.COST_FUNC[(a_i, "ALL")] = 1

        # Create taxonomy tree
        alcohol = Trees.TreeNode("Alcohol")
        wine = Trees.TreeNode("Wine")
        beer = Trees.TreeNode("Beer")
        alcohol.add_children(wine, beer)

        snack = Trees.TreeNode("Snack")
        cookies = Trees.TreeNode("Cookies")
        chips = Trees.TreeNode("Chips")
        snack.add_children(cookies, chips)

        dairy = Trees.TreeNode("Dairy")
        milk = Trees.TreeNode("Milk")
        cheese = Trees.TreeNode("Cheese")
        dairy.add_children(milk, cheese)

        root = Trees.TreeNode("ALL")
        root.add_children(alcohol, snack, dairy)
        self.TAXONOMY_TREE = Trees.TaxonomyTree(root, self.COST_FUNC)

    def __generate_new_inputs(self):
        # Generate some sensitive patterns
        NUM_SENS_PATTERNS = 2
        MIN_LEN_SENS_PAT = 2
        MAX_LEN_SENS_PAT = 2
        LEN_SEQ = 10
        SENSITIVE_PATTERNS = []
        USER_GENERATED_SEQ = []
        while True:
            for i in range(NUM_SENS_PATTERNS):
                pattern_len = random.randint(MIN_LEN_SENS_PAT, MAX_LEN_SENS_PAT)
                # Generate a random pattern and add it to the sensitive patterns list
                SENSITIVE_PATTERNS.append([random.choice(self.ALPHABET_LEAVES) for j in range(pattern_len)])
                # Generate a random sequence for input
                USER_GENERATED_SEQ = [random.choice(self.ALPHABET_LEAVES) for i in range(LEN_SEQ)]
            if main.do_sens_pats_occur(USER_GENERATED_SEQ, SENSITIVE_PATTERNS):
                break
        self.input_seq = USER_GENERATED_SEQ
        self.sens_pats = SENSITIVE_PATTERNS

    def test_sanitise_seq_top_down(self):
        def top_down(self, epsilon):
            return main.sanitise_seq_top_down(self.sens_pats, self.input_seq, epsilon, self.TAXONOMY_TREE)

        for i in range(10):
            self.__generate_new_inputs()
            sens_pat_prob_distr = ProbabilityDistribution(self.sens_pats, self.input_seq)
            print(main.do_sens_pats_occur(self.input_seq, self.sens_pats))
            inference_gain_upper_bound = Entropy.shannon_entropy(sens_pat_prob_distr)
            if main.do_sens_pats_occur(self.input_seq, self.sens_pats):
                most_general_seq = ["ALL"] * len(self.input_seq)
            else:
                most_general_seq = self.input_seq

            epsilon = 0
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, most_general_seq, msg=f"Privacy level {epsilon} should return the most generalised sequence")

            epsilon = inference_gain_upper_bound + 0.001
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, self.input_seq, msg=f"Privacy level {epsilon} should return the same sequence - no generalisation needed due to loose privacy requirements")

            epsilon = inference_gain_upper_bound / 2
            sanitised_sequence = top_down(self, epsilon)
            self.assertNotEqual(sanitised_sequence, self.input_seq, msg=f"Privacy level {epsilon} should not be totally refined")
            self.assertNotEqual(sanitised_sequence, most_general_seq, msg=f"Privacy level {epsilon} should not be totall generalised")

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
