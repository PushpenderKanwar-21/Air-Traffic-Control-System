# Air Traffic Control System
A student mini project for Design and Analysis of Algorithms (DAA) using Python, Tkinter, NetworkX, and Matplotlib.

## Features Included
1. Airspace Graph Model: 7 major Indian airport hubs (DEL, BOM, BLR, MAA, CCU, HYD, AMD) and 12 flight corridors.
2. Prim's Algorithm: Extracts the Minimum Spanning Tree (MST) using a Min-Heap priority queue in O(E log V) time.
3. Kruskal's Algorithm: Extracts the MST globally using Disjoint Set Union (DSU) in O(E log E) time.
4. Interactive Map Visualizer: Displays optimal green backbone corridors, red dashed bypassed routes, and root hub highlights.
5. Complexity Benchmark: Plots empirical scalability curves across synthetic networks from 10 to 200 vertices.

## Run Locally
Open the folder in VS Code, then run in the terminal:

pip install -r requirements.txt
python atc_final_project.py