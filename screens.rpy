

screen V1BaseUIScreenFNaSR:
    key ["K_ESCAPE", "mouseup_3"] action ShowMenu("V1GameMenuSelectorFNaSR")

# Главный экран
screen V1MainScreenFNaSR():
    zorder 10
    $ game = renpy.store.v1FNaSR.game

    timer 0.1 repeat True action Function(game.check_killer)

    use V1BaseUIScreenFNaSR()

    if game.debug:
        use V1DebugScreenFNaSR()

    if game.mainL.is_tablet:
        key "K_SPACE" action Function(game.camera_system.act_cameras)
        button:
            align(0.5, 1.0)
            #background None
            xsize 600
            ysize 200
            action Function(game.camera_system.act_cameras)
        imagebutton:
            align (0.5, 0.9)
            idle "v1_ui_monitor_button_FNaSR"#v1resFNaSR.images.other["FNaG_Monitor_Button"]
            #action Function(game.camera_system.act_cameras)

# Экран офиса
screen V1OfficeScreenFNaSR(game):
    vbox align (0.98, 0.04):
        text "Night: [game.night_system.loaded.night]" style "v1_text_24_style_FNaSR" xalign 1.0
        if game.god_mode:
            text "Deaths: {}".format(game.deaths["all"]) style "v1_text_24_style_FNaSR" xalign 1.0

    if game.mainL.is_bulb and not game.camera_system.animation:
        imagebutton:
            align (0.25, 0.9)
            idle ("v1_ui_bulb_on_FNaSR" if game.mainL.bulb else "v1_ui_bulb_off_FNaSR")#(v1resFNaSR.images.other["bulb_on"] if game.mainL.bulb else v1resFNaSR.images.other["bulb_off"])
            action Function(game.mainL.set_bulb, not game.mainL.bulb)

    if game.mainL.is_door:
        text game.door_system.get_text() style "v1_text_24_style_FNaSR" align (0.9, 0.4)
        add game.door_system.door_ImageButton align (0.9, 0.5)

# Экран камеры
screen V1CamerasScreenFNaSR(game):
    # Картинка камеры
    if not game.camera_system.animation:
        add "v1_C_static_entire_FNaSR" at v1_dynamic_camera_static_t_FNaSR()

        add v1resFNaSR.images.other["FNaG_Cam_Frame"]

        text "{i}[game.camera_system.charge]%{/i}" style "v1_text_24_style_FNaSR" align(0.025, 0.04)

        text game.game_time.get_time() style "v1_text_24_style_FNaSR" align(0.98, 0.032)
        #if game.night_system.loaded.level == -1:
        #    text "Total hours survived: {}".format(game.game_time.total_hours) style "v1_text_24_style_FNaSR" xalign 1.0

        imagemap:
            align (1.6, 1.7)
            idle v1resFNaSR.images.map["map_avaliable_mod"]
            hover v1resFNaSR.images.map["map_selected_mod"]
            insensitive v1resFNaSR.images.map["map_insensitive_mod"]

            for cam in game.camera_system.list_cameras:
                if cam.is_active:
                    $ b_s = cam.break_second
                    $ x, y, w, h = cam.coordinates
                    hotspot(x, y, w, h):
                        sensitive cam.id != game.camera_system.select and not b_s
                        action Function(game.camera_system.select_camera, cam)

                    if b_s > 0:
                        text "{size=-8}"+"RESTORE: {}s".format(b_s) style "v1_text_18_style_red_FNaSR" xpos x + w / 2 ypos y + h / 2 xanchor "center" yanchor "center"

screen V1TabletAnimScreenFNaSR(game):
    if game.camera_system.show_tablet:
        $ show_screen = "V1CamerasScreenFNaSR"
    else:
        $ show_screen = "V1OfficeScreenFNaSR"
    timer 0.18 action [Hide("V1TabletAnimScreenFNaSR"), Show(show_screen, game=game)]

    if game.camera_system.show_tablet:
        add "anim v1_tablet_open_entire_FNaSR"
    else:
        add "anim v1_tablet_close_entire_VNaSR"

