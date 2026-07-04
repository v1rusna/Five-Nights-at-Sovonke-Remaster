label v1_night_4_history_win_label_FNaSR:
    if not v1FNaSR.Settings.view_story:
        jump v1_game_FNaSR

    $ v1FNaSR_gg.voice.load("night_4")
    $ v1FNaSR_cf.voice.load("night_4")

    scene
    $ renpy.show("main_location", at_list=[truecenter], what=v1FNaSR.game.mainL.img_main_loc)
    camera at v1_camera_set_center_zoom_t_FNaSR()
    show black
    hide black with dissolve
    $ renpy.block_rollback()
    $ renpy.pause(1.0, hard=True)
    $ renpy.music.play(v1resFNaSR.sounds.sfx["call"], "ambience")
    $ renpy.block_rollback()
    $ renpy.pause(1.5, hard=True)
    $ renpy.block_rollback()
    $ renpy.music.stop("ambience")
    $ renpy.music.play(v1resFNaSR.sounds.sfx["answer_phone"], "sound")
    $ renpy.block_rollback()

    v1FNaSR_gg"Слушаю."
    v1FNaSR_cf"Вечер добрый, боец. Сегодня дисциплина и тишина. Две новых: Славяна и Женя."
    v1FNaSR_gg"Давайте."
    v1FNaSR_cf"Славяна завхоз, правая рука вожатой. Ходит с проверкой. Услышишь чёткие шаги у двери, свет выруби, дверь настежь, и сам прикинься неживым."
    v1FNaSR_gg"Прикинуться неживым, то-есть м... мёртвым?"
    v1FNaSR_cf"Ага. Лежи и не шевелись. Она заглянет, увидит, что «спишь», скажет «Спокойной ночи» и уйдет.{w=7.4}{nw}"
    $ v1FNaSR_cf.voice.block()
    v1FNaSR_cf"Если свет горит или дверь закрыта, ты саботажник. А с саботажниками она не церемонится."
    $ v1FNaSR_cf.voice.unblock()
    v1FNaSR_gg"Понял. Лежать и не дышать. А Женя?"
    v1FNaSR_cf"Женя верховная жрица тишины. Считает, что ночь должна быть чистой, как лист бумаги. Но есть проблема."
    v1FNaSR_gg"Какая?"
    v1FNaSR_cf"Пионеры-непоседы."
    v1FNaSR_gg"Какие, блин, пионеры?!{w=1.7} Вы надо мной издеваетесь?"
    v1FNaSR_cf"Они шалят. Прячут по лагерю музыкальные шкатулки. Заведут и сбегут. А шкатулка играет. Для Жени это кощунство. У неё там шумомер в библиотеке. Как зашкалит она придёт к источнику звука."
    v1FNaSR_gg"Ко мне?!"
    v1FNaSR_cf"А она разбираться будет? Спросит, кто шумит?"
    v1FNaSR_gg"И что делать?"
    v1FNaSR_cf"Слушать. Шкатулка заиграла, прижми ухо к планшету. Переключай камеры, лови ту, откуда звук. Найдёшь, жми «Заглушить». Мелодия умрёт, шумомер успокоится."
    v1FNaSR_gg"А если не найду?"
    v1FNaSR_cf"Если шумомер зашкалит, Женя решит, что это твоё дыхание тишину нарушает. И придёт его остановить. Насовсем."
    v1FNaSR_gg"Понял. Слушать."
    v1FNaSR_cf"Сегодня уши важнее глаз. Включай на полную. И молись, чтоб пионеры были не слишком активные. Удачи. Она тебе понадобится."

    $ renpy.music.play(v1resFNaSR.sounds.sfx["telephone_rings"], "sound")

    hide main_location
    jump v1_game_FNaSR