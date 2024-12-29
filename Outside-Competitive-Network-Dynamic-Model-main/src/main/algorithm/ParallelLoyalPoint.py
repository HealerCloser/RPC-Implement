import sys
sys.path.insert(0, 'src/main/structure')
sys.path.insert(0, 'src/main/utils')

from network import Network
from NetworkUtils import *

import pyopencl as cl
import numpy as np
import random
import math

cl_code = """
__kernel void ComputeSums(__global const int* inDirectedAdjacentList,
                          __global const int* unDirectedAdjacentList,
                          __global float* loyalPoint,
                          __global float* sums,
                          int leader,
                          int againstLeader,
                          int targetNode,
                          int n)
{
    int currentNode = get_global_id(0);
    
    if(currentNode >= n || currentNode == leader || currentNode == againstLeader)
    {
        return;
    }
    
    float sum = 0.0f;

    int nInDirectedList = inDirectedAdjacentList[0] == -1 ? 0 : inDirectedAdjacentList[currentNode + 1] - inDirectedAdjacentList[currentNode];
    for (int index = 0; index < nInDirectedList; index++) {
        int neighbourNode = inDirectedAdjacentList[inDirectedAdjacentList[currentNode] + index];
        float weight = 1.0f;

        sum += weight * (loyalPoint[neighbourNode] - loyalPoint[currentNode]);
    }

    int nUnDirectedList = unDirectedAdjacentList[0] == -1 ? 0 : unDirectedAdjacentList[currentNode + 1] - unDirectedAdjacentList[currentNode];
    for (int index = 0; index < nUnDirectedList; index++) {
        int neighbourNode = unDirectedAdjacentList[unDirectedAdjacentList[currentNode] + index];
        float weight = 1.0f;

        sum += weight * (loyalPoint[neighbourNode] - loyalPoint[currentNode]);
    }
    
    if (currentNode == targetNode) {
        int neighbourNode = againstLeader;
        float weight = 1.0f;
        
        sum += weight * (loyalPoint[neighbourNode] - loyalPoint[currentNode]);
    }
    
    sums[currentNode] = sum;
}

__kernel void ComputeLoyalPoint(__global float* loyalPoint,
                                __global float* sums,
                                __global float* errors,
                                int leader,
                                int againstLeader,
                                float E,
                                int n)
{
    int currentNode = get_global_id(0);
    
    if(currentNode >= n || currentNode == leader || currentNode == againstLeader)
    {
        return;
    }
    
    float oldLoyalPoint = loyalPoint[currentNode];
    float newLoyalPoint = oldLoyalPoint + E * sums[currentNode];
    
    errors[currentNode] = fabs(newLoyalPoint - oldLoyalPoint) > errors[currentNode] ? fabs(newLoyalPoint - oldLoyalPoint) : errors[currentNode];
    loyalPoint[currentNode] = newLoyalPoint;
}
"""

