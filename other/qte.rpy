init python in v1FNaSR:
    class QTEBlockException(Exception): pass

    class QTEVisual(ConstantBase):
        """Константы для визуальных эффектов QTE"""
        qte_pulse_time = 0.8  # Скорость пульсации в секундах

    class StateQte(FNaSRBase):
        """Глобальное состояние системы QTE"""
        block = False  # Блокировка запуска новых QTE
        current_qte = None  # Текущий активный QTE

    class QTEHandler(FNaSRBase):
        """
        Обработчик событий QTE с синхронизацией game loop.
        
        Управляет жизненным циклом QTE события и учитывает
        динамическое изменение скорости игры через time_scale_function.
        """
        
        def __init__(self):
            """Инициализация обработчика"""
            self.completed = False
            self.success_callback = None
            self.fail_callback = None
            self.time_scale_function = None
            self.start_time = None
            self.base_time_limit = None
            self.accumulated_time = 0.0
            self.last_update_time = None
        
        def start_timer(self, base_time_limit):
            """
            Запускает таймер QTE с привязкой к игровому времени.
            
            Args:
                base_time_limit: Базовый лимит времени в секундах
            """
            with lock:
                self.start_time = renpy.get_game_runtime()
                self.last_update_time = self.start_time
                self.base_time_limit = base_time_limit
                self.accumulated_time = 0.0
        
        def update_timer(self):
            """
            Обновляет аккумулированное время с учётом time_scale_function.
            Вызывается периодически для синхронизации с game loop.
            """
            with lock:
                if self.completed or self.start_time is None:
                    return
                
                current_time = renpy.get_game_runtime()
                delta_time = current_time - self.last_update_time
                self.last_update_time = current_time
                
                # Получаем текущую скорость игры из внешнего класса
                if self.time_scale_function:
                    time_scale = self.time_scale_function()
                else:
                    time_scale = 1.0
                
                # Накапливаем время с учётом скорости game loop
                self.accumulated_time += delta_time * time_scale
        
        def check_timeout(self):
            """
            Проверяет истечение времени с учётом time_scale_function.
            
            Returns:
                bool: True если время истекло, False иначе
            """
            with lock:
                if self.completed or self.start_time is None:
                    return False
                
                self.update_timer()
                return self.accumulated_time >= self.base_time_limit
        
        def get_time_progress(self):
            """
            Возвращает прогресс таймера от 0.0 до 1.0.
            Учитывает time_scale_function для синхронизации с game loop.
            
            Returns:
                float: Прогресс от 0.0 (начало) до 1.0 (конец)
            """
            with lock:
                if self.start_time is None or self.base_time_limit is None:
                    return 0.0
                
                self.update_timer()
                progress = self.accumulated_time / self.base_time_limit
                return min(progress, 1.0)
        
        def get_remaining_time(self):
            """
            Возвращает оставшееся время в секундах.
            
            Returns:
                float: Оставшееся время (может быть отрицательным)
            """
            with lock:
                if self.start_time is None or self.base_time_limit is None:
                    return 0.0
                
                self.update_timer()
                return self.base_time_limit - self.accumulated_time
        
        def execute_success(self):
            """
            Выполняется при успешном нажатии клавиши.
            Вызывает коллбэк успеха и закрывает экран QTE.
            """
            with lock:
                if not self.completed:
                    self.completed = True
                    
                    if self.success_callback:
                        self.success_callback()

                    StateQte.block = False
                    renpy.hide_screen("V1_qte_event_screen_FNaSR")
        
        def execute_fail(self):
            """
            Выполняется при истечении времени.
            Вызывает коллбэк провала и закрывает экран QTE.
            """
            with lock:
                if not self.completed:
                    self.completed = True
                    
                    if self.fail_callback:
                        self.fail_callback()
                    
                    StateQte.block = False
                    renpy.hide_screen("V1_qte_event_screen_FNaSR")
        
        def reset(self, on_success=None, on_fail=None, time_scale_function=None):
            """
            Сбрасывает состояние обработчика для повторного использования.
            
            Args:
                on_success: Функция, вызываемая при успехе
                on_fail: Функция, вызываемая при провале
                time_scale_function: Функция, возвращающая текущую скорость игры из вашего game loop
                    Должна возвращать float (по умолчанию 1.0 = нормальная скорость)
                    Пример: lambda: YourGameLoop.time_scale
                            lambda: store.game_manager.speed
                            lambda: persistent.time_multiplier
            """
            with lock:
                self.completed = False
                self.success_callback = on_success
                self.fail_callback = on_fail
                self.time_scale_function = time_scale_function
                self.time_scale_function = time_scale_function
                self.start_time = None
                self.last_update_time = None
                self.base_time_limit = None
                self.accumulated_time = 0.0
    
    class QTETools(FNaSRBase):

        @staticmethod 
        def normalize_key(key):
            """
            Нормализует название клавиши для унифицированного сравнения.
            
            Args:
                key: Строка с названием клавиши
                
            Returns:
                Нормализованное название клавиши
                
            Examples:
                'K_SPACE' -> 'K_SPACE'
                'space' -> 'K_SPACE'
                'a' -> 'K_A'
            """
            key = str(key).upper()
            
            if not key.startswith("K_") and len(key) > 1:
                key = "K_" + key
            elif not key.startswith("K_") and len(key) == 1:
                key = "K_" + key.lower()
                
            return key
            
        @staticmethod 
        def display_key_name(key):
            """
            Преобразует код клавиши в читаемое название для отображения.
            
            Args:
                key: Код клавиши (например, 'K_SPACE')
                
            Returns:
                Читаемое название клавиши
                
            Examples:
                'K_SPACE' -> 'ПРОБЕЛ'
                'K_A' -> 'A'
            """
            key_names = {
                "K_SPACE": "ПРОБЕЛ",
                "K_RETURN": "ENTER",
                "K_LSHIFT": "SHIFT",
                "K_RSHIFT": "SHIFT",
                "K_LCTRL": "CTRL",
                "K_RCTRL": "CTRL",
                # "K_UP": "↑",
                # "K_DOWN": "↓",
                # "K_LEFT": "←",
                # "K_RIGHT": "→",
            }
            
            # Проверка на специальные клавиши
            if key in key_names:
                return key_names[key]
            
            # Обработка обычных букв (K_A -> A)
            if key.startswith("K_") and len(key) == 3:
                return key[2]
            
            # Возврат как есть для остальных случаев
            return key.upper()

        @staticmethod 
        def start_qte(*args, **kwargs):
            """
            Запускает QTE событие.
            
            Args:
                *args: Позиционные аргументы для экрана QTE
                **kwargs: Именованные аргументы, включая:
                    - block (bool): Блокировать ли новые QTE (по умолчанию True)
                    - qte_handler (QTEHandler): Обработчик события (обязательно)
                    - time_scale_function: Функция получения скорости игры (опционально)
                    
            Raises:
                QTEBlockException: Если QTE заблокирован
            """
            with lock:
                if StateQte.block:
                    raise QTEBlockException("QTE is currently blocked.")

                StateQte.block = bool(kwargs.pop("block", True))

                #if "qte_handler" not in kwargs:
                #    raise Exception("QTE handler must be provided.")

                renpy.show_screen("V1_qte_event_screen_FNaSR", *args, **kwargs)

        @staticmethod 
        def create_qte_handler(on_success=None, on_fail=None, time_scale_function=None):
            """
            Создаёт и инициализирует новый обработчик QTE.
            
            Args:
                on_success: Функция, вызываемая при успехе
                on_fail: Функция, вызываемая при провале
                
            Returns:
                QTEHandler: Настроенный обработчик
                
            Example:
                # Синхронизация с внешним game loop
                handler = QTETools.create_qte_handler(
                    on_success=lambda: print("Success!"),
                    on_fail=lambda: print("Failed!")
                )
                
                # Без синхронизации (нормальная скорость 1.0)
                handler = QTETools.create_qte_handler(
                    on_success=success_func,
                    on_fail=fail_func
                )
            """
            with lock:
                if time_scale_function is None:
                    time_scale_function = GameTools.time_scale

                handler = QTEHandler()
                handler.reset(on_success, on_fail, time_scale_function)
                return handler

        @staticmethod
        def reset_qte_handler(handler, on_success=None, on_fail=None, time_scale_function=None):
            with lock:
                if on_success is None:
                    on_success = handler.success_callback

                if on_fail is None:
                    on_fail = handler.fail_callback

                if time_scale_function is None:
                    time_scale_function = GameTools.time_scale

                handler.reset(on_success, on_fail, time_scale_function)

        @staticmethod 
        def run_qte_chain(qte_sequence, time_scale_function=None):
            """
            Запускает последовательность QTE событий.
            
            Args:
                qte_sequence: Список кортежей формата:
                    (key, time_limit) или (key, time_limit, text)
                    где:
                    - key: Клавиша для нажатия
                    - time_limit: Время на нажатие в секундах
                    - text: Опциональный текст подсказки
                time_scale_function: Функция, возвращающая текущую скорость из вашего game loop
                    
            Returns:
                bool: True при успешном прохождении всей цепочки,
                    False при провале любого QTE
                    
            Example:
                # Простая цепочка без синхронизации
                qte_chain = [
                    ("space", 2.0, "Нажми пробел!"),
                    ("a", 1.5),
                    ("enter", 2.5, "Быстрее!")
                ]
                success = run_qte_chain(qte_chain)
                
                # С синхронизацией с вашим game loop
                success = run_qte_chain(
                    qte_chain, 
                    time_scale_function=lambda: YourGameClass.time_scale
                )
            """
            with lock:
                qte_result = [None]  # Список для изменения во вложенных функциях

                def make_success_callback():
                    """Создаёт коллбэк успеха для текущего QTE"""
                    def success():
                        qte_result[0] = True
                    return success

                def make_fail_callback():
                    """Создаёт коллбэк провала для текущего QTE"""
                    def fail():
                        qte_result[0] = False
                    return fail

                # Проход по каждому QTE в цепочке
                for qte in qte_sequence:
                    key = qte[0]
                    time_limit = qte[1]
                    text = qte[2] if len(qte) > 2 else ""

                    # Создание обработчика для текущего QTE
                    handler = QTETools.create_qte_handler(
                        make_success_callback(), 
                        make_fail_callback(),
                        time_scale_function
                    )
                    
                    # Запуск QTE
                    QTETools.start_qte(
                        key, 
                        time_limit, 
                        text_align=(0.5, 0.5), 
                        qte_handler=handler
                    )

                    # Ожидание завершения текущего QTE
                    while qte_result[0] is None:
                        renpy.pause(0.1)

                    # Проверка результата
                    if not qte_result[0]:
                        return False  # Провал в цепочке

                    qte_result[0] = None  # Сброс для следующего QTE

                return True  # Успешное прохождение всей цепочки

        @staticmethod 
        def update_handler(handler):
            if handler.check_timeout():
                handler.execute_fail()


