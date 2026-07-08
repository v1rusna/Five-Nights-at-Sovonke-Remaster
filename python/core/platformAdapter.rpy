init -9999 python in v1FNaSR:

    class UtilsAdapter(object):

        # Виртуальное разрешение проекта
        VIRTUAL_WIDTH = 1920
        VIRTUAL_HEIGHT = 1080

        # Реальное разрешение устройства
        REAL_WIDTH = None
        REAL_HEIGHT = None

        _scale = None
        _offset_x = None
        _offset_y = None

        @classmethod
        def init(cls):
            """
            Вызывается один раз после запуска игры.
            """

            cls.REAL_WIDTH = float(renpy.config.screen_width)
            cls.REAL_HEIGHT = float(renpy.config.screen_height)

            scale_x = cls.REAL_WIDTH / cls.VIRTUAL_WIDTH
            scale_y = cls.REAL_HEIGHT / cls.VIRTUAL_HEIGHT

            cls._scale = min(scale_x, scale_y)

            cls._offset_x = (
                cls.REAL_WIDTH - cls.VIRTUAL_WIDTH * cls._scale
            ) / 2.0

            cls._offset_y = (
                cls.REAL_HEIGHT - cls.VIRTUAL_HEIGHT * cls._scale
            ) / 2.0

        @classmethod
        def scale(cls, value):
            if value is None:
                return None
            return value * cls._scale

        @classmethod
        def point(cls, x, y):
            return (
                cls._offset_x + x * cls._scale,
                cls._offset_y + y * cls._scale,
            )

        @classmethod
        def size(cls, width=None, height=None):
            return (
                cls.scale(width),
                cls.scale(height),
            )

        @classmethod
        def rect(cls, x, y, width=None, height=None):
            x, y = cls.point(x, y)
            width, height = cls.size(width, height)

            return x, y, width, height


    class Adapter(object):

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

            x, y, width, height = UtilsAdapter.rect(
                x,
                y,
                width,
                height
            )

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

            return renpy.store.Transform(child, **kwargs)

        @classmethod
        def image(
            cls,
            filename,
            **kwargs
        ):
            return cls.transform(filename, **kwargs)

        @classmethod
        def scale_image(cls, image, width, height):
            width, height = UtilsAdapter.size(width, height)
            return renpy.store.im.Scale(image, int(width), int(height))

