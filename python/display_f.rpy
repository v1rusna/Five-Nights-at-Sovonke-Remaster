init python in v1FNaSRDisplay:
    from renpy.display import core
    from renpy.display.render import Render
    
    class MultiDisplayable(core.Displayable):
        def __init__(self, **kwargs):
            super(MultiDisplayable, self).__init__(**kwargs)
            self.items = []
            self.__show_items = []
            self.__cached_positions = {}  # кэш вычисленных позиций
            self.__last_width = None
            self.__last_height = None
            
        def add_image(self, displayable, **kwargs):
            """
            displayable - любой renpy Displayable
            kwargs - можно передавать pos=(x, y) или align=(ax, ay),
                    priority=int - приоритет отрисовки (чем больше, тем выше)
            """
            if not isinstance(displayable, renpy.display.core.Displayable):
                displayable = renpy.displayable(displayable)
                
            if not ("pos" in kwargs) and not ("align" in kwargs):
                raise ValueError("Must specify either 'pos' or 'align' when adding an image.")
            
            self.items.append({
                "d": displayable,
                "pos": kwargs.get("pos"),
                "align": kwargs.get("align"),
                "priority": kwargs.get("priority", 0)
            })
            
            self.__show_items = sorted(self.items, key=lambda x: x["priority"])
            self.__cached_positions.clear()  # очищаем кэш при изменении
            renpy.redraw(self, 0)  # запрашиваем перерисовку
            
        def remove_image(self, displayable):
            self.items = [i for i in self.items if i["d"] != displayable]
            self.__show_items = sorted(self.items, key=lambda x: x["priority"])
            self.__cached_positions.clear()
            renpy.redraw(self, 0)
            
        def get_image(self, displayable):
            if not isinstance(displayable, renpy.display.core.Displayable):
                displayable = renpy.displayable(displayable)
            for item in self.items:
                if item["d"] == displayable:
                    return item["d"]
            return None
        
        def _safe_get_size(self, d):
            try:
                return d.get_size()
            except Exception:
                return (0, 0)
        
        def _calculate_position(self, item, width, height):
            """Вычисляет позицию с кэшированием"""
            item_id = id(item["d"])
            cache_key = (item_id, width, height)
            
            # проверяем кэш
            if cache_key in self.__cached_positions:
                return self.__cached_positions[cache_key]
            
            # вычисляем позицию
            if item["pos"] is not None:
                x, y = item["pos"]
            elif item["align"] is not None:
                ax, ay = item["align"]
                w, h = self._safe_get_size(item["d"])
                x = int((width - w) * ax)
                y = int((height - h) * ay)
            else:
                x, y = 0, 0
            
            # сохраняем в кэш
            self.__cached_positions[cache_key] = (x, y)
            return (x, y)
        
        def render(self, width, height, st, at):
            # очищаем кэш если размер изменился
            if self.__last_width != width or self.__last_height != height:
                self.__cached_positions.clear()
                self.__last_width = width
                self.__last_height = height
            
            render = Render(width, height)
            
            for item in self.__show_items:
                d = item["d"]
                
                # рендерим дочерний объект
                r = renpy.render(d, width, height, st, at)
                
                # получаем позицию (с кэшированием)
                x, y = self._calculate_position(item, width, height)
                
                # добавляем на render
                render.blit(r, (x, y))
            
            # НЕ запрашиваем постоянную перерисовку если нет анимаций
            # renpy.redraw вызывается только когда нужно
            
            return render
        
        def event(self, ev, x, y, st):
            # обрабатываем события в обратном порядке (сверху вниз)
            for item in reversed(self.__show_items):
                d = item["d"]
                
                # вычисляем позицию дочернего объекта
                if item["pos"] is not None:
                    dx, dy = item["pos"]
                elif item["align"] is not None:
                    ax, ay = item["align"]
                    w, h = self._safe_get_size(d)
                    dx = int((renpy.config.screen_width - w) * ax)
                    dy = int((renpy.config.screen_height - h) * ay)
                else:
                    dx, dy = 0, 0
                
                # проверяем попадание в область объекта
                w, h = self._safe_get_size(d)
                if dx <= x <= dx + w and dy <= y <= dy + h:
                    # корректируем координаты события относительно объекта
                    r = d.event(ev, x - dx, y - dy, st)
                    if r is not None:
                        return r
            
            return None
        
        def visit(self):
            """Сообщаем RenPy о дочерних displayables для корректного управления"""
            return [item["d"] for item in self.items]
        
        def __repr__(self):
            return "V1MultiDisplayableFNaSR(%d items)" % len(self.items)

    class Parallax(renpy.Displayable):
        """
        Честно вдохновленный параллакс
        """
        __slots__ = [
            "displayable",
            "zoom",
            "anchor",
            "power",
            "sharpness_factor"
            "enable_y_shift"

            "xoffset",
            "yoffset",

            "mouse_pos_x",
            "mouse_pos_y",

            "perspective",
            "r_power"
        ]

        def __init__(self, displayable, zoom, anchor, power, sharpness_factor=1.0, enable_y_shift=True, **kwargs):
            super(Parallax, self).__init__(**kwargs)

            self.displayable = renpy.displayable(displayable)

            self.zoom = zoom
            self.anchor = (float(anchor[0]), float(anchor[1]))
            self.power = float(power)
            self.sharpness_factor = sharpness_factor

            self.enable_y_shift = enable_y_shift

            self.xoffset = 0.0
            self.yoffset = 0.0

            self.mouse_pos_x = 0.0
            self.mouse_pos_y = 0.0

            self.width = 0
            self.height = 0

        def get_size(self):
            return (self.width, self.height)

        def set_displayable(self, displayable):
            self.displayable = renpy.displayable(displayable)

        def change_offset(self):
            self.xoffset += (self.mouse_pos_x - (self.xoffset + self.anchor[0])) * self.sharpness_factor
            self.yoffset += (self.mouse_pos_y - (self.yoffset + self.anchor[1])) * self.sharpness_factor if self.enable_y_shift else 0.0

            renpy.redraw(self, 0.0)

        def render(self, width, height, st, at):
            x_shift = -(self.xoffset * self.power)
            y_shift = -(self.yoffset * self.power)

            self.change_offset()

            t_obj = renpy.store.Transform(self.displayable, zoom=self.zoom, anchor=(0.5, 0.5))

            child_r = renpy.render(t_obj, width, height, st, at)
            self.width, self.height = child_r.get_size()

            render = renpy.Render(self.width, self.height)

            render.subpixel_blit(child_r, (x_shift, y_shift))

            return render

        def event(self, ev, x, y, st):
            self.mouse_pos_x = x
            self.mouse_pos_y = y

            return self.displayable.event(ev, x, y, st)

        def visit(self):
            return [ self.displayable ]

        def __repr__(self):
            return "V1ParallaxFNaSR(displayable=%r, zoom=%r, anchor=%r, power=%r)" % (self.displayable, self.zoom, self.anchor, self.power)

    class Wrapper(object):
        def __new__(cls, class_wrappee, *args, **kwargs):
            class Wrapped(class_wrappee):
                def __init__(self, *a, **k):
                    super(Wrapped, self).__init__(*a, **k)
                    self._wrapper = cls

                    self.__v1items = []
                    self.__reg_v1items = []

                    for i in a:
                        if isinstance(i, renpy.display.core.Displayable) and i not in self.__reg_v1items:
                            self.__reg_v1items.append(i)
                            self.__v1items.append({"d": i, "size": (0,0)})

                    for key, value in k.items():
                        if isinstance(value, renpy.display.core.Displayable) and value not in self.__reg_v1items:
                            self.__reg_v1items.append(value)
                            self.__v1items.append({"d": value, "size": (0,0)})

                def render(self, width, height, st, at):
                    for item in self.__v1items:
                        d = item["d"]
                        r = renpy.render(d, width, height, st, at)
                        item["size"] = r.get_size()
            
                    return super(Wrapped, self).render(width, height, st, at)

                def event(self, ev, x, y, st):
                    for item in self.__v1items:
                        d = item["d"]

                        dx, dy = item["size"]

                        r = d.event(ev, x - dx, y - dy, st)
                    return super(Wrapped, self).event(ev, x, y, st)

                def __repr__(self):
                    return "V1WrappedFNaSR(%s)" % super(Wrapped, self).__repr__()

            # возвращаем экземпляр обертки, а не Wrapper
            return Wrapped(*args, **kwargs)

        @staticmethod
        def get_wrapped_items(instance):
            if hasattr(instance, "_wrapper") and instance._wrapper == Wrapper:
                return instance.__v1items
            return []

        @staticmethod
        def clear_wrapped_items(instance):
            if hasattr(instance, "_wrapper") and instance._wrapper == Wrapper:
                instance.__v1items = []

        @staticmethod
        def add_wrapped_item(instance, displayable, size=None):
            size = size if size is not None else (0,0)
            if hasattr(instance, "_wrapper") and instance._wrapper == Wrapper:
                if isinstance(displayable, renpy.display.core.Displayable):
                    instance.__v1items.append({"d": displayable, "size": size})