screen V1DebugScreenFNaSR():
    #zorder 99
    $ game = renpy.store.v1FNaSR.game

    #key "ctrl_K_a" action ShowMenu("V1DebugPanelScreenFNaSR")
    key "K_a" action ShowMenu("V1DebugPanelScreenFNaSR")

    vbox:
        #text "Количество мусора: {}".format(len(renpy.gc.garbage)) style "v1_text_12_style_FNaSR"
        #text "Размер очереди перерисовки: {}".format(len(renpy.display.render.redraw_queue)) style "v1_text_12_style_FNaSR"
        #text "Размер кэша рендера: {}".format(len(renpy.display.render.render_cache)) style "v1_text_12_style_FNaSR"
        #text "---------------" style "v1_text_12_style_FNaSR"
        text "debug panel: ctrl + a"style "v1_text_12_style_FNaSR"
        text "change: {}".format(game.camera_system.charge) style "v1_text_12_style_FNaSR"
        text "hours: {}".format(game.game_time.total_hours) style "v1_text_12_style_FNaSR"
        #text "enemy in loc: {}".format(repr(game.camera_system.get_enemy()).replace("[", "[[")) style "v1_text_12_style_FNaSR"
        text "---------------" style "v1_text_12_style_FNaSR"
        for enemy in game.enemy_system:
            if enemy.activity:
                if hasattr(enemy, "debug_info") and isinstance(enemy.debug_info, v1FNaSR.DebugInfo):
                    $ debug_text = v1FNaSR.DebugInfo.get_enemy_debug_text(enemy)
                else:
                    $ debug_text = v1FNaSR.DebugInfo.generate_enemy_debug_text(enemy)
                text debug_text style "v1_text_12_style_FNaSR"

    vbox xalign .5:
        textbutton"победить" background None text_style "v1_text_12_style_FNaSR" xalign .5 action Function(game.win)
        textbutton"сбросить прогресс" background None text_style "v1_text_12_style_FNaSR" xalign .5 action SetField(v1FNaSR.Settings, "nights_gone", dict())
        textbutton"god mode: [game.god_mode]" background None text_style "v1_text_12_style_FNaSR" xalign .5 action SetField(game, "god_mode", not game.god_mode)
        hbox xalign .5:
            textbutton"{size=+4}<<" background None text_style "v1_text_12_style_FNaSR" xalign .5 action Function(game.game_time.set_sleep_time, game.game_time._sleep_time-1)
            textbutton"{size=+4}<" background None text_style "v1_text_12_style_FNaSR" xalign .5 action Function(game.game_time.set_sleep_time, game.game_time._sleep_time-.1)
            textbutton str(game.game_time._sleep_time) background None text_style "v1_text_12_style_FNaSR" xalign .5
            textbutton"{size=+4}>" background None text_style "v1_text_12_style_FNaSR" xalign .5 action Function(game.game_time.set_sleep_time, game.game_time._sleep_time+.1)
            textbutton"{size=+4}>>" background None text_style "v1_text_12_style_FNaSR" xalign .5 action Function(game.game_time.set_sleep_time, game.game_time._sleep_time+1)


screen V1DebugPanelScreenFNaSR():
    default mode = None
    $ game = renpy.store.v1FNaSR.game

    on "show" action Function(game.game_time.freeze)
    on "hide" action Function(game.game_time.unfreeze)

    text "{size=+10}Панель управления" style "v1_text_12_style_FNaSR" align(0.5, 0.1)

    if mode is None:
        vbox align(0.5, 0.5) spacing 5:
            textbutton "{size=+5}Панель противников" text_style "v1_text_12_style_FNaSR" background None xalign 0.5 action SetScreenVariable("mode", "enemy")
            textbutton "{size=+5}Панель состояния игры" text_style "v1_text_12_style_FNaSR" background None xalign 0.5 action SetScreenVariable("mode", "game")
            textbutton "{size=+5}Сбросить счетчик смертей" text_style "v1_text_12_style_FNaSR" background None xalign 0.5 action SetField(game, "deaths", {"all": 0})
            textbutton "{size=+5}Закрыть" text_style "v1_text_12_style_FNaSR" background None xalign 0.5 action Return()
    else:
        textbutton "{size=+20}Вернуться" text_style "v1_text_12_style_FNaSR" background None align (0.1, 0.9) action SetScreenVariable("mode", None)

    if mode == "enemy":
        use V1DebugPanelEnemyScreenFNaSR()

    if mode == "game":
        use V1DebugPanelGameScreenFNaSR()

