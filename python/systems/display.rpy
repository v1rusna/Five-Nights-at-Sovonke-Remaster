init 5 python in v1FNaSR:
    class ObjectDisplaySystem(FNaSRBase):
        def __init__(self, default_layer="master"):
            self.items = {}  # key -> item dict (см. ниже)
            self.__show_list = []  # отсортированный список элементов по priority
            self.__removed_items = []
            self._visible_keys = set()  # какие ключи сейчас показаны на экране
            self.auto_update = False
            self.default_layer = default_layer

        def _make_wrapper_if_needed(self, item):
            """
            Возвращает 'what' для renpy.show — либо исходный displayable, либо Transform.
            Кэшируется в item['_cached_what'] и пересоздаётся только при изменении входных параметров.
            """
            # ключ для сравнения состояния
            state = (item["obj"], item.get("position"), item.get("align"),
                    tuple(item.get("at_list") or []), item.get("layer", self.default_layer))
            if item.get("_cached_state") == state and "_cached_what" in item:
                return item["_cached_what"]

            obj = renpy.displayable(item["obj"])
            if item.get("position") is not None:
                wrapper = renpy.store.Transform(obj, pos=item["position"])
            elif item.get("align") is not None:
                wrapper = renpy.store.Transform(obj, align=item["align"])
            else:
                wrapper = obj

            item["_cached_state"] = state
            item["_cached_what"] = wrapper
            return wrapper

        def add_obj(self, key, obj, align=None, position=None, priority=0, at_list=None, layer=None):
            with lock:
                if key in self.items:
                    raise KeyError("Object with key '%s' already exists." % key)
                if at_list is None:
                    at_list = []

                item = {
                    "key": key,
                    "obj": obj,
                    "align": align,
                    "position": position,
                    "priority": int(priority),
                    "at_list": at_list,
                    "layer": layer or self.default_layer,
                    # cache fields:
                    "_cached_state": None,
                    "_cached_what": None,
                }
                self.items[key] = item
                # обновляем отсортированный список
                self.__show_list = sorted(self.items.values(), key=lambda x: x["priority"])
                if self.auto_update:
                    self.update_display()

        def remove_obj(self, key):
            with lock:
                if key not in self.items:
                    raise KeyError("Object with key '%s' does not exist." % key)

                # помечаем как удалённый и удаляем из items
                obj = self.items[key]["obj"]
                _l = self.items[key]["layer"]
                del self.items[key]
                self.__removed_items.append({"key": key, "layer": _l})
                self.__show_list = sorted(self.items.values(), key=lambda x: x["priority"])
                if self.auto_update:
                    self.update_display()

                return obj

        def pop_obj(self, key, default=None):
            with lock:
                if key not in self.items:
                    return default
                obj = self.items[key]["obj"]
                self.remove_obj(key)
                return obj

        def get_obj(self, key, default=None):
            return self.items.get(key, {}).get("obj", default)

        def get_obj_list(self):
            return [k for k in self.items.keys()]

        def update_obj(self, key, **kwargs):
            """
            Обновляет поля элемента. Пересоздаёт кеш только если изменилось что-то существенное.
            """
            if key not in self.items:
                raise KeyError("Object with key '%s' does not exist." % key)
            item = self.items[key]

            changed = False
            for field in ("obj", "align", "position", "priority", "at_list", "layer"):
                if field in kwargs:
                    new = kwargs[field]
                    if field == "priority":
                        new = int(new)
                    if item.get(field) != new:
                        item[field] = new
                        changed = True

            if changed:
                # invalid cache so wrapper будет пересоздан при следующем показе
                item["_cached_state"] = None
                self.__show_list = sorted(self.items.values(), key=lambda x: x["priority"])
                if self.auto_update:
                    self.update_display()

        def update_display(self):
            """
            Показ/скрытие — делаем минимально возможные операции:
            - скрываем только те, которые были удалены или перестали быть в списке
            - показываем только новые или у которых изменился cached state
            - если поменялся порядок элементов (priority), то просто пересоздаём показ всех (без лишних hide/show по каждому),
            т.к. порядок на слое важен и иногда проще переотобразить.
            """
            desired_keys = [item["key"] for item in self.__show_list]
            current_keys = list(self._visible_keys)

            # если порядок изменился — проще пересоздать показ всех видимых
            reorder_needed = False
            # detect reorder: same set but different order
            if set(current_keys) == set(desired_keys) and current_keys != desired_keys:
                reorder_needed = True

            if reorder_needed:
                # скрываем все текущие, затем покажем в нужном порядке
                for key in current_keys:
                    execute_in_main_thread(renpy.hide, name="v1_obj_name_{}_FNaSR".format(key), layer=self.items[key]["layer"])
                self._visible_keys.clear()
                # покажем все заново
                for item in self.__show_list:
                    what = self._make_wrapper_if_needed(item)
                    execute_in_main_thread(
                        renpy.show,
                        name="v1_obj_name_{}_FNaSR".format(item["key"]),
                        what=what,
                        at_list=item.get("at_list"),
                        layer=item.get("layer", self.default_layer)
                    )
                    self._visible_keys.add(item["key"])
            else:
                # скрываем удалённые
                for removed in self.__removed_items:
                    key = removed["key"]
                    if key in self._visible_keys:
                        execute_in_main_thread(renpy.hide, name="v1_obj_name_{}_FNaSR".format(key), layer=removed["layer"])
                        self._visible_keys.discard(key)
                self.__removed_items = []

                # покажем новые и обновим изменившиеся
                desired_set = set(desired_keys)
                # скрыть то что не должно быть показано
                for key in list(self._visible_keys):
                    if key not in desired_set:
                        execute_in_main_thread(renpy.hide, name="v1_obj_name_{}_FNaSR".format(key), layer=self.items[key]["layer"])
                        self._visible_keys.discard(key)

                # показать/обновить оставшиеся по порядку
                for item in self.__show_list:
                    key = item["key"]
                    what = self._make_wrapper_if_needed(item)
                    # если ещё не показан — show
                    if key not in self._visible_keys:
                        execute_in_main_thread(
                            renpy.show,
                            name="v1_obj_name_{}_FNaSR".format(key),
                            what=what,
                            at_list=item.get("at_list"),
                            layer=item.get("layer", self.default_layer)
                        )
                        self._visible_keys.add(key)
                    else:
                        # если закешированный 'what' изменился (кэш инвалидирован), нужно перезадать show
                        # (renpy.show с тем же именем заменит displayable)
                        if item.get("_cached_state") is None:
                            what = self._make_wrapper_if_needed(item)
                            execute_in_main_thread(
                                renpy.show,
                                name="v1_obj_name_{}_FNaSR".format(key),
                                what=what,
                                at_list=item.get("at_list"),
                                layer=item.get("layer", self.default_layer)
                            )

        def hide_objects(self):
            # скрываем все, даже те которые недавно удалили
            for key in list(self._visible_keys):
                try:
                    renpy.hide(name="v1_obj_name_{}_FNaSR".format(key), layer=self.items[key]["layer"])
                except KeyError:
                    pass
            for removed in self.__removed_items:
                renpy.hide(name="v1_obj_name_{}_FNaSR".format(removed["key"]), layer=removed["layer"])
            self._visible_keys.clear()
            self.__removed_items = []

        def reset(self):
            self.hide_objects()
            self.items = {}
            self.__show_list = []
            self.__removed_items = []
            self._visible_keys = set()
            self.auto_update = False

        def __repr__(self):
            return "<V1ObjectDisplaySystemFNaSR objects={}>".format(len(self.items))
