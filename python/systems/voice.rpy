init python in v1FNaSR:
    renpy.music.register_channel("v1_character_voice_FNaSR", mixer="sound", loop=False)

    class VoiceCharacter:
        def __init__(self, audio):
            self.audio = audio      # dict[str, list[str]]
            self._current = []      # активный список файлов
            self._idx = 0
            self._is_block = False

        def load(self, name):
            if name not in self.audio:
                raise KeyError(
                    "VoiceCharacter: The '{}' key was not found in audio".format(name)
                )
            self._current = self.audio[name]
            self._idx = 0           # сброс каждый раз при load()

        def play_next(self):
            if not self._current or self._is_block:
                return

            if self._idx >= len(self._current):
                log("VoiceCharacter: аудио закончились (idx={}, total={})".format(self._idx, len(self._current)))
                return
            renpy.music.play(self._current[self._idx], channel="v1_character_voice_FNaSR")
            self._idx += 1
            renpy.block_rollback()

        def reset(self):
            self._idx = 0
            self._current = []

        def block(self):
            self._is_block = True

        def unblock(self):
            self._is_block = False
            

    def voice_character(voice_obj, *args, **kwargs):
        """
        Обёртка над Character с автоматическим воспроизведением голоса.
        
        Использование:
            gg = voice_character(_gg_voice, "Имя", color="#fff")
        """
        # Сохраняем существующий callback, если он есть
        existing_cb = kwargs.pop("callback", None)

        def _voice_callback(event, **cb_kw):
            if event == "begin":           # срабатывает перед показом реплики
                voice_obj.play_next()
            if existing_cb is not None:
                existing_cb(event, **cb_kw)

        kwargs["callback"] = _voice_callback
        c = renpy.store.Character(*args, **kwargs)
        c.voice = voice_obj                # удобный доступ: gg.voice.load(...)
        return c


