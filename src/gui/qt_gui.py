import logging
import os
import pathlib
import sys

from gui import config_tab
from PyQt6.QtCore import QObject, QRegularExpression, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.config.helper import singleton
from src.config.loader import IniConfigLoader
from src.gui.importer.d4builds import import_d4builds
from src.gui.importer.diablo_trade import import_diablo_trade
from src.gui.importer.maxroll import import_maxroll
from src.gui.importer.mobalytics import import_mobalytics
from src.logger import Logger

THREADPOOL = QThreadPool()
D4TRADE_TABNAME = "diablo.trade"
MAXROLL_D4B_MOBALYTICS_TABNAME = "maxroll / d4builds / mobalytics"


def start_gui():
    os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"
    app = QApplication([])
    app.setWindowIcon(QIcon(str(pathlib.Path("assets/logo.png"))))
    window = Gui()
    window.show()
    sys.exit(app.exec())


@singleton
class Gui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("D4LF")
        self.setGeometry(0, 0, 650, 800)

        # Center the window on the screen
        screen = QApplication.primaryScreen()
        rect = screen.geometry()
        self.move(rect.width() // 2 - self.width() // 2, (rect.height() // 2 - self.height() // 2) - 30)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabBar(_CustomTabBar())
        self.setCentralWidget(self.tab_widget)

        self._maxroll_or_d4builds_tab()
        self._diablo_trade_tab()
        self.tab_widget.addTab(config_tab.ConfigTab(), config_tab.CONFIG_TABNAME)

        Logger.addHandler(self.maxroll_log_handler)
        self.tab_widget.currentChanged.connect(self._handle_tab_changed)
        self._toggle_dark_mode()

    def _diablo_trade_tab(self):
        tab_diablo_trade = QWidget(self)
        self.tab_widget.addTab(tab_diablo_trade, "diablo.trade")

        layout = QVBoxLayout(tab_diablo_trade)

        def handle_text_changed(text):
            generate_button.setEnabled(bool(input_box.text().strip()) and bool(input_box2.text().strip()))

        hbox = QHBoxLayout()
        url_label = QLabel("url")
        hbox.addWidget(url_label)
        input_box = QLineEdit()
        input_box.textChanged.connect(handle_text_changed)
        hbox.addWidget(input_box)
        maxsize_label = QLabel("max listings")
        hbox.addWidget(maxsize_label)
        input_box2 = QLineEdit()
        input_box2.setText("1000")
        metrics = input_box2.fontMetrics()
        width = metrics.horizontalAdvance("0") * 10
        input_box2.setFixedWidth(width)
        input_box2.textChanged.connect(handle_text_changed)
        reg_ex = QRegularExpression("\\d*")
        input_validator = QRegularExpressionValidator(reg_ex, input_box2)
        input_box2.setValidator(input_validator)
        hbox.addWidget(input_box2)
        layout.addLayout(hbox)

        def generate_button_click():
            worker = _Worker(import_diablo_trade, url=input_box.text(), max_listings=int(input_box2.text()))
            worker.signals.finished.connect(on_worker_finished)
            generate_button.setEnabled(False)
            generate_button.setText("Generating...")
            self.tab_widget.tabBar().enableTabSwitching(False)
            THREADPOOL.start(worker)

        def on_worker_finished():
            generate_button.setEnabled(True)
            generate_button.setText("Generate")
            self.tab_widget.tabBar().enableTabSwitching(True)
            Logger.info("\n")

        hbox2 = QHBoxLayout()
        generate_button = QPushButton("Generate")
        generate_button.setEnabled(False)
        generate_button.clicked.connect(generate_button_click)
        hbox2.addWidget(generate_button)
        profiles_button = QPushButton("Open Userconfig Directory")
        profiles_button.clicked.connect(self._open_userconfig_directory)
        hbox2.addWidget(profiles_button)
        layout.addLayout(hbox2)

        log_label = QLabel("Log")
        layout.addWidget(log_label)

        log_output = QTextEdit()
        log_output.setReadOnly(True)
        layout.addWidget(log_output)

        self.diablo_trade_log_handler = _GuiLogHandler(log_output)

        instructions_label = QLabel("Instructions")
        layout.addWidget(instructions_label)

        instructions_text = QTextEdit()
        instructions_text.setText(
            "You can link any valid filter created by diablo.trade.\n\n"
            "https://diablo.trade/listings/items?exactPrice=true&rarity=legendary&sold=true&sort=newest\n\n"
            "Please note that only legendary items are supported at the moment. The listing must also have an exact price.\n"
            "You can create such a filter by using the one above as a base and then add your custom data to it.\n"
            f"It will then create a file based on the listings in: {IniConfigLoader().user_dir / "profiles"}"
        )
        instructions_text.setReadOnly(True)
        font_metrics = instructions_text.fontMetrics()
        text_height = font_metrics.height() * (instructions_text.document().lineCount() + 1)
        instructions_text.setFixedHeight(text_height)
        layout.addWidget(instructions_text)

        tab_diablo_trade.setLayout(layout)

    def _handle_tab_changed(self, index):
        if self.tab_widget.tabText(index) == MAXROLL_D4B_MOBALYTICS_TABNAME:
            Logger.addHandler(self.maxroll_log_handler)
            Logger.removeHandler(self.diablo_trade_log_handler)
        elif self.tab_widget.tabText(index) == D4TRADE_TABNAME:
            Logger.addHandler(self.diablo_trade_log_handler)
            Logger.removeHandler(self.maxroll_log_handler)

    def _maxroll_or_d4builds_tab(self):
        tab_maxroll = QWidget(self)
        self.tab_widget.addTab(tab_maxroll, MAXROLL_D4B_MOBALYTICS_TABNAME)

        layout = QVBoxLayout(tab_maxroll)

        def handle_text_changed(text):
            generate_button.setEnabled(bool(text.strip()))

        hbox = QHBoxLayout()
        url_label = QLabel("url")
        hbox.addWidget(url_label)
        input_box = QLineEdit()
        input_box.textChanged.connect(handle_text_changed)
        hbox.addWidget(input_box)
        layout.addLayout(hbox)

        def generate_button_click():
            url = input_box.text().strip()
            if "maxroll" in url:
                worker = _Worker(import_maxroll, url=url)
            elif "d4builds" in url:
                worker = _Worker(import_d4builds, url=url)
            else:
                worker = _Worker(import_mobalytics, url=url)
            worker.signals.finished.connect(on_worker_finished)
            generate_button.setEnabled(False)
            generate_button.setText("Generating...")
            self.tab_widget.tabBar().enableTabSwitching(False)
            THREADPOOL.start(worker)

        def on_worker_finished():
            generate_button.setEnabled(True)
            generate_button.setText("Generate")
            self.tab_widget.tabBar().enableTabSwitching(True)
            Logger.info("\n")

        hbox2 = QHBoxLayout()
        generate_button = QPushButton("Generate")
        generate_button.setEnabled(False)
        generate_button.clicked.connect(generate_button_click)
        hbox2.addWidget(generate_button)
        profiles_button = QPushButton("Open Userconfig Directory")
        profiles_button.clicked.connect(self._open_userconfig_directory)
        hbox2.addWidget(profiles_button)
        layout.addLayout(hbox2)

        log_label = QLabel("Log")
        layout.addWidget(log_label)

        log_output = QTextEdit()
        log_output.setReadOnly(True)
        layout.addWidget(log_output)

        self.maxroll_log_handler = _GuiLogHandler(log_output)

        instructions_label = QLabel("Instructions")
        layout.addWidget(instructions_label)

        instructions_text = QTextEdit()
        instructions_text.setText(
            "You can link either the build guide or a direct link to the specific planner.\n\n"
            "https://maxroll.gg/d4/build-guides/tornado-druid-guide\n"
            "or\n"
            "https://maxroll.gg/d4/planner/cm6pf0xa#5\n"
            "or\n"
            "https://d4builds.gg/builds/ef414fbd-81cd-49d1-9c8d-4938b278e2ee\n"
            "or\n"
            "https://mobalytics.gg/diablo-4/builds/barbarian/bash-bleed-barbarian-guide\n\n"
            f"It will create a file based on the label of the build in the planer in: {IniConfigLoader().user_dir / "profiles"}\n\n"
            "For d4builds you need to specify your browser in the params.ini file"
        )
        instructions_text.setReadOnly(True)
        font_metrics = instructions_text.fontMetrics()
        text_height = font_metrics.height() * (instructions_text.document().lineCount() + 1)
        instructions_text.setFixedHeight(text_height)
        layout.addWidget(instructions_text)

        tab_maxroll.setLayout(layout)

    @staticmethod
    def _open_userconfig_directory():
        os.startfile(IniConfigLoader().user_dir)

    def _toggle_dark_mode(self):
        if QApplication.instance().styleSheet():
            QApplication.instance().setStyleSheet("")
        else:
            QApplication.instance().setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #bbb;
                }
                QPushButton {
                    background-color: #333;
                    border: 1px solid #555;
                }
                QPushButton:hover {
                    border: 1px solid #888;
                }
                QPushButton:pressed {
                    background-color: #555;
                }
                QTextEdit {
                    background-color: #333;
                    color: #bbb;
                }
                QLineEdit {
                    background-color: #333;
                    color: #bbb;
                }
                QTabBar::tab {
                    background-color: #333;
                    color: #bbb;
                }
                QTabBar::tab:selected {
                    background-color: #2b2b2b;
                }
            """)


class _CustomTabBar(QTabBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tab_switching_enabled = True
        self.currentChanged.connect(self.updateTabColors)

    def mousePressEvent(self, event):
        if self.tab_switching_enabled:
            super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if self.tab_switching_enabled:
            super().keyPressEvent(event)

    def enableTabSwitching(self, enable):
        self.tab_switching_enabled = enable
        self.updateTabColors()

    def updateTabColors(self):
        for index in range(self.count()):
            color = "grey" if not self.tab_switching_enabled and index != self.currentIndex() else "black"
            self.setTabTextColor(index, QColor(color))


class _GuiLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_entry = self.format(record)
        self.text_widget.append(log_entry)


class _Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = _WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit()


class _WorkerSignals(QObject):
    finished = pyqtSignal()


if __name__ == "__main__":
    os.chdir(pathlib.Path(__file__).parent.parent.parent)
    Logger.init(lvl="DEBUG")
    start_gui()
