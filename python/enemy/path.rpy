init python in v1FNaSR:
    class EnemyPath(FNaSRBase):
        """
        Система пути противника
        """
        def __init__(self, enemy, *paths):
            if not isinstance(enemy, EnemyBase):
                raise TypeError("The 'enemy' parameter must be an object of the 'EnemyBase' class.")
 
            self.__enemy = enemy
            self.location = 0
            self.old_location = 0

            self.paths = []
            self.path_map = {}

            for i, p in enumerate(paths, 1):
                self.paths.append(p)
                self.path_map[i] = p

        def __len__(self):
            return len(self.path_map)

        def _event(self):
            execute_in_main_thread(global_event.emit, "enemy.path.new_location", self.__enemy)
            if self.is_max_loc():
                execute_in_main_thread(global_event.emit, "enemy.path.max_location", self.__enemy)

        def set_location(self, location_id, event=True):
            with lock:
                self.old_location = self.location
                self.location = location_id
                if event:
                    self._event()

        def get_camera_id_by_loc(self, loc=None):
            if loc is None:
                loc = self.location

            return self.path_map.get(loc, None)

        def is_max_loc(self):
            return self.location == len(self.path_map)

        def is_min_loc(self):
            return self.location == 1

        def next_loc(self, event=True):
            if not len(self.path_map):
                return

            with lock:
                self.old_location = self.location

                self.location += 1
                if self.location > len(self.path_map):
                    self.location = 1

                if event:
                    self._event()
                return self.path_map[self.location]

        def previous_loc(self, event=True):
            if not len(self.path_map):
                return

            self.old_location = self.location

            self.location -= 1
            if self.location < 1:
                self.location = len(self.path_map)

            if event:
                self._event()
            return self.path_map[self.location]

        def reset(self):
            self.location = 0
            self.old_location = 0
            self.next_loc()

        def remaining_locations(self):
            return len(self.path_map) - self.location

        @property
        def last_location(self):
            return self.paths[-1]

        @property
        def first_location(self):
            return self.paths[0]

        @classmethod
        def generate_path(cls, player_cam_id, CamerasById=None):
            if CamerasById is None:
                CamerasById = game.camera_system.cameras

            # получаем словарь расстояний
            distances = cls.camera_distances(player_cam_id, CamerasById)

            # группируем камеры по расстоянию
            distance_groups = cls.group_by_distance(distances)

            # удаляем камеру игрока (дистанция 0)
            distance_groups.pop(0, None)

            # оставляем несколько дальних групп (например, 3 дальние группы)
            farthest_distances = sorted(distance_groups.keys(), reverse=True)[:3]

            # создаем список кандидатов для спавна
            spawn_candidates = []
            for dist in farthest_distances:
                spawn_candidates.extend(distance_groups[dist])

            # случайно выбираем камеру спавна
            spawn_cam = random.choice(spawn_candidates)

            # строим путь от спавна до игрока
            path = cls.find_path(spawn_cam, player_cam_id, CamerasById)
            return path

        @staticmethod
        def find_path(start_id, target_id, CamerasById):
            """BFS-путь между двумя камерами."""
            if start_id == target_id:
                return [start_id]

            visited = set([start_id])
            queue = [[start_id]]

            while queue:
                path = queue.pop(0)
                current = path[-1]

                for nxt in CamerasById[current].camera_connections:
                    if nxt not in visited:
                        visited.add(nxt)
                        new_path = path + [nxt]
                        if nxt == target_id:
                            return new_path
                        queue.append(new_path)

            return None

        @staticmethod
        def camera_distances(start_id, CamerasById):
            """Словарь {camera_id: distance_from_start}"""
            distances = {start_id: 0}
            queue = [start_id]

            while queue:
                current = queue.pop(0)
                cur_dist = distances[current]

                for nxt in CamerasById[current].camera_connections:
                    if nxt not in distances:
                        distances[nxt] = cur_dist + 1
                        queue.append(nxt)

            return distances

        @staticmethod
        def group_by_distance(distances):
            """Группировка камер по дистанции"""
            grouped = {}
            for cam_id, d in distances.items():
                grouped.setdefault(d, []).append(cam_id)
            return grouped

    class _PathsGuard:
        def __get__(self, obj, owner):
            if obj is None:
                return self

            if obj._paths is None:
                obj._ensure_paths()

            return obj._paths

        def __set__(self, obj, value):
            if value is None:
                raise ValueError("paths cannot be None")
            obj._paths = value

    class AutoGeneratePath(EnemyPath):
        """
        Класс для автоматической генерации путей для противника, каждую ночь путь генерируется заново
        """
        paths = _PathsGuard()

        def __init__(self, enemy, target_id=None):
            super(AutoGeneratePath, self).__init__(enemy)

            self._paths = None
            self.path_map.clear()

            self.__target_id = target_id

        def reset(self):
            self.location = 0
            self.old_location = 0
            self._paths = None
            self.path_map.clear()

        def _ensure_paths(self):
            if self.__target_id is None:
                paths = self.generate_path(
                    player_cam_id=game.night_system.player_start,
                    CamerasById=game.camera_system.cameras
                )
            else:
                paths = self.generate_path(
                    player_cam_id=self.__target_id,
                    CamerasById=game.camera_system.cameras
                )

            if not paths:
                raise RuntimeError("AutoEnemyPath: generated empty path")

            self._paths = paths
            self.path_map = {i + 1: p for i, p in enumerate(paths)}

