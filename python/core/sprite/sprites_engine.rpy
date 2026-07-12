### sprites_engine.rpy ##########################################################
# Единая точка правды для всех спрайтов персонажей.
#
# Раньше: тысячи блоков вида
#   image X = ConditionSwitch(
#       "persistent.sprite_time=='sunset'", im.MatrixColor(im.Composite(...), im.matrix.tint(0.94,0.82,1.0)),
#       "persistent.sprite_time=='night'",  im.MatrixColor(im.Composite(...), im.matrix.tint(0.63,0.78,0.82)),
#       True, im.Composite(...))
# повторявшихся по 3 раза (far/normal/close) с идентичной структурой.
#
# Теперь: один список SPRITES (в sprites_data.rpy, генерируется convert_sprites.py
# из старого файла) + один цикл ниже, который строит все image() автоматически.
#
# Если понадобится поменять тон заката/ночи для ВСЕХ спрайтов разом --
# правится ровно 2 строки здесь, а не тысячи блоков по всему проекту.
##################################################################################

init 1 python in v1FNaSR:

    # ---- константы тонирования (раньше были продублированы в каждом блоке) ----
    SPRITE_SUNSET_TINT = renpy.store.im.matrix.tint(0.94, 0.82, 1.0)
    SPRITE_NIGHT_TINT = renpy.store.im.matrix.tint(0.63, 0.78, 0.82)
    SPRITE_RED_TINT = renpy.store.im.matrix.tint(1.0, 0.1, 0.1)

    # zoom -> (ширина канваса, папка на диске)
    SPRITE_ZOOM_INFO = {
        "far": (630, "far"),
        "normal": (900, "normal"),
        "close": (1050, "close"),
    }

    # ---- интеграция с вашим Adapter'ом (адаптация под платформу) ----
    #
    # Задайте здесь ссылку на функцию вашего Adapter'а. Поддерживаются
    # ДВА варианта сигнатуры -- какой у вас, такой и используйте:
    #
    #   1) Adapter возвращает скорректированные (width, height),
    #      а im.Scale применяет движок сам:
    #
    #          def my_adapter(displayable, width, height, zoom):
    #              return Adapter.get_size(width, height)   # -> (w, h)
    #          SPRITE_SCALE_FN = my_adapter
    #
    #   2) Adapter сам оборачивает displayable (например, Transform с
    #      im.Scale + позиционированием под платформу) и возвращает
    #      готовый объект:
    #
    #          def my_adapter(displayable, width, height, zoom):
    #              return Adapter.adapt_image(displayable, width, height)
    #          SPRITE_SCALE_FN = my_adapter
    #
    # По умолчанию выключено (SPRITE_SCALE_FN = None) -- поведение
    # полностью совпадает со старым файлом, без каких-либо изменений.
    SPRITE_SCALE_FN = lambda displayable, width, height, zoom: UtilsAdapter.size(width, height)
    GLOBAL_SPRITE_PATH = "images/sprites/%s/%s" if UtilsAdapter.ES else "compatibility/sprites/%s/%s"

    def _sprite_scale(base, width, height, zoom, explicit_scale):
        """explicit_scale -- необязательное (w, h) для КОНКРЕТНОГО спрайта,
        задаётся в данных (SPRITES) и имеет приоритет над SPRITE_SCALE_FN."""
        if explicit_scale is not None:
            w, h = explicit_scale
            return renpy.store.im.Scale(base, w, h)

        if SPRITE_SCALE_FN is not None:
            result = SPRITE_SCALE_FN(base, width, height, zoom)
            if isinstance(result, tuple):
                w, h = result
                if (w, h) != (width, height):
                    return renpy.store.im.Scale(base, w, h)
                return base
            return result  # Adapter уже вернул готовый (обёрнутый) displayable

        return base

    def _sprite_compose(width, layers, folder):
        """Собирает im.Composite из относительных путей слоёв для конкретного zoom."""
        parts = [(width, 1080)]
        for rel_path in layers:
            parts.append((0, 0))
            parts.append(GLOBAL_SPRITE_PATH % (folder, rel_path))
        return renpy.store.im.Composite(*parts)

    def _sprite_build(kind, width, layers, folder, zoom, explicit_scale):
        """Строит displayable для одного zoom-варианта по типу тонирования (kind)."""
        base = _sprite_compose(width, layers, folder)
        base = _sprite_scale(base, width, 1080, zoom, explicit_scale)

        if kind == "day":
            # день/закат/ночь -- единственный случай, где раньше был ConditionSwitch
            return renpy.store.ConditionSwitch(
                "persistent.sprite_time=='sunset'", renpy.store.im.MatrixColor(base, SPRITE_SUNSET_TINT),
                "persistent.sprite_time=='night'", renpy.store.im.MatrixColor(base, SPRITE_NIGHT_TINT),
                True, base,
            )
        if kind == "night":
            return renpy.store.im.MatrixColor(base, SPRITE_NIGHT_TINT)
        if kind == "red":
            return renpy.store.im.MatrixColor(base, SPRITE_RED_TINT)
        if kind == "plain":
            return base
        if isinstance(kind, tuple) and kind[0] == "tint":
            r, g, b = kind[1]
            return renpy.store.im.MatrixColor(base, renpy.store.im.matrix.tint(float(r), float(g), float(b)))

        raise Exception("register_sprite: неизвестный kind %r" % (kind,))

    def register_sprite(zoom_tuple, kind, base_name, layers, scale=None):
        """Регистрирует один или несколько image() -- по одному на каждый zoom
        из zoom_tuple ('far'/'normal'/'close'). Суффикс к имени добавляется
        только для far/close, 'normal' -- имя без суффикса (как в исходнике).

        scale (опционально):
        - None                              -> используется SPRITE_SCALE_FN (если задан)
        - (width, height)                   -> одинаковый явный размер для всех zoom из zoom_tuple
        - {"far": (w,h), "close": (w,h), ...} -> свой явный размер на каждый zoom
        """
        for zoom in zoom_tuple:
            width, folder = SPRITE_ZOOM_INFO[zoom]
            image_name = base_name if zoom == "normal" else "%s %s" % (base_name, zoom)

            if isinstance(scale, dict):
                explicit_scale = scale.get(zoom)
            else:
                explicit_scale = scale

            renpy.image(image_name, _sprite_build(kind, width, layers, folder, zoom, explicit_scale))


# Список SPRITES подключается отдельным файлом(-ами), сгенерированным(и)
# convert_sprites.py, например sprites_data.rpy:
#
#   init python:
#       for _row in SPRITES:
#           register_sprite(*_row)   # 4 элемента (без scale) или 5 (со scale) -- оба варианта ок
#
# Так удобно держать движок и данные раздельно: движок меняется редко,
# данные -- регулярно, при добавлении новых спрайтов/эмоций.
