import heapq

def find_shortest_and_safest_path(num_islands, edges, start, goal):
    # Create adjacency list
    graph = {i: [] for i in range(num_islands)}
    for (u, v, weight, risk) in edges:
        graph[u].append((v, weight, risk))
        graph[v].append((u, weight, risk))  # Assuming undirected graph

    # Priority queue
    pq = [(0, 0, start)]  # (total_cost, risk_cost, node)
    min_cost = {i: (float('inf'), float('inf')) for i in range(num_islands)}
    min_cost[start] = (0, 0)
    
    while pq:
        total_cost, risk_cost, u = heapq.heappop(pq)
        
        # If this is not the best known cost to u, skip
        if (total_cost, risk_cost) > min_cost[u]:
            continue

        # Process each neighbor
        for (v, weight, risk) in graph[u]:
            new_total_cost = total_cost + weight
            new_risk_cost = risk_cost + risk
            if (new_total_cost, new_risk_cost) < min_cost[v]:
                min_cost[v] = (new_total_cost, new_risk_cost)
                heapq.heappush(pq, (new_total_cost, new_risk_cost, v))
    
    # Result for goal
    return min_cost[goal]

def main():
    # Reading input from large_dataset.txt
    with open('large_dataset.txt', 'r') as file:
        lines = file.read().strip().split('\n')
    
    num_islands = int(lines[0])
    edges = []
    for line in lines[1:]:
        u, v, weight, risk = map(int, line.split())
        edges.append((u, v, weight, risk))
    
    # Define start and goal islands
    start, goal = 0, 74
    
    # Find shortest and safest path from island 0 to island 74
    result = find_shortest_and_safest_path(num_islands, edges, start, goal)
    print(f"Shortest and safest path from island {start} to island {goal}:")
    print(f"Total distance: {result[0]}")
    print(f"Total risk: {result[1]}")

if __name__ == "__main__":
    main()
