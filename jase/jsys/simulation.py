from .event_queue import EventQueue

class Sim:
    q = EventQueue()
    time = 0

    def __init__(self, time_scale=1, time_precision=1e-12):
        self.time_scale = time_scale
        self.time_precision = time_precision

    def reset(self):
        Sim.q = EventQueue()
        Sim.time = 0

    @classmethod
    def now(cls):
        return Sim.time

    def round(self, time):
        """Rounds the given time value to the desired time scale
        """
        return time

    def __add__(self, event):
        from .event import Event
        assert(isinstance(event, Event))
        self.add_event(event)

    def add_event(self, event):
        self.q.put(event)

    def run(self, until=float('inf')):
        print("running sim")
        while not self.q.empty:
            event = self.q.get()
            print("\nprocessing event", event,event.executed)
            self.time = event.time
            if not event.executed:
                event()
                event.executed = True
        print("Simulation stopped at time {}".format(self.time))

    def step(self, n=1):
        raise NotImplementedError

