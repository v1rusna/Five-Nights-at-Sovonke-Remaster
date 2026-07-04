init python in v1FNaSRThread:
    import threading
    import traceback
    import collections

    def print_thread_list():
        renpy.log("----------| FNaSR |----------")
        for t in threading.enumerate():
            lines = (
                "name={}, ".format(t.name),
                "ident={}, ".format(t.ident),
                "daemon={}, ".format(t.daemon),
                "alive={}".format(t.is_alive()),
            )
            renpy.log("".join(lines))
        renpy.log("------------------------------")

    # Очередь исключений
    _thread_exc_queue = collections.deque()
    _thread_exc_lock = threading.Lock()

    def _push_thread_exception(text):
        with _thread_exc_lock:
            _thread_exc_queue.append(text)

    def _pop_thread_exception():
        with _thread_exc_lock:
            if _thread_exc_queue:
                return _thread_exc_queue.popleft()
            return None

    def _handle_thread_exceptions():
        exc = _pop_thread_exception()
        if exc:
            renpy.log("FNaSR | THREAD EXCEPTION:\n" + exc)
            renpy.error(exc)
        return True

    class ThreadWithCatch(threading.Thread):
        def __init__(self, target, args=(), kwargs=None, **thread_kwargs):
            threading.Thread.__init__(self, **thread_kwargs)
            self.__target_fn = target
            self._my_args = args
            self._my_kwargs = kwargs if kwargs is not None else {}

        def run(self):
            try:
                self.execute_target()
            except Exception:
                tb = traceback.format_exc()
                renpy.log("FNaSR | UNCAUGHT EXCEPTION IN THREAD:\n" + tb)
                _push_thread_exception(tb)

        def execute_target(self):
            self.__target_fn(*self._my_args, **self._my_kwargs)

    class ThreadGame(ThreadWithCatch):
        def __init__(self, **thread_kwargs):
            super(ThreadGame, self).__init__(**thread_kwargs)
            self._running = threading.Event()
            self._running.set()

        def stop(self):
            self._running.clear()

        def execute_target(self):
            self.__target_fn(self._running.is_set, *self._my_args, **self._my_kwargs)



    # Регистрируем callback
    renpy.config.interact_callbacks.append(_handle_thread_exceptions)
