init 11 python in v1FNaSR:

    class UlyanaEnemy(EnemyAttackBase):
        def __init__(self, **k):
            super(UlyanaEnemy, self).__init__(**k)
            self.debug_info = DebugInfo(name="Ульяна", color="#FF3200", obj=self)

        def loss_kill(self):
            if random.random() < 0.01:
                random_s = [
                    renpy.store.sfx_hell_crickets_1,
                    renpy.store.sfx_hell_crickets_2,
                    renpy.store.sfx_hell_crickets_3
                ]

                execute_in_main_thread(renpy.music.play, random.choice(random_s), channel=self.sound_channel, loop=False, fadeout=1, fadein=2)

            if situation.is_done("ulyana.try_attack"):
                situation.next_situation("ulyana.lose_attack")
            return super(UlyanaEnemy, self).loss_kill()

        def time_murder(self):
            if self._time_murder is None:
                situation.next_situation("ulyana.try_attack")
                execute_in_main_thread(renpy.play, resources.sounds.sfx["enemy_deep_steps"], self.sound_channel)

            return super(UlyanaEnemy, self).time_murder()

        def calculate_change_factor(self):
            random_roll = super(UlyanaEnemy, self).calculate_change_factor()

            if self._is_door_closed:
                random_roll += 2
            else:
                random_roll -= 5

            return random_roll

    class LenaEnemy(EnemyAttackBase):
        def __init__(self, **k):
            super(LenaEnemy, self).__init__(**k)
            self.debug_info = DebugInfo(name="Лена", color="#B956FF", obj=self)

            self.__outside_the_window = False
            self.__bulb = True
            self.__is_move = False
            self._is_start_situation = False
            self._say_count = 0

            self.__image_main_loc_on = renpy.displayable(resources.images.bg["R_int_mt_house_night_light_un"])
            self.__image_main_loc_off = renpy.displayable(resources.images.bg["R_int_mt_house_night_un"])

            def handler(bulb):
                self.__bulb = bool(bulb)
                self.__show_image()

            renpy.store.v1FNaSREvent.on("enemy.bulb", handler)

        def update(self):
            if self.__outside_the_window:
                self.try_kill()
                return

            if game.camera_system.show_tablet and game.camera_system.select == self.enemy_path.get_camera_id_by_loc():
                if not self._is_start_situation:
                    self._is_start_situation = True
                    situation.next_situation("lena.look")

                self._say_count += 1
                if self._say_count == 15:
                    situation.next_situation("lena.look.long")

                if not self.__is_move:
                    self.__is_move = self.move_chance()
                return

            self._say_count = 0
            if self.__is_move_handle():
                self._is_start_situation = False
                return

            if self.enemy_path.is_max_loc():
                if self.try_move():
                    self.__outside_the_window = True
                    self.enemy_path.set_location(0)
                    self.__show_image()
            elif self.try_move():
                self._is_start_situation = False

        def __is_move_handle(self):
            if not self.__is_move:
                return False
            
            self.__is_move = False
            
            if self.enemy_path.is_max_loc():
                self.__outside_the_window = True
                self.enemy_path.set_location(0)
                self.__show_image()
                return True

            self.enemy_path.next_loc()
            self.position = [renpy.random.randint(0, 999), 0]
            return True

        def loss_kill(self):
            self.__outside_the_window = False
            game.mainL.set_bulb(self.__bulb)

            if random.random() < 0.01:
                execute_in_main_thread(renpy.music.play, renpy.store.sfx_knock_glass, channel=self.sound_channel, loop=False)

            return super(LenaEnemy, self).loss_kill()

        def try_kill(self):
            if self.time_murder():
                if self._is_door_closed:
                    self.loss_kill()
                    return False
                else:
                    self.kill_player()
                    return True

        def calculate_change_factor(self):
            random_roll = super(LenaEnemy, self).calculate_change_factor()

            if self._is_door_closed and self.enemy_path.is_max_loc():
                random_roll -= 5

            return random_roll

        def __show_image(self):
            if self.__outside_the_window:
                if self.__bulb:
                    game.mainL.set_img(self.__image_main_loc_on)
                else:
                    game.mainL.set_img(self.__image_main_loc_off)

        def reset(self):
            super(LenaEnemy, self).reset()
            self.__outside_the_window = False
            self.__bulb = True
            self._is_start_situation = False
            self._say_count = 0

    class AlisaEnemy(EnemyBase):
        def __init__(self, **k):
            super(AlisaEnemy, self).__init__(**k)
            self.debug_info = DebugInfo(name="Алиса", color="#FFAA00", obj=self)

            self.__steps_to_break = 3
            self.__signal_step = 3
            self.__old_is_bulb = None
            self.__is_show_button = False
            self._look_count = 0

            self._signal = False

            def _h(s):
                self._signal = bool(s)
                if self._signal:
                    execute_in_main_thread(renpy.music.play, resources.sounds.sfx["tablet_scaring_sound"], self.sound_channel, loop=True)
                else:
                    execute_in_main_thread(renpy.music.stop, self.sound_channel)

            self.__signalButton = renpy.store.v1rus.HoldingMouseImageButton(
                idle=renpy.store.Transform(resources.images.other["Signal_button"], xysize=(290 / 2, 60 / 2)),
                clicked=renpy.store.Transform(resources.images.other["Signal_button"], xysize=(290 / 2, 60 / 2)),
                click_action=renpy.store.Function(_h, True),
                unclick_action=renpy.store.Function(_h, False),
                allow_alternate=False
            )

            def handler(tablet_status):
                if tablet_status:
                    self.show_button(game.camera_system.select)
                else:
                    self.show_button(0)

            renpy.store.v1FNaSREvent.on("camera_system.tablet", handler)
            renpy.store.v1FNaSREvent.on("camera_system.select_camera", self.show_button)

        def generate_path(self):
            self.enemy_path = EnemyPath(self, *EnemyPath.generate_path(15))
            self.enemy_path.next_loc()

        def update(self):
            if not situation.is_done("alisa.look.button") and game.camera_system.show_tablet and game.camera_system.select == self.enemy_path.get_camera_id_by_loc():
                self._look_count += 1
                if self._look_count == 6:
                    situation.next_situation("alisa.look.long")

            self.signal()
            if self.enemy_path.is_max_loc():
                if self.__steps_to_break:
                    self.__steps_to_break -= 1
                else:
                    self.break_generator()
            elif self.try_move():
                self.show_button(game.camera_system.select)

        def break_generator(self):
            if self.__old_is_bulb is None:
                self.__old_is_bulb = game.mainL.is_bulb

            game.mainL.set_bulb(False)
            game.mainL.is_bulb = False

            game.camera_system.add_charge_update_step(-2)

        def show_button(self, select):
            if not self.activity:
                return
            if game.camera_system.show_tablet:
                if select == self.enemy_path.get_camera_id_by_loc():
                    situation.next_situation("alisa.look")
                    game.object_display.add_obj(
                        key="alisa_enemy_signal_button",
                        obj=self.__signalButton,
                        layer="screens",
                        align=(0.25, 0.89)
                    )
                else:
                    self.__signalButton.force_unclick()
                    game.object_display.pop_obj("alisa_enemy_signal_button")
                    self._look_count = 0
            else:
                self._look_count = 0
                self.__signalButton.force_unclick()
                game.object_display.pop_obj("alisa_enemy_signal_button")

        def signal(self):
            if self._signal:
                situation.next_situation("alisa.look.button")
                self.__signal_step -= 1
                self._look_count -= 1
                if self.__signal_step <= 0:
                    self.__steps_to_break = 3
                    self.__signal_step = 3
                    if self.__old_is_bulb is not None:
                        game.mainL.is_bulb = self.__old_is_bulb
                        self.__old_is_bulb = None
                    self.__signalButton.force_unclick()
                    game.object_display.pop_obj("alisa_enemy_signal_button")
                    self.enemy_path.set_location(1)
                    execute_in_main_thread(renpy.music.play, resources.sounds.sfx["enemy_running_fast"], self.sound_channel)
            else:
                self.__signal_step = 3

        def reset(self):
            super(AlisaEnemy, self).reset()

            self.__steps_to_break = 3
            self.__signal_step = 3
            self.__old_is_bulb = None
            self.__is_show_button = False
            self._look_count = 0

            self._signal = False

    class MikuEnemy(EnemyBase):
        def __init__(self, clicked=20, aggressiveness_coefficient=10, **k):
            super(MikuEnemy, self).__init__(**k)
            self.debug_info = DebugInfo(name="Мику", color="#00DEFF", obj=self)

            self.__is_in_house = False
            self.__clicked = clicked
            self.__miku_click = self.__clicked
            self._is_door_closed = False
            self._aggressiveness_coefficient = aggressiveness_coefficient

            s_p = display.Parallax(
                displayable=self.sprite,
                zoom=1.15,
                anchor=(renpy.config.screen_width>>1, renpy.config.screen_height>>1),
                power=0.10,
                sharpness_factor=0.1
            )

            self.__miku_button = display.Wrapper(
                renpy.display.behavior.ImageButton,
                idle_image=s_p,
                clicked=renpy.store.Function(self._miku_click)
            )

            def set_door_state(state):
                self._is_door_closed = bool(state)

            global_event.on("door_system.door_use", set_door_state)

        def update(self):
            if self.__is_in_house:
                if not game.camera_system.show_tablet:
                    situation.next_situation("miku.action")
                return

            if self.enemy_path.is_max_loc():
                if not self._is_door_closed:
                    if self.try_move():
                        self.entered_the_house()
            else:
                self.try_move()

        def entered_the_house(self):
            execute_in_main_thread(renpy.music.play, renpy.store.music_list["miku_song_voice"], self.sound_channel, loop=True)
            self.enemy_path.set_location(0)
            self.__is_in_house = True

            for enemy in game.enemy_system:
                enemy.difficulty += self._aggressiveness_coefficient

            self.show_sprite(self.__miku_button)

        def _miku_click(self):
            situation.next_situation("miku.action.click")
            self.__miku_click -= 1
            if self.__miku_click <= 0:
                execute_in_main_thread(renpy.music.stop, self.sound_channel)
                self.__miku_click = self.__clicked
                self.__is_in_house = False
                self.hide_sprite()

                for enemy in game.enemy_system:
                    enemy.difficulty -= self._aggressiveness_coefficient

        def reset(self):
            super(MikuEnemy, self).reset()
            self.__is_in_house = False
            self.__miku_click = self.__clicked
            self._is_door_closed = False

    class SlaviaEnemy(EnemyAttackBase):
        def __init__(self, **k):
            super(SlaviaEnemy, self).__init__(**k)
            self.debug_info = DebugInfo(name="Славя", color="#FFD200", obj=self)

            self.__trigger = None

            self.__on_bulb = True
            def handler(state):
                self.__on_bulb = bool(state)

            global_event.on("enemy.bulb", handler)

        def update(self):
            if self.enemy_path.is_max_loc():
                self.near_the_house()
            else:
                self.try_move()

        def near_the_house(self):
            if self.__trigger is not None:
                return

            if self.time_murder():
                self.__trigger = game.trigger_system.add_trigger(
                    condition_fn=lambda: self.__on_bulb or self._is_door_closed,
                    action_fn=self.kill,
                    lifetime=3,
                    dead_fn=self.loss_kill
                )

        def time_murder(self):
            if self._time_murder is None:
                execute_in_main_thread(renpy.play, resources.sounds.sfx["enemy_deep_steps"], self.sound_channel)
                situation.next_situation("slavia.action")

            return super(SlaviaEnemy, self).time_murder()

        def kill(self):
            self.kill_player()

        def loss_kill(self):
            super(SlaviaEnemy, self).loss_kill()
            self._time_murder = None
            self.__trigger = None
            execute_in_main_thread(renpy.play, resources.sounds.voice.sl["1"], self.sound_channel)
            situation.next_situation("slavia.action.left")
            #execute_in_main_thread(renpy.play, resources.sounds.sfx["good_night"], self.sound_channel)

        def reset(self):
            if self.__trigger is not None:
                game.trigger_system.remove_trigger(self.__trigger)
                self.__trigger = None
            self.__on_bulb = True
            super(SlaviaEnemy, self).reset()

    class ShurikEnemy(EnemyAttackBase):
        def __init__(self, **k):
            super(ShurikEnemy, self).__init__(**k)
            self.debug_info = DebugInfo(name="Шурик", color="#FFF226", obj=self)

            self.__sprite_parallax = display.Parallax(
                displayable=self.sprite,
                zoom=1.15,
                anchor=(renpy.config.screen_width>>1, renpy.config.screen_height>>1),
                power=0.10,
                sharpness_factor=0.1
            )

            self.__is_in_house = False
            self.__bulb = True
            self.enemy_path.set_location(0)

            def handler(bulb):
                self.__bulb = bool(bulb)

            renpy.store.v1FNaSREvent.on("enemy.bulb", handler)

        def update(self):
            if self.__is_in_house:
                self.try_kill()
                return

            if self.enemy_path.is_max_loc():
                if self._is_door_closed:
                    return
                if self.try_move():
                    execute_in_main_thread(renpy.play, resources.sounds.sfx["enemy_deep_steps"], self.sound_channel)
                    self.__is_in_house = True
                    self.enemy_path.set_location(0)
                    self.show_sprite(self.__sprite_parallax, align=(0.1, 0.0))
                    situation.next_situation("shurik.action")
            else:
                self.try_move()

        def try_kill(self):
            if not self.__bulb:
                situation.next_situation("shurik.action.bulb")
            if self.time_murder():
                if not self.__bulb:
                    self.loss_kill()
                    situation.next_situation("shurik.action.left")
                    return False
                else:
                    self.kill_player()
                    return False

        def loss_kill(self):
            super(ShurikEnemy, self).loss_kill()
            self.enemy_path.set_location(0)
            self.__is_in_house = False
            self.hide_sprite()

        def reset(self):
            super(ShurikEnemy, self).reset()
            self.enemy_path.set_location(0)
            self.__is_in_house = False
            self.__bulb = True

    class ElectronicEnemy(EnemyAttackBase):
        def __init__(self, **k):
            super(ElectronicEnemy, self).__init__(**k)
            self.debug_info = DebugInfo(name="Электроник", color="#FFFF00", obj=self)
            self.enemy_path.set_location(0)

            self._is_left = False
            self.__bulb = True

            def handler(bulb):
                if bulb and situation.is_done("electronic.action"):
                    situation.next_situation("electronic.action.bulb")
                self.__bulb = bool(bulb)

            renpy.store.v1FNaSREvent.on("enemy.bulb", handler)

        def update(self):
            if self.move_chance():
                if self.__bulb:
                    self.backward_movement()
                else:
                    self.forward_movement()

        def loss_kill(self):
            super(ElectronicEnemy, self).loss_kill()
            self.enemy_path.set_location(0)

        def forward_movement(self):
            if self.enemy_path.is_max_loc():
                if not self._is_door_closed:
                    self.kill_player()
                return
            self.enemy_path.next_loc()
            if self._is_left and not situation.is_done("electronic.action"):
                self.movement_opportunities -= 2
                situation.next_situation("electronic.action")
            self._is_left = True

        def backward_movement(self):
            if self.enemy_path.is_min_loc() or self.enemy_path.location == 0:
                self.enemy_path.set_location(0)
                self._is_left = False
                if situation.is_done("electronic.action.bulb"):
                    situation.next_situation("electronic.action.fear")
                return
            self.enemy_path.previous_loc()

        def reset(self):
            super(ElectronicEnemy, self).reset()
            self.enemy_path.set_location(0)
            self.__bulb = True
            self._is_left = False

    class OlgaEnemy(EnemyAttackBase):
        BUTTON_KEY = "olga_enemy_button"

        def __init__(self, call_time, image_button, alpha_button, size_button, **k):
            super(OlgaEnemy, self).__init__(**k)

            self.debug_info = DebugInfo(
                name="Ольга",
                color="#00b627",
                obj=self
            )

            self.call_time = float(call_time)
            self.cooldown = self.call_time

            self.is_call_active = False
            self.is_call_answered = True
            self.is_button_visible = False

            self.button_image = renpy.store.Transform(
                image_button,
                alpha=alpha_button,
                size=size_button
            )

            self.button = renpy.display.behavior.ImageButton(
                idle_image=self.button_image,
                clicked=renpy.store.Function(self.answer_phone)
            )

            renpy.store.v1FNaSREvent.on(
                "camera_system.tablet",
                self.on_tablet_state_changed
            )

        # -------------------------------------------------

        def update(self):
            if self.is_call_active:
                self.sync_button_with_tablet()
                return

            if self.cooldown > 0:
                self.cooldown -= 1
                return

            if self.move_chance():
                self.start_call()

        # -------------------------------------------------

        def start_call(self):
            self.is_call_active = True
            self.is_call_answered = False

            execute_in_main_thread(
                renpy.music.play,
                resources.sounds.sfx["call"],
                #renpy.store.sfx_home_phone_ring,
                self.sound_channel,
                loop=True
            )

            game.trigger_system.add_trigger(
                condition_fn=lambda: self.is_call_answered,
                action_fn=self.on_call_answered,
                lifetime=self.call_time,
                dead_fn=self.kill_player
            )

        def end_call(self):
            self.is_call_active = False
            self.hide_button()
            self.cooldown = self.call_time

        # -------------------------------------------------

        def answer_phone(self):
            execute_in_main_thread(renpy.music.stop, self.sound_channel)
            execute_in_main_thread(
                renpy.music.play,
                resources.sounds.sfx["answer_phone"],
                self.sound_channel,
                loop=False
            )

            self.is_call_answered = True
            self.end_call()

        def on_call_answered(self):
            execute_in_main_thread(renpy.music.stop, self.sound_channel)
            self.end_call()

        # -------------------------------------------------

        def on_tablet_state_changed(self, tablet_opened):
            if not self.is_call_active:
                self.hide_button()
                return

            if tablet_opened:
                self.hide_button()
            else:
                self.show_button()

        def sync_button_with_tablet(self):
            self.on_tablet_state_changed(game.camera_system.show_tablet)

        # -------------------------------------------------

        def show_button(self):
            if self.is_button_visible:
                return

            self.is_button_visible = True

            game.object_display.add_obj(
                key=self.BUTTON_KEY,
                obj=self.button,
                position=(
                    random.randint(0, renpy.config.screen_width),
                    random.randint(0, renpy.config.screen_height)
                ),
                layer="screens"
            )

        def hide_button(self):
            if not self.is_button_visible:
                return

            self.is_button_visible = False
            game.object_display.pop_obj(self.BUTTON_KEY)

        # -------------------------------------------------

        def reset(self):
            super(OlgaEnemy, self).reset()
            self.is_call_active = False
            self.is_call_answered = True
            self.is_button_visible = False
            self.cooldown = self.call_time
            self.hide_button()

        def loss_kill(self):
            super(OlgaEnemy, self).loss_kill()
            self.answer_phone()

    class YuliaEnemy(EnemyBase):
        def __init__(self, increased_panic=1, ignore_second=3, **k):
            self.debug_info = DebugInfo(
                name="Юля",
                color="#40d000",
                obj=self
            )

            super(YuliaEnemy, self).__init__(**k)
            self._in_house = False
            self._increased_panic = increased_panic
            self._ignore_second = ignore_second
            self._ignore = 0
            self._is_start_situation = False

            self.__sprite_parallax = display.Parallax(
                displayable=self.sprite,
                zoom=1.15,
                anchor=(renpy.config.screen_width>>1, renpy.config.screen_height>>1),
                power=0.10,
                sharpness_factor=0.1
            )

        def update(self):
            if self._in_house:
                if not game.camera_system.show_tablet:
                    situation.next_situation("yulia.action")
                self.increased_panic()
                return

            if self.enemy_path.is_max_loc():
                if not game.door_system.is_door_open:
                    return
                if self.try_move():
                    execute_in_main_thread(renpy.play, resources.sounds.sfx["enemy_deep_steps"], self.sound_channel)
                    self.show_sprite(self.__sprite_parallax)
                    self._in_house = True
                    self.enemy_path.set_location(0)
                    
                    c = game.camera_system.get_camera(4)
                    if c is not None and self in c.enemy:
                        c.enemy.remove(self)
                    if not game.camera_system.show_tablet:
                        situation.next_situation("yulia.action")
            else:
                self.try_move()


        def increased_panic(self):
            if game.camera_system.show_tablet:
                if not self._is_start_situation and situation.is_done("yulia.action"):
                    self._is_start_situation = True
                    situation.next_situation("yulia.action.tablet")
                self._ignore += 1
                if self._ignore >= self._ignore_second:
                    self.hide_sprite()
                    self.enemy_path.next_loc()
                    self._ignore = 0
                    self._in_house = False
                    self._is_start_situation = False
            else:
                self._ignore = 0

            if game.door_system.is_door_open:
                game.door_system.add_panic(self._increased_panic+1)
            else:
                game.door_system.add_panic(self._increased_panic)

        def reset(self):
            super(YuliaEnemy, self).reset()
            self._in_house = False
            self._ignore = 0
            self._is_start_situation = False

    class ZhenyaEnemy(EnemyAttackBase):
        NOISE_MAX = 100
        KILL_COUNT_MAX = 5
        NOISE_STEP = 1

        def __init__(self, mz_camera_id, image_button, button_align=(0.2, 0.89), text_align=(0.2, 0.89), **kwargs):
            super(ZhenyaEnemy, self).__init__(**kwargs)

            self.mz_camera_id = mz_camera_id

            self.noise_level = 0
            self.kill_count = 3
            self.noise_source = None

            self._is_playing_sound = False
            self._selected_camera = 0
            self._crutch = False

            self.key_text = "mz_enemy_noise_level_text"
            self.key_button = "mz_enemy_noise_source_button"

            self.text_align = text_align
            self.button_align = button_align
            self.image_button = image_button

            self._text_noise_level = self._create_noise_text()
            self._button = self._create_button()

            global_event.on("camera_system.tablet", self.tablet_handler)
            global_event.on("camera_system.select_camera", self.select_handler)

            self.debug_info = DebugInfo(
                name="Женя",
                color="#5481db",
                obj=self,
                additional_info=[
                    ("noise_level", lambda: self.noise_level),
                    ("noise_source", lambda: self.noise_source),
                ]
            )

        # ------------------------------------------------------------------ UI

        def _create_noise_text(self):
            return renpy.store.Text(
                self._noise_text(),
                style="v1_text_24_style_FNaSR"
            )

        def _noise_text(self):
            return "noise: {}/{}".format(self.noise_level, self.NOISE_MAX)

        def _create_button(self):
            return renpy.store.ImageButton(
                idle_image=renpy.store.Transform(
                    resources.images.other[self.image_button],
                    xysize=(145, 30)
                ),
                clicked=renpy.store.Function(self.destroy_noise_source)
            )

        def _update_text(self):
            self._text_noise_level.text = self._noise_text()

        def _show_button(self, show=True):
            display = game.object_display
            display.pop_obj(self.key_button)

            if show:
                if situation.is_done("zhenya.action.noise.button"):

                    situation.next_situation("zhenya.action.noise.button.show")
                display.add_obj(
                    key=self.key_button,
                    obj=self._button,
                    layer="screens",
                    align=self.button_align
                )

        def _show_text(self, show=True):
            self._text_noise_level = self._create_noise_text()
            display = game.object_display
            display.pop_obj(self.key_text)
            if show:
                display.add_obj(
                    key=self.key_text,
                    obj=self._text_noise_level,
                    layer="screens",
                    align=self.text_align
                )

        # ------------------------------------------------------------------ Events

        def select_handler(self, camera_id):
            if self.activity is False:
                return
            self._selected_camera = camera_id
            self._sync_ui()

        def tablet_handler(self, is_show):
            if self.activity is False:
                return
            if is_show:
                self.select_handler(game.camera_system.select)
            else:
                self._hide_ui()

        def _sync_ui(self):
            tablet = game.camera_system.show_tablet
            show_button = tablet and self._selected_camera == self.noise_source
            show_text = tablet and self._selected_camera == self.mz_camera_id

            self._show_button(show_button)
            self._show_text(show_text)

        def _hide_ui(self):
            self._show_button(False)
            self._show_text(False)

        # ------------------------------------------------------------------ Game loop

        def update(self):
            self._update_noise()
            self._update_kill_progress()

            if self.noise_source is None and self.move_chance():
                self.spawn_noise_source()

            self._sync_sound()
            self._sync_ui()

        # ------------------------------------------------------------------ Noise

        def _update_noise(self):
            delta = self.NOISE_STEP if self.noise_source is not None else -self.NOISE_STEP
            self.noise_level = max(0, min(self.NOISE_MAX, self.noise_level + delta))
            if not situation.is_done("zhenya.action.noise.5") and self.noise_level > 5:
                situation.next_situation("zhenya.action.noise.5")
                def _a():
                    self._crutch = True
                game.game_time.timer(_a, 5)
            if situation.is_done("zhenya.action.noise.5") and game.camera_system.show_tablet and self._crutch:
                situation.next_situation("zhenya.action.noise.button")
                self._crutch = False

            if self.noise_level >= 80:
                situation.next_situation("zhenya.action.noise.80")
            elif self.noise_level >= 70:
                situation.next_situation("zhenya.action.noise.70")
            

        def spawn_noise_source(self):
            active = [c.id for c in game.camera_system.list_cameras if c.is_active]
            if active:
                self.noise_source = random.choice(active)
                game.camera_system.sound_controller.set_noise_source(self.noise_source)
                situation.next_situation("zhenya.action")

        def destroy_noise_source(self):
            self.noise_source = None
            self._sync_sound()
            game.camera_system.sound_controller.delete_noise_source()
            game.object_display.pop_obj(self.key_button)
            if situation.is_done("zhenya.action.noise.button.show"):
                situation.next_situation("zhenya.action.noise.button.hide")
            if (situation.is_done("zhenya.action.noise.70") or situation.is_done("zhenya.action.noise.80")) and self.noise_level > 70:
                situation.next_situation("zhenya.action.noise.salvation")

        # ------------------------------------------------------------------ Sound

        def _sync_sound(self):
            should_play = self.noise_source is not None

            if should_play and not self._is_playing_sound:
                self._is_playing_sound = True
                execute_in_main_thread(
                    renpy.music.play,
                    resources.sounds.music["Music_Box_Melody_Playful"],
                    "v1_noise_FNaSR",
                    loop=True
                )

            elif not should_play and self._is_playing_sound:
                self._is_playing_sound = False
                execute_in_main_thread(renpy.music.stop, "v1_noise_FNaSR")

        # ------------------------------------------------------------------ Kill logic

        def _update_kill_progress(self):
            if self.noise_level >= self.NOISE_MAX:
                self.kill_count -= 1
            else:
                self.kill_count = min(self.KILL_COUNT_MAX, self.kill_count + 1)

            if self.kill_count <= 0:
                self.kill_player()

        # ------------------------------------------------------------------ Reset

        def loss_kill(self):
            super(ZhenyaEnemy, self).loss_kill()
            self.reset()

        def reset(self):
            super(ZhenyaEnemy, self).reset()
            self.noise_level = 0
            self.kill_count = 3
            self.noise_source = None
            self._is_playing_sound = False
            self._selected_camera = 0
            self._crutch = False
            #self._hide_ui()

    class ViolaEnemy(EnemyAttackBase):
        def __init__(self, spawn_camera_id, seconds_running=6, **kwargs):
            super(ViolaEnemy, self).__init__(**kwargs)

            self.stage = 0
            self.selected_camera = 0
            self.show_tablet = False
            self.spawn_camera_id = spawn_camera_id
            self.check_count = 0
            self.timer_created = False
            self.seconds_running = seconds_running
            self._look_stage = False

            global_event.on("camera_system.tablet", self.tablet_handler)
            global_event.on("camera_system.select_camera", self.select_handler)

            self.debug_info = DebugInfo(
                name="Виола",
                color="#8686e6",
                obj=self,
                additional_info=[
                    ("stage", lambda: self.stage),
                    ("check_count", lambda: self.check_count),
                ]
            )

        def select_handler(self, camera_id):
            if self.activity is False:
                return
            self.show_enemy(True, selected_camera=camera_id)

        def tablet_handler(self, is_show):
            if self.activity is False:
                return

            self.show_tablet = bool(is_show)

            if is_show:
                game.game_time.timer(self.show_enemy, sleep=0.19, show_tablet=is_show)
            else:
                self.show_enemy(is_show)


        def update(self):
            if self.stage <= 3:
                self.timer_created = False
                if self.move_chance():
                    self.stage += 1
                    self.check_count = 0
                    self.show_enemy(self.show_tablet, selected_camera=self.selected_camera)
            else:
                self.create_timer()

        def create_timer(self):
            with lock:
                if self.timer_created:
                    return

                game.game_time.timer(self.try_kill, sleep=self.seconds_running)
                self.timer_created = True

        def try_kill(self):
            if game.door_system.is_door_open:
                self.kill_player()
                return True
            else:
                self.loss_kill()
                execute_in_main_thread(renpy.play, renpy.store.sfx_campus_door_rattle, self.sound_channel)
                return False

        def loss_kill(self):
            situation.next_situation("viola.action.door")
            if situation.is_done("viola.action.observation"):
                game.game_time.timer(situation.next_situation, 3.5, "viola.action.relief")
            super(ViolaEnemy, self).loss_kill()
            self.stage = 0
            self._look_stage = False

        def show_enemy(self, show_tablet, selected_camera=None):
            show_tablet = bool(show_tablet)
            if selected_camera is not None:
                self.selected_camera = selected_camera

            if show_tablet and self.selected_camera == self.spawn_camera_id:
                self.check_count += 2
                if self.stage and self.check_count >= 8:
                    situation.next_situation("viola.action.observation")
                if self.stage == 1:
                    self._look_stage = True
                    situation.next_situation("viola.action.1")
                    self.hide_sprite()
                    self.show_sprite(renpy.store.Transform(
                        self.sprite,
                        xalign=0.5
                    ))
                elif self.stage == 2:
                    self._look_stage = True
                    situation.next_situation("viola.action.2")
                    self.hide_sprite()
                    self.show_sprite(renpy.store.Transform(
                        self.sprite,
                        xalign=0.1
                    ))
                elif self.stage == 3:
                    self._look_stage = True
                    self.hide_sprite()
                    self.show_sprite(renpy.store.Transform(
                        self.sprite,
                        xalign=-1.0,
                        rotate=30
                    ))
                else:
                    if self._look_stage:
                        situation.next_situation("viola.action.6seconds")
                    self.hide_sprite()
            else:
                self.hide_sprite()

        def calculate_change_factor(self):
            random_roll = super(ViolaEnemy, self).calculate_change_factor()

            return random_roll - self.check_count

        def reset(self):
            self.stage = 0
            self.selected_camera = 0
            self.check_count = 0
            self.timer_created = False
            self._look_stage = False

    class PioneerEnemy(EnemyAttackBase):
        def __init__(self, **k):
            super(PioneerEnemy, self).__init__(**k)
            self.debug_info = DebugInfo(name="Пионер", color="#e60000", obj=self)

            self.is_start_qte = False
            self.qte_handler = QTETools.create_qte_handler(
                on_success=self.on_qte_success,
                on_fail=self.on_qte_fail
            )

            self._parallax_sprite = display.Parallax(
                displayable=self.sprite,
                zoom=1.15,
                anchor=(renpy.config.screen_width>>1, renpy.config.screen_height>>1),
                power=0.10,
                sharpness_factor=0.1
            )

            self._in_home = False

            self.show_tablet = False
            def handler(tablet_status):
                self.show_tablet = bool(tablet_status)
                if not self.show_tablet and self._in_home:
                    self.show_sprite(self._parallax_sprite)
            global_event.on("camera_system.tablet", handler)

        def update(self):
            if self._in_home:
                if not self.show_tablet:
                    self.start_qte()
                return

            if self.enemy_path.is_max_loc():
                if self._is_door_closed:
                    return
                if self.try_move():
                    self._in_home = True
                    self.enemy_path.set_location(0)
                    if not self.show_tablet:
                        self.show_sprite(self._parallax_sprite)
            else:
                self.try_move()

        def start_qte(self):
            if self.is_start_qte:
                return
            self.is_start_qte = True

            self._is_bulb = game.mainL.is_bulb
            self._is_tablet = game.mainL.has_tablet
            self._is_door = game.mainL.is_door

            key = self.get_random_key()
            time = self.get_random_time()
            align = self.get_random_align()

            execute_in_main_thread(QTETools.start_qte, key, time, align, qte_handler=self.qte_handler)

        def on_qte_success(self):
            try:
                game.mainL.is_bulb =  self._is_bulb
                game.mainL.has_tablet =  self._is_tablet
                game.mainL.is_door =  self._is_door
            except Exception:
                pass

            self._reset_qte_handler()
            self._in_home = False
            self.enemy_path.set_location(0)
            self.enemy_path.next_loc()
            self.hide_sprite()

        def on_qte_fail(self):
            self._reset_qte_handler()
            self.kill_player()

        def _reset_qte_handler(self):
            self.is_start_qte = False
            QTETools.reset_qte_handler(self.qte_handler)

        def kill_player(self):
            self._in_home = False
            super(PioneerEnemy, self).kill_player()

        def loss_kill(self):
            super(PioneerEnemy, self).loss_kill()
            self.on_qte_success()


        def get_random_key(self):
            return random.choice(Constants.KEYS)

        def get_random_time(self):
            return random.uniform(2.0, 3.5)

        def get_random_align(self):
            return (random.uniform(0.2, 0.8), random.uniform(0.2, 0.8))


        def reset(self):
            super(PioneerEnemy, self).reset()
            self._in_home = False
            self._reset_qte_handler()
















    class GendaSolo(EnemyAttackBase):
        """
        Класс Замечательного ГеНдЫ с механикой исчезновения и атаки.
        
        Механика:
        - Генда исчезает с камеры при успешной проверке
        - Игрок должен заметить исчезновение на заданной камере
        - Если игрок закрыл планшет после обнаружения - атака
        - Если игрок открыл планшет во время атаки - провал атаки
        """
        
        # Количество проверок для гарантированного исчезновения
        MOVE_CHECKS_COUNT = 6
        
        def __init__(self, genda_camera_id=1, attack_delay=1.5, 
                    genda_none_image="anim v1_ext_square_night_party_genda_none_anim_FNaSR", 
                    **kwargs):
            """
            Инициализация крутого и неповторимого ~ГеНдЫ~.
            
            Args:
                genda_camera_id: ID камеры где появляется Генда (по умолчанию 1)
                attack_delay: Задержка перед убийством в секундах (по умолчанию 1.5)
                genda_none_image: Изображение пустой камеры после исчезновения
                **kwargs: Дополнительные параметры для базового класса
            """
            super(GendaSolo, self).__init__(**kwargs)
            
            # Параметры конфигурации
            self._genda_camera_id = genda_camera_id
            self._attack_delay = attack_delay
            self._genda_none_image = genda_none_image
            
            # Состояние Генды
            self._disappeared = False
            self._player_noticed_disappearance = False
            self._attack = False
            
            # Сохранение оригинального изображения камеры
            self._old_image = None
            
            # Состояние интерфейса
            self._selected_camera = genda_camera_id
            self._show_tablet = False
            
            # Регистрация обработчиков событий
            global_event.on("camera_system.tablet", self._on_tablet_change)
            global_event.on("camera_system.select_camera", self._on_camera_select)
            
            # Инициализация отладочной информации
            self.debug_info = DebugInfo(
                name="Генда",
                color="#494949",
                obj=self,
                additional_info=[
                    ("disappeared", lambda: self._disappeared),
                    ("player_noticed_disappearance", lambda: self._player_noticed_disappearance),
                    ("attack", lambda: self._attack),
                ]
            )
        
        def _on_tablet_change(self, tablet_status):
            """
            Обработчик изменения состояния планшета.
            
            Args:
                tablet_status: True если планшет открыт, False если закрыт
            """
            self._show_tablet = bool(tablet_status)
            
            # Игрок заметил исчезновение на правильной камере
            if (self._disappeared and 
                not self._player_noticed_disappearance and 
                self._selected_camera == self._genda_camera_id and 
                self._show_tablet):
                self._player_noticed_disappearance = True
            
            # Игрок открыл планшет во время атаки - провал атаки
            if self._attack and self._show_tablet:
                self.loss_kill()
            # Игрок закрыл планшет после обнаружения - начало атаки
            elif not tablet_status and self._disappeared and self._player_noticed_disappearance:
                self.attack_player()
        
        def _on_camera_select(self, camera_id):
            """
            Обработчик выбора камеры.
            
            Args:
                camera_id: ID выбранной камеры
            """
            self._selected_camera = camera_id
            
            # Игрок посмотрел на камеру Генды и заметил исчезновение
            if (self._disappeared and 
                not self._player_noticed_disappearance and 
                camera_id == self._genda_camera_id):
                self._player_noticed_disappearance = True
        
        def _check_multiple_move_chances(self):
            """
            Проверка нескольких шансов на перемещение подряд.
            
            Returns:
                bool: True если все проверки успешны
            """
            range_check = max(1, self.MOVE_CHECKS_COUNT - Settings.game_difficulty.level)
            return all(self.move_chance() for _ in range(range_check))
        
        def _change_camera_image(self, camera_id, new_image):
            """
            Изменить изображение камеры.
            
            Args:
                camera_id: ID камеры
                new_image: Новое изображение для камеры
            
            Returns:
                str or None: Старое изображение камеры или None
            """
            camera = game.camera_system.get_camera(camera_id)
            if camera is None:
                return None
            
            old_image = camera.image
            camera.image = new_image
            return old_image
        
        def _restore_camera_image(self):
            """Восстановить оригинальное изображение камеры."""
            if self._old_image is not None:
                camera = game.camera_system.get_camera(self._genda_camera_id)
                if camera is not None:
                    camera.image = self._old_image
                    self._old_image = None
        
        def update(self):
            # Если Генда уже исчез, ничего не делаем
            if self._disappeared:
                return
            
            # Проверка на исчезновение
            if self._check_multiple_move_chances():
                self._disappeared = True
                
                # Сохранение и изменение изображения камеры
                self._old_image = self._change_camera_image(
                    self._genda_camera_id,
                    self._genda_none_image
                )
                
                # Если игрок смотрит на камеру в момент исчезновения
                if self._selected_camera == self._genda_camera_id and self._show_tablet:
                    self._player_noticed_disappearance = True
        
        def attack_player(self):
            """
            Начало атаки на игрока.
            Показывает спрайт и воспроизводит звук атаки.
            """
            
            # Запускаем атаку только один раз
            if not self._attack:
                # Показать спрайт атаки по центру экрана
                self.show_sprite(align=(0.5, 0.5))
                
                # Воспроизвести звук атаки
                execute_in_main_thread(
                    renpy.music.play,
                    resources.sounds.sfx["genda_aaaaa"],
                    self.sound_channel,
                    loop=False
                )
                
                # Запланировать убийство игрока через заданное время
                game.game_time.timer(self.try_kill, sleep=self._attack_delay)
                self._attack = True
        
        def try_kill(self):
            """
            Попытка убить игрока.
            Вызывается через attack_delay секунд после начала атаки.
            
            Returns:
                bool: True если игрок был убит, False если атака была прервана
            """
            if self._attack:
                self.kill_player()
                return True
            return False
        
        def loss_kill(self):
            """
            Провал атаки (игрок открыл планшет).
            Сброс состояния атаки и восстановление камеры.
            """
            # Остановить звук и скрыть спрайт
            execute_in_main_thread(renpy.music.stop, self.sound_channel)
            self.hide_sprite()
            
            # Сбросить все флаги состояния
            self._disappeared = False
            self._player_noticed_disappearance = False
            self._attack = False
            
            # Восстановить оригинальное изображение камеры
            self._restore_camera_image()
            
            return super(GendaSolo, self).loss_kill()
        
        def reset(self):
            """
            Полный сброс состояния врага.
            Вызывается при перезапуске игры или ночи.
            """
            self.loss_kill()
            return super(GendaSolo, self).reset()



















