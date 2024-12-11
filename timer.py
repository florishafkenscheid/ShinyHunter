import time

class Timer:
    def __init__(self):
        self.start = 0
        self.end = 0
        self.time_elapsed = 0

    def _start(self):
        self.start = time.time()
    
    def _end(self):
        self.end = time.time()
    
    def _diff(self):
        self.time_elapsed = self.end - self.start
        return self.time_elapsed
    
    def _calc_total(self, count):
        total_seconds = count * self.time_elapsed
        return f"{total_seconds / 60} minutes" if total_seconds / 60 < 60 else f"{total_seconds / 3600:.0f} hours and {total_seconds / 60 % 60:.0f} minutes" 
        # return minutes if minutes < 60, else return hours and remainder minutes