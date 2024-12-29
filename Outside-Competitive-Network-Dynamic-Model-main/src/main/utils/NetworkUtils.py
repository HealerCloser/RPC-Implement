import sys
sys.path.insert(0, 'src/main/structure')

from network import Network

def extract_network_in_directed_adjacent_list(network):
    nodes = network.get_node_list()
    nodes_name = [node.get_id() for node in nodes]
    edges = network.get_edge_list()
    
    node_id = {node: id for id, node in enumerate(nodes_name)}    # Đánh số các nút
    
    in_directed_adjacent_list = {index: [] for index in range(len(nodes))}
    
    n_adj_node = 0
    for edge in edges:
        if edge.is_directed():
            source_id = node_id[edge.get_source()]
            target_id = node_id[edge.get_target()]
            in_directed_adjacent_list[target_id].append(source_id)
            n_adj_node += 1
            
    adj_key = list(in_directed_adjacent_list.keys())
    if not adj_key:
        return [-1]
    
    n_nodes = len(adj_key)
    array_size = n_nodes + 1 + n_adj_node
    result = [0] * array_size
    
    adjacent_node_begin_index = 0
    adjacent_node_value_index = n_nodes + 1
    result[adjacent_node_begin_index] = adjacent_node_value_index

    for adjacent_node_begin_index in range(1, n_nodes + 1):
        current_nodes = in_directed_adjacent_list[adj_key[adjacent_node_begin_index - 1]]

        # Fill adjacent nodes
        for index in range(len(current_nodes)):
            result[adjacent_node_value_index + index] = current_nodes[index]

        adjacent_node_value_index += len(current_nodes)
        result[adjacent_node_begin_index] = adjacent_node_value_index

    return result

def extract_network_out_directed_adjacent_list(network):
    nodes = network.get_node_list()
    nodes_name = [node.get_id() for node in nodes]
    edges = network.get_edge_list()

    # Mapping node to an index
    node_id = {node: id for id, node in enumerate(nodes_name)}

    # Initialize out-directed adjacency list
    out_directed_adjacent_list = {index: [] for index in range(len(nodes))}

    n_adj_node = 0
    for edge in edges:
        if edge.is_directed():
            source_index = node_id[edge.get_source()]
            target_index = node_id[edge.get_target()]
            out_directed_adjacent_list[source_index].append(target_index)
            n_adj_node += 1

    # Prepare result array
    adj_key = list(out_directed_adjacent_list.keys())
    if not adj_key:
        return [-1]

    n_node = len(nodes)
    array_size = n_node + 1 + n_adj_node
    result = [0] * array_size

    adjacent_node_begin_index = 0
    adjacent_node_value_index = n_node + 1
    result[adjacent_node_begin_index] = adjacent_node_value_index

    for adjacent_node_begin_index in range(1, n_node + 1):
        current_nodes = out_directed_adjacent_list[adj_key[adjacent_node_begin_index - 1]]

        # Fill adjacent nodes
        for index in range(len(current_nodes)):
            result[adjacent_node_value_index + index] = current_nodes[index]

        adjacent_node_value_index += len(current_nodes)
        result[adjacent_node_begin_index] = adjacent_node_value_index

    return result


def extract_network_un_directed_adjacent_list(network):
    nodes = network.get_node_list()
    nodes_name = [node.get_id() for node in nodes]
    edges = network.get_edge_list()

    # Mapping node to an index
    node_indexes = {node: index for index, node in enumerate(nodes_name)}

    # Initialize undirected adjacency list
    un_directed_adjacent_list = {index: [] for index in range(len(nodes))}

    n_adj_node = 0
    for edge in edges:
        if not edge.is_directed():
            source_index = node_indexes[edge.get_source()]
            target_index = node_indexes[edge.get_target()]
            un_directed_adjacent_list[source_index].append(target_index)
            un_directed_adjacent_list[target_index].append(source_index)
            n_adj_node += 2  # Two entries for undirected edges

    # Prepare result array
    adj_key = list(un_directed_adjacent_list.keys())
    if not adj_key:
        return [-1]

    n_node = len(nodes)
    array_size = n_node + 1 + n_adj_node
    result = [0] * array_size

    adjacent_node_begin_index = 0
    adjacent_node_value_index = n_node + 1
    result[adjacent_node_begin_index] = adjacent_node_value_index

    for adjacent_node_begin_index in range(1, n_node + 1):
        current_nodes = un_directed_adjacent_list[adj_key[adjacent_node_begin_index - 1]]

        # Fill adjacent nodes
        for index in range(len(current_nodes)):
            result[adjacent_node_value_index + index] = current_nodes[index]

        adjacent_node_value_index += len(current_nodes)
        result[adjacent_node_begin_index] = adjacent_node_value_index

    return result
    
    