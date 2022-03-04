import random
from unittest import TestCase

import main
from main import *


class TestMain(TestCase):
    def setUp(self) -> None:
        # Other parameters
        ALPHABET_LEAVES: list[str] = ["Wine", "Beer", "Cookies", "Chips", "Milk", "Cheese"]  # ie. leaves
        ALPHABET_GENERAL: list[str] = ["Alcohol", "Snack", "Dairy", "ALL"]  # i.e. Σ_g
        ALPHABET_EXTENDED: list[str] = ALPHABET_LEAVES + ALPHABET_GENERAL  # i.e. Σ_e

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
        alcohol = Treetools.TreeNode("Alcohol")
        wine = Treetools.TreeNode("Wine")
        beer = Treetools.TreeNode("Beer")
        alcohol.add_children(wine, beer)

        snack = Treetools.TreeNode("Snack")
        cookies = Treetools.TreeNode("Cookies")
        chips = Treetools.TreeNode("Chips")
        snack.add_children(cookies, chips)

        dairy = Treetools.TreeNode("Dairy")
        milk = Treetools.TreeNode("Milk")
        cheese = Treetools.TreeNode("Cheese")
        dairy.add_children(milk, cheese)

        root = Treetools.TreeNode("ALL")
        root.add_children(alcohol, snack, dairy)
        self.TAXONOMY_TREE = Treetools.TaxonomyTree(root, self.COST_FUNC)

        # Generate some sensitive patterns
        NUM_SENS_PATTERNS = 2
        MIN_LEN_SENS_PAT = 2
        MAX_LEN_SENS_PAT = 2
        self.LEN_SEQ = 10
        self.SENSITIVE_PATTERNS = []
        while True:
            for i in range(NUM_SENS_PATTERNS):
                pattern_len = random.randint(MIN_LEN_SENS_PAT, MAX_LEN_SENS_PAT)
                # Generate a random pattern and add it to the sensitive patterns list
                self.SENSITIVE_PATTERNS.append([random.choice(ALPHABET_LEAVES) for j in range(pattern_len)])
                # SENS_PATS = ["Beer", "Chips"], ["Wine", "Cheese"], ["Cookies", "Milk"]]

                # Generate a random sequence for input
                self.USER_GENERATED_SEQ = [random.choice(ALPHABET_LEAVES) for i in range(self.LEN_SEQ)]

                # self.USER_GENERATED_SEQ = ["Beer", "Chips", "Wine", "Beer", "Wine", "Chips", "Cheese", "Milk", "Cookies", "Cheese",
                #                      "Milk",
                #                      "Cheese"]
            if main.do_sens_pats_occur(self.USER_GENERATED_SEQ, self.SENSITIVE_PATTERNS):
                print("Created sensitive patterns and input sequence")
                break
            else:
                print("Patterns do not occur in input sequence, recreating sensitive patterns and input sequence")

    def test_sanitise_seq_top_down(self):
        epsilon = -1
        sanitised_sequence = sanitise_seq_top_down(self.SENSITIVE_PATTERNS, self.USER_GENERATED_SEQ, epsilon,
                                                   self.TAXONOMY_TREE)
        expected_ouput_seq = ["ALL"] * self.LEN_SEQ if main.do_sens_pats_occur(self.USER_GENERATED_SEQ,
                                                                               self.SENSITIVE_PATTERNS) else self.USER_GENERATED_SEQ
        self.assertEqual(sanitised_sequence, expected_ouput_seq)

        epsilon = math.inf
        sanitised_sequence = sanitise_seq_top_down(self.SENSITIVE_PATTERNS, self.USER_GENERATED_SEQ, epsilon,
                                                   self.TAXONOMY_TREE)
        self.assertEqual(sanitised_sequence, self.USER_GENERATED_SEQ)

        # print("---    Taxonomy tree    ---")
        # Treetools.TaxonomyTree.print_tree(TAX_TREE)
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