class ParallelLoyalPoint:
    
    def __init__(self, network):
        self.network = network
        self.node_count = len(network.get_node_list())
        self.node_list = []
        
        self.un_directed_adjacent_dict = {}
        self.out_directed_adjacent_dict = {}
        self.in_directed_adjacent_dict = {}

        # Convert network into adjacency lists and node list
        for node in network.get_node_list():
            node_name = node.get_id()
            self.node_list.append(node_name)
            self.in_directed_adjacent_dict[node_name] = []
            self.out_directed_adjacent_dict[node_name] = []
            self.un_directed_adjacent_dict[node_name] = []

        for edge in network.get_edge_list():
            source = edge.get_source()
            target = edge.get_target()
            direction = edge.is_directed()

            if direction:
                self.in_directed_adjacent_dict[target].append(source)
                self.out_directed_adjacent_dict[source].append(target)
            else:  # undirected edge
                self.un_directed_adjacent_dict[source].append(target)
                self.un_directed_adjacent_dict[target].append(source)
        
        
        self.un_directed_adjacent_list = []
        self.out_directed_adjacent_list = []
        self.in_directed_adjacent_list = []
        
        self.loyalpoint = np.zeros(self.node_count + 1, dtype=np.float32)
        self.sums = np.zeros(self.node_count + 1, dtype=np.float32)
        self.errors = np.zeros(self.node_count + 1, dtype=np.float32)
        self.E = 0.0
        
        self.context, self.queue = self._setup_opencl()
        self.program = cl.Program(self.context, cl_code).build()

        
        # #Chuyển mạng thành danh sách kề và danh sách nút
        # for node in network.get_node_list():
        #     node_name = node.get_id()
        #     self.node_list.append(node_name)
        #     self.in_directed_adjacent_list[node_name] = []
        #     self.out_directed_adjacent_list[node_name] = []
        #     self.un_directed_adjacent_list[node_name] = []

        # for edge in network.get_edge_list():
        #     source = edge.get_source()
        #     target = edge.get_target()
        #     direction = edge.is_directed()

        #     if direction:       # Cạnh có hướng
        #         self.in_directed_adjacent_list[target].append(source)
        #         self.out_directed_adjacent_list[source].append(target)
        #     else:               # Cạnh không hướng
        #         self.un_directed_adjacent_list[source].append(target)
        #         self.un_directed_adjacent_list[target].append(source)

        # Bắt đầu khởi tạo E
        self.initialize()
        self._setup_opencl()

    def extract_network_adjacent_list(self, network):
        self.un_directed_adjacent_list = extract_network_un_directed_adjacent_list(network)
        self.out_directed_adjacent_list = extract_network_out_directed_adjacent_list(network)
        self.in_directed_adjacent_list = extract_network_in_directed_adjacent_list(network)
        
    def initialize(self):
        max_out_deg_mixing = 0
        for node in self.network.get_node_list():
            sum_deg = len(self.out_directed_adjacent_dict[node.get_id()]) + len(self.un_directed_adjacent_dict[node.get_id()])
            if sum_deg > max_out_deg_mixing:
                max_out_deg_mixing = sum_deg
        self.E = 1.0 / max_out_deg_mixing
            
    def _setup_opencl(self):
        platform = cl.get_platforms()[0]
        device = platform.get_devices()[0]
        context = cl.Context([device])
        queue = cl.CommandQueue(context)
        return context, queue
    
    def _init_buffer(self):
        self.in_directed_adjacent_list = np.array(self.in_directed_adjacent_list, dtype=np.int32)
        self.out_directed_adjacent_list = np.array(self.out_directed_adjacent_list, dtype=np.int32)
        self.un_directed_adjacent_list = np.array(self.un_directed_adjacent_list, dtype=np.int32)
        self.loyalpoint = np.array(self.loyalpoint, dtype=np.float32)
        self.sums = np.array(self.sums, dtype=np.float32)
        self.errors = np.array(self.errors, dtype=np.float32)
        
        mem_flags = cl.mem_flags
        self.buffer_in_directed = cl.Buffer(self.context, mem_flags.READ_ONLY | mem_flags.COPY_HOST_PTR, hostbuf=self.in_directed_adjacent_list)
        self.buffer_out_directed = cl.Buffer(self.context, mem_flags.READ_ONLY | mem_flags.COPY_HOST_PTR, hostbuf=self.out_directed_adjacent_list)
        self.buffer_un_directed = cl.Buffer(self.context, mem_flags.READ_ONLY | mem_flags.COPY_HOST_PTR, hostbuf=self.un_directed_adjacent_list)
        self.buffer_loyal_point = cl.Buffer(self.context, mem_flags.READ_WRITE | mem_flags.COPY_HOST_PTR, hostbuf=self.loyalpoint)
        self.buffer_sums = cl.Buffer(self.context, mem_flags.READ_WRITE | mem_flags.COPY_HOST_PTR, hostbuf=self.sums)
        self.buffer_errors = cl.Buffer(self.context, mem_flags.READ_WRITE | mem_flags.COPY_HOST_PTR, hostbuf=self.errors)

    def compute_loyal_nodes_of_leader(self, leader):
        loyal_nodes_of_leader = {}  # Tập các nút trung thành với leader
        against_leader = 'AgainstLeader' # Nút cạnh tranh với leader
        self.network.add_node(against_leader)  # Thêm nút cạnh tranh vào mạng
        against_leader_id = list(self.network.nodes.keys()).index(against_leader)  # Lấy id của nút cạnh tranh

        # Tất cả các nut ngoại trừ leader
        normal_nodes = [node for node in self.network.nodes.keys() if node != leader and node != against_leader]

        # Tính độ trung thành của các nút với leader
        for node in normal_nodes:
            self.network.add_edge(node, against_leader, False)
            self.extract_network_adjacent_list(self.network)                            # Trích xuất danh sách kề
            print(self.un_directed_adjacent_list)
            print(self.out_directed_adjacent_list)
            print(self.in_directed_adjacent_list)
            self._init_buffer()                                                         # Khởi tạo buffer
            result = self.compute_competitive_parallel(leader, against_leader_id)
            loyal_nodes_of_leader[node] = self.zero(result.get(node, 0.0))              # Lưu trữ độ trung thành của nút hiện tại
            self.network.remove_edge(node, against_leader)                                          # Tách nút cạnh tranh khỏi nút hiện tại
        self.network.remove_node(against_leader)                                        # Xóa nút cạnh tranh khỏi danh sách nút
        return loyal_nodes_of_leader                                                    # trả kết quả cuối cùng

    
    def compute_competitive_parallel(self, leader, against_leader):         # Phiên bản tính song song
        normal_nodes = [i for i in range(self.node_count) if i != leader and i != against_leader]
        against_leader = self.node_count
        
        self.loyalpoint[leader] = 1.0                                           # Độ trung thành của leader mặc định là 1
        # temp_loyal_point[leader] = 1.0
        self.loyalpoint[against_leader] = -1.0                                  # Độ trung thành của nút cạnh tranh mặc định là -1
        # temp_loyal_point[against_leader] = -1.0
        
        iter = 0
        max_iter = 200
        error = 1            
        eps = 2* 1e-7
        while error > eps and iter < max_iter:

            error = 0

            for normal_node in normal_nodes:
                # Tính tổng
                kernel_sums = self.program.ComputeSums
                kernel_sums.set_args(self.buffer_in_directed, self.buffer_un_directed, self.buffer_loyal_point, self.buffer_sums, np.int32(leader), np.int32(against_leader), np.int32(normal_node), np.int32(self.node_count + 1))
                cl.enqueue_nd_range_kernel(self.queue, kernel_sums, (self.node_count + 1,), None).wait()

                # Tính loyal Point
                kernel_loyal = self.program.ComputeLoyalPoint
                kernel_loyal.set_args(self.buffer_loyal_point, self.buffer_sums, self.buffer_errors, np.int32(leader), np.int32(against_leader), np.float32(self.E), np.int32(self.node_count + 1))
                cl.enqueue_nd_range_kernel(self.queue, kernel_loyal, (self.node_count + 1,), None).wait()

                # Lấy error từ thiết bị
                cl.enqueue_copy(self.queue, self.errors, self.buffer_errors).wait()
                error = np.max(self.errors)
                iter += 1
                
            # Lấy kết quả từ thiết bị
            cl.enqueue_copy(self.queue, self.loyalpoint, self.buffer_loyal_point).wait()

        return {normal_node: self.loyalpoint[normal_node] for normal_node in normal_nodes}
   

    @staticmethod
    def zero(value, epsilon= 2 * 1e-7):
        return 0.0 if abs(value) < epsilon else value

    @staticmethod
    def random_in_range(min_val, max_val):
        return random.uniform(min_val, max_val)