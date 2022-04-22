import math
import random
from unittest import TestCase

import Entropy
import Trees
from Datasets import MSNBCDataset
from Distributions import ProbabilityDistribution
from Sanitise import TopDown


def generate_new_inputs(alpha_leaves, seq_len_range=(10, 20), sens_pat_len_range=(2, 2), num_sens_pats_range=(2, 5)):
    # Generate some sensitive patterns
    NUM_SENS_PATTERNS = random.randint(num_sens_pats_range[0], num_sens_pats_range[1])
    MIN_LEN_SENS_PAT = sens_pat_len_range[0]
    MAX_LEN_SENS_PAT = sens_pat_len_range[1]
    LEN_SEQ = random.randint(seq_len_range[0], seq_len_range[1])
    SENSITIVE_PATTERNS = []
    USER_GENERATED_SEQ = []
    while True:
        for i in range(NUM_SENS_PATTERNS):
            pattern_len = random.randint(MIN_LEN_SENS_PAT, MAX_LEN_SENS_PAT)
            # Generate a random pattern and add it to the sensitive patterns list
            SENSITIVE_PATTERNS.append([random.choice(alpha_leaves) for j in range(pattern_len)])
            # Generate a random sequence for input
            USER_GENERATED_SEQ = [random.choice(alpha_leaves) for i in range(LEN_SEQ)]
        if TopDown.do_sens_pats_occur(USER_GENERATED_SEQ, SENSITIVE_PATTERNS):
            break
    return USER_GENERATED_SEQ, SENSITIVE_PATTERNS

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

    def test_sanitise_seq_top_down(self):
        def top_down(self, epsilon):
            return TopDown.sanitise_seq_top_down(self.sens_pats, self.input_seq, epsilon, self.TAXONOMY_TREE)

        for i in range(10):
            self.input_seq, self.sens_pats = generate_new_inputs(self.ALPHABET_LEAVES)
            sens_pat_prob_distr = ProbabilityDistribution(self.input_seq)
            print(TopDown.do_sens_pats_occur(self.input_seq, self.sens_pats))
            inference_gain_upper_bound = Entropy.shannon_entropy(sens_pat_prob_distr)
            if TopDown.do_sens_pats_occur(self.input_seq, self.sens_pats):
                most_general_seq = ["ALL"] * len(self.input_seq)
            else:
                most_general_seq = self.input_seq

            epsilon = 0
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, most_general_seq,
                             msg=f"Privacy level {epsilon} should return the most generalised sequence")

            epsilon = inference_gain_upper_bound + 0.001
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, self.input_seq,
                             msg=f"Privacy level {epsilon} should return the same sequence - no generalisation needed due to loose privacy requirements")

            epsilon = inference_gain_upper_bound / 2
            sanitised_sequence = top_down(self, epsilon)
            self.assertNotEqual(sanitised_sequence, self.input_seq,
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
        # Other parameters
        self.ALPHABET_LEAVES: list[str] = [str(i) for i in range(1, 17 + 1)]
        ALPHABET_GENERAL: list[str] = ["Summary", "Misc", "News", "Sport", "Industry", "Reviews", "Living", "Overview",
                                       "All-News", "Social", "Root"]
        ALPHABET_EXTENDED: list[str] = self.ALPHABET_LEAVES + ALPHABET_GENERAL

        # Create cost function
        self.COST_FUNC = {}
        for a_i in ALPHABET_EXTENDED:
            for a_j in ALPHABET_EXTENDED:
                self.COST_FUNC[(a_i, a_j)] = math.inf if a_i != a_j else 0

        for i in [1, 13]:
            self.COST_FUNC[(str(i), "Summary")] = 0.2
        for i in [6, 7]:
            self.COST_FUNC[(str(i), "Misc")] = 0.2
        for i in [2, 16]:
            self.COST_FUNC[(str(i), "News")] = 0.2
        for i in [12, 17]:
            self.COST_FUNC[(str(i), "Sport")] = 0.2
        for i in [3, 11]:
            self.COST_FUNC[(str(i), "Industry")] = 0.2
        for i in [5, 14]:
            self.COST_FUNC[(str(i), "Reviews")] = 0.2
        for i in [4, 8, 9, 10, 15]:
            self.COST_FUNC[(str(i), "Living")] = 0.2

        for i in range(1, 17 + 1):
            for symbol in ["Overview", "All-News", "Social"]:
                self.COST_FUNC[str(i), symbol] = 0.6

        for a_i in ALPHABET_EXTENDED:
            if a_i != "Root":
                self.COST_FUNC[(a_i, "Root")] = 1

        # Create taxonomy tree

        summary = Trees.TreeNode("Summary")
        for i in [1, 13]:
            summary.add_children(Trees.TreeNode(str(i)))

        misc = Trees.TreeNode("Misc")
        for i in [6, 7]:
            misc.add_children(Trees.TreeNode(str(i)))

        news = Trees.TreeNode("News")
        for i in [2, 16]:
            news.add_children(Trees.TreeNode(str(i)))

        sport = Trees.TreeNode("Sport")
        for i in [12, 17]:
            sport.add_children(Trees.TreeNode(str(i)))

        industry = Trees.TreeNode("Industry")
        for i in [3, 11]:
            industry.add_children(Trees.TreeNode(str(i)))

        reviews = Trees.TreeNode("Reviews")
        for i in [5, 14]:
            reviews.add_children(Trees.TreeNode(str(i)))

        living = Trees.TreeNode("Living")
        for i in [4, 8, 9, 10, 15]:
            living.add_children(Trees.TreeNode(str(i)))

        overview = Trees.TreeNode("Overview")
        overview.add_children(summary, misc)

        all_news = Trees.TreeNode("All-News")
        all_news.add_children(news, sport, industry, reviews)

        social = Trees.TreeNode("Social")
        social.add_children(reviews, living)

        root = Trees.TreeNode("Root")
        root.add_children(overview, all_news, social)

        self.TAXONOMY_TREE = Trees.TaxonomyTree(root, self.COST_FUNC)

        _, self.sequences = MSNBCDataset.load_msnbc_dataset()

    def test_sanitise_seq_top_down(self):
        for seq in self.sequences:
            if len(seq) == 20:
                break
        print()
        print("len(seq):\t", len(seq))
        print("seq:\t\t", seq)
        print("test:\t\t", TopDown.sanitise_seq_top_down([["1", "1"]], seq, 1, self.TAXONOMY_TREE))

        def top_down(self, epsilon):
            return TopDown.sanitise_seq_top_down(self.sens_pats, self.input_seq, epsilon, self.TAXONOMY_TREE)

        for i in range(10):
            self.input_seq, self.sens_pats = generate_new_inputs(self.ALPHABET_LEAVES)
            sens_pat_prob_distr = ProbabilityDistribution(self.input_seq)
            print(TopDown.do_sens_pats_occur(self.input_seq, self.sens_pats))
            inference_gain_upper_bound = Entropy.shannon_entropy(sens_pat_prob_distr)
            if TopDown.do_sens_pats_occur(self.input_seq, self.sens_pats):
                most_general_seq = ["Root"] * len(self.input_seq)
            else:
                most_general_seq = self.input_seq

            epsilon = 0
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, most_general_seq,
                             msg=f"Privacy level {epsilon} should return the most generalised sequence")

            epsilon = inference_gain_upper_bound + 0.001
            sanitised_sequence = top_down(self, epsilon)
            self.assertEqual(sanitised_sequence, self.input_seq,
                             msg=f"Privacy level {epsilon} should return the same sequence - no generalisation needed due to loose privacy requirements")

            epsilon = inference_gain_upper_bound / 2
            sanitised_sequence = top_down(self, epsilon)
            self.assertNotEqual(sanitised_sequence, self.input_seq,
                                msg=f"Privacy level {epsilon} should not be totally refined")
            self.assertNotEqual(sanitised_sequence, most_general_seq,
                                msg=f"Privacy level {epsilon} should not be totally generalised")


    def tearDown(self) -> None:
        pass  # TODO
