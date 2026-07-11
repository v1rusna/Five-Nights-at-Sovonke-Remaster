init 5 python in v1FNaSR:
    class DoorSystem(FNaSRBase):
        def __init__(self):
            self._is_open = True
            self.panic = 0
            self.rollback = False

            self.__max_panic = Constants.DEFAULT_MAX_PANIC
            self.__rollback_threshold = Constants.DEFAULT_ROLLBACK_THRESHOLD
            self.__is_play_heartbeat = False

            self.door_ImageButton = renpy.store.v1rus.HoldingMouseImageButton(
                idle=resources.images.other["button_unclick"],
                clicked=resources.images.other["button_click"],
                click_action=renpy.store.Function(self.door, True),
                unclick_action=renpy.store.Function(self.door, False),
                allow_alternate=False
            )

        @property
        def is_door_open(self):
            return self._is_open

        @property
        def max_panic(self):
            return self.__max_panic

        @property
        def rollback_threshold(self):
            return self.__rollback_threshold

        def set_max_panic(self, value):
            value = int(value)
            if value > 0 or True:
                self.__max_panic = value
            if self.panic > self.__max_panic:
                self.panic = self.__max_panic

        def set_rollback_threshold(self, value):
            value = int(value)
            if value > 0:
                self.__rollback_threshold = value
            if self.rollback and self.panic <= self.__rollback_threshold:
                self.rollback = False

        def get_text(self):
            return "panic: {}/{}".format(self.panic, self.__max_panic)

        def door(self, status):
            if self.rollback:
                return

            status = bool(status)

            self._is_open = not status
            global_event.emit("door_system.door_use", status)

            if status:
                execute_in_main_thread(renpy.play, renpy.store.sfx_door_squeak_light, "sound")
                execute_in_main_thread(renpy.show, name="v1_door_hold_vignette_FNaSR", at_list=[renpy.store.v1_door_hold_vignette_appear_FNaSR], what="v1_door_hold_vignette_FNaSR", layer="screens")

                return

            execute_in_main_thread(renpy.play, resources.sounds.sfx["door_unhold"], "sound")
            execute_in_main_thread(renpy.show, name="v1_door_hold_vignette_FNaSR", at_list=[renpy.store.v1_door_hold_vignette_disappear_FNaSR], what="v1_door_hold_vignette_FNaSR", layer="screens")

        def open_door(self):
            self.door(False)

        def close_door(self):
            self.door(True)

        def update(self):
            if not self._is_open:
                self.panic += 1
            elif self.panic > 0:
                self.panic -= 1
            elif self.panic < 0:
                self.panic = 0

            if self.panic >= self.__max_panic / 2 and not self.__is_play_heartbeat:
                self.__is_play_heartbeat = True
                execute_in_main_thread(renpy.music.play, renpy.store.sfx_head_heartbeat, channel="v1heartbeatFNaSR", loop=True, fadein=2)
            elif self.panic < self.__max_panic / 2 and self.__is_play_heartbeat:
                self.__is_play_heartbeat = False
                execute_in_main_thread(renpy.music.stop, channel="v1heartbeatFNaSR", fadeout=2)

            if not self._is_open and self.panic >= self.__max_panic and not self.rollback:
                execute_in_main_thread(renpy.music.play, resources.sounds.sfx["panic_breathing_1"], channel="v1breathingFNaSR", loop=True, fadein=2)
                self.door(False)
                self.rollback = True

            if self.rollback and self.panic <= self.__rollback_threshold:
                execute_in_main_thread(renpy.music.stop, channel="v1breathingFNaSR", fadeout=2)
                self.rollback = False

            renpy.restart_interaction()

        def add_panic(self, panic=1):
            self.panic += int(panic)

            if self.panic > self.__max_panic:
                self.panic = self.__max_panic
            elif self.panic < 0:
                self.panic = 0

            if not self._is_open and self.panic >= self.__max_panic:
                self.door(False)
                self.rollback = True
            if self.rollback and self.panic <= self.__rollback_threshold:
                self.rollback = False

        def reset(self):
            self.door_ImageButton.force_unclick()
            self._is_open = True
            self.panic = 0
            self.rollback = False

            self.__max_panic = Constants.DEFAULT_MAX_PANIC
            self.__rollback_threshold = Constants.DEFAULT_ROLLBACK_THRESHOLD
