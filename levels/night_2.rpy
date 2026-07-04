label v1_night_2_history_win_label_FNaSR:
    if not v1FNaSR.Settings.view_story:
        jump v1_game_FNaSR

    $ v1FNaSR_gg.voice.load("night_2")
    $ v1FNaSR_cf.voice.load("night_2")

    scene
    $ renpy.show("main_location", at_list=[truecenter], what=v1FNaSR.game.mainL.img_main_loc)
    camera at v1_camera_set_center_zoom_t_FNaSR()
    show black
    hide black with dissolve
    $ renpy.block_rollback()
    $ renpy.pause(1.0, hard=True)
    $ renpy.music.play(v1resFNaSR.sounds.sfx["call"], "ambience")
    $ renpy.block_rollback()
    $ renpy.pause(2.0, hard=True)
    $ renpy.block_rollback()
    $ renpy.music.stop("ambience")
    $ renpy.music.play(v1resFNaSR.sounds.sfx["answer_phone"], "sound")
    $ renpy.block_rollback()

    v1FNaSR_gg"Да. Слушаю."
    v1FNaSR_cf"О, уже по другому разговариваешь. Ну ну. Сегодня программа богаче. Дуэт у нас."
    v1FNaSR_gg"В смысле дуэт?"
    v1FNaSR_cf"Первая Юля. Идёт из леса, бормочет что-то про берёзки. Сама по себе не опасна, пока на улице. Беда, если впустишь."
    #v1FNaSR_gg"А если впущу?"
    v1FNaSR_cf"Башка твоя превратится в радиоточку. Будешь сам с собой разговаривать, пока не вырубишься.{w=4}{nw}"
    $ v1FNaSR_cf.voice.block()
    v1FNaSR_cf"Лекарство простое: если уже впустил не паникуй. Открой планшет и уставься в экран. Минуты три смотри на камеры. Сама уйдёт."
    $ v1FNaSR_cf.voice.unblock()
    v1FNaSR_gg"Три минуты смотреть в планшет...{w=2} Понял."
    v1FNaSR_cf"Вторая Лена. Вот тут сложнее. Её не слышно. Вообще."
    v1FNaSR_gg"Как это, не слышно?"
    v1FNaSR_cf"А вот так. Тихо приходит, тихо стоит. Увидишь на камере, она будет как вкопанная, пока ты на неё смотришь. Но если резко пропала с экрана..."
    v1FNaSR_gg"Что тогда?"
    v1FNaSR_cf"Это не глюк камер. Это она уже у твоего окна стоит. Бледная, белая, смотрит. Увидел, дверь на засов и не дыши. Вообще не дыши. Пока тень в окне не растает."
    v1FNaSR_gg"Понял...{w=1} не дышать."
    v1FNaSR_cf"Ну давай, главное не обосрись и доживи хотя бы до утра. Если не доживёшь надгробие тебе уж постараюсь и поставлю красивое. Удачи."
    $ renpy.music.play(v1resFNaSR.sounds.sfx["telephone_rings"], "sound")
    v1FNaSR_gg"Кто тут еще не доживёт..."
    
    hide main_location
    jump v1_game_FNaSR

label v1_day_2_history_win_label_FNaSR:
    if not v1FNaSR.Settings.view_story:
        jump v1_main_menu_FNaSR
    if v1FNaSR.game.get_last_pass_result() == v1FNaSR.ResultNight.LOSS:
        jump v1_main_menu_FNaSR

    $ v1FNaSR_gg.voice.load("night_2_win")
    $ v1FNaSR_cf.voice.load("night_2_win")

    scene
    play ambience ambience_music_club_day fadein 1.5
    show bg v1_int_house_of_mt_sunset_parallax_FNaSR at truecenter
    camera at v1_camera_set_center_zoom_t_FNaSR()
    show black
    hide black with dissolve
    $ renpy.block_rollback()
    $ renpy.pause(1.0, hard=True)
    $ renpy.music.play(v1resFNaSR.sounds.sfx["call"], "v1_game_ambience_1_FNaSR")
    $ renpy.block_rollback()
    $ renpy.pause(1.5, hard=True)
    $ renpy.block_rollback()
    $ renpy.music.stop("v1_game_ambience_1_FNaSR")
    $ renpy.music.play(v1resFNaSR.sounds.sfx["answer_phone"], "sound")
    $ renpy.block_rollback()

    v1FNaSR_gg"Справился. Юлю прогнал смотрел в планшет, как вы сказали. Ушла. А Лену... Лену видел."
    v1FNaSR_cf"Ого. И жив остался?"
    v1FNaSR_gg"Она в окно смотрела. Я замер. Не дышал. Минуты две стояла, наверное... Потом пропала."
    v1FNaSR_cf"Ну, зырь. Ты не только слышать, но и видеть начал. Это хорошо. Тишина, она знаешь... иногда громче крика бывает. Держись."

    stop ambience fadeout 0.5
    scene black with dspr
    $ renpy.pause(0.5, hard=True)
    jump v1_main_menu_FNaSR