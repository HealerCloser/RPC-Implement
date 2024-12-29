import sys
sys.path.insert(0, 'src/main/structure')

import random
import math

from network import Network


class LoyalPoint2:
    
    def __init__(self, network):
        self.E = 0.0
        self.EPS = 2 * 1e-7
        self.node_list = []
        self.un_directed_adjacent_list = {}
        self.out_directed_adjacent_list = {}
        self.in_directed_adjacent_list = {}
        self.genes_weight = {}
        self.edges_weight = {}
        
        # Convert network's objects into lists
        for node in network.get_node_list():
            node_name = node.get_id()
            self.node_list.append(node_name)
            self.in_directed_adjacent_list[node_name] = []
            self.out_directed_adjacent_list[node_name] = []
            self.un_directed_adjacent_list[node_name] = []
            self.genes_weight[node_name] = node.get_weight()
            

        for edge in network.get_edge_list():
            source = edge.get_source()
            target = edge.get_target()
            direction = edge.is_directed()
            self.edges_weight[edge] = edge.get_weight()

            if direction:
                self.in_directed_adjacent_list[target].append(source)
                self.out_directed_adjacent_list[source].append(target)
            else:  # undirected edge
                self.un_directed_adjacent_list[source].append(target)
                self.un_directed_adjacent_list[target].append(source)

        # Initialize E (maximum out-degree sum)
        self.initialize()

    def initialize(self):
        max_out_deg_mixing = -1
        for node in self.node_list:
            sum_deg = len(self.out_directed_adjacent_list[node]) + len(self.un_directed_adjacent_list[node])
            if sum_deg > max_out_deg_mixing:
                max_out_deg_mixing = sum_deg
        self.E = 1.0 / max_out_deg_mixing

    def compute_loyal_nodes_of_leader(self, leader):
        
        loyal_nodes_of_leader = {}  # Tập các nút trung thành với leader
        against_leader = "###AgainstLeader###"  # Nút cạnh tranh với leader
        self.node_list.append(against_leader)

        # Tất cả các nuts ngoại trừ leader và against_leader
        normal_nodes = [node for node in self.node_list if node != leader and node != against_leader]

        # Tính độ trung thành của các nút với leader
        for node in normal_nodes:
            self.un_directed_adjacent_list[node].append(against_leader)     # Nối nút cạnh tranh với nút hiện tại
            result = self.compute_competitive(leader, against_leader)
            loyal_nodes_of_leader[node] = self.zero(result.get(node, 0.0))  # Lưu trữ độ trung thành của nút hiện tại
            self.un_directed_adjacent_list[node].remove(against_leader)     # Tách nút cạnh tranh khỏi nút hiện tại
        
        self.node_list.remove(against_leader)                               # Xóa nút cạnh tranh khỏi danh sách nút
        return loyal_nodes_of_leader                                        # trả kết quả cuối cùng

    
    def compute_competitive(self, leader, against_leader):
        max_iterations = 200                                                # Số lần lặp tối đa
        loyal_point = {node: self.genes_weight[node] for node in self.node_list if (node != leader and node != against_leader)}
        temp_loyal_point = {node: self.genes_weight[node] for node in self.node_list if (node != leader and node != against_leader)}

        loyal_point[leader] = 1.0                                           # Độ trung thành của leader mặc định là 1
        temp_loyal_point[leader] = 1.0
        loyal_point[against_leader] = -1.0                                  # Độ trung thành của nút cạnh tranh mặc định là -1
        temp_loyal_point[against_leader] = -1.0

        error = 1.0
        iter = 0

        while error > self.EPS and iter < max_iterations:
            error = 0.0

            for current_node in loyal_point.keys():
                if current_node == leader or current_node == against_leader:
                    continue

                # Kết hợp 2 danh sách kề của nút hiện tại
                in_un_node_list = self.in_directed_adjacent_list[current_node] + self.un_directed_adjacent_list[current_node]

                sum_val = 0.0
                for neighbor_node in in_un_node_list:
                    try: 
                        weight = self.edges_weight[(neighbor_node, current_node)]
                    except:
                        weight = 1.0
                    sum_val += weight * (loyal_point[neighbor_node] - loyal_point[current_node])

                new_loyal_point = loyal_point[current_node] + self.E * sum_val
                temp_loyal_point[current_node] = new_loyal_point
                error += abs(new_loyal_point - loyal_point[current_node])

            # Đổi giá trị loyal_point và temp_loyal_point
            loyal_point, temp_loyal_point = temp_loyal_point, loyal_point
            iter += 1

        return loyal_point

    @staticmethod
    def zero(value, epsilon= 2 * 1e-7):
        return 0.0 if abs(value) < epsilon else value

    @staticmethod
    def random_in_range(min_val, max_val):
        return random.uniform(min_val, max_val)


