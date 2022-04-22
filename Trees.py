import copy
from typing import Optional


class TreeNode:

    def __init__(self, name):
        self.__children = []
        self.__parent = None
        self.__depth = 0
        self.__symbol = name
        self.__height = 0

    def __repr__(self):
        return f"<{self.__symbol}>"

    def __eq__(self, other):
        return self.__symbol == other.__symbol

    @staticmethod
    def is_leaf(node):
        return len(node.get_children()) == 0

    @staticmethod
    def leaves(node) -> list:
        node = copy.deepcopy(node)
        if TreeNode.is_leaf(node):
            return [node]
        working_set = copy.deepcopy(node.get_children())
        leaves = []
        working_set_to_remove = []
        working_set_to_add = []
        # Run over working_set, each time replacing nodes with their leaves
        # and putting leaves into 'leaves'
        while len(working_set) > 0:
            # One iteration over working_set to replace nodes with children and move leaves out
            for n in working_set:
                if TreeNode.is_leaf(n):
                    # Take out leaves
                    leaves.append(n)
                    working_set_to_remove.append(n)
                else:
                    # replace n with children
                    working_set_to_add += n.get_children()
                    working_set_to_remove.append(n)
            # remove nodes that have children from working set
            for n in working_set_to_remove:
                working_set.remove(n)
            # add children of nodes into working set
            working_set += working_set_to_add
            working_set_to_add, working_set_to_remove = [], []
        return leaves

    def inc_height(self):
        self.__height += 1
        if self.__parent is not None:
            self.__parent.inc_height()

    # when a new node is added, all parents' heights increase by 1

    def __add_child(self, c):
        if type(c) is not TreeNode:
            raise ValueError("Can only add 'Tree' as child.")
        else:
            self.__children.append(c)
            c.set_parent(self)
            c.__depth = self.__depth + 1

    def add_children(self, *cs):
        for c in cs:
            self.__add_child(c)
        self.inc_height()

    def get_parent(self):
        return self.__parent

    def set_parent(self, n):
        self.__parent = n

    def get_depth(self):
        return self.__depth

    def get_height(self):
        return self.__height

    def get_children(self):
        return self.__children

    def get_symbol(self):
        return self.__symbol

    def get_path_from_root(self):
        path = [self]
        parent = self.__parent
        while parent is not None:
            path.append(parent)
            parent = parent.get_parent()
        return path[::-1]

    # returns list of nodes in root-to-node path
    # from level 0 (= root) to level of node
    # [ n0, n1, n2, ..., self ]


class TaxonomyTree:
    def __init__(self, root: TreeNode, cost_func: dict):
        self.__cost_func = cost_func
        if type(root) is not TreeNode:
            raise ValueError("Must be of type Tree")
        self.__root = root
        self.__leaves = TreeNode.leaves(self.__root)
        self.__node_list = TaxonomyTree.__enum_nodes(self.__root)

    @staticmethod
    def __enum_nodes(root_node: TreeNode):
        root_node = copy.deepcopy(root_node)
        working_nodes = [root_node]
        all_nodes = []
        to_add_to_working = []
        to_move_into_all_nodes = []
        while len(working_nodes) > 0:
            for node in working_nodes:
                to_move_into_all_nodes.append(node)
                if not TreeNode.is_leaf(node):
                    to_add_to_working += node.get_children()

            # move nodes that have been looked at into 'all nodes'
            for node in to_move_into_all_nodes:
                working_nodes.remove(node)
                all_nodes.append(node)
            # move nodes that need to be looked at next into 'working nodes'
            working_nodes += to_add_to_working

            to_add_to_working = []
            to_move_into_all_nodes = []
        return all_nodes

    def __repr__(self):
        return TaxonomyTree.__tree_to_str_rec(self.__root, 0)

    def get_cost_func(self):
        return self.__cost_func

    def get_root(self):
        return self.__root

    def find_leaf_node(self, symbol) -> Optional[TreeNode]:
        for n in self.__leaves:
            if n.get_symbol() == symbol:
                return n
        return None  # if it fails to find node with that symbol

    # Returns the nodes in the tree that match the given symbol
    def find_nodes(self, symbol, all_uniq_sym=True) -> list:
        matches = []
        for node in self.__node_list:
            node_sym = node.get_symbol()
            if node_sym == symbol:
                if not all_uniq_sym:
                    matches.append(node)
                else:
                    return [node]
        return matches

    def get_leaf_nodes(self):
        return self.__leaves

    def get_internal_nodes(self):
        return self.__node_list

    def get_leaf_symbols(self):
        return [leaf.get_symbol() for leaf in self.__leaves]

    @staticmethod
    def lowest_common_ancestor(node_a: TreeNode, node_b: TreeNode):
        path_a = [node.get_symbol() for node in node_a.get_path_from_root()[::-1]]
        path_b = [node.get_symbol() for node in node_b.get_path_from_root()[::-1]]
        for symbol in path_a:
            if symbol in path_b:
                return node_b.get_path_from_root()[path_b.index(symbol)]

        return None  # if no common ancestor

    @staticmethod
    def __tree_to_str_rec(t, depth):
        s = "{}|_{}".format(depth * "\t", t.get_symbol())
        s += "\n"
        if len(t.get_children()) == 0:
            return s
        else:
            for c in t.get_children():
                s += TaxonomyTree.__tree_to_str_rec(c, depth + 1)
        return s

    def print_tree(self):
        print(self)