screen V1DebugPanelEnemyScreenFNaSR():
    $ game = renpy.store.v1FNaSR.game

    text "{size=+5}Противниками" style "v1_text_12_style_FNaSR" align(0.5, 0.13)

    hbox:
        spacing 0 # расстояние между списком и полоской прокрутки
        xsize 999
        ysize 760

        align(0.56, 0.55)

        viewport id "DebugPanelEnemy":
            xfill False
            yfill False
            mousewheel True

            vbox spacing 3:
                textbutton "{color=#00b627}Активировать всех":
                    xalign 0.5
                    background None
                    text_style "v1_text_16_style_FNaSR"
                    action Function(v1FNaSR._Screen._activities_all_pioneer, True)

                textbutton "{color=#e60000}Деактивировать всех":
                    xalign 0.5
                    background None
                    text_style "v1_text_16_style_FNaSR"
                    action Function(v1FNaSR._Screen._activities_all_pioneer, False)

                for enemy in game.enemy_system:
                    if hasattr(enemy, "debug_info") and isinstance(enemy.debug_info, v1FNaSR.DebugInfo):
                        text "{size=+2}"+"{}(tag={}, path=[[{}], DebugInfo(name={}, color={}))".format(
                            enemy.__class__.__name__,
                            enemy.tag,
                            ", ".join(v1FNaSR.v1_map(str, enemy.enemy_path.paths)),
                            enemy.debug_info.name,
                            "{color="+enemy.debug_info.color+"}"+enemy.debug_info.color+"{/color}" if enemy.debug_info.color is not None else None
                        ) xalign 0.5 style "v1_text_16_style_FNaSR"

                    else:
                        text "{size=+2}"+"{}(tag={}, path=[[{}])".format(enemy.__class__.__name__, enemy.tag, ", ".join(v1FNaSR.v1_map(str, enemy.enemy_path.paths))) xalign 0.5 style "v1_text_16_style_FNaSR"

                    textbutton "Противник {}".format("{color=#00b627}активен{/color}" if enemy.activity else "{color=#e60000}неактивен{/color}"):
                        xalign 0.5
                        background None
                        text_style "v1_text_16_style_FNaSR"
                        action SetField(enemy, "activity", not enemy.activity)

                    hbox spacing 5 xalign 0.5:
                        textbutton "{size=+5}-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(enemy, "ai_level", enemy.ai_level-1) if enemy.ai_level > 1 else NullAction())
                        text "AI level: {}".format(enemy.ai_level) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                        textbutton "{size=+5}+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(enemy, "ai_level", enemy.ai_level+1) if enemy.ai_level < v1FNaSR.Constants.MAX_AI_LEVEL else NullAction())

                    hbox spacing 5 xalign 0.5:
                        textbutton "{size=+5}-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(enemy, "max_movement_opportunities", enemy.max_movement_opportunities-1) if enemy.max_movement_opportunities > 0 else NullAction())
                        text "Пропуск тиков: {}".format(enemy.max_movement_opportunities) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                        textbutton "{size=+5}+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(enemy, "max_movement_opportunities", enemy.max_movement_opportunities+1) if enemy.max_movement_opportunities < 99 else NullAction())

                    hbox spacing 5 xalign 0.5:
                        textbutton "-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(enemy, "difficulty", enemy.difficulty-1) if enemy.difficulty > -100 else NullAction())
                        text "Модификатор сложности: {}".format(enemy.difficulty) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                        textbutton "+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(enemy, "difficulty", enemy.difficulty+1) if enemy.difficulty < 100 else NullAction())

                    if len(enemy.enemy_path):
                        hbox spacing 5 xalign 0.5:
                            textbutton "-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action Function(enemy.enemy_path.previous_loc)
                            text "Локация: {}/{}({})".format(enemy.enemy_path.location, len(enemy.enemy_path), enemy.enemy_path.get_camera_id_by_loc()) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                            textbutton "+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action Function(enemy.enemy_path.next_loc)

                    text""

    vbar value YScrollValue("DebugPanelEnemy") bottom_bar "images/misc/none.png" top_bar "images/misc/none.png" thumb "images/misc/none.png"
     
