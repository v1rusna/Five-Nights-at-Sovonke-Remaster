label v1_night_5_history_win_label_FNaSR:
    if not v1FNaSR.Settings.view_story:
        jump v1_game_FNaSR

    $ v1FNaSR_gg.voice.load("night_5")
    $ v1FNaSR_cf.voice.load("night_5")

    scene
    $ renpy.show("main_location", at_list=[truecenter], what=v1FNaSR.game.mainL.img_main_loc)
    camera at v1_camera_set_center_zoom_t_FNaSR()
    show black
    hide black with dissolve
    $ renpy.block_rollback()
    $ renpy.pause(1.0, hard=True)
    $ renpy.music.play(v1resFNaSR.sounds.sfx["call"], "ambience")
    $ renpy.block_rollback()
    $ renpy.pause(1.0, hard=True)
    $ renpy.block_rollback()
    $ renpy.music.stop("ambience")
    $ renpy.music.play(v1resFNaSR.sounds.sfx["answer_phone"], "sound")
    $ renpy.block_rollback()

    v1FNaSR_gg"Последняя ночь. Говорите."
    v1FNaSR_cf"О, стальной голос. Нравится. Да, последняя. И сегодня ты у нас дирижёр. Слушай внимательно."
    v1FNaSR_gg"Я весь во внимании."
    v1FNaSR_cf"Мику. Наша соловьиха. Если впустишь, начнёт петь. Её трели как сигнал для всех остальных. Сбегутся, озвереют."
    v1FNaSR_gg"Так она в домик заходит? А на камерах её нет?"
    v1FNaSR_cf"Нет, она внутрь лезет. В домик твой. Как начнёт заливаться, выталкивай её из домика всеми силами, которые у тебя к тому времени останутся."
    v1FNaSR_gg"В смысле толкать? Силой из домика её выталкивать?"
    v1FNaSR_cf"Да"
    v1FNaSR_gg"А она это самое... Кусаться не будет?"
    v1FNaSR_cf"Вот как раз и проверишь. Пред последняя на сегодня. Ольга Дмитриевна. Сама Хозяйка. Может позвонить."
    v1FNaSR_gg"Позвонить? Сюда?"
    v1FNaSR_cf"На старый телефон в комнате. Услышишь звонок бросай всё. Ищи в темноте трубку. Ответить надо быстро. Как можно быстрее. Не ответишь..."
    v1FNaSR_gg"Понимаю. Последствия."
    v1FNaSR_cf"Виола. Наша медсестра. Сидит на камере медпункта. За ней надо следить, но не слишком пристально."
    v1FNaSR_gg"Что значит, не слишком?"
    v1FNaSR_cf"Чем дольше ты на неё смотришь, тем быстрее она заводится. Сначала отойдёт влево, потом к краю. Если исчезла с экрана, это не сбой."
    v1FNaSR_gg"Что тогда?"
    v1FNaSR_cf"Это финальная стадия. У тебя шесть секунд с момента её исчезновения, чтобы захлопнуть дверь. Шесть, мать их, секунд. Промедлил, всё."
    v1FNaSR_gg"Шесть секунд. Дверь."
    v1FNaSR_cf"И просто Пионер. Может зайти в гости."
    v1FNaSR_gg"И что с ним?"
    v1FNaSR_cf"Если зайдёт, будет короткая игра на реакцию. Не пройдёшь отчислишься по собственному желанию. В гробу."
    v1FNaSR_gg"Всё запомнил. Я справлюсь."
    v1FNaSR_cf"Рассвет близко. Ты почти дошёл. Пусть удача будет с тобой. Хотя бы в эту последнюю ночь."
    $ renpy.music.play(v1resFNaSR.sounds.sfx["telephone_rings"], "sound")
    v1FNaSR_gg"Спасибо..."

    hide main_location
    jump v1_game_FNaSR