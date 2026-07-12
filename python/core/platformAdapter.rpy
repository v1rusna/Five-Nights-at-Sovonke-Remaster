init python in v1FNaSR:

    class UtilsAdapter(object):

        # Виртуальное разрешение проекта
        VIRTUAL_WIDTH = 1920
        VIRTUAL_HEIGHT = 1080

        # Реальное разрешение устройства
        REAL_WIDTH = None
        REAL_HEIGHT = None

        ES = True

        _scale = None
        _offset_x = None
        _offset_y = None

        @classmethod
        def init(cls):
            cls.ES = "Everlasting" in renpy.store.config.name
            cls.REAL_WIDTH = float(renpy.config.screen_width)
            cls.REAL_HEIGHT = float(renpy.config.screen_height)
            #cls.REAL_WIDTH = float(1280)
            #cls.REAL_HEIGHT = float(720)
            #cls.VIRTUAL_WIDTH = 1280
            #cls.VIRTUAL_HEIGHT = 720

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


    class UIAdapter(object):

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

        @classmethod
        def scale_style(cls, size):
            scale_size = int(UtilsAdapter.scale(size))
            if scale_size >= size:
                return scale_size

            return scale_size + size / 4

    class PAdapter(object):
        @classmethod
        def get_mod_folder(cls):
            if UtilsAdapter.ES:
                return "FNaS_R"
            return ""

        @classmethod
        def path(cls, path):
            if UtilsAdapter.ES:
                return path

            prefix = "FNaS_R/"
            if path.startswith(prefix):
                return path[len(prefix):]
            return path



    class Adapter(UIAdapter, PAdapter): pass

    UtilsAdapter.init()





