import Trees


class GeneralisationFunction:
    def __init__(self, symbols, default_generalisation):
        self.default_generalisation = default_generalisation
        self.generalisation_strategies = {s: default_generalisation for s in symbols}
        self.generalisation_level = {s: 0 for s in symbols}

    def __repr__(self):
        default_strat = []
        not_default_strat = []
        for symbol in self.generalisation_strategies.keys():
            if self[symbol] == self.default_generalisation:
                default_strat.append(symbol)
            else:
                not_default_strat.append(symbol)
        maps = {symbol: self[symbol] for symbol in not_default_strat}
        if len(default_strat) > 0:
            maps["(all other symbols)"] = self.default_generalisation
        return str(maps)

    def __getitem__(self, symbol):
        return self.generalisation_strategies[symbol]

    def __setitem__(self, symbol, generalisation_symbol):
        self.generalisation_strategies[symbol] = generalisation_symbol

    def unique_strategies(self):
        return set(self.generalisation_strategies.values())

    def get_generalisation_level(self, symbol):
        return self.generalisation_level[symbol]

    def incr_generalisation_level(self, symbol):
        self.generalisation_level[symbol] += 1
