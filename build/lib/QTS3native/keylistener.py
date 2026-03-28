import keyboard
from PyQt5 import QtCore


class GlobalKeyboardListener(QtCore.QThread):
    keys_pressed = QtCore.pyqtSignal(tuple)

    NON_SYMBOL_KEYS = [
        "BACKSPACE",
        "TAB",
        "ENTER",
        "SHIFT",
        "CTRL",
        "ALT",
        "ALT_GR",
        "PAUSE",
        "CAPSLOCK",
        "ESCAPE",
        "SPACE",
        "PAGE_UP",
        "PAGE_DOWN",
        "END",
        "HOME",
        "LEFT",
        "UP",
        "RIGHT",
        "DOWN",
        "INSERT",
        "DELETE",
        "PRINT_SCREEN",
        "SCROLLLOCK",
        "NUMLOCK",
        "LWIN",
        "RWIN",
        "MENU",
        "APPS",
        "CLEAR",
        "HELP",
        "SELECT",
        "EXECUTE",
        "SLEEP",
        "DECIMAL",
        "SEPARATOR",
        "SUBTRACT",
        "ADD",
        "MULTIPLY",
        "DIVIDE",
        "NUMPAD_0",
        "NUMPAD_1",
        "NUMPAD_2",
        "NUMPAD_3",
        "NUMPAD_4",
        "NUMPAD_5",
        "NUMPAD_6",
        "NUMPAD_7",
        "NUMPAD_8",
        "NUMPAD_9",
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
        "F6",
        "F7",
        "F8",
        "F9",
        "F10",
        "F11",
        "F12",
        "F13",
        "F14",
        "F15",
        "F16",
        "F17",
        "F18",
        "F19",
        "F20",
        "F21",
        "F22",
        "F23",
        "F24",
        "MEDIA_PLAY_PAUSE",
        "MEDIA_STOP",
        "MEDIA_NEXT_TRACK",
        "MEDIA_PREV_TRACK",
        "VOLUME_UP",
        "VOLUME_DOWN",
        "VOLUME_MUTE",
        "BROWSER_BACK",
        "BROWSER_FORWARD",
        "BROWSER_REFRESH",
        "BROWSER_STOP",
        "BROWSER_SEARCH",
        "BROWSER_FAVORITES",
        "BROWSER_HOME",
        "LAUNCH_MAIL",
        "LAUNCH_MEDIA_SELECT",
        "LAUNCH_APP1",
        "LAUNCH_APP2",
    ]

    MODIFIER_KEYS = {"CTRL", "ALT", "SHIFT", "ALT_GR"}
    MODIFIER_ORDER = {
        "CTRL": 0,
        "ALT": 1,
        "ALT_GR": 2,
        "SHIFT": 3,
    }

    KEY_NAME_MAP = {
        "backspace": "BACKSPACE",
        "tab": "TAB",
        "enter": "ENTER",
        "return": "ENTER",
        "shift": "SHIFT",
        "left shift": "SHIFT",
        "right shift": "SHIFT",
        "ctrl": "CTRL",
        "left ctrl": "CTRL",
        "right ctrl": "CTRL",
        "alt": "ALT",
        "left alt": "ALT",
        "right alt": "ALT",
        "alt gr": "ALT_GR",
        "pause": "PAUSE",
        "caps lock": "CAPSLOCK",
        "esc": "ESCAPE",
        "escape": "ESCAPE",
        "space": "SPACE",
        "page up": "PAGE_UP",
        "page down": "PAGE_DOWN",
        "end": "END",
        "home": "HOME",
        "left": "LEFT",
        "up": "UP",
        "right": "RIGHT",
        "down": "DOWN",
        "insert": "INSERT",
        "delete": "DELETE",
        "print screen": "PRINT_SCREEN",
        "scroll lock": "SCROLLLOCK",
        "num lock": "NUMLOCK",
        "windows": "LWIN",
        "left windows": "LWIN",
        "right windows": "RWIN",
        "menu": "MENU",
        "apps": "APPS",
        "decimal": "DECIMAL",
        "separator": "SEPARATOR",
        "subtract": "SUBTRACT",
        "add": "ADD",
        "multiply": "MULTIPLY",
        "divide": "DIVIDE",
        "play/pause media": "MEDIA_PLAY_PAUSE",
        "stop media": "MEDIA_STOP",
        "next track": "MEDIA_NEXT_TRACK",
        "previous track": "MEDIA_PREV_TRACK",
        "volume up": "VOLUME_UP",
        "volume down": "VOLUME_DOWN",
        "volume mute": "VOLUME_MUTE",
        "browser back": "BROWSER_BACK",
        "browser forward": "BROWSER_FORWARD",
        "browser refresh": "BROWSER_REFRESH",
        "browser stop": "BROWSER_STOP",
        "browser search": "BROWSER_SEARCH",
        "browser favorites": "BROWSER_FAVORITES",
        "browser home": "BROWSER_HOME",
        "launch mail": "LAUNCH_MAIL",
        "launch media select": "LAUNCH_MEDIA_SELECT",
        "launch app 1": "LAUNCH_APP1",
        "launch app 2": "LAUNCH_APP2",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pressed_keys = set()
        self._hook = None
        self._running = False

    def normalise_key_name(self, key_name):
        if key_name is None:
            return None

        key_name = str(key_name).strip().lower()

        if key_name in self.KEY_NAME_MAP:
            return self.KEY_NAME_MAP[key_name]

        if key_name.startswith("numpad "):
            suffix = key_name.replace("numpad ", "")
            if suffix.isdigit():
                return f"NUMPAD_{suffix}"

        if key_name.startswith("f") and key_name[1:].isdigit():
            return key_name.upper()

        if len(key_name) == 1:
            return key_name

        return key_name.upper().replace(" ", "_")

    def build_key_tuple(self, current_key):
        held_modifiers = [key for key in self._pressed_keys if key in self.MODIFIER_KEYS]
        held_modifiers.sort(key=lambda key: self.MODIFIER_ORDER.get(key, 999))

        if current_key in self.MODIFIER_KEYS:
            return tuple(held_modifiers)

        return tuple(held_modifiers + [current_key])

    def _keyboard_callback(self, event):
        key_name = self.normalise_key_name(event.name)
        if key_name is None:
            return

        if event.event_type == "down":
            self._pressed_keys.add(key_name)
            self.keys_pressed.emit(self.build_key_tuple(key_name))

        elif event.event_type == "up":
            self._pressed_keys.discard(key_name)

    def run(self):
        self._running = True
        self._hook = keyboard.hook(self._keyboard_callback)

        while self._running:
            self.msleep(10)

        if self._hook is not None:
            keyboard.unhook(self._hook)
            self._hook = None

    def stop(self):
        self._running = False
        self.wait()