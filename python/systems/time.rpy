init -5 python in v1FNaSR:
    class Clock(FNaSRBase):
        def __init__(self, start_hour=0):
            # Храним время как число от 0 до 23 (где 0 - это полночь)
            self.__start_hour = start_hour
            self.hour = self.__start_hour % 24

        def set_hour(self, hour):
            """Устанавливает час (0-23)."""
            if 0 <= hour < 24:
                self.hour = hour % 24

        def next_hour(self):
            """Добавляет 1 час. Если было 23, станет 0."""
            self.hour += 1
            # Оператор % (остаток от деления) зацикливает время: 24 превращается в 0
            self.hour = self.hour % 24

        def get_time(self):
            """Возвращает строку в формате 12 AM/PM"""
            if self.hour == 0:
                return "12 AM"  # Полночь
            elif self.hour < 12:
                return "{} AM".format(self.hour)  # Утро
            elif self.hour == 12:
                return "12 PM"  # Полдень
            else:
                return "{} PM".format(self.hour - 12)  # День/Вечер (например, 13 -> 1 PM)

        def reset(self):
            self.hour = self.__start_hour % 24

    class GameTime(FNaSRBase):
        def __init__(self):
            self.total_hours = 0
            self.clock = Clock()
            self._time_tick = 0
            self._sleep_time = 1
            self._hour_time = Constants.DEFAULT_HOUR_TIME
            self._tn = {True: "AM", False: "PM"}
            self._tnb = True
            self._freeze = False
            self.__timers = []

        @property
        def is_freeze(self):
            return self._freeze

        @property
        def sleep_time(self):
            return self._sleep_time

        def freeze(self):
            with lock:
                self._freeze = True

        def unfreeze(self):
            with lock:
                self._freeze = False
            
        def sleep(self, sTime=None):
            if sTime is None:
                sTime = self._sleep_time
            time.sleep(sTime)

        def get_time(self):
            minutes = self.get_minutes()
            return "{:02d}:{:02d}".format(self.clock.hour, minutes)

        def get_minutes(self, step=1):
            minutes = self._time_tick * 60 / self._hour_time
            if step > 1:
                minutes = int(minutes // step * step)
            return int(minutes)

        def set_sleep_time(self, t):
            if t > 0:
                with lock:
                    self._sleep_time = t

        def set_hour_time(self, t):
            t = int(t)
            if t > 0:
                with lock:
                    self._hour_time = t

        def set_hour(self, t):
            with lock:
                self.clock.set_hour(t)

        def update(self):
            if self._freeze:
                self.sleep(0.1)
                return False

            self.sleep()
            self._time_tick += 1
            if self._time_tick >= self._hour_time:
                self.clock.next_hour()
                self.total_hours += 1
                self._time_tick = 0
            
            return True
                
        def reset(self):
            self._freeze = True

            self.clock.reset()
            self.total_hours = 0
            self._time_tick = 0
            self._sleep_time = 1
            self._hour_time = Constants.DEFAULT_HOUR_TIME
            self._tnb = True

            for t in self.__timers:
                t.stop()

            self.__timers = []
            self._freeze = False
            
        def timer(self, fn, sleep, *a, **k):
            _repeat = k.pop("Repeat", False)
            _ignore_freeze = k.pop("IgnoreFreeze", False)
            _ignore_game_loop = k.pop("IgnoreGameLoop", False)
            
            def wrapper(is_alive): # Если поток не остановлен is_alive вернет true, если был вызван метод stop вернется false
                time.sleep(sleep)
                while is_alive() or _ignore_game_loop:
                    if self._freeze and not _ignore_freeze:
                        time.sleep(0.1)
                        continue

                    fn(*a, **k)

                    if _repeat:
                        time.sleep(sleep)
                    else:
                        break

            t = renpy.store.v1FNaSRThread.ThreadGame(target=wrapper, name="V1FNaSRTimerThread_%s" % repr(fn)) # v1FNaSRThread.ThreadGame это поток с методом stop
            t.setDaemon(True)
            t.start()
            self.__timers.append(t)

            return t