screen V1DebugPanelGameScreenFNaSR():
    $ game = renpy.store.v1FNaSR.game
    $ panel = v1FNaSR.DebugPanel

    text "{size=+5}Игрой" style "v1_text_12_style_FNaSR" align(0.5, 0.13)

    hbox:
        spacing 0
        xsize 999
        ysize 760

        align(0.585, 0.55)

        viewport id "DebugPanelGame":
            xfill False
            yfill False
            mousewheel True

            vbox spacing 3:
                text "{color=#a607e0}{size=+6}--GameTime--" style "v1_text_12_style_FNaSR" xalign 0.5
                hbox spacing 5 xalign 0.5:
                    textbutton "-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(game.game_time, "total_hours", game.game_time.total_hours-1) if game.game_time.total_hours > 0 else NullAction())
                    text "Всего часов жизни: {}".format(game.game_time.total_hours) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                    textbutton "+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(game.game_time, "total_hours", game.game_time.total_hours+1) if game.game_time.total_hours < 99 else NullAction())

                hbox spacing 5 xalign 0.5:
                    textbutton "-" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(game.game_time.clock.set_hour, game.game_time.clock.hour-1)
                    text "Часов: {}".format(game.game_time.clock.hour) xalign 0.5 style "v1_text_16_style_FNaSR"
                    textbutton "+" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(game.game_time.clock.set_hour, game.game_time.clock.hour+1)

                hbox spacing 5 xalign 0.5:
                    textbutton "-" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(game.game_time.set_hour_time, game.game_time._hour_time-1)
                    text "Длинна часа: {}".format(game.game_time._hour_time) xalign 0.5 style "v1_text_16_style_FNaSR"
                    textbutton "+" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(game.game_time.set_hour_time, game.game_time._hour_time+1)

                text""

                text "{color=#a607e0}{size=+6}--CameraSystem--" style "v1_text_12_style_FNaSR" xalign 0.5
                hbox spacing 5 xalign 0.5:
                    textbutton "{size=+5}-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(game.camera_system, "charge", game.camera_system.charge-1) if game.camera_system.charge > 0 else NullAction())
                    text "Заряд: {}".format(game.camera_system.charge) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                    textbutton "{size=+5}+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(game.camera_system, "charge", game.camera_system.charge+1) if game.camera_system.charge < 100 else NullAction())

                hbox spacing 5 xalign 0.5:
                    textbutton "{size=+5}-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(game.camera_system, "discharge", game.camera_system.discharge-1) if game.camera_system.discharge > 1 else NullAction())
                    text "Разряд батареи: {}".format(game.camera_system.discharge) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                    textbutton "{size=+5}+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(game.camera_system, "discharge", game.camera_system.discharge+1) if game.camera_system.discharge < 99 else NullAction())

                text""

                textbutton "Починить все камеры" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(panel.repair_all_cameras)
                textbutton "Сломать все камеры" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(panel.break_all_cameras)
                textbutton "Сломать случайные камеры" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(panel.break_random_cameras)

                text""

                text "{size=+4}Список камер:" style "v1_text_12_style_FNaSR" xalign 0.5
                for camera in game.camera_system.list_cameras:
                    text "{size=-1}"+"Camera(id={}, is_active={}, break_second={}, enemy=[[{}])".format(camera.id, camera.is_active, camera.break_second, ", ".join([e.tag for e in camera.enemy])) xalign 0.5 style "v1_text_16_style_FNaSR"
                    textbutton "{size=-2}"+"Камера {}".format("{color=#00b627}активна{/color}" if camera.is_active else "{color=#e60000}неактивна{/color}"):
                        xalign 0.5
                        background None
                        text_style "v1_text_16_style_FNaSR"
                        action SetField(camera, "is_active", not camera.is_active)

                    if camera.break_second:
                        textbutton "{size=-2}Починить" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(camera.repair)
                    else:
                        textbutton "{size=-2}Сломать" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(camera.break_c, renpy.random.randint(5, 99))

                text""

                text "{color=#a607e0}{size=+6}--NightSystem--" style "v1_text_12_style_FNaSR" xalign 0.5
                textbutton "Перезапустить ночь" xalign 0.5 background None text_style "v1_text_16_style_FNaSR" action Function(game.restart_night)
                hbox spacing 5 xalign 0.5:
                    textbutton "{size=+5}-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(game.night_system.loaded, "end_of_shift", game.night_system.loaded.end_of_shift-1) if game.night_system.loaded.end_of_shift > 0 else NullAction())
                    text "Конец смены: {}ч".format(game.night_system.loaded.end_of_shift) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                    textbutton "{size=+5}+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action (SetField(game.night_system.loaded, "end_of_shift", game.night_system.loaded.end_of_shift+1) if game.night_system.loaded.end_of_shift < 99 else NullAction())

                text "{size=+4}Список ночей:" style "v1_text_12_style_FNaSR" xalign 0.5
                for night in game.night_system:
                    text "Night(night={}, level={}, end_of_shift={}, player_start={}, always_available={})".format(
                        night.night,
                        night.level,
                        night.end_of_shift,
                        night.player_start,
                        night.always_available
                    ) xalign 0.5 style "v1_text_16_style_FNaSR"

                text""

                text "{color=#a607e0}{size=+6}--DoorSystem--" style "v1_text_12_style_FNaSR" xalign 0.5
                textbutton "{size=-2}"+"Дверь {}".format("{color=#00b627}открыта{/color}" if game.door_system.is_door_open else "{color=#e60000}закрыта{/color}"):
                    xalign 0.5
                    background None
                    text_style "v1_text_16_style_FNaSR"
                    action Function(game.door_system.door, game.door_system.is_door_open)

                hbox spacing 5 xalign 0.5:
                    textbutton "{size=+5}-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action Function(game.door_system.add_panic, -1)
                    text "Паника: {}/{}".format(game.door_system.panic, game.door_system.max_panic) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                    textbutton "{size=+5}+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action Function(game.door_system.add_panic, 1)

                hbox spacing 5 xalign 0.5:
                    textbutton "{size=+5}-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action Function(game.door_system.set_max_panic, game.door_system.max_panic-1)
                    text "Максимум паники: {}".format(game.door_system.max_panic) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                    textbutton "{size=+5}+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action Function(game.door_system.set_max_panic, game.door_system.max_panic+1)

                hbox spacing 5 xalign 0.5:
                    textbutton "{size=+5}-" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action Function(game.door_system.set_rollback_threshold, game.door_system.rollback_threshold-1)
                    text "Граница сброса: {}/{}".format(game.door_system.rollback_threshold, game.door_system.max_panic) align(0.5, 0.5) style "v1_text_16_style_FNaSR"
                    textbutton "{size=+5}+" align(0.5, 0.5) background None text_style "v1_text_16_style_FNaSR" action Function(game.door_system.set_rollback_threshold, game.door_system.rollback_threshold+1)

                text""

                text "{color=#a607e0}{size=+6}--MainLocation--" style "v1_text_12_style_FNaSR" xalign 0.5
                textbutton "{size=-2}"+"Механика света {}".format("{color=#00b627}доступна{/color}" if game.mainL.is_bulb else "{color=#e60000}недоступна{/color}"):
                    xalign 0.5
                    background None
                    text_style "v1_text_16_style_FNaSR"
                    action SetField(game.mainL, "is_bulb", not game.mainL.is_bulb)

                textbutton "{size=-2}"+"Механика камер {}".format("{color=#00b627}доступна{/color}" if game.mainL.is_tablet else "{color=#e60000}недоступна{/color}"):
                    xalign 0.5
                    background None
                    text_style "v1_text_16_style_FNaSR"
                    action SetField(game.mainL, "is_tablet", not game.mainL.is_tablet)

                textbutton "{size=-2}"+"Механика двери {}".format("{color=#00b627}доступна{/color}" if game.mainL.is_door else "{color=#e60000}недоступна{/color}"):
                    xalign 0.5
                    background None
                    text_style "v1_text_16_style_FNaSR"
                    action SetField(game.mainL, "is_door", not game.mainL.is_door)

                textbutton "{size=-2}"+"Свет {}".format("{color=#00b627}включен{/color}" if game.mainL.bulb else "{color=#e60000}выключен{/color}"):
                    xalign 0.5
                    background None
                    text_style "v1_text_16_style_FNaSR"
                    action Function(game.mainL.set_bulb, not game.mainL.bulb)


    vbar value YScrollValue("DebugPanelGame") bottom_bar "images/misc/none.png" top_bar "images/misc/none.png" thumb "images/misc/none.png"



