from PyQt5 import QtWidgets, QtGui, QtCore
import pygetwindow as gw
import win32gui
import sys


class _OutlinedLabel(QtWidgets.QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.text_color = QtGui.QColor("white")
        self.outline_color = QtGui.QColor("black")
        self.outline_width = 2

    def paintEvent(self, event):
        if not self.text():
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setFont(self.font())

        flags = int(self.alignment()) | int(QtCore.Qt.TextWordWrap)

        draw_rect = self.rect().adjusted(
            self.outline_width,
            self.outline_width,
            -self.outline_width,
            -self.outline_width
        )

        painter.setPen(self.outline_color)

        for offset_x in range(-self.outline_width, self.outline_width + 1):
            for offset_y in range(-self.outline_width, self.outline_width + 1):
                if offset_x == 0 and offset_y == 0:
                    continue

                painter.drawText(
                    draw_rect.translated(offset_x, offset_y),
                    flags,
                    self.text()
                )

        painter.setPen(self.text_color)
        painter.drawText(draw_rect, flags, self.text())


class log_window(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        flags: QtCore.Qt.WindowFlags = QtCore.Qt.WindowFlags(),
        width: int = 289,
        height: int = 500,
    ):
        super().__init__(parent, flags)

        self._width = width
        self._height = height

    def setupUi(self):
        self.x_offset = 10
        self.y_offset = 20
        

        self.setWindowFlags(
            QtCore.Qt.Window
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.current_text = ""

        self.setObjectName("Form")
        self.resize(self._width, self._height)

        self.label = _OutlinedLabel("", self)
        self.label.setGeometry(QtCore.QRect(0, 0, self._width, self._height))
        self.label.setStyleSheet(
            'background-color: transparent; font: 63 10pt "Bahnschrift SemiBold";'
        )
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.label.setText("")
        self.label.setObjectName("label")

        self.move_window_check = QtCore.QTimer()
        self.move_window_check.timeout.connect(self.move_window_to_rpcs3)
        self.move_window_check.start(1)

    @staticmethod
    def is_hwnd_visible_9_point(hwnd):
        if hwnd is None:
            return False

        if win32gui.IsWindowVisible(hwnd) == 0:
            return False

        if win32gui.IsIconic(hwnd):
            return False

        left, top, right, bottom = win32gui.GetClientRect(hwnd)

        width = right - left
        height = bottom - top

        if width <= 0 or height <= 0:
            return False

        sample_points = [
            (width // 2, height // 2),
            (width // 4, height // 4),
            (width // 2, height // 4),
            ((width * 3) // 4, height // 4),
            (width // 4, height // 2),
            ((width * 3) // 4, height // 2),
            (width // 4, (height * 3) // 4),
            (width // 2, (height * 3) // 4),
            ((width * 3) // 4, (height * 3) // 4),
        ]

        for point_x, point_y in sample_points:
            screen_x, screen_y = win32gui.ClientToScreen(hwnd, (point_x, point_y))
            top_hwnd = win32gui.WindowFromPoint((screen_x, screen_y))

            if top_hwnd == hwnd:
                return True

        return False

    def get_rpcs3_window_location(self):
        found_hwnd = None

        for current_window in gw.getAllWindows():
            try:
                title = current_window.title

                if ("FPS" in title and "Skate 3" in title) and ("BLUS" in title or "BLES" in title):
                    found_hwnd = current_window._hWnd

            except Exception as e:
                print(e)

        if found_hwnd is None:
            return None

        is_vis = self.is_hwnd_visible_9_point(found_hwnd)
        client_left, client_top, _, _ = win32gui.GetClientRect(found_hwnd)
        x, y = win32gui.ClientToScreen(found_hwnd, (client_left, client_top))
        return (x, y, is_vis)

    def log(self, text):
        self.current_text = f"{text}\n{self.current_text}"
        self.label.setText(self.current_text)

    def _set_text(self, text):
        self.current_text = text
        self.label.setText(self.current_text)

    def move_window_to_rpcs3(self):
        window_pos = self.get_rpcs3_window_location()

        if window_pos is None:
            return

        x = window_pos[0]
        y = window_pos[1]

        self.move(x + self.x_offset, y + self.y_offset)
        self.setVisible(window_pos[2])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    log_windows = log_window()
    log_windows.setupUi()
    log_windows.show()
    log_windows.log("hello")
    log_windows.log("this should outline")
    log_windows.log("multi line works now")

    sys.exit(app.exec_())