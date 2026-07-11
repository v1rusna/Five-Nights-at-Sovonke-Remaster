init 11 python in v1FNaSR:
    class EnemySystem(FNaSRBase):
        def __init__(self):
            self.enemy_chanel = {}
            self.enemy_killer = None
            self.__enemy_list = list()
            self.__enemy_dict = dict()

        def __iter__(self):
            return iter(list(self.__enemy_list))

        def add_enemy(self, enemy):
            if not isinstance(enemy, EnemyBase):
                raise Exception("The 'enemy' parameter must be 'EnemyBase' or inherit from it.")

            if enemy.tag in self.__enemy_dict:
                raise Exception("The enemy tag '{}' is already in use.".format(enemy.tag))

            self.__enemy_list.append(enemy)
            self.__enemy_dict[enemy.tag] = enemy
            self.enemy_chanel[enemy.tag] = enemy.sound_channel

        def remove_enemy(self, enemy_or_tag):
            if isinstance(enemy_or_tag, EnemyBase):
                _e = enemy_or_tag
            else:
                _e = self.__enemy_dict.pop(enemy_or_tag, None)
                self.enemy_chanel.pop(enemy_or_tag, None)

            if _e in self.__enemy_list:
                self.__enemy_list.remove(_e)

        def get_enemy(self, tag, default=None):
            return self.__enemy_dict.get(tag, default)

        def get_enemy_list(self):
            return list(self.__enemy_list)

        def update(self):
            for enemy in self.__enemy_list:
                if enemy.activity:
                    enemy.update()

        def reset(self):
            self.enemy_killer = None
            self.reset_enemy()

        def reset_enemy(self):
            for e in self.__enemy_list:
                e.reset()

    class EnemyScreamer(FNaSRBase):
        def __init__(self, enemy=None):
            """enemy не должен быть None перед проигрышем"""
            self.enemy = enemy
        def __call__(self):
            enemy = self.enemy

            renpy.music.play(filenames=enemy.screamer_sound, channel="v1_screamer_sfx_FNaSR")

            if enemy.transform_data.is_black_fade:
                renpy.show("black_fade", [enemy.transform_data.bg_t()], "screens", renpy.store.Solid("#000"), zorder=49)
            renpy.show(name="v1_%s_s" % enemy.tag, at_list=[enemy.transform_data.screamer_t], what=enemy.sprite, layer="screens", zorder=50)
            renpy.show_layer_at(at_list=[enemy.transform_data.camera_t], layer="master", reset=False, camera=True)
            if enemy.transform_data.is_screen_t:
                renpy.show_layer_at(at_list=[enemy.transform_data.camera_t], layer="screens", reset=False, camera=True)

            renpy.block_rollback()
            renpy.pause(2, hard=True)

            if enemy.transform_data.is_black_fade:
                renpy.hide("black_fade", "screens")
            renpy.hide("v1_%s_s" % enemy.tag, "screens")
            renpy.show_layer_at(at_list=[], layer="master", reset=False, camera=True)
            if enemy.transform_data.is_screen_t:
                renpy.show_layer_at(at_list=[], layer="screens", reset=False, camera=True)

            renpy.show("black")
            renpy.block_rollback()
            renpy.pause(1, hard=True)

    class TransformScreamer(FNaSRBase):
        def __init__(self, screamer_t=None, camera_t=None, bg_t=None, is_screen_t=False, is_black_fade=False):
            self.screamer_t = screamer_t
            self.camera_t = camera_t
            self.bg_t = bg_t
            self.is_screen_t = is_screen_t
            self.is_black_fade = is_black_fade

            if screamer_t is None:
                self.screamer_t = renpy.store.v1_slavya_screamer_t_FNaSR
            if camera_t is None:
                self.camera_t = renpy.store.v1_general_screamer_camera_t_FNaSR
            if bg_t is None:
                self.bg_t = renpy.store.v1_fading_t_FNaSR(0.8, 0.0, 0.85, renpy.store._warper.easein_quad)