screen V1MainMenuFrameFNaSR(s=True, show_enemy=None, night=None, time="23:57"):
    $ mm = v1FNaSR.MainMenu
    if night is None:
        $ night = v1FNaSR.game.night_system.get_next_night()

    add mm.get_bg()

    #if renpy.random.random() > 0.8 and s:
    #    $ item = mm.get_enemy()
    #    add item[0] pos item[1]

    if show_enemy is not None:
        add show_enemy align(0.5, 0.5)
    elif renpy.random.random() > 0.7 and s:
        add mm.get_enemy()[0] xalign .9

    add "v1_C_static_entire_FNaSR" at v1_camera_static_t_FNaSR()

    add v1resFNaSR.images.other["FNaG_Cam_Frame"]

    vbox align (0.98, 0.04):
        text "Night: {}".format(night) style "v1_text_24_style_FNaSR" xalign 1.0 at v1_text_flicker_FNaSR()
        text time style "v1_text_24_style_FNaSR" xalign 1.0 at v1_text_flicker_FNaSR()


    if not s:
        add mm.text("Пять Ночей в Совёнке Remaster", size=24, g_power=0.0575) align(0.5, 0.1)
    else:
        textbutton mm.text("Пять Ночей в Совёнке Remaster", size=24, g_power=0.0575) background None align(0.5, 0.1) action SetVariable("v1FNaSR.FNaSR.debug", not v1FNaSR.FNaSR.debug)

        #imagemap align (1.6, 1.7):
        #    idle v1resFNaSR.images.map["map_avaliable_mod"]
        #    hover v1resFNaSR.images.map["map_selected_mod"]
        #    insensitive v1resFNaSR.images.map["map_insensitive_mod"]
        #    for cam in v1FNaSR.game.camera_system.list_cameras:
        #        if cam.is_active:
        #            $ x, y, w, h = cam.coordinates
        #            hotspot(x, y, w, h) action (Function(mm.restart_screen), Function(mm.set_bg, cam.image))

    textbutton mm.text("v1rus team") background None align(0.0185, 0.97) hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action OpenURL("https://t.me/+VewEitmB66k0MmQy")


screen V1MainMenuFNaSR:
    tag v1menuFNaSR

    use V1MainMenuFrameFNaSR()
    $ mm = v1FNaSR.MainMenu

    key "mouseup_3" action NullAction()
    key "K_ESCAPE" action NullAction()

    vbox align(0.15, 0.5) spacing 15:
        textbutton mm.text("Играть") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action(Hide('V1MainMenuFNaSR'), Jump('v1_play_FNaSR'))
        textbutton mm.text("Выбор ночи") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(mm.screen_switching, "V1MainMenuFNaSR", "V1MainMenuChoiceNightFNaSR")
        textbutton mm.text("Достижения") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(mm.screen_switching, "V1MainMenuFNaSR", "V1MainMenuAchievementsFNaSR")
        textbutton mm.text("Настройки") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(mm.screen_switching, "V1MainMenuFNaSR", "V1MainMenuSettingsFNaSR")
        textbutton mm.text("Выйти") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action (Hide('V1MainMenuFNaSR'), Jump('v1_exit_mm_FNaSR'))

