import bisect
from collections import defaultdict
import json
import pickle
from typing import Hashable, Optional


class AssociativeGraph:
    def __init__(self, edges: list[tuple[Hashable, Hashable, float]], bidirectional: bool = True):
        self.bidirectional = bidirectional
        
        self.priority_queues = defaultdict(list)
        for start, end, weight in edges:
            self.add_edge(start, end, weight)
            
    def add_edge(self, start: Hashable, end: Hashable, weight: float):
        bisect.insort(self.priority_queues[start], (-weight, end))
        if self.bidirectional:
            bisect.insort(self.priority_queues[end], (-weight, start))
        
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
            (x[0], round(x[1], 3))
            for x in sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]
            if x[0] not in nodes
        ]
        
    def remove_edge(self, start: Hashable, end: Hashable):
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

    def update_edge(self, start: Hashable, end: Hashable, weight: float):
        self.remove_edge(start, end)
        if weight != 0:
            self.add_edge(start, end, weight)
    
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
            'bidirectional': self.bidirectional,
            'priority_queues': self.priority_queues
        }
        
    @classmethod
    def _from_saved_data(cls, data):
        instance = cls([], bidirectional=data['bidirectional'])
        instance.priority_queues = data['priority_queues']
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
