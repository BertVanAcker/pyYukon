from machine import Timer

class timerFuction:
    def __init__(self, period_sec, callback, timer_id=-1, one_shot=False):
        """
        period_sec  : float interval in seconds
        callback    : function to call (runs in IRQ context!)
        timer_id    : hardware timer ID (use -1 for a virtual timer on ESP32)
        one_shot    : if True, fires only once; otherwise periodic
        """
        self._timer = Timer(timer_id)
        self._period_ms = int(period_sec * 1000)
        self._callback = callback
        self._mode = Timer.ONE_SHOT if one_shot else Timer.PERIODIC

    def start(self):
        # note: callback runs in IRQ; keep it fast and no allocations
        self._timer.init(period=self._period_ms, mode=self._mode,
                         callback=lambda t: self._callback())

    def stop(self):
        self._timer.deinit()