screen V1MainMenuChoiceNightFNaSR:
    tag v1menuFNaSR

    $ mm = v1FNaSR.MainMenu
    use V1MainMenuFrameFNaSR()

    key "mouseup_3" action Function(mm.screen_switching, "V1MainMenuChoiceNightFNaSR", "V1MainMenuFNaSR")
    key "K_ESCAPE" action Function(mm.screen_switching, "V1MainMenuChoiceNightFNaSR", "V1MainMenuFNaSR")

    add mm.text("Выбор ночи", size=22) align(0.5, 0.14)

    vbox align(0.15, 0.5) spacing 15:
        add mm.text("Список ночей", size=28)

        for n in v1FNaSR.game.night_system:
            button:
                background None
                if v1FNaSR.Settings.nights_gone.get(n.night, False) or n.always_available:
                    hover_sound v1resFNaSR.sounds.ui["button_h"]
                    activate_sound v1resFNaSR.sounds.ui["button_c"]
                    action (Hide('V1MainMenuChoiceNightFNaSR'), Call('v1_play_FNaSR', n))
                
                fixed:
                    fit_first True
                    
                    text mm.text("Ночь {}".format(n.night))
                    
                    if not v1FNaSR.Settings.nights_gone.get(n.night, False) and not n.always_available:
                        add "v1_button_static_entire_FNaSR" at v1_button_static_hover_t_FNaSR()

        textbutton mm.text("custom night") background None action [
            Function(v1FNaSR.game.night_system.custom_night.init_custom),
            Function(mm.screen_switching, "V1MainMenuChoiceNightFNaSR", "V1MainMenuCustomNightFNaSR")
        ]
        
        textbutton mm.text("Назад") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(mm.screen_switching, "V1MainMenuChoiceNightFNaSR", "V1MainMenuFNaSR")

screen V1MainMenuSettingsFNaSR:
    tag v1menuFNaSR

    use V1MainMenuFrameFNaSR(False)
    $ mm = v1FNaSR.MainMenu
    $ bar_null = Frame(v1resFNaSR.images.other["bar_null"],36,36)
    $ bar_full = Frame(v1resFNaSR.images.other["bar_full"],36,36)

    $ setting_history = "не пропускать" if v1FNaSR.Settings.view_story else "пропускать"
    $ situations_history = "показывать" if v1FNaSR.Settings.view_situations else "пропускать"
    $ game_difficulty = v1FNaSR.Settings.game_difficulty

    key "mouseup_3" action Function(mm.screen_switching, "V1MainMenuSettingsFNaSR", "V1MainMenuFNaSR")
    key "K_ESCAPE" action Function(mm.screen_switching, "V1MainMenuSettingsFNaSR", "V1MainMenuFNaSR")

    add mm.text("Настройки", size=22) align(0.5, 0.14)

    vbox align(0.5, 0.5) spacing 10:
        for volume_type, label in (("music volume", "Музыка"), ("sound volume", "Звуки"), ("voice volume", "Эмбиент")):
            add mm.text(label) xalign 0.5
            bar:
                value Preference(volume_type)
                left_bar bar_full
                right_bar bar_null
                thumb None
                hover_thumb None
                xmaximum 0.25
                ymaximum 36
                xalign 0.5

        textbutton mm.text("Сбросить прогресс ночей"):
            background None
            xalign 0.5
            hover_sound v1resFNaSR.sounds.ui["button_h"]
            activate_sound v1resFNaSR.sounds.ui["button_c"]
            action Function(mm.screen_switching, "V1MainMenuSettingsFNaSR", "V1ConfirmationScreenFNaSR",
                label="Вы действительно хотите сбросить прогресс?",
                yes_action=(SetField(v1FNaSR.Settings, "nights_gone", dict()), Function(mm.screen_switching, "V1ConfirmationScreenFNaSR", "V1MainMenuSettingsFNaSR")),
                no_action=Function(mm.screen_switching, "V1ConfirmationScreenFNaSR", "V1MainMenuSettingsFNaSR"),
                use_menu_frame=True
            )

        textbutton mm.text("Сюжет: {}".format(setting_history)) background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] xalign 0.5 action SetField(v1FNaSR.Settings, "view_story", not v1FNaSR.Settings.view_story)

        textbutton mm.text("Ситуации: {}".format(situations_history)) background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] xalign 0.5 action SetField(v1FNaSR.Settings, "view_situations", not v1FNaSR.Settings.view_situations)

        textbutton mm.text("Сложность: {}".format(game_difficulty)) background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] xalign 0.5 action Function(mm.screen_switching, "V1MainMenuSettingsFNaSR", "V1MainMenuSettingsDifficultyFNaSR")


        textbutton mm.text("Назад"):
            background None xalign 0.5 
            hover_sound v1resFNaSR.sounds.ui["button_h"] 
            activate_sound v1resFNaSR.sounds.ui["button_c"] 
            action [Function(v1FNaSR.Settings.save), Function(mm.screen_switching, "V1MainMenuSettingsFNaSR", "V1MainMenuFNaSR")]

