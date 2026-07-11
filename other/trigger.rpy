# -*- coding: utf-8 -*-
init 11 python in v1FNaSR:
    import threading
    import traceback

    # Фолбек для Py2
    try:
        monotime = time.monotonic
    except:
        from time import time as monotime


    class Trigger(FNaSRBase):
        """
        Базовый объект триггера.
        """
        __slots__ = (
            "condition_fn", "action_fn", "interval", "lifetime",
            "created_time", "last_check", "dead_fn", "repeat", "name"
        )

        def __init__(self, condition_fn, action_fn,
                    interval, lifetime,
                    dead_fn, repeat):

            self.condition_fn = condition_fn
            self.action_fn = action_fn
            self.interval = interval
            self.lifetime = lifetime
            self.dead_fn = dead_fn
            self.repeat = repeat

            # Время создания будет установлено менеджером
            self.created_time = 0.0
            self.last_check = 0.0

            self.name = action_fn.__name__


    class TriggerManager(FNaSRBase):
        """
        Управляет всеми триггерами в отдельном потоке.
        Использует масштабируемое время для синхронизации с главным циклом.
        """

        def __init__(self, default_sleep=0.05, continue_condition=None):
            # частота обновления управляющего потока
            self.default_sleep = default_sleep

            # список активных триггеров
            self._triggers = []

            # поток менеджера
            self._thread = None
            self._lock = threading.Lock()

            self._running = False
            
            # условие продолжения обработки триггеров
            self._continue_condition = continue_condition
            
            # === МАСШТАБИРУЕМОЕ ВРЕМЯ ===
            # Накопленное игровое время (в секундах)
            self._scaled_time = 0.0
            
            # Последнее реальное время обновления
            self._last_real_time = monotime()
            
            # Функция для получения текущего time_scale (по умолчанию 1.0)
            # Должна возвращать float > 0
            self._time_scale_fn = None

        def start(self):
            """
            Запустить управляющий поток.
            """
            if self._running:
                return

            self._running = True
            self._last_real_time = monotime()
            self._thread = threading.Thread(target=self._loop, name="V1FNaSRTriggerManager")
            self._thread.setDaemon(True)
            self._thread.start()

        def stop(self):
            """
            Остановить управляющий поток.
            """
            self._running = False

        def set_continue_condition(self, condition_fn):
            """
            Устанавливает условие продолжения обработки триггеров.
            """
            self._continue_condition = condition_fn

        def remove_continue_condition(self):
            """
            Удаляет условие продолжения.
            """
            self._continue_condition = None

        def set_time_scale_function(self, time_scale_fn):
            """
            Устанавливает функцию для получения масштаба времени.
            
            Пример:
                def get_time_scale():
                    return 1.0 / sleep_time  # если sleep_time=0.1, то scale=10.0
                
                TriggerSystem.set_time_scale_function(get_time_scale)
            
            Или проще:
                def get_time_scale():
                    return sleep_time  # 0.1 = медленнее, 1.0 = нормально
                
                TriggerSystem.set_time_scale_function(get_time_scale)
            """
            self._time_scale_fn = time_scale_fn

        def _get_time_scale(self):
            """
            Получает текущий масштаб времени.
            """
            if self._time_scale_fn is None:
                return 1.0
            
            try:
                scale = self._time_scale_fn()
                # Защита от некорректных значений
                if scale <= 0:
                    return 1.0
                return float(scale)
            except:
                log("Error in time_scale_fn: {}".format(traceback.format_exc()))
                return 1.0

        def _update_scaled_time(self):
            """
            Обновляет масштабируемое время на основе реального времени и time_scale.
            """
            now_real = monotime()
            delta_real = now_real - self._last_real_time
            self._last_real_time = now_real
            
            # Получаем текущий масштаб времени
            time_scale = self._get_time_scale()
            
            # Увеличиваем игровое время с учетом масштаба
            self._scaled_time += delta_real * time_scale
            
            return self._scaled_time

        # ------------------------------
        # API создания триггера
        # ------------------------------
        def add_trigger(self,
                        condition_fn,
                        action_fn,
                        interval=0.5,
                        lifetime=None,
                        dead_fn=None,
                        repeat=False):
            """
            Добавляет новый триггер.
            repeat=False → одноразовый
            repeat=True  → многоразовый
            """
            if interval is None or interval <= 0:
                interval = 0.01

            tr = Trigger(condition_fn, action_fn,
                        interval, lifetime, dead_fn, repeat)

            with self._lock:
                # Устанавливаем время создания в масштабируемом времени
                tr.created_time = self._scaled_time
                tr.last_check = self._scaled_time
                self._triggers.append(tr)

            return tr

        def remove_trigger(self, trigger):
            """
            Удаляет триггер.
            """
            with self._lock:
                if trigger in self._triggers:
                    self._triggers.remove(trigger)

        def clear_triggers(self):
            """
            Удаляет все триггеры.
            """
            with self._lock:
                self._triggers.clear()

        # ------------------------------
        # Главный цикл
        # ------------------------------
        def _loop(self):
            while self._running:
                time.sleep(self.default_sleep)

                # Проверка continue condition
                if self._continue_condition is not None:
                    try:
                        if not self._continue_condition():
                            # Обновляем время, но не обрабатываем триггеры
                            self._update_scaled_time()
                            continue
                    except:
                        log("Error in continue_condition: {}".format(traceback.format_exc()))

                # Обновляем масштабируемое время
                now = self._update_scaled_time()

                with self._lock:
                    # копия, чтобы можно было удалять
                    triggers = list(self._triggers)

                for tr in triggers:

                    # 1) Lifetime check (используем масштабируемое время)
                    if tr.lifetime is not None:
                        if now - tr.created_time >= tr.lifetime:
                            if tr.dead_fn:
                                tr.dead_fn()
                            self.remove_trigger(tr)
                            continue

                    # 2) Интервал проверки (используем масштабируемое время)
                    if now - tr.last_check < tr.interval:
                        continue

                    tr.last_check = now

                    # 3) Условие
                    try:
                        if tr.condition_fn():
                            tr.action_fn()

                            if not tr.repeat:
                                # одноразовый → удаляем
                                self.remove_trigger(tr)
                    except:
                        # Ошибки не ломают менеджер
                        log("Error in Trigger '{}': {}".format(tr.name, traceback.format_exc()))
                        # удаляем проблемный триггер
                        self.remove_trigger(tr)


    # ------------------------------
    # Пример использования
    # ------------------------------
    
    # 1. Создаем менеджер
    # TriggerSystem = TriggerManager()
    
    # 2. Настраиваем масштаб времени
    # Вариант А: если sleep_time больше = медленнее
    # def get_time_scale():
    #     return sleep_time  # 0.1 = в 10 раз медленнее, 1.0 = нормально
    
    # Вариант Б: если sleep_time меньше = быстрее
    # def get_time_scale():
    #     return 1.0 / max(sleep_time, 0.01)  # 0.1 -> 10x быстрее
    
    # TriggerSystem.set_time_scale_function(get_time_scale)
    
    # 3. Запускаем
    # TriggerSystem.start()