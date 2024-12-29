
import sys

sys.path.insert(0, 'src/main/structure')

from network import Network
from LoyalPoint2 import LoyalPoint2
import time

# Record the start ti
start_time = time.time()

def load_network_from_file(edge_weight_file, gene_weight_file):
    network = Network()

    # Nạp dữ liệu trọng số gen
    with open(gene_weight_file, 'r') as gwf:
        for row in gwf:
            r = row.split()
            node_id = r[0]
            gene_weight = float(r[1])
            network.add_node(node_id, gene_weight)

    # Nạp dữ liệu trọng số cạnh
    with open(edge_weight_file, 'r') as ewf:
        next(ewf)
        for row in ewf:
            r = row.split()
            node_1 = r[0]
            node_2 = r[1]
            # if r[2] == '1':
            #     direction = True
            # else:
            #     direction = False
            edge_weight = float(r[2])
            network.add_node(node_1)
            network.add_node(node_2)
            network.add_edge(node_1, node_2, edge_weight)

    return network



edge_weight_file = 'E:/GR1/OCNDM/Outside-Competitive-Network-Dynamic-Model-main/src/main/resource/co_exp_network/TCGA-BRCA__co_expression__t_70_.tsv'
gene_weight_file = 'E:/GR1/OCNDM/Outside-Competitive-Network-Dynamic-Model-main/src/main/resource/differentially_expressed_genes/TCGA-BRCA_de_genes.tsv'
test = load_network_from_file(edge_weight_file, gene_weight_file)
lp = LoyalPoint2(test)
total_support = {node:0.0 for node in lp.node_list}
i = 0
for node in total_support.keys():
    if i == 20: break
    i += 1
    print(i)
    point = lp.compute_loyal_nodes_of_leader(node)
    print(point)
    sum_point = sum(point.values())
    print(sum_point)
    total_support[node] = sum_point
    print(total_support[node])
sorted_lp = sorted(total_support.items(), key=lambda x: x[1], reverse=True)

# In 5 giá trị lớn nhất
sorted_lp = [(key, value) for key, value in sorted_lp if value != 0]
top_5 = sorted_lp[:5]
for i, (key, value) in enumerate(top_5, start=1):
    print(f"Rank {i}: {key} = {value:.10f}")

# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

# Print the elapsed time in seconds
print(f"Code execution time: {elapsed_time:.6f} seconds")