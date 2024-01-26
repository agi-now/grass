# Associative Graph Lookup

This library implements an efficient way to lookup what nodes are most associated to a group of nodes.
Associations are defined as a uni- or bidirectional weighted edges between nodes.

## Installation

## Usage

```python
from grass import AssociativeGraph

# Initiate the graph from the list of edges (start node, end node, association weight)
# By default the graph is bidirectional
graph = AssociativeGraph(edges=[
    ('A', 'B', 0.1),
    ('A', 'C', 0.2),
    ('A', 'D', 0.4),
    ('B', 'C', 0.3)
], bidirectional=True)

# Find what nodes are the most associated with node 'A'.
# Returns [('D', 0.4), ('C', 0.2), ('B', 0.1)].
# Format of the output is [(node, weight), ...]
graph.lookup('A')

# Find what nodes are the most associated with nodes 'A' and 'B'.
# Returns [('C', 0.5), ('D', 0.4)].
# Note that node 'C' has more priority now.
# This is because it's associated to both 'A' (0.2) and 'B' (0.3), 
# giving 0.5 weight in total.
graph.lookup('A', 'B')

# Weighted lookup
# Returns [('D', 0.8), ('C', 0.7)]
graph.lookup('A', 'B', weights=[2, 1])

# Modify the graph
graph.add_edge('A', 'E', 0.8)
graph.update_edge('A', 'B', 0.5)

# Let's see the changes reflected in the lookup
# Returns [('E', 0.8), ('C', 0.5), ('D', 0.4)]
graph.lookup('A', 'B')


# Save/load the graph to/from the disk in json format
graph.save_json('graph.json')
graph = AssociativeGraph.load_json('graph.json')

# Save/load the graph to/from the disk in Pickle format
graph.save_pkl('graph.pkl')
graph = AssociativeGraph.load_pkl('graph.pkl')
```
