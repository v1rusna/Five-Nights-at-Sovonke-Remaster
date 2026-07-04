
init -100 python in v1rus:
    import threading
    import queue
    
    main_thread_queue = queue.Queue()
    
    def execute_in_main_thread(func, *args, **kwargs):
        """Добавить функцию в очередь для выполнения в главном потоке"""
        main_thread_queue.put((func, args, kwargs))
    
    def process_main_thread_queue():
        """Callback для обработки очереди в главном потоке"""
        try:
            while True:
                func, args, kwargs = main_thread_queue.get_nowait()
                func(*args, **kwargs)
        except queue.Empty:
            pass
    
    # Регистрируем callback
    renpy.config.interact_callbacks.append(process_main_thread_queue)


    class Flashlight(renpy.Displayable):

        def __init__(self, child, mask, curtain="#000", **kwargs):
            super(Flashlight, self).__init__(**kwargs)

            self.events = True

            self.child = renpy.displayable(child)
            self.mask = renpy.displayable(mask)
            self.curtain = renpy.displayable(curtain)

            self.xpos, self.ypos = renpy.get_mouse_pos()

        def render(self, width, height, st, at):

            scene = renpy.render(self.child, width, height, st, at)
            curtain = renpy.render(self.curtain, width, height, st, at)

            mask = renpy.render(self.mask, width, height, st, at)
            mask_width, mask_height = mask.get_size()

            light = renpy.Render(width, height, opaque=False)

            light.place(self.mask, self.xpos - (mask_width / 2.0), self.ypos - (mask_height / 2.0))

            rv = renpy.Render(width, height, opaque=False)

            rv.operation = renpy.display.render.IMAGEDISSOLVE
            rv.operation_alpha = True
            rv.operation_complete = 256.0 / (256.0 + 256.0)
            rv.operation_parameter = 256

            if renpy.display.render.models:
                rv.mesh = True
                rv.add_shader("renpy.imagedissolve",)
                rv.add_uniform("u_renpy_dissolve_offset", 0)
                rv.add_uniform("u_renpy_dissolve_multiplier", 1.0)
                rv.add_property("mipmap", renpy.config.mipmap_dissolves if (self.style.mipmap is None) else self.style.mipmap)

            rv.blit(light, (0, 0), focus=False, main=False)
            rv.blit(curtain, (0, 0), focus=False, main=False)
            rv.blit(scene, (0, 0), focus=True, main=True)

            return rv

        def event(self, ev, x, y, st):

            if self.events and ev.type == pygame.MOUSEMOTION:
                self.xpos, self.ypos = renpy.get_mouse_pos()
                renpy.redraw(self, 0)

                return self.child.event(ev, x, y, st)
            else:
                return None

        def visit(self):
            return [self.child, self.mask, self.curtain]

    
    import pygame

    class HoldingMouseImageButton(renpy.Displayable):
        """
        Честно вдохновленный класс
        """
        def __init__(self, idle, clicked=None, click_action=None, unclick_action=None, allow_alternate=False, **kwargs):
            super(HoldingMouseImageButton, self).__init__(**kwargs)

            self.displayable = renpy.displayable(idle)

            self.idle = self.displayable
            self.clicked = renpy.displayable(clicked) if clicked is not None else self.idle
        
            self.width = 0
            self.height = 0

            self.allow_alternate = allow_alternate

            self.click_action = click_action if click_action is not None else NullAction()
            self.unclick_action = unclick_action if unclick_action is not None else NullAction()

            self._clicked = False

        def force_unclick(self):
            if self._clicked:
                renpy.display.behavior.run(self.unclick_action)

            self._clicked = False
            self.displayable = self.idle

        def render(self, width, height, st, at):
            child_r = renpy.render(self.displayable, width, height, st, at)
            self.width, self.height = child_r.get_size()

            render = renpy.Render(self.width, self.height)

            render.blit(child_r, (0, 0))

            pygame.time.set_timer(renpy.display.core.PERIODIC, renpy.display.core.PERIODIC_INTERVAL)

            return render

        def event(self, ev, x, y, st):
            if (0 <= x <= self.width) and (0 <= y <= self.height):
                if ev.type == pygame.MOUSEBUTTONDOWN and (ev.button == 1 or (ev.button == 3 and self.allow_alternate)):
                    self._clicked = True
                    self.displayable = self.clicked
                    renpy.display.behavior.run(self.click_action)
                    renpy.redraw(self, 0.0)
                    return self.clicked.event(ev, x, y, st)

            if ev.type == pygame.MOUSEBUTTONUP and self._clicked:
                self._clicked = False
                self.displayable = self.idle
                renpy.display.behavior.run(self.unclick_action)
                renpy.redraw(self, 0.0)
                return self.idle.event(ev, x, y, st)
            
            return None
        
        def visit(self):
            return [ self.idle, self.clicked ]



init python:
    def v1_after_load_FNaSR():
        global save_name
        if "FNaSR" in save_name:
            renpy.error("The 'Five Nights at Sovenk Remaster' mod does not support the renpy save system.")

    config.after_load_callbacks.append(v1_after_load_FNaSR)














