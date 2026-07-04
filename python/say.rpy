init 1 python in v1FNaSRSay:

    FNaSRBase = renpy.store.v1FNaSR.FNaSRBase
    lock = renpy.store.v1FNaSR.lock
    execute_in_main_thread = renpy.store.v1FNaSR.execute_in_main_thread
    game = renpy.store.v1FNaSR.game
    global_event = renpy.store.v1FNaSR.global_event
    lock = renpy.store.v1FNaSR.lock

    import random
    import uuid


    class Text(FNaSRBase):
        def __init__(self, text,
                    pause=0,
                    decay_time=0,
                    appearance_time=0,
                    lifetime=6,
                    align=None):

            if align is None:
                align = (random.uniform(0.2, 0.8), random.uniform(0.2, 0.8))

            self.text = str(text)
            self.align = align

            self.pause = float(pause)
            self.decay_time = float(decay_time)
            self.appearance_time = float(appearance_time)
            self.lifetime = float(lifetime)

            self._key = "v1_text_{}_FNaSR".format(uuid.uuid4().hex)

            self._is_shown = False
            self._is_hiding = False

        # -------------------------

        def show(self):
            if self._is_shown:
                return

            self._is_shown = True
            self._is_hiding = False

            execute_in_main_thread(
                renpy.show_screen,
                "v1_text_screen_FNaSR",
                text=self.text,
                align=self.align,
                appearance_time=self.appearance_time,
                decay_time=self.decay_time,
                state="show",                                                                           
                _tag=self._key
            )

            global_event.once("game.loop.stop", self.hide)
            if self.lifetime > 0:
                game.game_time.timer(self.hide, self.lifetime)

        def hide(self):
            if not self._is_shown or self._is_hiding:
                return

            self._is_hiding = True

            # просто обновляем screen — без with
            execute_in_main_thread(
                renpy.show_screen,
                "v1_text_screen_FNaSR",
                text=self.text,
                align=self.align,
                appearance_time=self.appearance_time,
                decay_time=self.decay_time,
                state="hide",
                _tag=self._key
            )

            # реальное удаление после fade-out
            if self.decay_time > 0:
                game.game_time.timer(
                    lambda: execute_in_main_thread(
                        renpy.hide_screen,
                        self._key
                    ),
                    self.decay_time
                )
            else:
                execute_in_main_thread(
                    renpy.hide_screen,
                    self._key
                )

            #if self in self._list_all_show_text:
            #    with lock:
            #        if self in self._list_all_show_text:
            #            self._list_all_show_text.remove(self)
            self._is_shown = False



    class SayText(FNaSRBase):
        def __init__(self, *text_list):
            for text in text_list:
                if not isinstance(text, Text):
                    raise TypeError("All items must be Text")

            self._text_list = list(text_list)
            self._index = 0
            self._running = False

        def start(self):
            if self._running:
                return

            self._running = True
            self._index = 0
            self._show_next()

        def resume(self):
            if self._running:
                return

            self._running = True
            self._show_next()

        def _show_next(self):
            if not self._running:
                return

            if self._index >= len(self._text_list):
                self._running = False
                return

            if not game.is_game_loop_alive():
                self.stop()

            text = self._text_list[self._index]
            text.show()

            self._index += 1

            game.game_time.timer(
                self._show_next,
                text.pause
            )

        def stop(self):
            self._running = False
            for text in self._text_list:
                text.hide()


    test_say_text = SayText(
        Text(
            "",
            pause=1
        ),
        Text(
            "Первый текст",
            pause=1
        ),
        Text(
            "Второй текст",
            pause=0.5,
            decay_time=0.5,
        ),
        Text(
            "Третий текст",
            pause=2.5,
            decay_time=1.0,
            appearance_time=0.5,
            lifetime=3
        ),
        Text(
            "Четвертый текст",
            pause=2.5,
            decay_time=1.5,
            appearance_time=1.5,
            lifetime = 4
        ),
        Text(
            "Пятый текст",
            pause=2.5,
            decay_time=1.5,
            appearance_time=1.5,
            lifetime = 4
        ),
        Text(
            "Шестой текст",
            pause=2.5,
            decay_time=1.5,
            appearance_time=1.5,
            lifetime = 4
        ),
        Text(
            "Седьмой текст",
            pause=2.5,
            decay_time=1.5,
            appearance_time=1.5,
            lifetime = 4
        ),
        Text(
            "Восьмой текст",
            pause=2.5,
            decay_time=1.5,
            appearance_time=1.5,
            lifetime = 4
        ),
        Text(
            "Девятый текст",
            pause=2.5,
            decay_time=1.5,
            appearance_time=1.5,
            lifetime = 4
        ),
        Text(
            "Десятый текст",
            pause=2.5,
            decay_time=1.5,
            appearance_time=1.5,
            lifetime = 4
        )
    )

    ulyana_try_attack_text_2 = SayText(
        Text(
            "Бля!!! Ульяна!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.6, 0.8)),
            lifetime=2,
            appearance_time=0.5,
            decay_time=0.5
        ),
    )
    # Господи, господи, господи... только не открывайся, только держись...
    ulyana_try_attack_text_5 = SayText(
        Text(
            "Господи!",
            align=(random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)),
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.4,
            pause=1
        ),
        Text(
            "господи!",
            align=(random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)),
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.4,
            pause=0.8
        ),
        Text(
            "господи!",
            align=(random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)),
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.4,
            pause=0.8
        ),
        Text(
            "только не открывайся",
            align=(random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)),
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.4,
            pause=1.5
        ),
        Text(
            "только держись...",
            align=(random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)),
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.5
        ),
    )

    ulyana_try_attack_text_6 = SayText(
        Text(
            "А-а-а-а...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.6, 0.8)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.2,
            pause=2
        ),
        Text(
            "твою мать...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.6, 0.8)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3
        ),
    )
    # Я повесился на двери. Я реально повесился на двери, как ёлочная игрушка. Ленка б сейчас поржала...
    ulyana_try_attack_text_7 = SayText(
        Text(
            "Я повесился на двери",
            align=(random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)),
            lifetime=5,
            appearance_time=0.3,
            decay_time=0.4,
            pause=3.3
        ),
        Text(
            "Я реально повесился на двери, как ёлочная игрушка",
            align=(random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)),
            lifetime=6,
            appearance_time=0.5,
            decay_time=0.5,
            pause=5.3
        ),
        Text(
            "Ленка б сейчас поржала...",
            align=(random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)),
            lifetime=3.5,
            appearance_time=0.5,
            decay_time=0.5
        )
    )
    # Чего она там бормочет... Берёзки, берёзки... Странная какая-то...
    yulia_action_text_8 = SayText(
        Text(
            "Чего она там бормочет...",
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Берёзки, берёзки...",
            lifetime=4,
            appearance_time=0.5,
            decay_time=0.5,
            pause=2
        ),
        Text(
            "Странная какая-то...",
            lifetime=2,
            appearance_time=0.3,
            decay_time=0.2
        )
    )

    yulia_action_text_9 = SayText(
        Text(
            "АХ ТЫ Ж...",
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.2,
            pause=1.2
        ),
        Text(
            "ОНА ВНУТРИ!!!",
            lifetime=2.5,
            appearance_time=0.2,
            decay_time=0.2
        )
    )
    # Экран, экран, смотреть в экран!!!
    yulia_action_text_10 = SayText(
        Text(
            "Экран",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.2,
            pause=1
        ),
        Text(
            "экран",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.2,
            pause=1
        ),
        Text(
            "смотреть в экран!!!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=2,
            appearance_time=0.2,
            decay_time=0.2
        )
    )
    # Уходи... Уходи, дура ненормальная... Не смотри на меня, в экран смотри, в экран..
    yulia_action_text_11 = SayText(
        Text(
            "Уходи...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.3,
            pause=1.5
        ),
        Text(
            "Уходи, дура ненормальная...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.3,
            pause=2
        ),
        Text(
            "Не смотри на меня",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.2,
            decay_time=0.2,
            pause=1.8
        ),
        Text(
            "в экран смотри, в экран...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.2,
            decay_time=0.2
        )
    )

    yulia_action_text_12 = SayText(
        Text(
            "Чего она там бормочет...",
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Берёзки, берёзки...",
            lifetime=4,
            appearance_time=0.5,
            decay_time=0.5,
            pause=2
        ),
        Text(
            "Странная какая-то...",
            lifetime=2,
            appearance_time=0.3,
            decay_time=0.2
        )
    )
    # Лена... Стоит. Смотрит прямо в камеру.
    lena_look_text_14 = SayText(
        Text(
            "Лена...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.4,
            pause=1
        ),
        Text(
            "Стоит",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3.5,
            appearance_time=0.5,
            decay_time=0.5,
            pause=1.5
        ),
        Text(
            "Смотрит прямо в камеру",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.2
        )
    )
    # Не отводи взгляд... Не отводи... Она не двигается, пока я смотрю...
    lena_look_text_15 = SayText(
        Text(
            "Не отводи взгляд...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Не отводи...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3.5,
            appearance_time=0.5,
            decay_time=0.5,
            pause=1.5
        ),
        Text(
            "Она не двигается, пока я смотрю...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.2
        )
    )
    # Сколько можно стоять? У тебя ноги не затекли? У меня уже глаза сохнут...
    lena_look_text_17 = SayText(
        Text(
            "Сколько можно стоять?",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2.5
        ),
        Text(
            "У тебя ноги не затекли?",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3.5,
            appearance_time=0.5,
            decay_time=0.5,
            pause=2.5
        ),
        Text(
            "У меня уже глаза сохнут...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.2
        )
    )
    # Охренеть... Это Алиса?!
    alisa_text_18 = SayText(
        Text(
            "Охренеть...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.4,
            pause=1.3
        ),
        Text(
            "Это Алиса?!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3.5,
            appearance_time=0.5,
            decay_time=0.5,
            pause=2.5
        ),
        Text(
            "{size=-10}{i}нет это муся :3{/i}{/size}",
            align=(0.1,0.1),
            lifetime=2,
            appearance_time=0.3,
            decay_time=0.2
        )
    )
    # Кнопка, кнопка... Где эта серая кнопка?!
    alisa_text_19 = SayText(
        Text(
            "Кнопка, кнопка...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2.2
        ),
        Text(
            "Где эта серая кнопка?!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3.5,
            appearance_time=0.5,
            decay_time=0.5
        )
    )

    alisa_text_20 = SayText(
        Text(
            "ОРИ, ЗАРАЗА, ОРИ ГРОМЧЕ!!!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.5,
            decay_time=0.5
        )
    )
    # Шурик... Зашел, гад.
    shurik_text_21 = SayText(
        Text(
            "Шурик...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=1.5
        ),
        Text(
            "Зашел, гад",
            lifetime=3.2,
            appearance_time=0.4,
            decay_time=0.4
        )
    )
    # Свет вырубить... Свет вырубить, он уйдет...
    shurik_text_22 = SayText(
        Text(
            "Свет вырубить...",
            lifetime=4,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Свет вырубить",
            lifetime=4,
            appearance_time=0.4,
            decay_time=0.4,
            pause=1.6
        ),
        Text(
            "он уйдет...",
            lifetime=3.5,
            appearance_time=0.4,
            decay_time=0.4
        )
    )
    # Стой... стой, долго не простоишь... Темноту не любишь гад..
    shurik_text_23 = SayText(
        Text(
            "Стой...",
            lifetime=4,
            appearance_time=0.4,
            decay_time=0.4,
            pause=1.5
        ),
        Text(
            "стой, долго не простоишь...",
            lifetime=4.5,
            appearance_time=0.4,
            decay_time=0.4,
            pause=3
        ),
        Text(
            "Темноту не любишь гад..",
            lifetime=3.5,
            appearance_time=0.4,
            decay_time=0.4
        )
    )

    shurik_text_24 = SayText(
        Text(
            "Ушел...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.5,
            decay_time=0.5
        )
    )

    electronic_text_25 = SayText(
        Text(
            "БЛЯТЬ!!!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3,
            pause=0.8
        ),
        Text(
            "ЭЛЕКТРОНИК!!!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.4
        )
    )

    electronic_text_26 = SayText(
        Text(
            "",
            lifetime=0.1,
            pause=2
        ),
        Text(
            "Успел?",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=1.7
        ),
        Text(
            "Не успел?",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=1.9
        ),
        Text(
            "Где он?!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4
        )
    )

    electronic_text_27 = SayText(
        Text(
            "",
            lifetime=0.1,
            pause=1.5
        ),
        Text(
            "Твою мать",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "я так и инфаркт получу...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4
        )
    )

    slavia_text_28 = SayText(
        Text(
            "Славяна...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Идет проверка",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4
        )
    )

    slavia_text_29 = SayText(
        Text(
            "Я сплю...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.5,
            pause=2
        ),
        Text(
            "Крепко сплю...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.5,
            pause=2
        ),
        Text(
            "Я вообще мертвый...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4
        )
    )

    slavia_text_30 = SayText(
        Text(
            "Ушла?",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.5,
            pause=1.5
        ),
        Text(
            "Ушла...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.5,
            pause=1.5
        ),
        Text(
            "Кажется, можно дышать...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4
        )
    )

    zhenya_text_31 = SayText(
        Text(
            "Что за...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Музыка?",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    zhenya_text_32 = SayText(
        Text(
            "Шкатулка!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3,
            pause=1.5
        ),
        Text(
            "Пионеры!!!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3,
            pause=1.5
        ),
        Text(
            "Женя сейчас придет!!!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3
        )
    )
    
    zhenya_text_33 = SayText(
        Text(
            "Где ты, где ты, где ты...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3,
            pause=3
        ),
        Text(
            "Ну давай, покажись...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3
        )
    )

    zhenya_text_34 = SayText(
        Text(
            "ВОТ ТЫ!!!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3
        )
    )

    zhenya_text_35 = SayText(
        Text(
            "",
            lifetime=0.1,
            pause=1
        ),
        Text(
            "Заткнись...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4,
            pause=1.6
        ),
        Text(
            "Заткнись, ради бога...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )
    # Нет-нет-нет, только не это... Я ищу, я ищу!!!
    zhenya_text_36 = SayText(
        Text(
            "Нет-нет-нет, только не это...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2.5
        ),
        Text(
            "Я ищу, я ищу!!!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    zhenya_text_37 = SayText(
        Text(
            "ГДЕ ЭТА ЧЕРТОВА ШКАТУЛКА?!",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    zhenya_text_38 = SayText(
        Text(
            "",
            lifetime=0.1,
            pause=1.5
        ),
        Text(
            "Успел...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4,
            pause=1.5
        ),
        Text(
            "Кажется, успел...",
            align=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)),
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    miku_text_39 = SayText(
        Text(
            "А!!!",
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3,
            pause=1
        ),
        Text(
            "Ты как сюда залезла?!",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    miku_text_40 = SayText(
        Text(
            "Пошла вон!",
            lifetime=3,
            appearance_time=0.2,
            decay_time=0.3,
            pause=1.5
        ),
        Text(
            "Пошла вон отсюда!!!",
            lifetime=3.5,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Выметайся!!!",
            lifetime=3.5,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    viola_text_41 = SayText(
        Text(
            "Сидит...",
            lifetime=3,
            appearance_time=0.5,
            decay_time=0.5,
            pause=1.5
        ),
        Text(
            "Смотрит...",
            lifetime=3,
            appearance_time=0.5,
            decay_time=0.5,
            pause=1.5
        ),
        Text(
            "Ты чего хочешь-то?",
            lifetime=3,
            appearance_time=0.5,
            decay_time=0.5
        )
    )

    viola_text_42 = SayText(
        Text(
            "Отошла влево...",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4,
            pause=1.5
        ),
        Text(
            "Ближе к краю...",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    viola_text_43 = SayText(
        Text(
            "Не смотри на неё так пристально, дурак!",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2.3
        ),
        Text(
            "Отведи взгляд!",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4,
            pause=1.1
        ),
        Text(
            "Отведи!",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    viola_text_44 = SayText(
        Text(
            "ШЕСТЬ СЕКУНД!!!",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    viola_text_45 = SayText(
        Text(
            "Успел...",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Успел, бля...",
            lifetime=3,
            appearance_time=0.3,
            decay_time=0.4
        )
    )

    viola_text_46 = SayText(
        Text(
            "Больше никогда...",
            lifetime=5,
            appearance_time=0.5,
            decay_time=0.5,
            pause=3.5
        ),
        Text(
            "Никогда не буду пристально смотреть на медсестер...",
            lifetime=4,
            appearance_time=0.5,
            decay_time=0.5
        )
    )

    random_situation_text_47 = SayText(
        Text(
            "Да что ж вы все стучите?!",
            lifetime=4,
            appearance_time=0.3,
            decay_time=0.4,
            pause=3.2
        ),
        Text(
            "Я вам не домофон!",
            lifetime=3.5,
            appearance_time=0.3,
            decay_time=0.4
        )
    )
    # Ленка, если б ты знала, где твой брат работает... Врагу не пожелаешь. Хотя врагам бы пожелал. Пусть тоже под дверями посидят.
    random_situation_text_48 = SayText(
        Text(
            "Ленка, если б ты знала, где твой брат работает...",
            lifetime=4,
            appearance_time=0.4,
            decay_time=0.4,
            pause=4
        ),
        Text(
            "Врагу не пожелаешь.",
            lifetime=3.5,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2.5
        ),
        Text(
            "Хотя врагам бы пожелал.",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Пусть тоже под дверями посидят.",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4
        )
    )
    # Ну, заходите ещё... Когда научитесь чай с печеньками приносить.
    random_situation_text_49 = SayText(
        Text(
            "Ну, заходите ещё...",
            lifetime=4,
            appearance_time=0.4,
            decay_time=0.4,
            pause=4
        ),
        Text(
            "Когда научитесь чай с печеньками приносить.",
            lifetime=3.5,
            appearance_time=0.4,
            decay_time=0.4
        )
    )
    # Ещё чуть-чуть... Ещё немного... Солнце скоро. Солнце их не любит. А я люблю солнце. Солнце, это жизнь. Солнце, это Ленка...
    random_situation_text_50 = SayText(
        Text(
            "Ещё чуть-чуть...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Ещё немного...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=3
        ),
        Text(
            "Солнце скоро.",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=3
        ),
        Text(
            "Солнце их не любит.",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=3.5
        ),
        Text(
            "А я люблю солнце.",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2.5
        ),
        Text(
            "Солнце, это жизнь.",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2.5
        ),
        Text(
            "Солнце, это Ленка...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4
        )
    )
    # Мама... Если ты там есть... Я не знаю, как тут выживают... Но я стараюсь... Я очень стараюсь...
    random_situation_text_51 = SayText(
        Text(
            "Мама...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=1
        ),
        Text(
            "Если ты там есть...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2.5
        ),
        Text(
            "Я не знаю, как тут выживают...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Но я стараюсь...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4,
            pause=2
        ),
        Text(
            "Я очень стараюсь...",
            lifetime=3,
            appearance_time=0.4,
            decay_time=0.4
        )
    )


init:
    transform v1_show_st_FNaSR(time=1.0):
        alpha 0.0
        easein time alpha 1.0

    transform v1_hide_st_FNaSR(time=1.0):
        alpha 1.0
        easeout time alpha 0.0






screen v1_text_screen_FNaSR(text, align=(0.5, 0.5),
                            appearance_time=0.0,
                            decay_time=0.0,
                            state="show"):

    text text:
        style "v1_text_24_style_FNaSR"
        align align
        if state == "show":
            at v1_show_st_FNaSR(appearance_time)
        else:
            at v1_hide_st_FNaSR(decay_time)

