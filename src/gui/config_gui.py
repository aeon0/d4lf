import enum
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from config.loader import IniConfigLoader
from config.models import _IniBaseModel

CONFIG_TABNAME = "Config"


def _save_change(header, key, value):
    IniConfigLoader().save_value(header, key, value)


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

        instructions_text = QTextBrowser()
        instructions_text.setOpenExternalLinks(True)
        instructions_text.append(
            "All values are saved automatically immediately upon changing. To view a description of what each value is,"
            " please view "
            "<a href='https://github.com/aeon0/d4lf?tab=readme-ov-file#configs'>the config portion of the readme</a>"
        )
        instructions_text.append("")
        instructions_text.append("Note: Modifying params.ini manually while this is running is not supported" " (and really not necessary)")
        instructions_text.append("")
        instructions_text.append("Upcoming functionality:")
        instructions_text.append(" - Validation")
        instructions_text.append(" - Description of fields in the GUI")
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

    @staticmethod
    def _generate_parameter_value_widget(section_config_header, config_key, config_value):
        parameter_value_widget = QLineEdit(str(config_value))
        parameter_value_widget.editingFinished.connect(
            lambda: _save_change(section_config_header, config_key, parameter_value_widget.text())
        )

        if config_key == "check_chest_tabs":
            parameter_value_widget = QChestTabWidget(section_config_header, config_key, config_value)
        elif config_key == "profiles":
            parameter_value_widget = QProfilesWidget(section_config_header, config_key, config_value)
        elif isinstance(config_value, enum.StrEnum):
            parameter_value_widget = IgnoreScrollWheelComboBox()
            enum_type = type(config_value)
            parameter_value_widget.addItems(list(enum_type))
            parameter_value_widget.setCurrentText(config_value)
            parameter_value_widget.currentTextChanged.connect(
                lambda: _save_change(section_config_header, config_key, parameter_value_widget.currentText())
            )
        elif isinstance(config_value, bool):
            parameter_value_widget = QCheckBox()
            parameter_value_widget.setChecked(config_value)
            parameter_value_widget.stateChanged.connect(
                lambda: _save_change(section_config_header, config_key, str(parameter_value_widget.isChecked()))
            )

        return parameter_value_widget


class IgnoreScrollWheelComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            return QComboBox.wheelEvent(self, event)

        return event.ignore()


class QChestTabWidget(QWidget):
    def __init__(self, section_header, config_key, chest_tab_config):
        super().__init__()
        self.all_checkboxes: list[QCheckBox] = []
        stash_checkbox_layout = QHBoxLayout()
        stash_checkbox_layout.setContentsMargins(0, 0, 0, 0)
        for x in range(6):
            stash_checkbox = QCheckBox(self)
            stash_checkbox.setText(str(x + 1))
            self.all_checkboxes.append(stash_checkbox)
            if x in chest_tab_config:
                stash_checkbox.setChecked(True)

            stash_checkbox.stateChanged.connect(lambda: self._save_changes_on_box_change(section_header, config_key))
            stash_checkbox_layout.addWidget(stash_checkbox)
        self.setLayout(stash_checkbox_layout)

    def _save_changes_on_box_change(self, section_header, config_key):
        active_tabs = [check_box.text() for check_box in self.all_checkboxes if check_box.isChecked()]
        _save_change(section_header, config_key, ",".join(active_tabs))


class QProfilesWidget(QWidget):
    def __init__(self, section_header, config_key, current_profiles):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.current_profile_line_edit = QLineEdit()
        self.current_profile_line_edit.setText(", ".join(current_profiles))
        self.current_profile_line_edit.setReadOnly(True)
        layout.addWidget(self.current_profile_line_edit)

        open_picker_button = QPushButton()
        open_picker_button.setText("...")
        open_picker_button.setMinimumWidth(20)
        open_picker_button.clicked.connect(
            lambda: self._launch_picker(section_header, config_key, self.current_profile_line_edit.text().split(", "))
        )
        layout.addWidget(open_picker_button)

        self.setLayout(layout)

    def _launch_picker(self, section_header, config_key, current_profiles):
        profile_picker = QProfilePicker(self, current_profiles)
        if profile_picker.exec():
            selected_profiles = ", ".join(profile_picker.get_selected_profiles())
            _save_change(section_header, config_key, selected_profiles)
            self.current_profile_line_edit.setText(selected_profiles)


class QProfilePicker(QDialog):
    def __init__(self, parent, current_profiles):
        super().__init__(parent)
        self.setWindowTitle("Select profiles")

        layout = QVBoxLayout()
        self.setGeometry(100, 100, 400, 400)

        profile_folder = IniConfigLoader().user_dir / "profiles"
        message = QLabel(
            f"Below is a list of all profiles found in {profile_folder}. "
            f"Choose as many as you'd like to use at one time by clicking on them."
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        all_profiles_list_widget = QListWidget()
        all_profiles_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        all_profiles = os.listdir(profile_folder)
        self.profile_list_items: list[QListWidgetItem] = []
        for profile_file in all_profiles:
            profile_name = os.path.splitext(profile_file)[0]
            list_item = QListWidgetItem(profile_name, all_profiles_list_widget)
            self.profile_list_items.append(list_item)
            if profile_name in current_profiles:
                list_item.setSelected(True)
        layout.addWidget(all_profiles_list_widget)

        ok_cancel_buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(ok_cancel_buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def get_selected_profiles(self):
        return [list_item.text() for list_item in self.profile_list_items if list_item.isSelected()]
