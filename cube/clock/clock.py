from datetime import datetime


class Clock:

    def __init__(self, k: int):
        self.real_start_time = datetime.now()
        self.k = k

    def time_transfer(self, now_time: datetime,
                      start_time: datetime) -> datetime:
        time_diff = now_time - self.real_start_time
        adjusted_diff = self.k * time_diff
        adjusted_time = start_time + adjusted_diff
        return adjusted_time
