import heapq, time, random
import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

airports = {
    "DEL": (77.10, 28.55), "BOM": (72.87, 19.09), "BLR": (77.70, 13.19),
    "MAA": (80.17, 12.99), "CCU": (88.44, 22.65), "HYD": (78.43, 17.24), "AMD": (72.63, 23.07)
}
routes = [
    ("DEL", "BOM", 1150, 1.4), ("DEL", "AMD", 780, 1.1), ("DEL", "CCU", 1300, 1.2),
    ("DEL", "HYD", 1250, 1.2), ("BOM", "AMD", 440, 1.3), ("BOM", "BLR", 840, 1.3),
    ("BOM", "HYD", 620, 1.2),  ("BLR", "HYD", 500, 1.1), ("BLR", "MAA", 290, 1.1),
    ("HYD", "MAA", 520, 1.1),  ("HYD", "CCU", 1180, 1.2), ("MAA", "CCU", 1360, 1.3)
]

graph, edge_list = {node: [] for node in airports}, []
for u, v, d, c in routes:
    w = round(d * c, 2)
    graph[u].append((v, w)); graph[v].append((u, w))
    edge_list.append((w, u, v))

def run_prims(graph_data, start):
    mst, visited, heap = [], {start}, []
    for neighbor, w in graph_data[start]: heapq.heappush(heap, (w, start, neighbor))
    total = 0.0
    while heap and len(visited) < len(graph_data):
        w, u, v = heapq.heappop(heap)
        if v not in visited:
            visited.add(v); mst.append((u, v, w)); total += w
            for neighbor, next_w in graph_data[v]:
                if neighbor not in visited: heapq.heappush(heap, (next_w, v, neighbor))
    return mst, total

class DisjointSet:
    def __init__(self, nodes): self.parent = {n: n for n in nodes}
    def find(self, i):
        if self.parent[i] != i: self.parent[i] = self.find(self.parent[i])
        return self.parent[i]
    def union(self, u_root, v_root): self.parent[u_root] = v_root

def run_kruskals(nodes, edges):
    dsu, mst, total = DisjointSet(nodes), [], 0.0
    for w, u, v in sorted(edges, key=lambda x: x[0]):
        r_u, r_v = dsu.find(u), dsu.find(v)
        if r_u != r_v:
            dsu.union(r_u, r_v); mst.append((u, v, w)); total += w
            if len(mst) == len(nodes) - 1: break
    return mst, total

class ATCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATC Backbone Optimizer - Prim's vs Kruskal's (DAA)")
        self.root.geometry("1140x700")

        sidebar = ttk.Frame(root, padding=12)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(sidebar, text="Air Traffic Control", font=("Arial", 13, "bold")).pack(anchor=tk.W)
        ttk.Label(sidebar, text="DAA Comparative Optimization", font=("Arial", 9, "italic"), foreground="#555").pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(sidebar, text="Select Algorithm:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.algo_var = tk.StringVar(value="Prim's Algorithm")
        self.algo_dropdown = ttk.Combobox(sidebar, textvariable=self.algo_var, values=["Prim's Algorithm", "Kruskal's Algorithm"], state="readonly", width=20)
        self.algo_dropdown.pack(fill=tk.X, pady=(2, 6))
        self.algo_dropdown.bind("<<ComboboxSelected>>", lambda e: self.toggle_hub())

        self.lbl_hub = ttk.Label(sidebar, text="Prim's Starting Hub (Root):", font=("Arial", 9, "bold"))
        self.lbl_hub.pack(anchor=tk.W)
        self.hub_var = tk.StringVar(value="DEL")
        self.hub_dropdown = ttk.Combobox(sidebar, textvariable=self.hub_var, values=list(airports.keys()), state="readonly", width=20)
        self.hub_dropdown.pack(fill=tk.X, pady=(2, 8))

        tk.Button(sidebar, text="Run Route Optimization", command=self.optimize, bg="#007acc", fg="white", font=("Arial", 9, "bold"), relief="flat", pady=4).pack(fill=tk.X, pady=(0, 4))
        tk.Button(sidebar, text="Plot Complexity Benchmark", command=self.plot_scalability, bg="#27ae60", fg="white", font=("Arial", 9, "bold"), relief="flat", pady=4).pack(fill=tk.X, pady=(0, 8))

        ttk.Separator(sidebar).pack(fill=tk.X, pady=8)
        ttk.Label(sidebar, text="Performance Analytics", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.lbl_metrics = tk.Label(sidebar, text="", justify=tk.LEFT, font=("Consolas", 8), bg="white", relief="solid", bd=1, padx=6, pady=6, anchor="w")
        self.lbl_metrics.pack(fill=tk.X, pady=(4, 8))

        ttk.Label(sidebar, text="Greedy Edge Selection Order:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.txt_routes = tk.Text(sidebar, height=7, width=28, font=("Consolas", 8), bg="white", relief="solid", bd=1)
        self.txt_routes.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.optimize()

    def toggle_hub(self):
        self.hub_dropdown.config(state="disabled" if self.algo_var.get() == "Kruskal's Algorithm" else "readonly")

    def optimize(self):
        algo, hub = self.algo_var.get(), self.hub_var.get()
        t0 = time.perf_counter(); mst_p, cost_p = run_prims(graph, hub); time_p = (time.perf_counter() - t0) * 1000
        t1 = time.perf_counter(); mst_k, cost_k = run_kruskals(airports.keys(), edge_list); time_k = (time.perf_counter() - t1) * 1000

        mst, cost, runtime, complexity = (mst_p, cost_p, time_p, "O(E log V)") if algo == "Prim's Algorithm" else (mst_k, cost_k, time_k, "O(E log E)")
        orig_cost = sum(round(d * c, 2) for _, _, d, c in routes)
        drop = ((orig_cost - cost) / orig_cost) * 100

        self.lbl_metrics.config(text=(
            f"Active Algorithm  : {algo.split()[0]}\nComplexity        : {complexity}\nExecution Time    : {runtime:.4f} ms\n"
            f"-------------------------------\nSide-by-Side Compare:\n • Prim's Runtime : {time_p:.4f} ms\n • Kruskal Runtime: {time_k:.4f} ms\n"
            f"-------------------------------\nOriginal Cost     : {orig_cost:.1f}\nOptimized MST     : {cost:.1f}\nCongestion Drop   : {drop:.1f}%"
        ))
        self.txt_routes.delete("1.0", tk.END)
        for i, (u, v, w) in enumerate(mst, 1): self.txt_routes.insert(tk.END, f"{i}. {u} <-> {v} : {w}\n")

        self.ax.clear()
        self.ax.axis("off")
        G = nx.Graph()
        for u, v, d, c in routes: G.add_edge(u, v, weight=round(d * c, 2))

        mst_set = {tuple(sorted((u, v))) for u, v, _ in mst}
        non_mst = [e for e in G.edges() if tuple(sorted(e)) not in mst_set]
        mst_lines = [e for e in G.edges() if tuple(sorted(e)) in mst_set]

        nx.draw_networkx_edges(G, airports, edgelist=non_mst, ax=self.ax, edge_color="#e74c3c", style="dashed", width=1.5, alpha=0.4)
        nx.draw_networkx_edges(G, airports, edgelist=mst_lines, ax=self.ax, edge_color="#27ae60", width=3)
        node_colors = ["#f1c40f" if (n == hub and algo == "Prim's Algorithm") else "#2980b9" for n in G.nodes()]
        nx.draw_networkx_nodes(G, airports, ax=self.ax, node_size=850, node_color=node_colors, edgecolors="#1b4f72")
        nx.draw_networkx_labels(G, airports, ax=self.ax, font_color="black" if (algo == "Prim's Algorithm") else "white", font_size=8, font_weight="bold")
        nx.draw_networkx_edge_labels(G, airports, edge_labels=nx.get_edge_attributes(G, "weight"), ax=self.ax, font_size=7)

        self.ax.plot([], [], color="#27ae60", lw=3, label="MST Selected Backbone")
        self.ax.plot([], [], color="#e74c3c", ls="--", label="Secondary Corridors")
        if algo == "Prim's Algorithm": self.ax.scatter([], [], color="#f1c40f", s=80, label=f"Root Hub ({hub})")
        self.ax.legend(loc="lower right", framealpha=0.9, fontsize=8)
        self.ax.set_title(f"ATC Airspace Optimization via {algo}", fontsize=11, fontweight="bold")
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.02)
        self.canvas.draw()

    def plot_scalability(self):
        sizes = [10, 25, 50, 100, 200]
        p_times, k_times = [], []

        for n in sizes:
            nodes = [f"N{i}" for i in range(n)]
            syn_graph, syn_edges = {u: [] for u in nodes}, []
            for i in range(n - 1):
                w = round(random.uniform(100, 1500), 1)
                syn_graph[nodes[i]].append((nodes[i+1], w)); syn_graph[nodes[i+1]].append((nodes[i], w))
                syn_edges.append((w, nodes[i], nodes[i+1]))
            for _ in range(n * 2):
                u, v = random.sample(nodes, 2); w = round(random.uniform(100, 1500), 1)
                syn_graph[u].append((v, w)); syn_graph[v].append((u, w))
                syn_edges.append((w, u, v))

            t0 = time.perf_counter(); run_prims(syn_graph, nodes[0]); p_times.append((time.perf_counter() - t0) * 1000)
            t1 = time.perf_counter(); run_kruskals(nodes, syn_edges); k_times.append((time.perf_counter() - t1) * 1000)

        self.ax.clear()
        self.ax.axis("on")

        self.ax.plot(sizes, p_times, marker="o", markersize=6, color="#007acc", lw=2, label="Prim's: O(E log V)")
        self.ax.plot(sizes, k_times, marker="s", markersize=6, color="#e67e22", lw=2, label="Kruskal's: O(E log E)")

        self.ax.set_title("Empirical Scalability: Prim's vs Kruskal's Runtime Curve", fontsize=11, fontweight="bold", pad=12)
        self.ax.set_xlabel("Number of Airports / Vertices (V)", fontsize=9, fontweight="bold", labelpad=8)
        self.ax.set_ylabel("Execution Time (Milliseconds)", fontsize=9, fontweight="bold", labelpad=8)

        # Explicitly show numbers on X and Y axes
        self.ax.set_xticks(sizes)
        self.ax.set_xticklabels([str(s) for s in sizes], fontsize=8, visible=True)
        self.ax.tick_params(axis="both", which="both", bottom=True, left=True, labelbottom=True, labelleft=True, labelsize=8)

        self.ax.grid(True, linestyle="--", alpha=0.6)
        self.ax.legend(loc="upper left", framealpha=0.9, fontsize=8)

        # Generous margins so numbers are never clipped on high-DPI screens
        self.fig.subplots_adjust(left=0.18, right=0.94, top=0.90, bottom=0.20)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    ATCApp(root)
    root.mainloop()