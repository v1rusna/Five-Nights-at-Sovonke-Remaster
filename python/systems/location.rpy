init -5 python in v1FNaSR:
    class MainLocation(FNaSRBase):
        def __init__(self):
            self.is_bulb = True
            self.is_tablet = True
            self.is_door = True

            self.bulb = True

            self.img_main_loc = display.Parallax(
                displayable=resources.images.bg["R_int_mt_house_night_light"],
                zoom=1.15,
                anchor=(renpy.config.screen_width>>1, renpy.config.screen_height>>1),
                power=0.07,
                sharpness_factor=0.1
            )

            self.__img_bulb_on = renpy.displayable(resources.images.bg["R_int_mt_house_night_light"])
            self.__img_bulb_off = renpy.displayable(resources.images.bg["R_int_mt_house_night"])

            self.__images = {
                True: self.__img_bulb_on,
                False: self.__img_bulb_off
            }

            #self.__tablet_button = InfoObject(
            #    is_show=False,
            #    align=InfoObject(x=0.5, y=1.0),
            #    image=renpy.displayable(resources.images.other["FNaG_Monitor_Button"]),
            #    button=renpy.display.behavior.Button(
            #        background=None,
            #        xsize=700,
            #        ysize=200,
            #        clicked=renpy.store.Function(game.camera_system.act_cameras)
            #    )
            #)

        #def show_tablet_button(self, xalign=None, yalign=None):
        #    align = self.__tablet_button.align
        #    xalign = align.x if xalign is None else xalign
        #    yalign = align.y if yalign is None else yalign
        #    if not self.__tablet_button.is_show:
        #        game.object_display.add_obj(
        #            key="tablet_button_object",
        #            obj=self.__tablet_button.button,
        #            align=(xalign, yalign),
        #            layer="screens"
        #        )
        #        self.__tablet_button.is_show = True
        #    else:
        #        game.object_display.update_obj(
        #            key="tablet_button_object",
        #            align=(xalign, yalign)
        #        )

        #def hide_tablet_button(self):
        #    if self.__tablet_button.is_show:
        #        game.object_display.remove_obj(
        #            key="tablet_button_object"
        #        )
        #        self.__tablet_button.is_show = False

        def set_img(self, img):
            self.img_main_loc.displayable = renpy.displayable(img)

        def set_images_main_location(self, bulb_on=None, bulb_off=None):
            if bulb_on is not None:
                self.__images[True] = renpy.displayable(bulb_on)
            if bulb_off is not None:
                self.__images[False] = renpy.displayable(bulb_off)

            self.img_main_loc.displayable = self.__images[self.bulb]

        def update(self):
            if not self.is_tablet:
                self.hide_tablet_button()

        def reset(self):
            self.is_bulb = True
            self.is_tablet = True
            self.is_door = True

            self.bulb = True

            self.__images = {
                True: self.__img_bulb_on,
                False: self.__img_bulb_off
            }

            self.img_main_loc.displayable = self.__images[True]

        def set_bulb(self, value, play_sound=True):
            _old = self.bulb
            self.bulb = bool(value)
            self.img_main_loc.displayable = self.__images[self.bulb]

            global_event.emit("enemy.bulb", self.bulb)

            if self.bulb:
                if play_sound and _old != self.bulb:
                    execute_in_main_thread(renpy.play, resources.sounds.sfx["switch_on"], "sound")
            else:
                if play_sound and _old != self.bulb:
                    execute_in_main_thread(renpy.play, resources.sounds.sfx["switch_off"], "sound")
