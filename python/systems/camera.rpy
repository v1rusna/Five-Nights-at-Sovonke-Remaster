init python in v1FNaSR:
    class StateCameraSystem:
        TABLET_CLOSE = "tablet.close"
        TABLET_OPEN = "tablet.open"

    class _CameraConnections:
        def __init__(self, connections):
            if connections is None:
                self._data = set()
            elif isinstance(connections, int):
                self._data = {connections}
            elif isinstance(connections, (list, tuple, set)):
                self._data = set(connections)
            else:
                raise Exception("The 'connections' parameter must be 'int', 'list', 'tuple', 'set' or 'NoneType'.")

        def _add(self, value):
            self._data.add(value)

        # Добавление одного элемента
        def add(self, value):
            self._data.add(value)
            game.camera_system.generate_connections()

        # Удаление элемента
        def remove(self, value):
            self._data.remove(value)
            game.camera_system.generate_connections()

        # Безопасное удаление (не бросает ошибку)
        def discard(self, value):
            self._data.discard(value)
            game.camera_system.generate_connections()

        # Возврат количества элементов
        def __len__(self):
            return len(self._data)

        # Проверка "value in connections"
        def __contains__(self, value):
            return value in self._data

        # Итерация: for x in connections
        def __iter__(self):
            return iter(self._data)

        # Индексация: obj[0]
        def __getitem__(self, index):
            # Преобразуем set к упорядоченному списку
            data_list = list(self._data)
            return data_list[index]

        def __delitem__(self, index):
            lst = list(self._data)
            del lst[index]
            self._data = set(lst)
            game.camera_system.generate_connections()

        # Преобразование в список при необходимости
        def to_list(self):
            return list(self._data)

        # Простой вывод в log / debug
        def __repr__(self):
            return "_CameraConnections(%s)" % list(self._data)

    class Camera(FNaSRBase):
        def __init__(self, id, image, coordinates, camera_connections=None, ambient=None):
            self.id = id
            self.image = image
            self.coordinates = coordinates if coordinates is not None else (0,0,0,0)
            self.is_active = coordinates is not None
            self.enemy = []
            self.camera_connections = _CameraConnections(camera_connections)
            self.ambient = ambient

            self.__break_time = 0
            self.__default_image = image

        @property
        def break_second(self):
            return self.__break_time

        def break_c(self, second):
            second = int(second)
            if second > 0:
                self.__break_time = second

                black = renpy.store.Solid("#000")
                txt = renpy.store.Text("CAMERA\nOFFLINE", color="#FF0000", slow=False, xalign=0.5, yalign=0.5)

                self.image = renpy.display.layout.Container(black, txt, layout="fixed")

        def repair(self):
            self.__break_time = 0

        def update(self):
            if self.__break_time > 0:
                self.__break_time -= 1
            elif self.image != self.__default_image:
                self.image = self.__default_image

        def reset(self):
            self.image = self.__default_image
            self.is_active = True
            self.enemy.clear()

    class CameraSystem(FNaSRBase):
        def __init__(self):
            self._null_camera = Camera(-1, "black", None)
            self.__cameras = dict()
            self.__list_cameras = []

            self.select = 1
            self.show_tablet = False
            self.charge = 100
            self.discharge = 1
            self.animation = False

            self.__is_open = False
            self.__update_step = Constants.DEFAULT_UPDATE_STEP

            self.__old_state_tablet = False

            self.sound_controller = CameraSoundController(self)

            def handler(enemy):
                with lock:
                    if not hasattr(enemy, "_v1_located_at_location"):
                        enemy._v1_located_at_location = []

                    c_id = enemy.enemy_path.get_camera_id_by_loc()
                    old_c_id = enemy.enemy_path.get_camera_id_by_loc(enemy.enemy_path.old_location)
                    old_camera = self.__cameras.get(old_c_id)

                    if old_camera and enemy in old_camera.enemy:
                        old_camera.enemy.remove(enemy)
                        if old_camera.id in enemy._v1_located_at_location:
                            enemy._v1_located_at_location.remove(old_camera.id)

                    if c_id is not None:
                        camera = self.__cameras[c_id]
                        if enemy not in camera.enemy:
                            camera.enemy.append(enemy)
                        if c_id not in enemy._v1_located_at_location:
                            enemy._v1_located_at_location.append(c_id)

                    if len(enemy._v1_located_at_location) > 1:
                        execute_in_main_thread(renpy.log, "FNaSR | Enemy '{}' desync detected: ...".format(enemy.tag))
                        if enemy.enemy_path.location != 0:
                            enemy._v1_located_at_location = [c_id] if c_id is not None else []
                        else:
                            enemy._v1_located_at_location = []

                        for camera in self.__cameras.values():
                            if enemy in camera.enemy:
                                camera.enemy.remove(enemy)

                        if c_id is not None and enemy.enemy_path.location != 0:
                            self.__cameras[c_id].enemy.append(enemy)

                    if self.show_tablet:
                        self.state(StateCameraSystem.TABLET_OPEN)

            global_event.on("enemy.path.new_location", handler)

        def __iter__(self):
            return iter(dict(self.__cameras))

        def __len__(self):
            return len(self.__cameras)

        def act_cameras(self):
            if self.charge <= 0:
                renpy.music.play(resources.sounds.sfx["error"], "sound")
                return

            self.animation = True
            self.__old_state_tablet = self.show_tablet
            self.show_tablet = not self.show_tablet
            if self.show_tablet and self.charge > 0:
                self.__show_t()
            else:
                self.__hide_t()

            if not self.show_tablet == self.__old_state_tablet:
                self.__show_animation_t()

            renpy.store.v1FNaSREvent.emit("camera_system.tablet", self.show_tablet)

        def __show_t(self):
            self.__update_step -= 1
            self.__is_open = True
            if renpy.random.randint(0,1):
                renpy.music.play(resources.sounds.sfx["tablet_open_1"], "sound")
            else:
                renpy.music.play(resources.sounds.sfx["tablet_open_2"], "sound")

            renpy.music.play(resources.sounds.sfx["camera_static_1_new"], "v1_show_camera_ambience_FNaSR", loop=True, fadein=0.1)

            camera = self.__cameras[self.select]
            if camera.ambient is not None:
                renpy.music.play(resources.sounds.ambient[camera.ambient], "v1_camera_ambience_FNaSR", loop=True, fadein=0.1)

            game.game_time.timer(self.state, 0.18, StateCameraSystem.TABLET_OPEN, IgnoreFreeze=True)

        def __hide_t(self):
            renpy.music.stop("v1_camera_ambience_FNaSR")
            renpy.music.play(resources.sounds.sfx["tablet_close_1"], "sound")

            renpy.music.stop("v1_show_camera_ambience_FNaSR")

            self.state(StateCameraSystem.TABLET_CLOSE)

        def __show_animation_t(self):
            _oit = game.mainL.is_tablet
            game.mainL.is_tablet = False

            def _h():
                game.mainL.is_tablet = _oit
                self.animation = False
            game.game_time.timer(_h, 0.18, IgnoreFreeze=True)

            execute_in_main_thread(renpy.show_screen, "V1TabletAnimScreenFNaSR", game)

        def select_camera(self, camera):
            renpy.music.stop("v1_camera_ambience_FNaSR")
            self.__update_step -= 1

            self.select = camera.id
            self.state(StateCameraSystem.TABLET_OPEN)

            renpy.music.play(resources.sounds.sfx["blip3"], "v1_camera_sfx_FNaSR", fadein=0.1)
            if camera.ambient is not None:
                renpy.music.play(resources.sounds.ambient[camera.ambient], "v1_camera_ambience_FNaSR", loop=True, fadein=0.1)

            self.sound_controller.on_camera_selected()

            global_event.emit("camera_system.select_camera", self.select)


        def add_camera(self, camera):
            if not isinstance(camera, Camera):
                raise Exception("The 'camera' parameter must be 'Camera' or inherit from it.")

            if camera.id in self.__cameras:
                raise Exception("Camera with this ID already exists.")

            self.__cameras[camera.id] = camera
            self.__list_cameras.append(camera)

            self.generate_connections()

        def remove_camera(self, camera_or_id):
            if isinstance(camera_or_id, Camera):
                cam_id = camera_or_id.id
            else:
                cam_id = int(camera_or_id)

            if cam_id not in self.__cameras or cam_id == -1:
                return

            removed = self.__cameras.pop(cam_id, None)
            if removed is None:
                return

            for cam in self.__cameras.values():
                cam.camera_connections.discard(cam_id)

            self.__list_cameras.remove(removed)

        def get_camera(self, camera_id, default=None):
            return self.__cameras.get(camera_id, default)

        def generate_connections(self):
            cameras = self.__cameras

            for cam in cameras.values():
                for other_id in list(cam.camera_connections):
                    if other_id == cam.id:
                        continue

                    if other_id not in cameras:
                        continue

                    other_cam = cameras[other_id]

                    other_cam.camera_connections._add(cam.id)

            self.sound_controller.on_graph_changed()

        def get_image(self):
            return self.__cameras.get(self.select, self._null_camera).image

        @property
        def cameras(self):
            return dict(self.__cameras)

        @property
        def list_cameras(self):
            return list(self.__cameras.values())

        def update(self):
            if self.charge <= 0:
                return

            for camera in self.__cameras.values():
                camera.update()

            if self.__is_open:
                self.__is_open = self.show_tablet
                self.__update_step -= 2
            else:
                self.__update_step -= 1

            if self.__update_step <= 0:
                self.__update_step = Constants.DEFAULT_UPDATE_STEP
                self.charge -= self.discharge

                if self.charge <= 0:
                    if self.show_tablet:
                        """Так делать нельзя, так делать фу фу фу, логика не должна повторятся, я сделал это потому что я конченый"""
                        self.show_tablet = False
                        self.animation = True
                        self.__hide_t()
                        self.__show_animation_t()
                        execute_in_main_thread(renpy.music.play, resources.sounds.sfx["error"], "sound")
                        global_event.emit("camera_system.tablet", self.show_tablet)
                    return

        def get_enemy(self):
            return self.__cameras[self.select].enemy

        def reset(self):
            for c in self.__cameras.values():
                c.reset()

            self.select = 1
            self.show_tablet = False
            self.charge = 100
            self.discharge = 1
            self.animation = False

            self.__is_open = False
            self.__update_step = Constants.DEFAULT_UPDATE_STEP

        def add_charge_update_step(self, update_step):
            self.__update_step += int(update_step)

        def set_charge(self, charge):
            self.charge = int(charge)

        def state(self, name_state):
            """Это вообще поебота полная, мне не нравится этот метод, но что то менять мне очеееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееень лень"""
            GameTools.remove_all_display_obj(category="camera")
            if name_state == StateCameraSystem.TABLET_CLOSE:
                renpy.hide_screen("V1CamerasScreenFNaSR")
            elif name_state == StateCameraSystem.TABLET_OPEN:
                renpy.hide_screen("V1OfficeScreenFNaSR")
                GameTools.add_display_obj(
                    category="camera",
                    key="camera_image",
                    obj=self.get_image(),
                    priority = -1
                )

                enemies = self.get_enemy()

                for e in enemies:
                    if e.activity:
                        GameTools.add_display_obj(
                            category="camera",
                            key="camera_enemy_{}".format(e.tag),
                            obj=e.sprite,
                            position=e.position
                        )


    class CameraSoundController(object):
        def __init__(self,
                    camera_system,
                    channel="v1_noise_FNaSR",
                    min_volume=0.05,
                    falloff_factor=0.6):

            self._camera_system = camera_system
            self._channel = channel

            self._noise_source_id = None
            self._distance_cache = {}

            self._min_volume = float(min_volume)
            self._falloff_factor = float(falloff_factor)


        # =====================================================
        # PUBLIC API
        # =====================================================

        def set_noise_source(self, camera_id):
            cameras = self._camera_system.cameras

            if camera_id not in cameras:
                raise Exception("Noise source camera does not exist.")

            self._noise_source_id = camera_id
            self._rebuild_cache()
            self.update_volume()

            #execute_in_main_thread(
            #    renpy.music.play,
            #    resources.sounds.music["Music_Box_Melody_Playful"],
            #    self._channel,
            #    loop=True
            #)

        def delete_noise_source(self):
            self._noise_source_id = None
            self._rebuild_cache()
            #execute_in_main_thread(renpy.music.stop, self._channel)

        def on_camera_selected(self):
            self.update_volume()


        def on_graph_changed(self):
            if self._noise_source_id is not None:
                self._rebuild_cache()
                self.update_volume()


        def update_volume(self):
            if self._noise_source_id is None:
                return

            selected_id = self._camera_system.select
            distance = self._distance_cache.get(selected_id)

            volume = self._calculate_volume(distance)

            renpy.music.set_volume(
                volume,
                delay=0.1,
                channel=self._channel
            )


        # =====================================================
        # INTERNAL
        # =====================================================

        def _rebuild_cache(self):
            self._distance_cache.clear()

            source = self._noise_source_id
            if source is None:
                return

            cameras = self._camera_system.cameras

            visited = set()
            queue = deque([(source, 0)])

            while queue:
                cam_id, dist = queue.popleft()

                if cam_id in visited:
                    continue

                visited.add(cam_id)
                self._distance_cache[cam_id] = dist

                camera = cameras.get(cam_id)
                if camera is None:
                    continue

                for neighbor_id in camera.camera_connections:
                    if neighbor_id not in visited:
                        queue.append((neighbor_id, dist + 1))


        def _calculate_volume(self, distance):
            if distance is None:
                return self._min_volume

            volume = math.exp(-self._falloff_factor * distance)

            if volume < self._min_volume:
                return self._min_volume

            return volume















