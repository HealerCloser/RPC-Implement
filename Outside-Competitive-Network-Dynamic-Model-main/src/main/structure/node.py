class Node:
    
    def __init__(self, node_id, weight=0.0):
        self.node_id = node_id
        self.weight = weight

    def get_id(self):
        return str(self.node_id)
    
    def get_weight(self):
        return self.weight
    
    def __str__(self):
        return f'{str(self.node_id)}'