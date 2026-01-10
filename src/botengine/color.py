class Color:
    """
    Color your command line output text with Color.WHATEVER and Color.END
    """
    # import colorama

    # Cross-platform color compatibility. Please see notes at:
    # https://github.com/tartley/colorama
    # from colorama import Fore, reinit, Style

    # reinit() runs faster vs. init().
    # Color only matters when running locally, so we init() colorama in the main() method.
    # reinit()

    PURPLE = "Fore.MAGENTA"
    CYAN = "Fore.CYAN"
    BLUE = "Fore.BLUE"
    GREEN = "Fore.GREEN"
    YELLOW = "Fore.YELLOW"
    RED = "Fore.RED"
    BOLD = "Style.BRIGHT"
    END = "Style.RESET_ALL"
    UNDERLINE = "\033[4m"
