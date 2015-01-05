from heapq import heappush, heappop

class EventQueue:
    def __init__(self):
        self.heap = []

    def put(self, event):
        event.n = len(self.heap) + 1
        heappush(self.heap, event)

    def get(self):
        item = heappop(self.heap)
        return item

    def __len__(self):
        return len(self.heap)

    @property
    def empty(self):
        return len(self.heap) <= 0
