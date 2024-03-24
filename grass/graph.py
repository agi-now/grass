import bisect
from collections import defaultdict
import json
import pickle
from typing import Hashable, Optional


class AssociativeGraph:
    def __init__(self, edges: list[tuple[Hashable, Hashable, float]], bidirectional: bool = True):
        self.bidirectional = bidirectional
        self._decay_factor = 1
        
        self.connected_nodes = set()
        
        self.priority_queues = defaultdict(list)
        for start, end, weight in edges:
            self.set_weight(start, end, weight)
            
    def set_weight(self, start: Hashable, end: Hashable, weight: float):
        if (start, end) in self.connected_nodes:
            self._remove_edge(start, end)
            
        if weight == 0:
            return
        
        self.connected_nodes.add((start, end))
        
        # breakpoint()
        
        bisect.insort(self.priority_queues[start], (-weight / self._decay_factor, end))
        if self.bidirectional:
            bisect.insort(self.priority_queues[end], (-weight / self._decay_factor, start))
        
    def lookup(self, *nodes, weights: Optional[list[float]] = None, depth: int = 100):
        if weights is None:
            weights = [1] * len(nodes)
        
        result = defaultdict(float)
        for node, input_weight in zip(nodes, weights):
            for i in range(depth):
                try:
                    association_weight, associated_node = self.priority_queues[node][i]
                    result[associated_node] += -association_weight * input_weight
                except IndexError:
                    break
        
        return [
            (x[0], round(x[1] - x[1] * (1 - self._decay_factor), 3))
            for x in sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]
            if x[0] not in nodes
        ]
        
    def _remove_edge(self, start: Hashable, end: Hashable):
        self.priority_queues[start] = [
            (weight, node)
            for weight, node in self.priority_queues[start]
            if node != end
        ]
        if self.bidirectional:
            self.priority_queues[end] = [
                (weight, node)
                for weight, node in self.priority_queues[end]
                if node != start
            ]

    def remove_node(self, node: Hashable):
        """ Removes the node from the graph. 
        In order to remove the node we would need to iterate all priority queues,
        which is not efficient.
        Instead we can save all removed nodes in a set and ignore them during lookup.
        This is not a perfect solution, but it's way faster.
        """
        raise NotImplementedError()

    def _get_data_to_save(self):
        return {
            'decay_factor': self._decay_factor,
            'bidirectional': self.bidirectional,
            'priority_queues': self.priority_queues,
            'connected_nodes': list(self.connected_nodes),
        }

    def decay(self, factor: float):
        """ Positive factor increases the decay, negative decreases it. 
        This is a percentage-based decay - factor 0.1 means 10% decay.
        """
        self._decay_factor *= 1 - factor
        
    @classmethod
    def _from_saved_data(cls, data):
        instance = cls([], bidirectional=data['bidirectional'])
        instance.decay(data['decay_factor'])
        instance.priority_queues = data['priority_queues']
        instance.connected_nodes = set([
            (start, end) for start, end in data['connected_nodes']
        ])
        return instance

    def save_pkl(self, path: str):
        with open(path, 'wb+') as f:
            pickle.dump(self._get_data_to_save(), f)
    
    def save_json(self, path: str):
        with open(path, 'w+') as f:
            json.dump(self._get_data_to_save(), f)
            
    @classmethod
    def load_pkl(cls, path: str):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        return cls._from_saved_data(data)
    
    @classmethod
    def load_json(cls, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
        
        return cls._from_saved_data(data)
