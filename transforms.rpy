init 10 python:
    import math

    def v1_button_static_hover_func_FNaSR(t_obj, st, at):
        button_alpha = 1.0

        normalized_t = st / 0.5
        warped_t = v1_ease_FNaSR(normalized_t)

        if normalized_t > 1.0:
            t_obj.alpha = 0.5
            return None
        button_alpha = 1.0 - 0.5 * warped_t
        t_obj.alpha = button_alpha
        return 0.0

    def v1_ease_FNaSR(t):
        return 0.5 - math.cos(math.pi * t) / 2.0

    def v1_shake_t_func_FNaSR(t_obj, st, at):
        shake_power = 5.0

        t_obj.xoffset = random.uniform(-shake_power, shake_power)
        t_obj.yoffset = random.uniform(-shake_power, shake_power)

        return 0.0

    def v1_shake_rotate_t_func_FNaSR(t_obj, st, at):
        shake_rotate_power = 3.0

        t_obj.rotate = random.uniform(-shake_rotate_power, shake_rotate_power)

        return 0.0

    def v1_door_hold_vignette_appear_t_func_FNaSR(t_obj, st, at):
        DOOR_HOLDING_VIGNETTE_APPEAR = 0.8
        door_hold_vignette_current_alpha = 0.0

        normalized_t = st / DOOR_HOLDING_VIGNETTE_APPEAR
        warped_t = v1_ease_FNaSR(normalized_t)

        door_hold_vignette_current_alpha += warped_t

        if door_hold_vignette_current_alpha < 1.0:
            t_obj.alpha = door_hold_vignette_current_alpha
            return 0.0

        t_obj.alpha = 1.0
        return None

    def v1_door_hold_vignette_disappear_t_func_FNaSR(t_obj, st, at):
        DOOR_HOLDING_VIGNETTE_DISAPPEAR = 0.8
        
        if st >= DOOR_HOLDING_VIGNETTE_DISAPPEAR:
            t_obj.alpha = 0.0
            return None  # Завершаем трансформацию
        
        normalized_t = st / DOOR_HOLDING_VIGNETTE_DISAPPEAR
        warped_t = v1_ease_FNaSR(normalized_t)
        t_obj.alpha = 1.0 - warped_t  # Уменьшаем от 1.0 до 0.0
        
        return 0.0  # Продолжаем обновление

