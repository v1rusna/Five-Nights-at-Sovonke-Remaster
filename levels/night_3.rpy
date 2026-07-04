label v1_night_3_history_win_label_FNaSR:
    if not v1FNaSR.Settings.view_story:
        jump v1_game_FNaSR

    $ v1FNaSR_gg.voice.load("night_3")
    $ v1FNaSR_cf.voice.load("night_3")

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
    $ renpy.pause(1.5, hard=True)
    $ renpy.block_rollback()

    v1FNaSR_cf"Молчание?{w=1.4} Молчание обычно знак согласия.{w=2.1} Или тупости.{w=1}{nw}"
    $ v1FNaSR_cf.voice.block()
    v1FNaSR_cf"Ладно, сегодня ты у нас инженер.{w=2} Алиса объявилась."
    $ v1FNaSR_cf.voice.unblock()
    v1FNaSR_gg"Алиса?"
    v1FNaSR_cf"Техник-самоучка. Любит генератор ломать. Увидишь на камере её, не зевай. На экране кнопка серая появится, «Сигнал» называется. Жми и держи. Сирена орёт сразу, пока кнопку жмёшь. Она визг не любит, убежит."
    v1FNaSR_gg"А если не успею?"
    v1FNaSR_cf"Допустишь до генератора останешься в темноте. Планшет сдохнет за полчаса, и ты как крот в коробке. Дальше сам думай."
    v1FNaSR_gg"Понял. А это всё на сегодня?"
    v1FNaSR_cf"А, забыл. Шурик и Электроник. Братья-акробаты."
    v1FNaSR_gg"Кто?"
    v1FNaSR_cf"Шурик простой парень. Если дверь открыта зайдёт поболтать. Беседа короткая: ты выключаешь свет. Он в темноте постоит, поскрипит шестерёнками и уйдёт. Всё."
    v1FNaSR_gg"Ну, это легко..."
    v1FNaSR_cf"Не спеши. Как выключишь свет, Электроник уже на марше. Он на темноту идёт. Дойдёт до открытой двери, всё. Летальный исход."
    v1FNaSR_gg"Так мне свет включать или выключать?!"
    v1FNaSR_cf"А это уже сам решай, боец. Выключатель теперь, оружие двойного назначения. Пользуйся с умом.{w=5.7}{nw}"
    $ v1FNaSR_cf.voice.block()
    v1FNaSR_cf"И ещё: если их не видно на камерах, не обольщайся. Значит, сидят в своих клубах, злобу копят."
    $ v1FNaSR_cf.voice.unblock()
    $ renpy.music.play(v1resFNaSR.sounds.sfx["telephone_rings"], "sound")
    v1FNaSR_gg"Спасибо... успокоил."

    hide main_location
    jump v1_game_FNaSR