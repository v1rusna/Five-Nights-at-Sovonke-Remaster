

label v1_night_1_history_win_label_FNaSR:
    if not v1FNaSR.Settings.view_story:
        jump v1_game_FNaSR

    $ v1FNaSR_gg.voice.load("night_1")
    $ v1FNaSR_cf.voice.load("night_1")

    scene
    $ renpy.show("main_location", at_list=[truecenter], what=v1FNaSR.game.mainL.img_main_loc)
    camera at v1_camera_set_center_zoom_t_FNaSR()
    show black
    hide black with dissolve
    $ renpy.block_rollback()
    $ renpy.pause(1.0, hard=True)
    $ renpy.music.play(v1resFNaSR.sounds.sfx["call"], "sound2")
    pause 0.5
    play sound [sfx_bed_squeak2, sfx_body_bump]
    $ renpy.block_rollback()
    $ renpy.pause(3.0, hard=True)
    $ renpy.block_rollback()
    $ renpy.music.stop("ambience")
    $ renpy.music.play(v1resFNaSR.sounds.sfx["answer_phone"], "sound")
    $ renpy.block_rollback()
    

    v1FNaSR_gg"А... Алло? Да, слушаю..."
    v1FNaSR_cf"О, живой. Ну здравствуй, салага. Не обоссался там с перепугу?"
    v1FNaSR_gg"Да вроде... нет. А что случилось? Инструктаж же?"
    v1FNaSR_cf"Инструктаж, инструктаж. Слушай сюда, времени мало. Первое правило. Запомнишь, может и доживёшь до утра."
    v1FNaSR_gg"В смысле... доживу? Вы чего?.."
    v1FNaSR_cf"Ульяна. Слышал про такую?"
    v1FNaSR_gg"Не... не слышал."
    v1FNaSR_cf"Маленькая, быстрая, как гончая. Услышишь за дверью шаги, будто когтями по дереву, сразу хватай дверь. Закрывай на все засовы и висни на ручке. Понял?"
    v1FNaSR_gg"Понял... А долго? Сколько висеть-то?"
    v1FNaSR_cf"Пока она сама за ручку не дёрнет. Раз, и отпускай. Проверила, ушла. Если раньше отпустишь... ну, сам понимаешь."
    v1FNaSR_gg"Не понимаю..."
    v1FNaSR_cf"Труп ты будешь, вот что. Аминь. И ещё: в планшет не пялься просто так. Камеры батарею жрут. Сядет планшет, считай, ты в коробке с завязанными глазами. Всё. Работай."
    $ renpy.music.play(v1resFNaSR.sounds.sfx["telephone_rings"], "sound")
    v1FNaSR_gg"Твою мать..."

    hide main_location
    jump v1_game_FNaSR
    
label v1_day_1_history_win_label_FNaSR:
    if not v1FNaSR.Settings.view_story:
        jump v1_main_menu_FNaSR
    if v1FNaSR.game.get_last_pass_result() == v1FNaSR.ResultNight.LOSS:
        jump v1_main_menu_FNaSR

    $ v1FNaSR_gg.voice.load("night_1_win")
    $ v1FNaSR_cf.voice.load("night_1_win")

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
    $ renpy.pause(2.0, hard=True)
    $ renpy.block_rollback()
    $ renpy.music.stop("v1_game_ambience_1_FNaSR")
    $ renpy.music.play(v1resFNaSR.sounds.sfx["answer_phone"], "sound")
    $ renpy.block_rollback()

    v1FNaSR_gg"Я...{w=1} я сделал.{w=1}{nw}"
    $ v1FNaSR_gg.voice.block()
    v1FNaSR_gg"Были шаги.{w=1.3} Я держал.{w=1.2} Пока не дернула.{w=1.8} Я слышал этот звук...{w=1.6} Господи, я думал, сердце выпрыгнет."
    $ v1FNaSR_gg.voice.unblock()
    v1FNaSR_cf"Ого. Живой. Ну, молодец. Дверь, значит, держит, и ты не обосрался. Но рано радуешься. Это была пристрелка. Бумажная мишень. Дальше хуже будет."

    stop ambience fadeout 0.5
    scene black with dspr
    $ renpy.pause(0.5, hard=True)
    jump v1_main_menu_FNaSR
    