screen V1MainMenuSettingsDifficultyFNaSR:
    tag v1menuFNaSR

    use V1MainMenuFrameFNaSR(False)
    $ mm = v1FNaSR.MainMenu

    key "mouseup_3" action Function(mm.screen_switching, "V1MainMenuSettingsDifficultyFNaSR", "V1MainMenuSettingsFNaSR")
    key "K_ESCAPE" action Function(mm.screen_switching, "V1MainMenuSettingsDifficultyFNaSR", "V1MainMenuSettingsFNaSR")

    $ game_difficulty = v1FNaSR.Settings.game_difficulty
    $ description_difficulty = None

    add mm.text("Настройки Сложности", size=22) align(0.5, 0.14)

    vbox align(0.75, 0.5):
        if mm._dd is not None:
            for line in mm._dd:
                add mm.text(line, size=22) xalign 0.5

    vbox align(0.15, 0.5) spacing 15:
        add mm.text("Текущая сложность: {}".format(game_difficulty), size=28)

        for difficulty in v1FNaSR.GameDifficulty.list_difficulties():
            textbutton mm.text(difficulty, g_power=0.15) background None xalign 0.5 hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"]:
                action (SetField(v1FNaSR.Settings, "game_difficulty", difficulty), Function(mm.screen_switching, "V1MainMenuSettingsDifficultyFNaSR", "V1MainMenuSettingsFNaSR"))
                hovered SetField(mm, "_dd", difficulty.description)
                unhovered SetField(mm, "_dd", None)

        textbutton mm.text("Назад", g_power=0.15) background None xalign 0.5 hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(mm.screen_switching, "V1MainMenuSettingsDifficultyFNaSR", "V1MainMenuSettingsFNaSR")

screen V1MainMenuAchievementsFNaSR:
    tag v1menuFNaSR

    use V1MainMenuFrameFNaSR()
    $ mm = v1FNaSR.MainMenu

    key "mouseup_3" action Function(mm.screen_switching, "V1MainMenuAchievementsFNaSR", "V1MainMenuFNaSR")
    key "K_ESCAPE" action Function(mm.screen_switching, "V1MainMenuAchievementsFNaSR", "V1MainMenuFNaSR")

    add mm.text("Достижения", size=22) align(0.5, 0.14)

    vbox align(0.5, 0.5):
        textbutton mm.text("Назад") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(mm.screen_switching, "V1MainMenuAchievementsFNaSR", "V1MainMenuFNaSR")

screen V1MainMenuCustomNightFNaSR:
    tag v1menuFNaSR

    $ mm = v1FNaSR.MainMenu
    $ ns = v1FNaSR.game.night_system

    use V1MainMenuFrameFNaSR(False, show_enemy=ns.custom_night.enemy_select.sprite, night="Custom")

    key "mouseup_3" action [Function(mm.screen_switching, "V1MainMenuCustomNightFNaSR", "V1MainMenuChoiceNightFNaSR"),Function(ns.custom_night.reset_custom)]
    key "K_ESCAPE" action [Function(mm.screen_switching, "V1MainMenuCustomNightFNaSR", "V1MainMenuChoiceNightFNaSR"),Function(ns.custom_night.reset_custom)]

    add mm.text("Custom Night", size=22) align(0.5, 0.14)

    hbox align(0.5, 0.9) spacing 20:
        textbutton mm.text("-") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(ns.custom_night.set_ai_level, level=max(ns.custom_night.enemy_select.ai_level - 1, 0))
        add mm.text("{}/{}".format(ns.custom_night.enemy_select.ai_level, v1FNaSR.Constants.MAX_AI_LEVEL)) align(0.5, 0.9)
        textbutton mm.text("+") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(ns.custom_night.set_ai_level, level=min(ns.custom_night.enemy_select.ai_level + 1, v1FNaSR.Constants.MAX_AI_LEVEL))

    hbox align(0.5, 0.9) spacing 250:
        textbutton mm.text("<<<") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(ns.custom_night.select_enemy, direction=-1)
        textbutton mm.text(">>>") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Function(ns.custom_night.select_enemy, direction=1)

    hbox align(0.5, 0.95) spacing 60:
        textbutton mm.text("Назад") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action [
            Function(ns.custom_night.reset_custom),
            Function(mm.screen_switching, "V1MainMenuCustomNightFNaSR", "V1MainMenuChoiceNightFNaSR")
        ]
        textbutton mm.text("Начать") background None hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action [
            Hide('V1MainMenuCustomNightFNaSR'),
            Call("v1_play_FNaSR", ns.custom_night)
        ]