init 11:
    transform v1_align_FNaSR(x=0.0, y=0.0):
        align(x,y)

    transform v1_camera_set_center_zoom_t_FNaSR():
        xalign 0.5 yalign 0.5 zoom 1.1 subpixel True

    transform v1_text_flicker_FNaSR(fdelay=0.7):
        alpha 1.0
        pause fdelay
        alpha 0.0
        pause fdelay
        repeat

    # Честно вдохновленные скримеры

    transform v1_fading_t_FNaSR(anim_time=1.0, alpha_start=1.0, alpha_end=0.0, warper=_warper.linear):
        alpha alpha_start
        warp warper anim_time alpha alpha_end

    transform v1_uliya_screamer_t_FNaSR():
        xanchor 0.5 yanchor 0.0 xpos 0.5 ypos 0.1 alpha 0.0 zoom 0.8 subpixel True transform_anchor True
        parallel:
            easein_quad 0.4 ypos 0.0 alpha 1.0
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR
        parallel:
            yanchor 0.0 xpos 0.51 zoom 1.05
            pause 0.1
            yanchor 0.04 xpos 0.495 zoom 1.08
            pause 0.1
            yanchor 0.08 xpos 0.49 zoom 1.1
            pause 0.1
            yanchor 0.16 xpos 0.515 zoom 1.15
            pause 0.1
            yanchor 0.2 xpos 0.5 zoom 1.2
            pause 0.1
            yanchor 0.24 xpos 0.51 zoom 1.4
            pause 0.1
            yanchor 0.26 xpos 0.495 zoom 1.6
            pause 0.1
            yanchor 0.28 xpos 0.49 zoom 1.8
            pause 0.1
            yanchor 0.3 xpos 0.5 zoom 2.0

    transform v1_slavya_screamer_t_FNaSR():
        xanchor 0.5 yanchor 0.1 xpos 0.0 ypos 0.05 alpha 0.0 zoom 0.8 subpixel True transform_anchor True
        ease 0.1 yanchor 0.0 xpos 0.5 ypos 0.01 alpha 1.0 zoom 1.0
        parallel:
            linear 0.8 blur 5
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR
        parallel:
            yanchor 0.0 xpos 0.51 zoom 1.05
            pause 0.1
            yanchor 0.04 xpos 0.495 zoom 1.08
            pause 0.1
            yanchor 0.08 xpos 0.49 zoom 1.1
            pause 0.1
            yanchor 0.1 xpos 0.515 zoom 1.15
            pause 0.1
            yanchor 0.12 xpos 0.5 zoom 1.2
            pause 0.1
            yanchor 0.12 xpos 0.51 zoom 1.4
            pause 0.1
            yanchor 0.12 xpos 0.495 zoom 1.6
            pause 0.1
            yanchor 0.12 xpos 0.49 zoom 1.8
            pause 0.1
            yanchor 0.12 xpos 0.5 zoom 2.0

    transform v1_true_uliya_screamer_t_FNaSR():
        xanchor 0.5 yanchor 0.1 xpos 0.8 alpha 0.0 zoom 0.8 ypos 0.1 rotate -10.0 subpixel True transform_anchor True
        ease 0.2 xpos 0.5 yalign 0.6 alpha 1.0 zoom 1.0 rotate 0.0
        parallel:
            easein_quad 0.7 yalign 0.75
        parallel:
            linear 0.8 blur 5
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR
        parallel:
            xpos 0.51 zoom 1.05
            pause 0.1
            xpos 0.495 zoom 1.08
            pause 0.1
            xpos 0.49 zoom 1.1
            pause 0.1
            xpos 0.515 zoom 1.15
            pause 0.1
            xpos 0.5 zoom 1.2
            pause 0.1
            xpos 0.51 zoom 1.4
            pause 0.1
            xpos 0.495 zoom 1.6
            pause 0.1
            xpos 0.49 zoom 1.8
            pause 0.1
            xpos 0.5 zoom 1.9

    transform v1_olga_screamer_t_FNaSR():
        xanchor 0.5 yanchor 0.1 xpos 0.8 ypos 0.25 alpha 0.0 zoom 0.8 subpixel True transform_anchor True
        ease 0.2 yanchor 0.0 xpos 0.5 ypos 0.01 alpha 1.0 zoom 1.0
        parallel:
            linear 0.8 blur 5
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR
        parallel:
            yanchor 0.0 xpos 0.51 zoom 1.05
            pause 0.1
            yanchor 0.04 xpos 0.495 zoom 1.08
            pause 0.1
            yanchor 0.08 xpos 0.49 zoom 1.1
            pause 0.1
            yanchor 0.1 xpos 0.515 zoom 1.15
            pause 0.1
            yanchor 0.12 xpos 0.5 zoom 1.2
            pause 0.1
            yanchor 0.12 xpos 0.51 zoom 1.4
            pause 0.1
            yanchor 0.12 xpos 0.495 zoom 1.6
            pause 0.1
            yanchor 0.12 xpos 0.49 zoom 1.8
            pause 0.1
            yanchor 0.12 xpos 0.5 zoom 2.0

    transform v1_uliana_screamer_t_FNaSR():
        xanchor 0.5 yanchor -0.15 alpha 1.0 zoom 1.1 subpixel True transform_anchor True
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR
        parallel:
            yanchor 0.05 xpos 0.51 zoom 1.12
            pause 0.1
            yanchor 0.08 xpos 0.495 zoom 1.15
            pause 0.1
            yanchor 0.09 xpos 0.49 zoom 1.17
            pause 0.1
            yanchor 0.1 xpos 0.515 zoom 1.19
            pause 0.1
            yanchor 0.12 xpos 0.5 zoom 1.2
            pause 0.1
            yanchor 0.13 xpos 0.51 zoom 1.4
            pause 0.1
            yanchor 0.15 xpos 0.495 zoom 1.6
            pause 0.1
            yanchor 0.17 xpos 0.49 zoom 1.8
            pause 0.1
            yanchor 0.19 xpos 0.5 zoom 2.0

    transform v1_phantom_screamer_t_FNaSR():
        xanchor 0.5 yanchor 0.0 alpha 1.0 zoom 1.1 subpixel True transform_anchor True
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR
        parallel:
            yanchor 0.05 xpos 0.51 zoom 1.12
            pause 0.1
            yanchor 0.08 xpos 0.495 zoom 1.15
            pause 0.1
            yanchor 0.09 xpos 0.49 zoom 1.17
            pause 0.1
            yanchor 0.1 xpos 0.515 zoom 1.19
            pause 0.1
            yanchor 0.12 xpos 0.5 zoom 1.2
            pause 0.1
            yanchor 0.13 xpos 0.51 zoom 1.4
            pause 0.1
            yanchor 0.15 xpos 0.495 zoom 1.6
            pause 0.1
            yanchor 0.17 xpos 0.49 zoom 1.8
            pause 0.1
            yanchor 0.19 xpos 0.5 zoom 2.0

    transform v1_miku_screamer_t_FNaSR():
        xanchor 0.5 yanchor 0.0 xpos 0.5 ypos 0.2 alpha 0.0 zoom 0.8 subpixel True transform_anchor True
        parallel:
            pause 0.05
            easein_quad 0.25 ypos 0.1 alpha 1.0
            easein_quad 0.3 ypos -0.1
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR
        parallel:
            yanchor 0.2 xpos 0.51 zoom 1.05
            pause 0.1
            yanchor 0.17 xpos 0.495 zoom 1.08
            pause 0.1
            yanchor 0.13 xpos 0.49 zoom 1.1
            pause 0.1
            yanchor 0.1 xpos 0.515 zoom 1.15
            pause 0.1
            yanchor 0.07 xpos 0.5 zoom 1.2
            pause 0.1
            yanchor 0.02 xpos 0.51 zoom 1.4
            pause 0.1
            yanchor 0.0 xpos 0.495 zoom 1.6
            pause 0.1
            yanchor -0.02 xpos 0.49 zoom 1.8
            pause 0.1
            yanchor -0.05 xpos 0.5 zoom 2.0

    # Вдохновленные transform камеры

    transform v1_yulia_screamer_camera_t_FNaSR():
        ease 0.05 xalign 0.5 yalign 0.5 alpha 1.0 zoom 1.1 subpixel True transform_anchor True matrixcolor HueMatrix(value=0.0) * SaturationMatrix(value=1.0)
        parallel:
            linear 0.8 blur 15 matrixcolor HueMatrix(value=90.0) * SaturationMatrix(value=0.1)
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR

    transform v1_general_screamer_camera_t_FNaSR():
        ease 0.05 xalign 0.5 yalign 0.5 alpha 1.0 zoom 1.1 subpixel True transform_anchor True matrixcolor SaturationMatrix(value=1.0)
        parallel:
            linear 0.8 blur 15 matrixcolor SaturationMatrix(value=0.1)
        parallel:
            function v1_shake_t_func_FNaSR
        parallel:
            function v1_shake_rotate_t_func_FNaSR

    # Прочие

    transform v1_door_hold_vignette_appear_FNaSR():
        function v1_door_hold_vignette_appear_t_func_FNaSR

    transform v1_door_hold_vignette_disappear_FNaSR():
        function v1_door_hold_vignette_disappear_t_func_FNaSR

    transform v1_dynamic_camera_static_t_FNaSR():
        alpha 0.05
        choice:
            linear 0.04 alpha 0.2
            linear 0.02 alpha 0.05
        choice:
            linear 0.01 alpha 0.25
            linear 0.04 alpha 0.05
        choice:
            alpha 0.15
            pause 0.01
            alpha 0.05
        choice:
            alpha 0.35
            pause 0.04
            alpha 0.05
        pause 1.5
        repeat

    transform v1_camera_static_t_FNaSR():
        alpha 1.0
        ease 0.5 alpha 0.05
        v1_dynamic_camera_static_t_FNaSR()

    transform v1_camera_enemy_impact_static_t_FNaSR():
        alpha 1.0
        pause 0.1
        alpha 0.9
        pause 0.05
        alpha 1.0
        pause 0.03
        alpha 0.85
        pause 0.03
        alpha 1.0
        pause 0.1
        alpha 0.95
        pause 0.05
        repeat

    transform v1_button_static_hover_t_FNaSR():
        size (110, 40)
        function v1_button_static_hover_func_FNaSR





























