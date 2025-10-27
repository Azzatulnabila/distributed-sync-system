from collections import OrderedDict
import time
import threading

class LRUCachePolicy:
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
        evicted = None
        if len(self.od) > self.capacity:
            evicted = self.od.popitem(last=False)
        return evicted

    def invalidate(self, key):
        if key in self.od:
            del self.od[key]

class SimpleMetrics:
    """
    Thread-safe metrics collector for hit/miss counters and basic timing.
    Designed to be lightweight and easy to dump as JSON.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self.counters = {"cache_hit":0, "cache_miss":0, "locks_acquired":0, "locks_failed":0}
        self.timers = {}

    def inc(self, name, n=1):
        with self._lock:
            self.counters[name] = self.counters.get(name,0) + n

    def timeit_start(self, label):
        with self._lock:
            self.timers[label] = time.time()

    def timeit_end(self, label):
        with self._lock:
            start = self.timers.pop(label, None)
            if start:
                return time.time() - start
            return None

    def snapshot(self):
        with self._lock:
            return {"counters": dict(self.counters), "timers": dict(self.timers)}
