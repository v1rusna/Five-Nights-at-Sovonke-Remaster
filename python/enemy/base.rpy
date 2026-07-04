init python in v1FNaSR:
    try:
        from builtins import map as v1_map
    except:
        from __builtins__ import map as v1_map

    class EnemyBase(FNaSRBase):
        def __init__(self, tag, sprite, nights_start, paths, ai_level, max_movement_opportunities=3, class_screamer=None, screamer_sound=None, transform_data=None):
            """
            tag                 - тег противника
            sprites             - спрайты противника (первый спрайт будет взят за основу)
            nights_start        - ночь с которой противник активен
            paths               - список путей который состоит из id камер, например [13, 1, 4] - противник начнет с причала, после пойдёт на площадь, и далее к домику ольги 
            ai_level            - Уровень противника
            class_screamer=None - класс скримера, если None будет использоваться стандартный класс 'EnemyScreamer'
            screamer_sound=None - звук скримера, если None будет использоваться стандартный
            transform_data=None - какие transform использовать для скримера, объект класса 'TransformScreamer'
            """
            self.tag = tag
            #self.sprites = map(lambda _s: renpy.store.Transform(_s, matrixcolor=renpy.store.SaturationMatrix(0.4)), sprites)
            self.sprite = renpy.store.Transform(sprite, matrixcolor=renpy.store.SaturationMatrix(0.4))
            self.original_sprite = sprite
            self.nights_start = nights_start
            self.activity = True
            self.position = [random.randint(0, 999), 0]
            self.class_screamer = class_screamer
            if self.class_screamer is not None:
                self.class_screamer.enemy = self
            else:
                self.class_screamer = EnemyScreamer(self)


            self._v1_default = dict()
            self._v1_default["ai_level"] = ai_level

            self.ai_level = ai_level
            self.movement_opportunities = 0
            self.max_movement_opportunities = max_movement_opportunities
            self.difficulty = 0
            self._attempts_move = 0


            self.screamer_sound = screamer_sound
            self.transform_data = transform_data

            if (isinstance(paths, type) and issubclass(paths, AutoGeneratePath)):
                self.enemy_path = AutoGeneratePath(self)
            elif isinstance(paths, list):
                if paths and (isinstance(paths[0], type) and issubclass(paths[0], AutoGeneratePath)):
                    path = paths.pop(0)
                    self.enemy_path = path(self, *paths)
                else:
                    self.enemy_path = EnemyPath(self, *paths)
            else:
                raise TypeError("The 'paths' parameter must be a list or an AutoGeneratePath subclass.")

            self.enemy_path.next_loc()

            if screamer_sound is None:
                self.screamer_sound = resources.sounds.sfx["enemy_screamer_1"]

            if transform_data is None:
                self.transform_data = TransformScreamer()

            self._sprite_key = "{}_{}_{}".format(self.__class__.__name__, self.tag, self.sprite)

            self.sound_channel = "v1_enemy_%s_sfx_FNaSR" % self.tag
            Tools._register_channel(self.sound_channel, mixer="sound", loop=False)

            self._v1_show_sprite = False

        def update(self):
            self.try_move()

        def try_move(self):
            if self.move_chance():
                self.enemy_path.next_loc()
                self.position = [renpy.random.randint(0, 999), 0]
                return True
            
            return False

        def move_chance(self):
            difficulty_multiplier = 1 + (game.game_time.total_hours * 0.1)
            movement_chance = min(Constants.MAX_AI_LEVEL, math.ceil(self.ai_level * difficulty_multiplier))

            self.movement_opportunities += 1

            if self.movement_opportunities >= self.max_movement_opportunities:
                self.movement_opportunities = 0
                random_roll = self.calculate_change_factor()
                result = random_roll <= movement_chance

                self.handle_attempts_move(result)

                return result
            return False

        def calculate_change_factor(self):
            n1, n2 = Constants.ENEMY_MOVE_CHANCE_FACTOR_RANGE
            return random.randint(n1, n2) - min(len(self.enemy_path) + self._attempts_move + self.difficulty * 2, Constants.MAX_CHANGE_FACTOR_PENALTY)

        def handle_attempts_move(self, result):
            if result:
                self._attempts_move = 0
            else:
                self._attempts_move += 1

        def reset(self):
            self.enemy_path.reset()
            self.activity = True
            self.movement_opportunities = 0
            self.difficulty = 0
            self._attempts_move = 0
            self._v1_show_sprite = False
            self.ai_level = self._v1_default["ai_level"]
            self.hide_sprite()
            execute_in_main_thread(renpy.music.stop, self.sound_channel)

        def show_sprite(self, sprite=None, **k):
            if not self._v1_show_sprite:
                if sprite is None:
                    sprite = self.sprite
                game.object_display.add_obj(
                    key=self._sprite_key,
                    obj=sprite,
                    **k
                )
                self._v1_show_sprite = True

        def hide_sprite(self):
            if self._v1_show_sprite:
                game.object_display.pop_obj(self._sprite_key)
                self._v1_show_sprite = False

        def __repr__(self):
            return "<{} tag={} at {}>".format(self.__class__.__name__, self.tag, hex(id(self)))

    class EnemyAttackBase(EnemyBase):
        def __init__(self, time_murder_variation=(3,5), **enemy_kwargs):
            super(EnemyAttackBase, self).__init__(**enemy_kwargs)

            self._t_m_v = time_murder_variation
            self._time_murder = None
            self._is_door_closed = False

            def set_door_state(state):
                self._is_door_closed = bool(state)

            global_event.on("door_system.door_use", set_door_state)

        def update(self):
            if self.enemy_path.is_max_loc():
                self.try_kill()
            else:
                self.try_move()

        def kill_player(self):
            game.enemy_system.enemy_killer = self

        def loss_kill(self):
            self.enemy_path.next_loc()

        def try_kill(self):
            if self.time_murder():
                if self._is_door_closed:
                    self.loss_kill()
                    execute_in_main_thread(renpy.play, renpy.store.sfx_campus_door_rattle, self.sound_channel)
                    return False
                else:
                    self.kill_player()
                    return True

        def get_time_murder(self):
            return renpy.random.randint(self._t_m_v[0], self._t_m_v[1])

        def time_murder(self):
            if self._time_murder is None:
                self._time_murder = self.get_time_murder()

            if self._time_murder:
                self._time_murder -= 1
                return False
            else:
                self._time_murder = None
                return True

        def reset(self):
            super(EnemyAttackBase, self).reset()
            self._time_murder = None
            self._is_door_closed = False






