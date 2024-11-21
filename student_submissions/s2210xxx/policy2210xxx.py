from policy import Policy
import heapq
import numpy as np  # Add this import

class Policy2352906(Policy):
    def __init__(self):
        self.best_solution = None
        self.best_value = float('-inf')
        
    def get_fitness(self, observation, info):
        list_prods = observation["products"]
        filled_ratio = info["filled_ratio"]
        total_area = filled_ratio * sum(prod['size'][0] * prod['size'][1] for prod in list_prods)
        occupied_area = 0

        for prod in list_prods:
            if prod["quantity"] > 0:
                occupied_area += prod["size"][0] * prod["size"][1] * prod["quantity"]

        wasted_area = total_area - occupied_area
        if wasted_area <= 0:
            return float('inf') 
        return 1 / wasted_area
    
    def get_best_solution(self, observation, info):
        list_prods = observation["products"]
        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = 0, 0
        stock = None
        for prod in list_prods:
            if prod["quantity"] > 0:
                prod_size = prod["size"]
                for i, s in enumerate(observation["stocks"]):
                    stock = s
                    stock_w, stock_h = self._get_stock_size_(stock)
                    prod_w, prod_h = prod_size
                    if stock_w < prod_w or stock_h < prod_h:
                        continue
                    for x in range(stock_w - prod_w + 1):
                        for y in range(stock_h - prod_h + 1):
                            if self._can_place_(stock, (x, y), prod_size):
                                stock_idx = i
                                pos_x, pos_y = x, y
                                break
                        if stock_idx != -1:
                            break
                    if stock_idx != -1:
                        break
                if stock_idx != -1:
                    break
        return stock_idx, pos_x, pos_y
    
    def get_action(self, observation, info):
        list_prods = observation["products"]

        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = 0, 0
        
        stock_idx, pos_x, pos_y = self.get_best_solution(observation, info)
        if stock_idx == -1:
            return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}
        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}
    
    
    
    
        
