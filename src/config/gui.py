import logging
import os
import pathlib
import sys
import threading

from logger import Logger
from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QMainWindow, QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget
from utils.importer.maxroll import import_build

from config.helper import singleton
from config.loader import IniConfigLoader


@singleton
class Gui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("D4LF")
        self.setGeometry(100, 100, 600, 600)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.tab_maxroll = QWidget(self)
        self.tab_widget.addTab(self.tab_maxroll, "maxroll.gg")

        self.layout = QVBoxLayout(self.tab_maxroll)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Enter url here")
        self.input_box.textChanged.connect(self._handle_text_changed)
        self.layout.addWidget(self.input_box)

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self._generate_button_click)
        self.generate_button.setEnabled(False)
        self.layout.addWidget(self.generate_button)

        self.profiles_button = QPushButton("Open Userconfig Directory")
        self.profiles_button.clicked.connect(self._open_userconfig_directory)
        self.layout.addWidget(self.profiles_button)

        self.log_label = QLabel("Log")
        self.layout.addWidget(self.log_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)

        log_handler = GuiLogHandler(self.log_output)
        Logger.addHandler(log_handler)

        self.instructions_label = QLabel("Instructions")
        self.layout.addWidget(self.instructions_label)

        self.instructions_text = QTextEdit()
        self.instructions_text.setText(
            "You can link either the build guide or a direct link to the specific planner you are after.\n\n"
            "https://maxroll.gg/d4/build-guides/tornado-druid-guide\n"
            "or\n"
            "https://maxroll.gg/d4/planner/g54iz0wt#4\n\n"
            f"It will create a file based on the label of the build in the planer in: {IniConfigLoader().user_dir / "profiles"}\n\n"
            "Supported browsers are Edge, Chrome, and Firefox, you can specify the browser to use in the params.ini file"
        )
        self.instructions_text.setReadOnly(True)
        self.layout.addWidget(self.instructions_text)

        self.tab_maxroll.setLayout(self.layout)

    def _generate_button_click(self):
        url = self.input_box.text()
        threading.Thread(target=import_build, kwargs={"url": url}).start()

    def _handle_text_changed(self, text):
        self.generate_button.setEnabled(bool(text.strip()))

    @staticmethod
    def _open_userconfig_directory():
        os.startfile(IniConfigLoader().user_dir)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()


def start_gui():
    app = QApplication(sys.argv)
    window = Gui()
    window.show()
    app.exec()


class GuiLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_entry = self.format(record)
        self.text_widget.append(log_entry)


if __name__ == "__main__":
    os.chdir(pathlib.Path(__file__).parent.parent.parent)
    Logger.init(lvl="DEBUG")
    start_gui()
