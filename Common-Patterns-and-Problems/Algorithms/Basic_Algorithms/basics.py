import heapq
from collections import deque, defaultdict

# 1. Heap (Min-Heap)
def demo_heap():
    heap = []
    for val in [5, 3, 8, 1, 2]:
        heapq.heappush(heap, val)
    while heap:
        print("Heap pop:", heapq.heappop(heap))

# 2. Queue
def demo_queue():
    queue = deque()
    for val in [10, 20, 30]:
        queue.append(val)
    while queue:
        print("Queue pop:", queue.popleft())

# 3. Merge Sort
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    merged = []
    l = r = 0
    while l < len(left) and r < len(right):
        if left[l] < right[r]:
            merged.append(left[l])
            l += 1
        else:
            merged.append(right[r])
            r += 1
    merged.extend(left[l:])
    merged.extend(right[r:])
    return merged

# 4. Graph (Adjacency List)
class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, u, v):
        self.graph[u].append(v)

    def print_graph(self):
        for node in self.graph:
            print(f"{node} -> {self.graph[node]}")

# 5. Topological Sort (DFS-based)
def topological_sort(graph):
    visited = set()
    stack = []

    def dfs(v):
        visited.add(v)
        for neighbor in graph[v]:
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(v)

    for node in graph:
        if node not in visited:
            dfs(node)

    stack.reverse()
    return stack

# 6. Tree and Traversals
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def in_order(root):
    if root:
        in_order(root.left)
        print("In-order:", root.val)
        in_order(root.right)

def pre_order(root):
    if root:
        print("Pre-order:", root.val)
        pre_order(root.left)
        pre_order(root.right)

def post_order(root):
    if root:
        post_order(root.left)
        post_order(root.right)
        print("Post-order:", root.val)

# Demo
if __name__ == "__main__":
    print("Heap:")
    demo_heap()

    print("\nQueue:")
    demo_queue()

    print("\nMerge Sort:")
    arr = [5, 2, 9, 1, 6]
    print("Original:", arr)
    print("Sorted:", merge_sort(arr))

    print("\nGraph & Topological Sort:")
    g = Graph()
    g.add_edge("A", "C")
    g.add_edge("B", "C")
    g.add_edge("C", "D")
    g.add_edge("D", "E")
    g.print_graph()
    print("Topological Sort:", topological_sort(g.graph))

    print("\nTree Traversals:")
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)

    in_order(root)
    pre_order(root)
    post_order(root)
