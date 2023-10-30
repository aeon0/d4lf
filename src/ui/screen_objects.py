from template_finder import SearchArgs


class ScreenObjects:
    char_menu_active = SearchArgs(ref="char_menu_active", threshold=0.8, roi="char_menu_active", use_grayscale=False, threshold=0.9)
