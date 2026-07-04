# -*- coding: utf-8 -*-
init -20 python in v1FNaSREvent:
    """
    Event Emitter System
    ================================

    Потокобезопасная система событий с поддержкой паттернов и приоритетов.

    Архитектура:
    -----------
    Модуль предоставляет два способа работы с событиями:

    1. **Глобальная система событий** (v1FNaSREvent.on/emit/etc.)
    - Единый экземпляр EventEmitter
    - Используется для событий, которые должны быть доступны везде
    - Рекомендуется для игровой логики, UI-событий, системных уведомлений

    2. **Локальные системы событий** (EventEmitter())
    - Создание изолированных экземпляров для конкретных компонентов
    - Полезно для модульной архитектуры, плагинов, независимых систем
    - Каждый экземпляр имеет собственный набор обработчиков

    Основные возможности:
    - Подписка на события по точному имени или с использованием wildcards (*, ?)
    - Приоритеты обработчиков (выше приоритет → раньше выполняется)
    - Одноразовые обработчики (once)
    - Потокобезопасность через threading.RLock
    - Простой API для управления событиями

    Примеры использования:
    ---------------------

    Глобальная система событий:
        python:
            def on_player_damage(amount):
                print("Player took {} damage".format(amount))
            
            # Подписка через глобальную систему
            v1FNaSREvent.on("player.damage", on_player_damage)
            
            # Вызов события через глобальную систему
            v1FNaSREvent.emit("player.damage", 10)

    Локальная система событий:
        python:
            # Создаём локальный эмиттер для боевой системы
            combat_events = v1FNaSREvent.EventEmitter()
            
            def on_combat_start():
                print("Combat started!")
            
            # Подписка на локальную систему
            combat_events.on("combat.start", on_combat_start)
            
            # Вызов события в локальной системе
            combat_events.emit("combat.start")
            
            # Создаём ещё один изолированный эмиттер для квестов
            quest_events = v1FNaSREvent.EventEmitter()
            quest_events.on("quest.complete", show_reward)

    Когда использовать глобальную систему:
        - Игровые события (player.*, game.*, ui.*)
        - Системные уведомления
        - События, на которые подписываются разные части игры
        
        python:
            v1FNaSREvent.on("game.save", save_player_data)
            v1FNaSREvent.on("game.save", save_settings)
            v1FNaSREvent.emit("game.save")

    Когда использовать локальную систему:
        - Изолированные модули/плагины
        - Временные системы событий (например, для одного мини-геймa)
        - Когда нужно избежать конфликтов имён с глобальными событиями
        
        python:
            # Мини-игра с собственными событиями
            minigame = v1FNaSREvent.EventEmitter()
            minigame.on("level.complete", next_level)
            minigame.on("game.over", show_results)
            
            # После завершения мини-игры можно очистить все её события
            minigame.clear()

    Wildcards в паттернах:
        python:
            # Подписка на все события игрока
            v1FNaSREvent.on("player.*", lambda *a: print("Player event"))
            
            # Подписка на все события
            v1FNaSREvent.on("*", lambda *a: print("Any event"))

    Приоритеты:
        python:
            # Выполнится первым (priority=10)
            v1FNaSREvent.on("game.start", handler1, priority=10)
            
            # Выполнится вторым (priority=0, по умолчанию)
            v1FNaSREvent.on("game.start", handler2)

    Одноразовые обработчики:
        python:
            # Выполнится только один раз
            v1FNaSREvent.once("tutorial.complete", show_reward)
            
            v1FNaSREvent.emit("tutorial.complete")  # show_reward вызовется
            v1FNaSREvent.emit("tutorial.complete")  # show_reward НЕ вызовется

    Отписка:
        python:
            # Удалить конкретный обработчик
            v1FNaSREvent.off("player.damage", on_player_damage)
            
            # Удалить все обработчики события
            v1FNaSREvent.off("player.damage")
            
            # Очистить все события (глобальные)
            v1FNaSREvent.clear()
            
            # Очистить локальную систему
            my_emitter = v1FNaSREvent.EventEmitter()
            my_emitter.clear()

    API Reference:
    -------------

    Глобальные функции (v1FNaSREvent.*):
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    on(pattern, handler, priority=0)
        Подписаться на событие в глобальной системе.

    once(pattern, handler, priority=0)
        Подписаться на событие один раз в глобальной системе.

    off(pattern=None, handler=None)
        Отписаться от события в глобальной системе.

    clear()
        Удалить все обработчики глобальной системы.

    emit(event_name, *args, **kwargs)
        Вызвать событие в глобальной системе. Возвращает список результатов.

    Класс EventEmitter:
    ~~~~~~~~~~~~~~~~~~
    EventEmitter()
        Создать новую локальную систему событий.

    Методы экземпляра:
        .on(pattern, handler, priority=0)
        .once(pattern, handler, priority=0)
        .off(pattern=None, handler=None)
        .clear()
        .emit(event_name, *args, **kwargs)

    Примечания:
    -----------
    - Обработчики с одинаковым приоритетом вызываются в порядке подписки
    - При ошибке в обработчике исключение пробрасывается наружу
    - Паттерны используют fnmatch: * (любые символы), ? (один символ)
    - Потокобезопасно, можно использовать из разных потоков
    - Глобальная и локальные системы полностью независимы друг от друга
    """

    import fnmatch
    import threading

    try:
        _lock = threading.RLock()
    except:
        class DummyLock(object):
            def acquire(self): pass
            def release(self): pass
            def __enter__(self): return self
            def __exit__(self, *a): pass
        _lock = DummyLock()

    class EventRecord(object):
        __slots__ = ["handler", "once", "priority", "id"]

        _counter = 0

        def __init__(self, handler, once, priority):
            self.handler = handler
            self.once = once
            self.priority = priority
            self.id = EventRecord._counter
            EventRecord._counter += 1


    class EventEmitter(object):
        def __init__(self):
            # pattern -> list of EventRecord
            self._handlers = {}

        # -------------------------
        # SUBSCRIBE
        # -------------------------

        def on(self, pattern, handler, priority=0):
            if not callable(handler):
                raise TypeError("handler must be callable")

            rec = EventRecord(handler, False, priority)

            with _lock:
                self._handlers.setdefault(pattern, []).append(rec)

        def once(self, pattern, handler, priority=0):
            if not callable(handler):
                raise TypeError("handler must be callable")

            rec = EventRecord(handler, True, priority)

            with _lock:
                self._handlers.setdefault(pattern, []).append(rec)

        # -------------------------
        # UNSUBSCRIBE
        # -------------------------

        def off(self, pattern=None, handler=None):
            """
            off() — удалить всё
            off(pattern) — удалить все обработчики такого паттерна
            off(pattern, handler) — удалить конкретный обработчик
            """
            with _lock:
                if pattern is None:
                    self._handlers.clear()
                    return

                if pattern not in self._handlers:
                    return

                if handler is None:
                    del self._handlers[pattern]
                    return

                lst = self._handlers[pattern]
                new_list = [r for r in lst if r.handler is not handler]
                if new_list:
                    self._handlers[pattern] = new_list
                else:
                    del self._handlers[pattern]

        def clear(self):
            with _lock:
                self._handlers.clear()

        # -------------------------
        # EMIT
        # -------------------------

        def emit(self, event_name, *args, **kwargs):
            """
            Возвращает список результатов обработчиков.
            """
            with _lock:
                matches = []

                # Находим все паттерны, совпадающие с именем события
                for pattern, handlers in self._handlers.items():
                    if fnmatch.fnmatchcase(event_name, pattern):
                        for rec in handlers:
                            # Сортировка по приоритету (desc) и id (asc)
                            matches.append(rec)

                # Сортируем: приоритет выше → раньше
                matches.sort(key=lambda r: (-r.priority, r.id))

            if not matches:
                return []

            results = []
            to_remove = []

            # Вызываем обработчики
            for rec in matches:
                try:
                    res = rec.handler(*args, **kwargs)
                    results.append(res)
                except Exception:
                    raise  # важно не скрывать ошибки

                if rec.once:
                    to_remove.append(rec)

            # Убираем одноразовые обработчики
            if to_remove:
                with _lock:
                    for rec in to_remove:
                        # ищем и удаляем по identity
                        for pattern, lst in list(self._handlers.items()):
                            if rec in lst:
                                lst.remove(rec)
                                if not lst:
                                    del self._handlers[pattern]

            return results

    ev = EventEmitter()

    def on(*args, **kwargs):
        ev.on(*args, **kwargs)

    def once(*args, **kwargs):
        ev.once(*args, **kwargs)

    def off(*args, **kwargs):
        ev.off(*args, **kwargs)

    def clear():
        ev.clear()

    def emit(*args, **kwargs):
        ev.emit(*args, **kwargs)