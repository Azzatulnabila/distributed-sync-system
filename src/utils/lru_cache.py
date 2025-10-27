# src/utils/lru_cache.py
from collections import OrderedDict

class SimpleLRU:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.od = OrderedDict()

    def get(self, key):
        if key in self.od:
            self.od.move_to_end(key)
            return self.od[key]
        return None

    def put(self, key, value):
        self.od[key] = value
        self.od.move_to_end(key)
        if len(self.od) > self.capacity:
            return self.od.popitem(last=False)  # evicted
        return None

    def invalidate(self, key):
        if key in self.od:
            del self.od[key]
