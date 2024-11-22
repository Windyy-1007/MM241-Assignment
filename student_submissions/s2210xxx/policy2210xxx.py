from policy import Policy
import heapq
import numpy as np  # Add this import
import pulp

class Policy2352906(Policy):
    # 2D cutting stock problem
    # Column generation algorithm
    def __init__(self):
        self.stock_types = []
        self.piece_dimensions = []
        self.demands = []
        self.best_solution = None
        self.best_value = float('-inf')
        self.population_size = 50
        self.population = []
        self.iterations = 0
        self.patterns = []
    
    def initialize_input(self, stock_types, piece_dimensions, demands):
        # Ensure stock_types is a list of tuples (width, height, cost)
        self.stock_types = [(stock.shape[1], stock.shape[0], cost) for stock, cost in stock_types]
        self.piece_dimensions = piece_dimensions
        self.demands = demands
        self.generate_initial_patterns()
    
    def generate_initial_patterns(self):
        self.patterns = []
        for stock in self.stock_types:
            if len(stock) != 3:
                print(f"Invalid stock tuple: {stock}")
                raise ValueError("Each stock tuple must have exactly three elements (width, height, cost).")
            stock_w, stock_h, _ = stock
            stock_patterns = []
            for prod_idx, (prod_w, prod_h) in enumerate(self.piece_dimensions):
                pattern = []
                for i in range(stock_w // prod_w):
                    for j in range(stock_h // prod_h):
                        if self._can_place_(stock, (i * prod_w, j * prod_h), (prod_w, prod_h)):
                            pattern.append({
                                "position": (i * prod_w, j * prod_h),
                                "quantity": 1,
                                "product_idx": prod_idx,
                                "stock_idx": self.stock_types.index(stock)
                            })
                if pattern:
                    stock_patterns.append(pattern)
            self.patterns.extend(stock_patterns)
    
    def solve_rmp(self):
        # Solve the restricted master problem (RMP)
        prob = pulp.LpProblem("RMP", pulp.LpMinimize)
        
        # Decision variables for each pattern
        x = [pulp.LpVariable(f"x_{i}", lowBound=0, cat=pulp.LpContinuous) for i in range(len(self.patterns))]
        
        # Objective function: minimize the total cost
        prob += pulp.lpSum([x[i] * self.stock_types[self.patterns[i][0]["stock_idx"]][2] for i in range(len(self.patterns))])
        
        # Constraints: satisfy the demand for each piece
        for j, demand in enumerate(self.demands):
            prob += pulp.lpSum([x[i] * sum(gene["quantity"] for gene in self.patterns[i] if gene["product_idx"] == j) for i in range(len(self.patterns))]) >= demand
        
        prob.solve()
        
        if prob.status == 1:
            self.best_solution = []
            for i, var in enumerate(prob.variables()):
                if var.varValue is not None and var.varValue > 0:
                    self.best_solution.append(self.patterns[i])
            self.best_value = pulp.value(prob.objective)
        else:
            print("No valid solution found.")
            self.best_solution = None
            self.best_value = float('-inf')
    
    def generate_new_columns(self):
        # Generate new columns (patterns) using a subproblem
        for stock in self.stock_types:
            if len(stock) != 3:
                print(f"Invalid stock tuple: {stock}")
                raise ValueError("Each stock tuple must have exactly three elements (width, height, cost).")
            stock_w, stock_h, _ = stock
            for prod_idx, (prod_w, prod_h) in enumerate(self.piece_dimensions):
                pattern = []
                for i in range(stock_w // prod_w):
                    for j in range(stock_h // prod_h):
                        if self._can_place_(stock, (i * prod_w, j * prod_h), (prod_w, prod_h)):
                            pattern.append({
                                "position": (i * prod_w, j * prod_h),
                                "quantity": 1,
                                "product_idx": prod_idx,
                                "stock_idx": self.stock_types.index(stock)
                            })
                if pattern:
                    self.patterns.append(pattern)
    
    def _can_place_(self, stock, position, prod_size):
        pos_x, pos_y = position
        prod_w, prod_h = prod_size

        if pos_x + prod_w > stock[0] or pos_y + prod_h > stock[1]:
            return False

        return True
    
    def get_action(self, observation, info):
        # Ensure observation["stocks"] is a list of tuples (2D array, cost)
        self.stock_types = [(stock, cost) for stock, cost in observation["stocks"]]
        self.piece_dimensions = observation["products"]
        # Solve the RMP
        self.solve_rmp()
        # Generate new columns
        self.generate_new_columns()
        # Return the best solution found
        if self.best_solution:
            best_gene = self.best_solution[self.iterations % len(self.best_solution)]
            prod_idx = best_gene.get("product_idx")
            prod_size = self.piece_dimensions[prod_idx] if prod_idx is not None else (0, 0)
            print(f"Best solution: {self.best_solution}, Best value: {self.best_value}")
            print("Action returned:", best_gene.get("stock_idx", -1), prod_size, best_gene["position"])
            self.iterations += 1
            return {
                "stock_idx": best_gene.get("stock_idx", -1),
                "size": prod_size,
                "position": best_gene["position"]
            }
        else:
            # Return a default action or continue evolving
            print("No valid solution found. Continuing evolution.")
            return {
                "stock_idx": -1,
                "size": (0, 0),
                "position": (0, 0)
            }

# Example usage:
# stock_types = [((W1, H1, cost1), cost1), ((W2, H2, cost2), cost2), ..., ((Wm, Hm, costm), costm)]
# piece_dimensions = [(w1, h1), (w2, h2), ..., (wn, hn)]
# demands = [d1, d2, ..., dn]
# policy = Policy2352906()
# policy.initialize_input(stock_types, piece_dimensions, demands)
# observation = {"stocks": stock_types, "products": piece_dimensions}
# info = {}
# action = policy.get_action(observation, info)








