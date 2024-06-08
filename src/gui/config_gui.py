import enum

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config.loader import IniConfigLoader
from config.models import _IniBaseModel

CONFIG_TABNAME = "Config"


class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        scrollable_layout = QVBoxLayout()
        scroll_widget = QWidget()
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scrollable_layout.addWidget(self._generate_params_section(IniConfigLoader().general, "General", "general"))
        scrollable_layout.addWidget(self._generate_params_section(IniConfigLoader().char, "Character", "char"))
        scrollable_layout.addWidget(self._generate_params_section(IniConfigLoader().advanced_options, "Advanced", "advanced_options"))
        scroll_widget.setLayout(scrollable_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        instructions_label = QLabel("Instructions")
        layout.addWidget(instructions_label)

        instructions_text = QTextEdit()
        instructions_text.setText("blah")
        instructions_text.setReadOnly(True)
        font_metrics = instructions_text.fontMetrics()
        text_height = font_metrics.height() * (instructions_text.document().lineCount() + 1)
        instructions_text.setFixedHeight(text_height)
        layout.addWidget(instructions_text)

        self.setLayout(layout)

    def _generate_params_section(self, parameter_list: _IniBaseModel, section_readable_header: str, section_config_header: str):
        group_box = QGroupBox(section_readable_header)
        form_layout = QFormLayout()

        for parameter in parameter_list:
            config_key, config_value = parameter
            parameter_value_widget = self._generate_parameter_value_widget(section_config_header, config_key, config_value)
            form_layout.addRow(config_key, parameter_value_widget)

        group_box.setLayout(form_layout)
        return group_box

    def _generate_parameter_value_widget(self, section_config_header, config_key, config_value):
        parameter_value_widget = QLineEdit(str(config_value))
        parameter_value_widget.editingFinished.connect(
            lambda: self._save_change(section_config_header, config_key, parameter_value_widget.text())
        )
        if isinstance(config_value, enum.StrEnum):
            parameter_value_widget = IgnoreScrollWheelComboBox()
            enum_type = type(config_value)
            parameter_value_widget.addItems(list(enum_type))
            parameter_value_widget.setCurrentText(config_value)
            parameter_value_widget.currentTextChanged.connect(
                lambda: self._save_change(section_config_header, config_key, parameter_value_widget.currentText())
            )
        elif isinstance(config_value, bool):
            parameter_value_widget = QCheckBox()
            parameter_value_widget.setChecked(config_value)
            parameter_value_widget.stateChanged.connect(
                lambda: self._save_change(section_config_header, config_key, str(parameter_value_widget.isChecked()))
            )

        return parameter_value_widget

    def _save_change(self, header, key, value):
        IniConfigLoader().save_value(header, key, value)


class IgnoreScrollWheelComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            return QComboBox.wheelEvent(self, event)

        return event.ignore()
