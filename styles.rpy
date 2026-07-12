init 11:
    $ v1_font_24_size_FNaSR = v1FNaSR.Adapter.scale_style(24)
    $ v1_font_16_size_FNaSR = v1FNaSR.Adapter.scale_style(16)
    $ v1_font_12_size_FNaSR = v1FNaSR.Adapter.scale_style(12)

    style v1_text_24_style_FNaSR:
        size v1_font_24_size_FNaSR
        font v1FNaSR.Adapter.path("FNaS_R/fonts/retrobanker.ttf")
        outlines [(2, "#000000", 2, 2)]

    style v1_text_24_typewriter_style_FNaSR is v1_text_24_style_FNaSR:
        font v1FNaSR.Adapter.path("FNaS_R/fonts/SpecialElite.ttf")

    style v1_text_24_mod_button_FNaSR is v1_text_24_style_FNaSR:
        color "#d4d4d4"

    style v1_text_24_mod_button_static_FNaSR is v1_text_24_style_FNaSR:
        color "#ffffff"

    style v1_text_12_style_FNaSR is v1_text_24_style_FNaSR:
        size v1_font_12_size_FNaSR

    style v1_text_16_style_FNaSR is v1_text_24_style_FNaSR:
        size v1_font_16_size_FNaSR

