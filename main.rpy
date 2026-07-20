init 11 python:
    mods["v1_start_FNaSR"] = " {image=v1_mod_button_text_FNaSR} "

label v1_init_FNaSR:
    $ renpy.block_rollback()
    
    $ v1FNaSR.game.start_mod()

    $ config.quit_callbacks.append(v1FNaSR.game.stop_game_loop)
    $ config.quit_callbacks.append(v1FNaSR.game.quit_mod)

    $ renpy.block_rollback()

label v1_main_menu_FNaSR:
    $ v1FNaSR.game.stop_game_loop()
    $ v1FNaSR.GameTools.hide_screens()
    $ v1FNaSR.GameTools.stop_all_channels()
    $ v1FNaSR.game.reset()

    $ renpy.block_rollback()
    show anim v1_tablet_open_entire_FNaSR
    $ renpy.music.play(v1resFNaSR.sounds.sfx["tablet_open_2"], "sound")
    $ renpy.pause(0.18, hard=True)
    hide anim v1_tablet_open_entire_FNaSR
    $ renpy.music.play(v1resFNaSR.sounds.sfx["camera_static_1_new"], "music", loop=True, fadein=0.5)

label v1_main_menu_loop_FNaSR:
    show screen V1MainMenuFNaSR
    $ renpy.pause(hard=True)
    jump v1_main_menu_loop_FNaSR

label v1_game_FNaSR(game=None):
    if game is None:
        $ game = v1FNaSR.game
    $ v1FNaSR.Selector.stop()
    play ambiance v1resFNaSR.sounds.ambient["night_wind_inside_1"]
    $ renpy.block_rollback()
    $ game.start_game_loop()
    scene black

    $ game.object_display.update_display()
    camera at v1_camera_set_center_zoom_t_FNaSR()
    
    show screen V1MainScreenFNaSR(game)
    show screen V1OfficeScreenFNaSR(game)

    #$ v1FNaSRSay.test_say_text.start()

label v1_loop_label_FNaSR():
    $ renpy.block_rollback()
    $ renpy.pause(hard=True)
    $ renpy.jump("v1_loop_label_FNaSR")



label v1_play_FNaSR(night=None):
    $ renpy.music.play(v1resFNaSR.sounds.sfx["tablet_close_1"], "sound")
    scene black
    show anim v1_tablet_close_entire_VNaSR
    $ renpy.music.stop("music")
    $ renpy.pause(0.18, hard=True)
    hide anim v1_tablet_close_entire_VNaSR
    $ renpy.pause(.1, hard=True)
    $ v1FNaSR.GameTools.hide_screens()
    if night is None:
        $ v1FNaSR.game.night_system.next_load()
    elif night.level == -1:
        $ v1FNaSR.game.night_system.custom_night.start()
    else:
        $ v1FNaSR.game.night_system.night_load(night)

label v1_start_FNaSR: # <- Точка входа
    $ _game_menu_screen = None
    $ renpy.block_rollback()
    stop music fadeout 2
    window hide dissolve

    $ renpy.music.play(v1resFNaSR.sounds.sfx["startday"], channel="sound", loop=False)
    $ renpy.scene()
    $ renpy.show("bg black")
    $ renpy.with_statement(dissolve2)
    $ renpy.pause(2.0, hard=True)

    $ v1FNaSR._Screen._replace()
    $ renpy.block_rollback()

    if not persistent.v1_recommendation_say_FNaSR:
        show v1_recommendation_FNaSR with dissolve
        $ renpy.pause(1.0, hard=True)
        pause 5
        hide v1_recommendation_FNaSR with dissolve
        $ renpy.pause(1.0, hard=True)
        $ persistent.v1_recommendation_say_FNaSR = True
        jump v1_prolog_label_FNaSR

    jump v1_init_FNaSR

label v1_exit_mm_FNaSR:
    $ renpy.music.play(v1resFNaSR.sounds.sfx["tablet_close_1"], "sound")
    scene black
    show anim v1_tablet_close_entire_VNaSR
    $ renpy.music.stop("v1_show_camera_ambience_FNaSR")
    $ renpy.pause(0.18, hard=True)
    hide anim v1_tablet_close_entire_VNaSR
    $ renpy.pause(.1, hard=True)
    jump v1_exit_FNaSR

label v1_exit_FNaSR: # <- Точка выхода
    $ _game_menu_screen = "game_menu_selector"
    $ v1FNaSR.game.stop_game_loop()
    $ v1FNaSR.GameTools.hide_screens()
    $ v1FNaSR.GameTools.stop_all_channels()
    $ v1FNaSR.game.reset()
    $ v1FNaSR.game.quit_mod()
    $ v1FNaSR._Screen._replace()
    $ renpy.block_rollback()
    scene black with dissolve
    $ renpy.pause(.5, hard=True)
    $ MainMenu(confirm=False)()