init:
    # Анимация нажатия клавиши (масштабирование)
    transform v1_qte_key_pressure_FNaSR:
        zoom 1.0
        linear v1FNaSR.QTEVisual.qte_pulse_time zoom 1.1
        linear v1FNaSR.QTEVisual.qte_pulse_time zoom 1.0
        repeat

    # Анимация пульсации (изменение прозрачности)
    transform v1_qte_pulse_FNaSR:
        alpha 0.8
        linear v1FNaSR.QTEVisual.qte_pulse_time alpha 1.0
        linear v1FNaSR.QTEVisual.qte_pulse_time alpha 0.8
        repeat


screen V1_qte_event_screen_FNaSR(key, time_limit, text_align, qte_handler):
    # Нормализация клавиши при показе экрана
    default normalized_key = v1FNaSR.QTETools.normalize_key(key)
    
    # Запуск таймера при показе экрана
    on "show" action Function(qte_handler.start_timer, time_limit)

    # Модальный экран (блокирует другие действия)
    modal True

    # Периодическая проверка таймаута (обновление каждые 0.016 секунды ≈ 60 FPS)
    # Частое обновление необходимо для точной синхронизации с game loop
    timer 0.016 repeat True action Function(v1FNaSR.QTETools.update_handler, qte_handler)

    # Обработка нажатия правильной клавиши
    key normalized_key action Function(qte_handler.execute_success)

    # Визуальное отображение
    frame:
        background None
        at v1_qte_key_pressure_FNaSR
        align text_align
        padding (30, 20)

        vbox:
            spacing 10
            
            # Основной текст клавиши
            text v1FNaSR.QTETools.display_key_name(normalized_key):
                style "v1_text_24_style_FNaSR"
                at v1_qte_pulse_FNaSR


#init python:
#    mods["v1_qte_test_FNaSR"] = "v1_qte_test_FNaSR"

label v1_qte_test_FNaSR:
    python:
        result = "<none>"

        def on_success():
            global result
            result = "success"

        def on_fail():
            global result
            result = "fail"

    scene bg int_catacombs_entrance
    "Тестирование системы QTE с учётом изменения скорости игры."
    
    $ handler = v1FNaSR.QTETools.create_qte_handler(
        on_success=on_success,
        on_fail=on_fail,
        time_scale_function=lambda: 2.0
    )
    $ v1FNaSR.QTETools.start_qte("space", 2.0, (0.5, 0.5), qte_handler=handler)

    $ renpy.pause(2.1, hard=True)
    "Результат QTE: [result]"











