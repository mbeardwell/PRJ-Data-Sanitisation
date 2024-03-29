from Sanitise import Trees
from Sanitise.Helper import Alphabet, CostFunction
from Sanitise.Trees import TaxonomyTree


class TestParams:
    def __init__(self):
        self.alphabet_leaves: Alphabet = None
        self.alphabet_general: Alphabet = None
        self.alphabet_extended: Alphabet = None
        self.cost_func: CostFunction = None
        self.tax_tree: TaxonomyTree = None

    def __repr__(self):
        repr = f"Leaves: {self.alphabet_leaves}\n"
        repr += f"Cost function: {self.cost_func}\n"
        repr += f"Taxonomy Tree: {self.tax_tree}"
        return repr

    def get_alphabet_ext(self):
        return self.alphabet_extended

    def get_alphabet_gen(self):
        return self.alphabet_general

    def get_alphabet_leaves(self):
        return self.alphabet_leaves

    def get_cost_func(self):
        return self.cost_func

    def get_tax_tree(self):
        return self.tax_tree


class MSNBC(TestParams):
    def __init__(self):
        super().__init__()
        self.alphabet_leaves = Alphabet([str(i) for i in range(1, 17 + 1)])
        self.alphabet_general = Alphabet(
            ["Summary", "Misc", "News", "Sport", "Industry", "Reviews", "Living", "Overview",
             "All-News", "Social", "Root"])
        self.alphabet_extended = Alphabet(self.alphabet_leaves.elements + self.alphabet_general.elements)
        self.cost_func = self.make_cost_func(self.alphabet_extended)
        self.tax_tree = self.make_tax_tree(self.cost_func)

    def make_cost_func(self, alphabet_extended):
        cost_func = CostFunction(alphabet_extended)

        for i in [1, 13]:
            cost_func[(str(i), "Summary")] = 0.2
        for i in [6, 7]:
            cost_func[(str(i), "Misc")] = 0.2
        for i in [2, 16]:
            cost_func[(str(i), "News")] = 0.2
        for i in [12, 17]:
            cost_func[(str(i), "Sport")] = 0.2
        for i in [3, 11]:
            cost_func[(str(i), "Industry")] = 0.2
        for i in [5, 14]:
            cost_func[(str(i), "Reviews")] = 0.2
        for i in [4, 8, 9, 10, 15]:
            cost_func[(str(i), "Living")] = 0.2

        for i in range(1, 17 + 1):
            for symbol in ["Overview", "All-News", "Social"]:
                cost_func[str(i), symbol] = 0.6

        cost_func.set_gen_to_root_cost("Root", 1)

        return cost_func

    def make_tax_tree(self, cost_func):
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

        return Trees.TaxonomyTree(root, cost_func)


class Groceries(TestParams):
    def __init__(self):
        super().__init__()
        self.alphabet_leaves = Alphabet(["Wine", "Beer", "Cookies", "Chips", "Milk", "Cheese"])
        self.alphabet_general = Alphabet(["Alcohol", "Snack", "Dairy", "ALL"])
        self.alphabet_extended = Alphabet(self.alphabet_leaves.elements + self.alphabet_general.elements)
        self.cost_func = self.make_cost_func(self.alphabet_extended)
        self.tax_tree = self.make_tax_tree(self.cost_func)

    def make_cost_func(self, alphabet_extended):
        cost_func = CostFunction(alphabet_extended)

        cost_func[("Wine", "Alcohol")] = 0.2
        cost_func[("Beer", "Alcohol")] = 0.5
        cost_func[("Cookies", "Snack")] = 0.8
        cost_func[("Chips", "Snack")] = 0.3
        cost_func[("Milk", "Dairy")] = 0.5
        cost_func[("Cheese", "Dairy")] = 0.5
        cost_func.set_gen_to_root_cost("ALL", 1)
        return cost_func

    def make_tax_tree(self, cost_func):
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
        return Trees.TaxonomyTree(root, cost_func)
