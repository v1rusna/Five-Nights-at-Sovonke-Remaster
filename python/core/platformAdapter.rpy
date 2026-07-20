init python in v1FNaSR:

    class UtilsAdapter(object):
        """
        Пересчитывает координаты/размеры из виртуального разрешения проекта
        (VIRTUAL_WIDTH x VIRTUAL_HEIGHT) в реальное разрешение устройства,
        сохраняя пропорции (letterbox/pillarbox через единый _scale).
        """

        # Виртуальное разрешение проекта
        VIRTUAL_WIDTH = 1920
        VIRTUAL_HEIGHT = 1080

        # Реальное разрешение устройства (заполняется в init())
        REAL_WIDTH = None
        REAL_HEIGHT = None

        # Флаг "мы собраны под Everlasting Summer" -- влияет на пути к
        # ресурсам и на то, какие UI-хаки применяются (см. PAdapter.path).
        ES = True

        _scale = None
        _offset_x = None
        _offset_y = None

        @classmethod
        def init(cls):
            """Вычисляет масштаб и отступы один раз при старте мода."""
            cls.ES = "Everlasting" in renpy.store.config.name
            cls.REAL_WIDTH = float(renpy.config.screen_width)
            cls.REAL_HEIGHT = float(renpy.config.screen_height)

            scale_x = cls.REAL_WIDTH / cls.VIRTUAL_WIDTH
            scale_y = cls.REAL_HEIGHT / cls.VIRTUAL_HEIGHT

            # Берём минимальный масштаб, чтобы контент вписался в экран
            # целиком без обрезки (letterbox/pillarbox по краям).
            cls._scale = min(scale_x, scale_y)

            cls._offset_x = (cls.REAL_WIDTH - cls.VIRTUAL_WIDTH * cls._scale) / 2.0
            cls._offset_y = (cls.REAL_HEIGHT - cls.VIRTUAL_HEIGHT * cls._scale) / 2.0

        @classmethod
        def scale(cls, value):
            """Масштабирует одно скалярное значение (например, zoom)."""
            if value is None:
                return None
            return value * cls._scale

        @classmethod
        def point(cls, x, y):
            """Переводит точку из виртуальных координат в реальные (с отступами)."""
            return (
                cls._offset_x + x * cls._scale,
                cls._offset_y + y * cls._scale,
            )

        @classmethod
        def size(cls, width=None, height=None):
            """Масштабирует пару ширина/высота без смещения."""
            return (
                cls.scale(width),
                cls.scale(height),
            )

        @classmethod
        def rect(cls, x, y, width=None, height=None):
            """Масштабирует прямоугольник целиком: позицию и размер."""
            x, y = cls.point(x, y)
            width, height = cls.size(width, height)
            return x, y, width, height


    class UIAdapter(object):
        """Хелперы для построения displayable-объектов RenPy в виртуальных координатах."""

        @classmethod
        def transform(
            cls,
            child=None,
            x=0,
            y=0,
            width=None,
            height=None,
            zoom=1.0,
            anchor=(0.0, 0.0),
            rotate=0,
            alpha=1.0,
        ):
            """Оборачивает child в Transform с координатами/размером, пересчитанными под экран."""
            x, y, width, height = UtilsAdapter.rect(x, y, width, height)

            kwargs = {
                "xpos": x,
                "ypos": y,
                "zoom": UtilsAdapter.scale(zoom),
                "anchor": anchor,
                "rotate": rotate,
                "alpha": alpha,
            }

            if width is not None:
                kwargs["xsize"] = width

            if height is not None:
                kwargs["ysize"] = height

            return renpy.display.transform.Transform(child, **kwargs)

        @classmethod
        def image(cls, filename, **kwargs):
            """Короткий алиас transform() специально для изображений."""
            return cls.transform(filename, **kwargs)

        @classmethod
        def scale_image(cls, image, width, height):
            """Масштабирует изображение под реальный размер экрана через im.Scale."""
            width, height = UtilsAdapter.size(width, height)
            return renpy.display.im.Scale(image, int(width), int(height))

        @classmethod
        def scale_style(cls, size):
            """
            Масштабирует размер стиля (например, шрифта) так, чтобы он не
            становился МЕНЬШЕ исходного при уменьшении экрана -- в этом
            случае добавляется четверть исходного размера как компенсация
            читаемости.
            """
            scale_size = int(UtilsAdapter.scale(size))
            if scale_size >= size:
                return scale_size
            return scale_size + size / 4

    class PAdapter(object):
        """Адаптация путей к ресурсам под сборку ES (Everlasting Summer) и остальные."""

        @classmethod
        def get_mod_folder(cls):
            if UtilsAdapter.ES:
                return "FNaS_R"
            return ""

        @classmethod
        def path(cls, path):
            """
            В сборке ES пути используются как есть. В остальных сборках
            префикс "FNaS_R/" отсутствует в файловой структуре, поэтому
            его нужно срезать.
            """
            if UtilsAdapter.ES:
                return path

            prefix = "FNaS_R/"
            if path.startswith(prefix):
                return path[len(prefix):]
            return path


    class Adapter(UIAdapter, PAdapter):
        pass

    UtilsAdapter.init()
