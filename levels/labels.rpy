init python in v1FNaSR:
    def end_helper(fadeout_time=0):
        end_label = game.night_system.loaded.end_label
        game.night_system.loaded.end_callback()
        game.reset()
        GameTools.stop_all_channels(fadeout_time)
        GameTools.hide_screens()
        renpy.block_rollback()
        return end_label

label v1_loss_label_FNaSR:
    scene black
    $ enemy_killer = v1FNaSR.game.enemy_system.enemy_killer
    $ death_time = v1FNaSR.game.game_time.get_time()
    $ night = v1FNaSR.game.night_system.loaded.night

    $ v1FNaSR.game.enemy_system.reset_enemy()
    $ v1FNaSR.GameTools.stop_all_channels(2)
    $ enemy_killer.class_screamer()
    $ end_label = v1FNaSR.end_helper()

    #scene black
    $ renpy.pause(0.5, hard=True)

    $ v1FNaSRTypeWriter.show_text("Ночь {}\nВремя: {}\nСмена окончена...".format(night, death_time))

    $ v1FNaSR.SituationMemory.reset()
    $ v1FNaSR.Settings.save()
    $ renpy.block_rollback()

    if end_label is not None:
        jump expression end_label
    jump v1_main_menu_FNaSR

label v1_win_label_FNaSR:
    scene black

    $ end_of_shift = game.night_system.loaded.end_of_shift
    $ night = v1FNaSR.game.night_system.loaded.night
    $ end_label = v1FNaSR.end_helper()

    scene black
    $ v1FNaSRTypeWriter.show_text("Ночь {}\nВремя: {}:00\nСмена окончена...".format(night, end_of_shift))

    $ v1FNaSR.SituationMemory.save()
    $ v1FNaSR.Settings.save()
    $ renpy.block_rollback()

    if end_label is not None:
        jump expression end_label
    jump v1_main_menu_FNaSR