label v1_prolog_label_FNaSR:
    $ v1FNaSR_nt.voice.load("prologue")
    $ v1FNaSR_sw.voice.load("prologue")
    $ v1FNaSR_gg.voice.load("prologue")
    $ v1FNaSR_cn.voice.load("prologue")
    $ v1FNaSR_cf.voice.load("prologue")
    scene black
    scene bg v1_view_train_window_FNaSR with dissolve
    $ renpy.music.play(v1resFNaSR.sounds.ambient["Ambient_The_rhythmic"], channel="ambience", loop=True, fadein=2)
    v1FNaSR_nt"Электричка тащилась через осеннюю глушь.{w=2.2} За стеклом — бесконечное серо-желтое месиво: поля, перелески, покосившиеся заборы.{w=4.2}{nw}"
    $ v1FNaSR_nt.voice.block()
    v1FNaSR_nt"Все выцвело.{w=1} Как старая фотография.{w=1} Как моя жизнь."
    $ v1FNaSR_nt.voice.unblock()
    $ renpy.music.play(v1resFNaSR.sounds.sfx["styk"], channel="sound")
    v1FNaSR_nt"Прижимаюсь лбом к ледяному стеклу. В ушах все еще стоит этот ровный, бездушный голос из соцзащиты..."
    v1FNaSR_sw"Временная мера...{w=1.1} пока подберем жилье...{w=1.2} тебе почти восемнадцать, а с сестрой нужно что-то решать..."
    v1FNaSR_nt"Решать.{w=1} Они всегда так говорят.{w=0.95} «Решать».{w=0.765}{nw}"
    $ v1FNaSR_nt.voice.block()
    v1FNaSR_nt"А мне просто нужно было заткнуться, кивнуть и найти деньги.{w=2.5} Любой ценой."
    $ v1FNaSR_nt.voice.unblock()
    v1FNaSR_nt"В рюкзаке — пара футболок, теплый свитер, дешевые консервы.{w=3.21}{nw}"
    $ v1FNaSR_nt.voice.block()
    v1FNaSR_nt"И фотография.{w=1.1} Ленка, семь лет, смешные хвостики, щербатая улыбка.{w=3}{nw}"
    v1FNaSR_nt"Я пообещал ей, что вернусь.{w=2.1} Скоро.{w=0.9} С деньгами.{w=0.85}{nw}"
    v1FNaSR_nt"Я не могу её подвести.{w=1.85} Я не имею права подвести."
    $ v1FNaSR_nt.voice.unblock()
    v1FNaSR_nt"Объявление в газете — как насмешка: «СРОЧНО! СТОРОЖ. НОЧНЫЕ СМЕНЫ. ХОРОШАЯ ОПЛАТА».{w=4.4}{nw}"
    $ v1FNaSR_nt.voice.block()
    v1FNaSR_nt"Пункт {b}{u}«опыт не требуется»{/u}{/b} жирной линией.{w=2.05}{nw}"
    v1FNaSR_nt"Конечно, кто ж еще поедет в эту дыру за большими деньгами? Только совсем отчаявшиеся.{w=3.15} Только такие, как я."
    $ v1FNaSR_nt.voice.unblock()
    # ЗВУК: Скрип открывающейся двери купе, грохот тележки.
    play sound sfx_door_squeak_light
    v1FNaSR_cn"Через двадцать минут твоя, милок. Последняя. Ты к лесникам, что ли?"
    v1FNaSR_gg"К лагерю...{w=1} «Совенок»."
    v1FNaSR_cn"Ну... счастливо тебе."#v1FNaSR_cn"Ну... счастливо тебе. Ой, счастливо..."
    v1FNaSR_nt"Стекло запотело от дыхания.{w=1.1}{nw} Я провел рукавом.{w=1}{nw} И увидел.{w=0.7}{nw}"
    $ v1FNaSR_nt.voice.block()
    v1FNaSR_nt"Сначала просто огни.{w=1} Потом — крыши, водокачка, старая арка.{w=1.7}{nw}"
    v1FNaSR_nt"В грязно-багровом свете заката это выглядело...{w=2.7} неправильно.{w=1.2} Мертво.{w=1} Ни огонька.{w=0.75} Ни звука.{w=0.85}{nw}"
    v1FNaSR_nt"Лагерь лежал внизу, как выброшенный на берег корабль-призрак.{w=2.3} Тишина давила на уши.{w=1.2} Мне стало по-настоящему страшно."
    $ v1FNaSR_nt.voice.unblock()
    stop ambience fadeout 2.0
    # ЗВУК: Резкий визг тормозов, лязг дверей, порыв ветра.
    play sound sfx_insert_crowbar_door
    v1FNaSR_nt"Я вдохнул поглубже. Взвалил рюкзак. Последний пассажир. Последняя остановка. Назад дороги нет. Ленка ждет."
    scene bg v1_checkpoint_FNaSR with dissolve
    v1FNaSR_nt"Дорога нырнула под сосны. У КПП в будке сидел мужик в засаленной куртке. Он даже не посмотрел на меня, только мотнул головой в сторону лагеря. От него пахло перегаром и равнодушием."
    v1FNaSR_cf"Топай до домика вожатой. Ключ под ковриком. Инструктаж в десять. Ночью тут...{w=2} не заблудись."
    v1FNaSR_nt"Сделал шаг.{w=1} Воздух стал плотным, как кисель.{w=1.8} Звуки пропали.{w=1} Даже ветер шумел будто из-под воды.{w=1}{nw}"
    $ v1FNaSR_nt.voice.block()
    scene bg v1_ext_houses_night_FNaSR with dissolve
    v1FNaSR_nt"Я шел по пустой аллее мимо заколоченных окон.{w=2} Чувство было такое, будто за мной следят.{w=1.85} Не люди.{w=1} Стены.{w=0.8} Деревья.{w=0.85} Сам лагерь смотрел на меня в упор.{w=1}{nw}"
    scene bg ext_house_of_mt_night_without_light with dissolve
    v1FNaSR_nt"Впереди, у темного озера, стоял домик.{w=1.5} Маленький, кривой. Мое пристанище на эти пять ночей. Моя тюрьма."
    $ v1FNaSR_nt.voice.unblock()
    # ЗВУК: Шорох ноги по половику, скрип ключа, громкий щелчок замка.
    play sound [sfx_alisa_picklock, v1resFNaSR.sounds.sfx["door_unhold"]]
    scene black with dissolve
    v1FNaSR_nt"Дверь открылась, дохнув пылью и сыростью. Пустота. Тишина. Я переступил порог. В мою первую ночь. В самое долгое ожидание рассвета."
    pause 1.5
    jump v1_init_FNaSR








