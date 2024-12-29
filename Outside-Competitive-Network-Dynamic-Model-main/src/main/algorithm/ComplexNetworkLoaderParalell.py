import sys

sys.path.insert(0, 'src/main/structure')

from network import Network
from LoyalPoint import LoyalPoint
from ParallelLoyalPoint import ParallelLoyalPoint
import time

# Record the start time
start_time = time.time()

def load_network_from_file(file_path):
    network = Network()
    with open(file_path, 'r') as f:
        next(f)
        for row in f:
            r = row.split()
            node_1 = r[0]
            node_2 = r[1]
            if r[2] == '1':
                direction = True
            else:
                direction = False
            network.add_node(node_1)
            network.add_node(node_2)
            network.add_edge(node_1, node_2, direction)
    return network

file_path = 'src/main/resource/4-Human Gene Regulatory Network - Input.txt'
test = load_network_from_file(file_path)
lp = ParallelLoyalPoint(test)
total_support = {node:0.0 for node in lp.node_list}
i = 0
for node in range(len(total_support)):
    if i == 20: break
    i += 1
    print(i)
    point = lp.compute_loyal_nodes_of_leader(node)
    sum_point = sum(point.values())
    print(sum_point)
    total_support[node] = sum_point
    print(total_support[node])
sorted_lp = sorted(total_support.items(), key=lambda x: x[1], reverse=True)

# In 5 giá trị lớn nhất
top_5 = sorted_lp[:5]
for i, (key, value) in enumerate(top_5, start=1):
    print(f"Rank {i}: {key} = {value:.10f}")
    
# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

# Print the elapsed time in seconds
print(f"Code execution time: {elapsed_time:.6f} seconds")