screen V1GameMenuSelectorFNaSR:
    zorder 999
    modal True

    $ game = renpy.store.v1FNaSR.game
    $ mm = v1FNaSR.MainMenu

    $ bar_null = Frame(v1resFNaSR.images.other["bar_null"],36,36)
    $ bar_full = Frame(v1resFNaSR.images.other["bar_full"],36,36)
    default settings = False

    on "show" action [Function(game.game_time.freeze), SetField(renpy.store.v1FNaSR.Selector, "is_open", True)]
    on "hide" action [Function(game.game_time.unfreeze), SetField(renpy.store.v1FNaSR.Selector, "is_open", False)]

    key ["K_ESCAPE", "mouseup_3"] action Return()

    add "black" alpha 0.5

    add mm.text("Пять Ночей в Совёнке Remaster", size=24, g_power=0.0575) align(0.5, 0.1)

    vbox align(0.5, 0.5) spacing 15:
        if not settings:
            textbutton mm.text("Продолжить") background None xalign 0.5 hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action Return()

            if game.night_system.is_night_loaded:
                textbutton mm.text("Начать ночь заново"):
                    background None xalign 0.5
                    hover_sound v1resFNaSR.sounds.ui["button_h"]
                    activate_sound v1resFNaSR.sounds.ui["button_c"]
                    action [Return(), Function(game.restart_night)]

                textbutton mm.text("В меню мода"):
                    background None xalign 0.5
                    hover_sound v1resFNaSR.sounds.ui["button_h"]
                    activate_sound v1resFNaSR.sounds.ui["button_c"]
                    action [Return(), Function(renpy.jump, "v1_main_menu_FNaSR")]
                
            textbutton mm.text("Настройки"):
                background None xalign 0.5
                hover_sound v1resFNaSR.sounds.ui["button_h"]
                activate_sound v1resFNaSR.sounds.ui["button_c"]
                action SetScreenVariable("settings", True)

            textbutton mm.text("Выйти"):
                background None xalign 0.5
                hover_sound v1resFNaSR.sounds.ui["button_h"]
                activate_sound v1resFNaSR.sounds.ui["button_c"]
                action [Return(), Function(renpy.jump, "v1_exit_FNaSR")]
        else:
            for volume_type, label in (("music volume", "Музыка"), ("sound volume", "Звуки"), ("voice volume", "Эмбиент")):
                add mm.text(label) xalign 0.5
                bar:
                    value Preference(volume_type)
                    left_bar bar_full
                    right_bar bar_null
                    thumb None
                    hover_thumb None
                    xmaximum 0.25
                    ymaximum 36
                    xalign 0.5

            textbutton mm.text("Назад"):
                background None xalign 0.5
                hover_sound v1resFNaSR.sounds.ui["button_h"]
                activate_sound v1resFNaSR.sounds.ui["button_c"]
                action SetScreenVariable("settings", False)


screen V1ConfirmationScreenFNaSR(label, yes_action, no_action, time_freeze=True, screen_call=None, use_menu_frame=False):
    zorder 10

    $ game = renpy.store.v1FNaSR.game
    $ mm = v1FNaSR.MainMenu
    $ add_action = Hide("V1ConfirmationScreenFNaSR")

    $ yes_action = mm.normalize_action(yes_action, add_action)
    $ no_action  = mm.normalize_action(no_action, add_action)

    if use_menu_frame:
        use V1MainMenuFrameFNaSR(False)
    else:
        add mm.text("Пять Ночей в Совёнке Remaster", size=24, g_power=0.0575) align(0.5, 0.1)

    if time_freeze:
        on "show" action Function(game.game_time.freeze)
        on "hide" action Function(game.game_time.unfreeze)
    if screen_call is not None:
        on "show" action Hide(screen_call)
        on "hide" action Show(screen_call)

    key "K_ESCAPE" action no_action

    vbox:
        align (0.5, 0.5)
        spacing 15

        add mm.text(label) xalign 0.5

        hbox:
            xalign 0.5
            spacing 30

            textbutton mm.text("     <-[[ Да ]->     ") background None xalign 0.5 hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action yes_action
            textbutton mm.text("     <-[[ Нет ]->     ") background None xalign 0.5 hover_sound v1resFNaSR.sounds.ui["button_h"] activate_sound v1resFNaSR.sounds.ui["button_c"] action no_action

screen V1SaveLoadScreenFNaSR:
    add mm.text("Пять Ночей в Совёнке Remaster", size=24, g_power=0.0575) align(0.5, 0.1)
    vbox align(0.5, 0.5) spacing 15:
        text mm.text("Не сейчас") xalign 0.5
        textbutton mm.text("Понял") background None xalign 0.5 action Return()

screen V1SayScreenFNaSR:
    #window background None id "window":

        #$ timeofday = persistent.timeofday

        #add get_image("gui/dialogue_box/"+timeofday+"/dialogue_box.png") xpos 174 ypos 916

        #text what id "what" xpos 194 ypos 964 xmaximum 1541 size 28 line_spacing 2
        #if who:
        #    text who id "who" xpos 194 ypos 931 size 28 line_spacing 2

    text what id "what" xalign 0.5 ypos 964 xmaximum 1541 size 28 line_spacing 2
    if who:
        text who id "who" xalign 0.5 ypos 931 size 28 line_spacing 2

















