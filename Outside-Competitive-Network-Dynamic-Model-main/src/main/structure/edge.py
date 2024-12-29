class Edge:
    
    def __init__(self, source, target, directed=False, weight = 0.0):
        self.source = source
        self.target = target
        self.directed = directed
        self.weight = weight
        
    def get_source(self):
        return str(self.source)
    
    def get_target(self):
        return str(self.target)
    
    def is_directed(self):
        return self.directed
    
    def get_weight(self):
        return self.weight

    def __str__(self):
        direction = "->" if self.directed else "-"
        return f"{self.source.node_id} {direction} {self.target.node_id}"