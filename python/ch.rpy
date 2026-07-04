init 1 python in v1FNaSR:
    def _v1_generate_audio_list(core_list, start, end): return [core_list[str(i)] for i in range(start, end+1)]

    class CharacterVoiceList(ConstantBase):
        _gg_voice = VoiceCharacter({
            "prologue": [
                resources.sounds.voice.gg["1"],
            ],
            "night_1": _v1_generate_audio_list(resources.sounds.voice.gg, 2, 8),
            "night_1_win": [
                resources.sounds.voice.gg["9"],
            ],
            "night_2": _v1_generate_audio_list(resources.sounds.voice.gg, 10, 16),
            "night_2_win": [
                resources.sounds.voice.gg["17"],
                resources.sounds.voice.gg["18"],
            ],
            "night_3": _v1_generate_audio_list(resources.sounds.voice.gg, 19, 25),
            "night_4": _v1_generate_audio_list(resources.sounds.voice.gg, 26, 35),
            "night_5": _v1_generate_audio_list(resources.sounds.voice.gg, 36, 48),
        })
        _cf_voice = VoiceCharacter({
            "prologue": [
                resources.sounds.voice.cf["1"],
            ],
            "night_1": _v1_generate_audio_list(resources.sounds.voice.cf, 2, 7),
            "night_1_win": [
                resources.sounds.voice.cf["8"],
            ],
            "night_2": _v1_generate_audio_list(resources.sounds.voice.cf, 9, 15),
            "night_2_win": [
                resources.sounds.voice.cf["16"],
                resources.sounds.voice.cf["17"],
            ],
            "night_3": _v1_generate_audio_list(resources.sounds.voice.cf, 18, 24),
            "night_4": _v1_generate_audio_list(resources.sounds.voice.cf, 25, 34),
            "night_5": _v1_generate_audio_list(resources.sounds.voice.cf, 35, 46),
        })
        _nt_voice = VoiceCharacter({
            "prologue": _v1_generate_audio_list(resources.sounds.voice.nt, 1, 10),
            "end": _v1_generate_audio_list(resources.sounds.voice.nt, 11, 21),
        })
        _sw_voice = VoiceCharacter({
            "prologue": [
                resources.sounds.voice.sw["1"],
            ]
        })
        _cn_voice = VoiceCharacter({
            "prologue": [
                resources.sounds.voice.cn["1"],
                resources.sounds.voice.cn["2"],
            ]
        })

init 99 python:
    def v1FNaSRC(voice_obj, name, color):
        character = v1FNaSR.voice_character(voice_obj, name, kind=adv, who_color=color, who_drop_shadow=(2,2), what_color="#FFDD7D", what_drop_shadow=(2,2))
        return character

    v1FNaSR_gg = v1FNaSRC(v1FNaSR.CharacterVoiceList._gg_voice, "Главный герой", "#0b93bd")
    v1FNaSR_sw = v1FNaSRC(v1FNaSR.CharacterVoiceList._sw_voice, "Соцработница", "#1bb50d")
    v1FNaSR_cn = v1FNaSRC(v1FNaSR.CharacterVoiceList._cn_voice, "Проводница", "#950aa7")
    v1FNaSR_cf = v1FNaSRC(v1FNaSR.CharacterVoiceList._cf_voice, "Начальник", "#7506be")
    v1FNaSR_nt = v1FNaSRC(v1FNaSR.CharacterVoiceList._nt_voice, None, "#000000")