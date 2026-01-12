import os
import winreg
import re


class GameConfig:
    def __init__(self, name, steam_id, relative_dll_path):
        self.name = name
        self.steam_id = steam_id
        self.relative_dll_path = relative_dll_path


SUPPORTED_GAMES = {
    "cyberpunk_2077": GameConfig(
        name="Cyberpunk 2077",
        steam_id="1091500",
        relative_dll_path=os.path.join("bin", "x64"),
    )
}


def get_all_steam_libraries():
    """Finds all Steam library folders on the system."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        libraries = [steam_path]
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            with open(vdf_path, "r", encoding="utf-8") as f:
                content = f.read()
                found_paths = re.findall(r'"path"\s+"([^"]+)"', content)
                for p in found_paths:
                    libraries.append(p.replace("\\\\", "\\"))
        return list(set(libraries))
    except Exception:
        return []


def find_steam_game_path(game_config):
    """Searches for the game folder across all Steam libraries."""
    for lib in get_all_steam_libraries():
        candidate = os.path.join(lib, "steamapps", "common", game_config.name)
        if os.path.exists(candidate):
            return os.path.join(candidate, game_config.relative_dll_path)
    return None
