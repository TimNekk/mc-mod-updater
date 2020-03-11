from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import script as s
import threading
import os
import data
from time import sleep
import pathlib
import subprocess
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# noinspection PyAttributeOutsideInit


def print_console(text):
    data.console_text += text + '\n'
    print(text)


def save_data_py():
    text = "console_text = ''\n"
    text += "user_mc_version = '{}'\n".format(data.user_mc_version)
    text += "user_mc_path = r'{}'\n".format(data.user_mc_path)
    text += "console_font = '{}'\n".format(data.console_font)
    text += "save_old_mods = {}\n".format(data.save_old_mods)
    text += "dark_mode = {}\n".format(data.dark_mode)
    text += "mods = []\n"

    with open('data.py', 'w') as file:
        file.write(text)


def reset_data_py():
    expected_mc_path = pathlib.Path.home() / 'AppData' / 'Roaming' / '.minecraft' / 'mods'
    if not os.path.exists(expected_mc_path):
        expected_mc_path = ''

    text = "console_text = ''\n"
    text += "user_mc_version = ''\n"
    text += "user_mc_path = r'{}'\n".format(str(expected_mc_path))
    text += "console_font = '8'\n"
    text += "save_old_mods = False\n"
    text += "dark_mode = True\n"
    text += "dark_mode = True\n"
    text += "mods = []\n"

    with open('data.py', 'w') as file:
        file.write(text)

    data.console_text = ''
    data.user_mc_version = ''
    data.user_mc_path = str(expected_mc_path)
    data.console_font = '8'
    data.save_old_mods = False
    data.dark_mode = True
    data.mods = []

    print_console('data.py reset!\n')


class UpdatingThread(QThread):
    mod_added = pyqtSignal(dict)
    done = pyqtSignal(bool)

    def __init__(self, mainwindow, mod=False, index=99999999999999999999):
        super().__init__()
        self.mainwindow = mainwindow
        self.mod = mod
        self.index = index

    def run(self):
        # Установлен ли путь до папки MC
        if not data.user_mc_path:
            print_console('Please, select MC directory!')
            self.mainwindow.stacked_widget.setCurrentIndex(2)
            return False

        self.mainwindow.refresh_button.hide()
        self.mainwindow.mods_button.setDisabled(True)
        self.mainwindow.console_button.setDisabled(True)
        self.mainwindow.settings_button.setDisabled(True)
        self.mainwindow.mc_version_select_box.setDisabled(True)
        self.mainwindow.progress_bar_widget.show()
        self.mainwindow.mods_widget_horizontal_layout.removeItem(self.mainwindow.mods_widget_horizontal_layout_spacer_item)

        print_console('Refreshing started!\n')

        # ---------------------------------------------------------------
        # Test
        # ---------------------------------------------------------------
        test = False
        if test:
            mods = [{'name': 'Chisel', 'file_name': 'Chisel-MC1.12-0.1.0.22.jar',
                     'url': 'https://www.curseforge.com/minecraft/mc-mods/chisel/files/all', 'version': '0.1.0.22',
                     'mc_version': '1.12',
                     'download_link': 'https://www.curseforge.com/minecraft/mc-mods/chisel/download/2813538/file',
                     'new_version_text': 'Chisel - MC1.12.2-1.0.1.44', 'new_version': '1.0.1.44'},
                    {'name': 'JourneyMap', 'file_name': 'journeymap-1.12.2-5.5.9.jar',
                     'url': 'https://www.curseforge.com/minecraft/mc-mods/journeymap/files/all', 'version': '5.5.9',
                     'mc_version': '1.12.2', 'download_link': False}, {'name': 'Test', 'file_name': 'Test.jar',
                                                                       'url': 'https://www.curseforge.com/minecraft/mc-mods/Test/files/all',
                                                                       'version': 'Test',
                                                                       'mc_version': 'Test', 'download_link': False}]

            for mod in mods:
                mod['mod_slot'] = self.create_mod_slot(mod)
                self.mods.append(mod)
                self.update_scroll_area()
        # ---------------------------------------------------------------
        # Test
        # ---------------------------------------------------------------

        elif not test:
            files = []

            # Если нужно обновить конкретный мод
            if self.mod:
                file_name = self.mod['new_version_text']
                file_path = os.path.join(data.user_mc_path, file_name)
                files.append([file_name, file_path])
            else:
                self.mainwindow.mods = []

                # Проход через все файлы в попке mods
                for file_name in os.listdir(data.user_mc_path):
                    # Это файл, а не папка?
                    if os.path.isfile(os.path.join(data.user_mc_path, file_name)):
                        files.append(file_name)

                self.mainwindow.mods_count = len(files)

            for file in files:
                self.mod = s.get_mod_info(file)

                # Достаточно ли информации чтобы работать с модом
                if self.mod:
                    print_console(self.mod['name'])
                    self.mod = s.update_mod_url(self.mod, self.mainwindow.mc_version_select_box.currentText())

                    # HTTP Error 429: Too Many Requests
                    if self.mod == '429':
                        break

                    # Нашли ли ссылку на этот мод
                    if not self.mod['url']:
                        continue

                    self.mod = s.check_if_mod_is_updated(self.mod, self.mainwindow.mc_version_select_box.currentText())
                    # Мод прошел все проверки и обработки

                    self.mod_added.emit(self.mod)

                    print_console('')

        # Уюирание прогресс бара
        self.mainwindow.mods_count = 0
        self.mainwindow.mods_done = 0
        self.mainwindow.progress_bar_widget.hide()


        self.mainwindow.mods_button.setDisabled(False)
        self.mainwindow.console_button.setDisabled(False)
        self.mainwindow.settings_button.setDisabled(False)
        self.mainwindow.mc_version_select_box.setDisabled(False)
        self.mainwindow.mods_widget_horizontal_layout_spacer_item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainwindow.mods_widget_horizontal_layout.insertItem(2, self.mainwindow.mods_widget_horizontal_layout_spacer_item)

        # Показать кноки refresh и update_all
        self.done.emit(True)

        print_console('\nRefreshing is done!\n')


class UiMainWindow(object):
    def __init__(self):
        self.mods = []
        self.old_mods = []
        self.color_dark_grey = 'rgb(37, 37, 37);'
        self.color_light_grey = 'rgb(50, 50, 50);'
        self.color_red = 'rgb(255, 47, 50)'
        self.border_color = self.color_red
        self.stop_threads = False
        self.mods_count = 0
        self.mods_done = 0

    def setup_ui(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(579, 558)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
        main_window.setSizePolicy(size_policy)
        main_window.setTabShape(QtWidgets.QTabWidget.Rounded)

        # main_widget

        self.main_widget = QtWidgets.QWidget(main_window)
        self.main_widget.setObjectName("main_widget")

        self.main_widget_vertical_layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.main_widget_vertical_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.main_widget_vertical_layout.setContentsMargins(15, 15, 15, 15)
        self.main_widget_vertical_layout.setSpacing(15)
        self.main_widget_vertical_layout.setObjectName("main_widget_vertical_layout")

        # main_widget -> title_widget

        self.title_widget = QtWidgets.QWidget(self.main_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.title_widget.sizePolicy().hasHeightForWidth())
        self.title_widget.setSizePolicy(size_policy)
        self.title_widget.setObjectName("title_widget")

        self.title_widget_horizontal_layout = QtWidgets.QHBoxLayout(self.title_widget)
        self.title_widget_horizontal_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.title_widget_horizontal_layout.setContentsMargins(15, 15, 15, 15)
        self.title_widget_horizontal_layout.setSpacing(6)
        self.title_widget_horizontal_layout.setObjectName("title_widget_horizontal_layout")

        self.title = QtWidgets.QLabel(self.title_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.title.sizePolicy().hasHeightForWidth())
        self.title.setSizePolicy(size_policy)
        self.title.setObjectName("title")
        self.title_widget_horizontal_layout.addWidget(self.title)

        self.program_version = QtWidgets.QLabel(self.title_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.program_version.sizePolicy().hasHeightForWidth())
        self.program_version.setSizePolicy(size_policy)
        self.program_version.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.program_version.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.program_version.setObjectName("program_version")
        self.title_widget_horizontal_layout.addWidget(self.program_version)

        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.title_widget_horizontal_layout.addItem(spacer_item)
        self.main_widget_vertical_layout.addWidget(self.title_widget)

        # main_widget -> top_widget

        self.top_widget = QtWidgets.QWidget(self.main_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.top_widget.sizePolicy().hasHeightForWidth())
        self.top_widget.setSizePolicy(size_policy)
        self.top_widget.setObjectName("top_widget")

        self.top_widget_horizontal_layout = QtWidgets.QHBoxLayout(self.top_widget)
        self.top_widget_horizontal_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.top_widget_horizontal_layout.setContentsMargins(15, 15, 15, 15)
        self.top_widget_horizontal_layout.setSpacing(15)
        self.top_widget_horizontal_layout.setObjectName("top_widget_horizontal_layout")

        self.mods_button = QtWidgets.QPushButton(self.top_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.mods_button.sizePolicy().hasHeightForWidth())
        self.mods_button.setSizePolicy(size_policy)
        self.mods_button.setMinimumSize(QtCore.QSize(125, 40))
        self.mods_button.setMaximumSize(QtCore.QSize(16777215, 40))
        self.mods_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.mods_button.setObjectName("mods_button")
        self.mods_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.top_widget_horizontal_layout.addWidget(self.mods_button)

        self.console_button = QtWidgets.QPushButton(self.top_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.console_button.sizePolicy().hasHeightForWidth())
        self.console_button.setSizePolicy(size_policy)
        self.console_button.setMinimumSize(QtCore.QSize(125, 40))
        self.console_button.setMaximumSize(QtCore.QSize(16777215, 40))
        self.console_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.console_button.setObjectName("console_button")
        self.console_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.top_widget_horizontal_layout.addWidget(self.console_button)

        self.settings_button = QtWidgets.QPushButton(self.top_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.settings_button.sizePolicy().hasHeightForWidth())
        self.settings_button.setSizePolicy(size_policy)
        self.settings_button.setMinimumSize(QtCore.QSize(125, 40))
        self.settings_button.setMaximumSize(QtCore.QSize(16777215, 40))
        self.settings_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.settings_button.setObjectName("settings_button")
        self.settings_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.top_widget_horizontal_layout.addWidget(self.settings_button)

        self.main_widget_vertical_layout.addWidget(self.top_widget)

        # main_widget -> stacked_widget

        self.stacked_widget = QtWidgets.QStackedWidget(self.main_widget)
        self.stacked_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.stacked_widget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.stacked_widget.setLineWidth(0)
        self.stacked_widget.setMidLineWidth(0)
        self.stacked_widget.setObjectName("stacked_widget")

        # main_widget -> stacked_widget -> mods_page

        self.mods_page = QtWidgets.QWidget()
        self.mods_page.setObjectName("mods_page")

        self.mods_page_vertical_layout = QtWidgets.QVBoxLayout(self.mods_page)
        self.mods_page_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.mods_page_vertical_layout.setSpacing(15)
        self.mods_page_vertical_layout.setObjectName("mods_page_vertical_layout")

        # main_widget -> stacked_widget -> mods_page -> update_widget

        self.update_widget = QtWidgets.QWidget(self.mods_page)
        self.update_widget.setEnabled(True)
        self.update_widget.setObjectName("update_widget")

        self.update_widget_vertical_layout = QtWidgets.QVBoxLayout(self.update_widget)
        self.update_widget_vertical_layout.setContentsMargins(9, 9, 9, 9)
        self.update_widget_vertical_layout.setSpacing(0)
        self.update_widget_vertical_layout.setObjectName("update_widget_vertical_layout")

        self.scroll_area = QtWidgets.QScrollArea(self.update_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.scroll_area.sizePolicy().hasHeightForWidth())
        self.scroll_area.setSizePolicy(size_policy)
        self.scroll_area.setMinimumSize(QtCore.QSize(0, 0))
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scroll_area.setLineWidth(0)
        self.scroll_area.setMidLineWidth(0)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_area_widget_contents = QtWidgets.QWidget()
        self.scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 549, 200))
        self.scroll_area_widget_contents.setObjectName("scroll_area_widget_contents")

        self.scroll_area.setWidget(self.scroll_area_widget_contents)

        self.update_widget_vertical_layout.addWidget(self.scroll_area)

        self.scroll_area_widget_contents_vertical_layout = QtWidgets.QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area_widget_contents_vertical_layout.setObjectName("scroll_area_widget_contents_vertical_layout")

        # spacer_item_4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # self.scroll_area_widget_contents_vertical_layout.addItem(spacer_item_4)

        self.mods_page_vertical_layout.addWidget(self.update_widget)

        # main_widget -> stacked_widget -> mods_page -> mods_widget

        self.mods_widget = QtWidgets.QWidget(self.mods_page)
        self.mods_widget.setMaximumSize(QtCore.QSize(0, 84))
        self.mods_widget.setEnabled(True)
        self.mods_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.mods_widget.setObjectName("mods_widget")

        self.mods_widget_horizontal_layout = QtWidgets.QHBoxLayout(self.mods_widget)
        self.mods_widget_horizontal_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.mods_widget_horizontal_layout.setContentsMargins(15, 15, 15, 15)
        self.mods_widget_horizontal_layout.setSpacing(15)
        self.mods_widget_horizontal_layout.setObjectName("mods_widget_horizontal_layout")

        self.mc_version_label = QtWidgets.QLabel(self.mods_widget)
        self.mc_version_label.setObjectName("mc_version_label")
        self.mods_widget_horizontal_layout.addWidget(self.mc_version_label)

        self.mc_version_select_box = QtWidgets.QComboBox(self.mods_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.mc_version_select_box.sizePolicy().hasHeightForWidth())
        self.mc_version_select_box.setSizePolicy(size_policy)
        self.mc_version_select_box.setMinimumSize(QtCore.QSize(75, 54))
        self.mc_version_select_box.setMaximumSize(QtCore.QSize(75, 54))
        self.mc_version_select_box.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.mc_version_select_box.setAcceptDrops(False)
        self.mc_version_select_box.setEditable(False)
        self.mc_version_select_box.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.mc_version_select_box.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContentsOnFirstShow)
        self.mc_version_select_box.setDuplicatesEnabled(False)
        self.mc_version_select_box.setFrame(True)
        self.mc_version_select_box.setObjectName("mc_version_select_box")
        self.mc_versions = s.get_all_mc_versions()
        for mc_version in self.mc_versions:
            self.mc_version_select_box.addItem(mc_version)

        self.mods_widget_horizontal_layout.addWidget(self.mc_version_select_box)

        self.mods_widget_horizontal_layout_spacer_item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mods_widget_horizontal_layout.addItem(self.mods_widget_horizontal_layout_spacer_item)

        self.refresh_button = QtWidgets.QPushButton(self.mods_widget)
        self.refresh_button.setMinimumSize(QtCore.QSize(125, 40))
        self.refresh_button.setMaximumSize(QtCore.QSize(125, 40))
        self.refresh_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.clicked.connect(self.refresh_button_pressed)
        self.mods_widget_horizontal_layout.addWidget(self.refresh_button)

        self.update_all_button = QtWidgets.QPushButton(self.mods_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.update_all_button.sizePolicy().hasHeightForWidth())
        self.update_all_button.setSizePolicy(size_policy)
        self.update_all_button.setMinimumSize(QtCore.QSize(125, 40))
        self.update_all_button.setMaximumSize(QtCore.QSize(125, 40))
        self.update_all_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.update_all_button.setObjectName("update_all_button")
        self.update_all_button.hide()
        self.mods_widget_horizontal_layout.addWidget(self.update_all_button)

        self.progress_bar_widget = QtWidgets.QWidget(self.mods_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.progress_bar_widget.sizePolicy().hasHeightForWidth())
        self.progress_bar_widget.setSizePolicy(size_policy)
        self.progress_bar_widget.setMaximumSize(QtCore.QSize(16777215, 40))
        self.progress_bar_widget.setObjectName("progress_bar_widget")
        self.progress_bar_widget_vertical_layout = QtWidgets.QVBoxLayout(self.progress_bar_widget)
        self.progress_bar_widget_vertical_layout.setContentsMargins(5, 5, 5, 5)
        self.progress_bar_widget_vertical_layout.setSpacing(0)
        self.progress_bar_widget_vertical_layout.setObjectName("progress_bar_widget_vertical_layout")
        self.progress_bar_widget.hide()

        # main_widget -> stacked_widget -> mods_page -> mods_widget -> progress_bar_widget

        self.progress_bar = QtWidgets.QWidget(self.progress_bar_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.progress_bar.setSizePolicy(size_policy)
        self.progress_bar.setFixedWidth(0)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar_widget_vertical_layout.addWidget(self.progress_bar)
        self.mods_widget_horizontal_layout.addWidget(self.progress_bar_widget)

        self.mods_page_vertical_layout.addWidget(self.mods_widget)

        self.stacked_widget.addWidget(self.mods_page)

        # main_widget -> stacked_widget -> console_page

        self.console_page = QtWidgets.QWidget()
        self.console_page.setObjectName("console_page")

        self.console_page_vertical_layout = QtWidgets.QVBoxLayout(self.console_page)
        self.console_page_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.console_page_vertical_layout.setSpacing(15)
        self.console_page_vertical_layout.setObjectName("console_page_vertical_layout")

        # main_widget -> stacked_widget -> console_page -> console_widget

        self.console_widget = QtWidgets.QWidget(self.console_page)
        self.console_widget.setObjectName("console_widget")

        self.console_widget_vertical_layout = QtWidgets.QVBoxLayout(self.console_widget)
        self.console_widget_vertical_layout.setContentsMargins(15, 15, 15, 15)
        self.console_widget_vertical_layout.setSpacing(9)
        self.console_widget_vertical_layout.setObjectName("console_widget_vertical_layout")

        self.console_text_edit = QtWidgets.QPlainTextEdit(self.console_widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.console_text_edit.setFont(font)
        self.console_text_edit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.console_text_edit.setFrameShadow(QtWidgets.QFrame.Plain)
        self.console_text_edit.setReadOnly(True)
        self.console_text_edit.setObjectName("plain_text_edit")
        self.console_widget_vertical_layout.addWidget(self.console_text_edit)
        self.console_page_vertical_layout.addWidget(self.console_widget)
        self.stacked_widget.addWidget(self.console_page)

        # main_widget -> stacked_widget -> settings_page

        self.settings_page = QtWidgets.QWidget()
        self.settings_page.setObjectName("settings_page")

        self.settings_page_vertical_layout = QtWidgets.QVBoxLayout(self.settings_page)
        self.settings_page_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_page_vertical_layout.setSpacing(15)
        self.settings_page_vertical_layout.setObjectName("settings_page_vertical_layout")

        # main_widget -> stacked_widget -> settings_page > settings_widget

        self.settings_widget = QtWidgets.QWidget(self.settings_page)
        self.settings_widget.setObjectName("settings_widget")

        self.settings_widget_vertical_layout = QtWidgets.QVBoxLayout(self.settings_widget)
        self.settings_widget_vertical_layout.setContentsMargins(15, 15, 15, 15)
        self.settings_widget_vertical_layout.setSpacing(15)
        self.settings_widget_vertical_layout.setObjectName("settings_widget_vertical_layout")

        # main_widget -> stacked_widget -> settings_page > settings_widget -> path_widget

        self.path_widget = QtWidgets.QWidget(self.settings_widget)
        self.path_widget.setMinimumSize(QtCore.QSize(0, 25))
        self.path_widget.setMaximumSize(QtCore.QSize(16777215, 56))
        self.path_widget.setObjectName("path_widget")

        self.path_widget_horizontal_layout = QtWidgets.QHBoxLayout(self.path_widget)
        self.path_widget_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.path_widget_horizontal_layout.setSpacing(15)
        self.path_widget_horizontal_layout.setObjectName("path_widget_horizontal_layout")

        self.path_line_edit = QtWidgets.QLineEdit(self.path_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.path_line_edit.sizePolicy().hasHeightForWidth())
        self.path_line_edit.setSizePolicy(size_policy)
        self.path_line_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.path_line_edit.setText("")
        self.path_line_edit.setFrame(False)
        self.path_line_edit.setReadOnly(True)
        self.path_line_edit.setObjectName("path_line_edit")
        self.path_widget_horizontal_layout.addWidget(self.path_line_edit)

        self.browse_button = QtWidgets.QPushButton(self.path_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.browse_button.sizePolicy().hasHeightForWidth())
        self.browse_button.setSizePolicy(size_policy)
        self.browse_button.setMinimumSize(QtCore.QSize(125, 0))
        self.browse_button.setMaximumSize(QtCore.QSize(125, 16777215))
        self.browse_button.setObjectName("browse_button")
        self.browse_button.clicked.connect(self.open_file_browser)
        self.path_widget_horizontal_layout.addWidget(self.browse_button)

        self.settings_widget_vertical_layout.addWidget(self.path_widget)

        # main_widget -> stacked_widget -> settings_page > settings_widget

        self.line = QtWidgets.QFrame(self.settings_widget)
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.settings_widget_vertical_layout.addWidget(self.line)

        # main_widget -> stacked_widget -> settings_page > settings_widget -> check_box_widget

        self.check_box_widget = QtWidgets.QWidget(self.settings_widget)
        self.check_box_widget.setObjectName("check_box_widget")

        self.check_box_widget_vertical_layout = QtWidgets.QVBoxLayout(self.check_box_widget)
        self.check_box_widget_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.check_box_widget_vertical_layout.setObjectName("check_box_widget_vertical_layout")

        self.save_check_box = QtWidgets.QCheckBox(self.check_box_widget)
        self.save_check_box.setChecked(data.save_old_mods)
        self.save_check_box.setObjectName("save_check_box")
        self.check_box_widget_vertical_layout.addWidget(self.save_check_box)

        self.dark_check_box = QtWidgets.QCheckBox(self.check_box_widget)
        self.dark_check_box.setChecked(data.dark_mode)
        self.dark_check_box.setObjectName("dark_check_box")
        self.check_box_widget_vertical_layout.addWidget(self.dark_check_box)

        self.settings_widget_vertical_layout.addWidget(self.check_box_widget)

        # main_widget -> stacked_widget -> settings_page > settings_widget

        self.line_3 = QtWidgets.QFrame(self.settings_widget)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setLineWidth(2)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setObjectName("line_3")
        self.settings_widget_vertical_layout.addWidget(self.line_3)

        # main_widget -> stacked_widget -> settings_page > settings_widget -> slide_widget

        self.slide_widget = QtWidgets.QWidget(self.settings_widget)
        self.slide_widget.setObjectName("slide_widget")

        self.slide_widget_horizontal_layout = QtWidgets.QHBoxLayout(self.slide_widget)
        self.slide_widget_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.slide_widget_horizontal_layout.setSpacing(15)
        self.slide_widget_horizontal_layout.setObjectName("horizontalLayout_10")

        self.font_label = QtWidgets.QLabel(self.slide_widget)
        self.font_label.setObjectName("font_label")
        self.slide_widget_horizontal_layout.addWidget(self.font_label)

        self.font_size_label = QtWidgets.QLabel(self.slide_widget)
        self.font_size_label.setObjectName("font_size_label")
        self.slide_widget_horizontal_layout.addWidget(self.font_size_label)

        self.horizontal_slider = QtWidgets.QSlider(self.slide_widget)
        self.horizontal_slider.setMaximumSize(QtCore.QSize(150, 15))
        self.horizontal_slider.setMinimum(6)
        self.horizontal_slider.setMaximum(16)
        self.horizontal_slider.setPageStep(1)
        self.horizontal_slider.setProperty("value", int(data.console_font))
        self.horizontal_slider.setTracking(True)
        self.horizontal_slider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontal_slider.setInvertedAppearance(False)
        self.horizontal_slider.setInvertedControls(False)
        self.horizontal_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.horizontal_slider.setObjectName("horizontal_slider")
        self.slide_widget_horizontal_layout.addWidget(self.horizontal_slider)

        spacer_item_6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.slide_widget_horizontal_layout.addItem(spacer_item_6)

        self.settings_widget_vertical_layout.addWidget(self.slide_widget)

        # main_widget -> stacked_widget -> settings_page > settings_widget

        self.line_2 = QtWidgets.QFrame(self.settings_widget)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setLineWidth(2)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.settings_widget_vertical_layout.addWidget(self.line_2)

        spacer_item_7 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.settings_widget_vertical_layout.addItem(spacer_item_7)

        self.apply_widget = QtWidgets.QWidget(self.settings_widget)
        self.apply_widget.setObjectName("apply_widget")
        self.apply_widget_horizontal_layout = QtWidgets.QHBoxLayout(self.apply_widget)

        self.apply_widget_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.apply_widget_horizontal_layout.setSpacing(15)
        self.apply_widget_horizontal_layout.setObjectName("apply_widget_horizontal_layout")

        spacer_item_8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.apply_widget_horizontal_layout.addItem(spacer_item_8)

        self.default_button = QtWidgets.QPushButton(self.apply_widget)
        self.default_button.setMinimumSize(QtCore.QSize(125, 40))
        self.default_button.setMaximumSize(QtCore.QSize(125, 40))
        self.default_button.setObjectName("default_button")
        self.default_button.clicked.connect(self.reset_settings)
        self.apply_widget_horizontal_layout.addWidget(self.default_button)

        self.apply_button = QtWidgets.QPushButton(self.apply_widget)
        self.apply_button.setMinimumSize(QtCore.QSize(125, 40))
        self.apply_button.setMaximumSize(QtCore.QSize(125, 40))
        self.apply_button.setObjectName("apply_button")
        self.apply_button.clicked.connect(self.apply_button_pressed)
        self.apply_widget_horizontal_layout.addWidget(self.apply_button)

        self.settings_widget_vertical_layout.addWidget(self.apply_widget)

        self.settings_page_vertical_layout.addWidget(self.settings_widget)

        self.stacked_widget.addWidget(self.settings_page)

        self.main_widget_vertical_layout.addWidget(self.stacked_widget)

        main_window.setCentralWidget(self.main_widget)

        self.retranslate_ui(main_window)
        self.stacked_widget.setCurrentIndex(0)

        try:
            self.mc_version_select_box.setCurrentIndex(s.get_all_mc_versions().index(data.user_mc_version))
        except ValueError:
            self.mc_version_select_box.setCurrentIndex(0)

        QtCore.QMetaObject.connectSlotsByName(main_window)

    def open_file_browser(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory()
        if os.path.exists(filename + '/mods'):
            print_console('\nMinecraft directory set to: ' + filename)
            data.user_mc_path = filename + '/mods'
        else:
            print_console('\nInvalid Minecraft directory!')
    
        # Сохранение data.py
        save_data_py()

        self.update_ui()

    def update_ui(self):

        if data.user_mc_path:
            self.path_line_edit.setText(str(data.user_mc_path[:-5]))
            self.border_color = self.color_dark_grey
        else:
            self.path_line_edit.clear()
            self.border_color = self.color_red

        stylesheet = "#main_widget {border-radius: 0px; background-color: rgb(50, 50, 50)}"
        stylesheet += ".QWidget {background-color: rgb(37, 37, 37); border-radius:10px}"
        stylesheet += ".QPushButton {background-color:rgb(50, 50, 50); transition:background-color; color: white; border-radius: 10px; font: 10pt \"Arial\"}"
        stylesheet += ".QPushButton:hover {background-color:rgb(60, 60, 60)}"
        stylesheet += ".QLabel, .QCheckBox {color: white; font: 10pt \"Arial\"}"
        stylesheet += "#title {font: 75 18pt \"Arial\"}"
        stylesheet += "#program_version {margin-top: 6px}"
        stylesheet += ".QComboBox {background-color: rgb(50, 50, 50); color: white; border-radius: 10px; font: 10pt \"Arial\"}"
        stylesheet += ".QScrollArea {border-radius:10px 10px 0px 0px; background-color: rgb(37, 37, 37)}"
        stylesheet += "#mods_page, #console_page, #settings_page {background-color: rgb(50, 50, 50)}"
        stylesheet += ".QPlainTextEdit {background-color: rgb(37, 37, 37); color: white; font: " + data.console_font + "pt \"Arial\"; border: 1px solid rgb(50, 50, 50); border-radius: 10px;}"
        stylesheet += ".Line {color: rgb(50, 50, 50)}"
        stylesheet += ".QLineEdit {background-color: rgb(50, 50, 50); border-radius: 5px; color: white; border:1px solid " + self.border_color + " }"
        stylesheet += "#font_size_label {font: 75 12pt \"Arial\"}"
        stylesheet += "#progress_bar_widget {background-color:rgb(50, 50, 50);}"
        stylesheet += "#progress_bar {background-color: rgb(255, 47, 50); border-radius: 7px;}"

        MainWindow.setStyleSheet(stylesheet)

    def refresh_button_pressed(self):
        self.updating_thread = UpdatingThread(self)
        self.updating_thread.mod_added.connect(self.add_mod)
        self.updating_thread.done.connect(self.show_refresh_and_update_buttons)
        self.updating_thread.start()

    def show_refresh_and_update_buttons(self):
        self.refresh_button.show()

        if self.mods:
            self.update_all_button.show()

    def add_mod(self, mod):
        self.mods_done += 1

        # Добавление в self.mods
        self.mods.append(mod)

        # Создание Мод слота
        try:
            mod['mod_slot']
        except KeyError:
            mod['mod_slot'] = self.create_mod_slot(mod)

        self.update_scroll_area()

    def update_mod(self, mod):
        # TODO - Переделать под новый refresh
        mod = s.update_mod(mod=mod,
                           mods_dir=data.user_mc_path,
                           save_old_mod=self.save_check_box.isChecked())

        self.delete_mod(mod)

        index = self.mods.index(mod)
        self.refresh(mod, index)

    def update_scroll_area(self):
        self.clear_scroll_area()

        for i, mod in enumerate(self.mods, 1):
            print(mod)
            mod['mod_slot'].children()[1].setText(str(i))  # Установка нумерации
            self.scroll_area_widget_contents_vertical_layout.addWidget(mod['mod_slot'])  # Добавление слотов в виджет
        else:
            self.update_all_button.hide()

        # Добавление спейсера
        spacer_item_4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.scroll_area_widget_contents_vertical_layout.addItem(spacer_item_4)

    def clear_scroll_area(self):
        # Удаление всех слотов
        while self.scroll_area_widget_contents_vertical_layout.count():
            child = self.scroll_area_widget_contents_vertical_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def delete_mod(self, mod):
        self.mods.remove(mod)  # Удаление из self.mods
        mod['mod_slot'].setParent(None)  # Удаление слота
        self.update_scroll_area()  # Изменение нумерации слотов
        s.delete_mod(mod)

    def create_mod_slot(self, mod):
        # Создание слота
        mod_slot = QtWidgets.QFrame(self.scroll_area_widget_contents)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(mod_slot.sizePolicy().hasHeightForWidth())
        mod_slot.setSizePolicy(size_policy)
        mod_slot.setStyleSheet("border-radius: 10px;\n"
                               "border: 1px solid rgb(50, 50, 50);\n"
                               "border-radius: 7px;")
        mod_slot.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mod_slot.setFrameShadow(QtWidgets.QFrame.Raised)
        mod_slot.setObjectName("mod_slot")

        mod_slot_horizontal_layout = QtWidgets.QHBoxLayout(mod_slot)
        mod_slot_horizontal_layout.setContentsMargins(7, 7, 7, 7)
        mod_slot_horizontal_layout.setSpacing(7)
        mod_slot_horizontal_layout.setObjectName("mod_slot_1_horizontal_layout")

        # Добавление "Count" label
        mod_slot_count_label = QtWidgets.QLabel(mod_slot)
        mod_slot_count_label.setMinimumSize(QtCore.QSize(20, 20))
        mod_slot_count_label.setMaximumSize(QtCore.QSize(20, 20))
        mod_slot_count_label.setStyleSheet("background-color: rgb(50, 50, 50);")
        mod_slot_count_label.setAlignment(QtCore.Qt.AlignCenter)
        mod_slot_count_label.setObjectName("mod_slot_1_count_label")
        mod_slot_count_label.setText('#')
        mod_slot_horizontal_layout.addWidget(mod_slot_count_label)

        # Добавление "Name" button
        mod_slot_name_button = QtWidgets.QPushButton(mod_slot)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(mod_slot_name_button.sizePolicy().hasHeightForWidth())
        mod_slot_name_button.setSizePolicy(size_policy)
        mod_slot_name_button.setMaximumSize(QtCore.QSize(16777215, 16777215))
        mod_slot_name_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        mod_slot_name_button.setStyleSheet("* {\n"
                                           "    background-color: none;\n"
                                           "    border: none;\n"
                                           "    color: white;\n"
                                           "}\n"
                                           "\n"
                                           "*:hover {\n"
                                           "    background-color: none;\n"
                                           "    color: rgb(165, 165, 165)\n"
                                           "}")
        mod_slot_name_button.setObjectName("mod_slot_1_name_button")
        mod_slot_name_button.setText(mod['name'])  # Присвиевание имени
        mod_slot_name_button.clicked.connect(
            lambda: subprocess.Popen(r'explorer /select,"{}"'.format(os.path.join(data.user_mc_path, mod['file_name']))))
        mod_slot_horizontal_layout.addWidget(mod_slot_name_button)

        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        mod_slot_horizontal_layout.addItem(spacer_item)

        # Добавление "Version" label
        mod_slot_version_label = QtWidgets.QLabel(mod_slot)
        mod_slot_version_label.setStyleSheet("border: none;")
        mod_slot_version_label.setObjectName("mod_slot_1_version_label")
        mod_slot_version_label.setText(mod['version'])  # Присвиевание версии
        mod_slot_horizontal_layout.addWidget(mod_slot_version_label)

        # Добавление "Update" button
        if mod['download_link']:
            mod_slot_version_label.setText('{0} -> {1}'.format(mod['version'], mod['new_version']))

            mod_slot_update_button = QtWidgets.QPushButton(mod_slot)
            mod_slot_update_button.setMinimumSize(QtCore.QSize(75, 20))
            mod_slot_update_button.setMaximumSize(QtCore.QSize(75, 16777215))
            mod_slot_update_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            mod_slot_update_button.setObjectName("mod_slot_1_update_button")
            mod_slot_update_button.setText("Update")

            mod_slot_update_button.clicked.connect(lambda: self.update_mod(mod))  # Подключение кнопки к функции
            mod_slot_horizontal_layout.addWidget(mod_slot_update_button)

        # Добавление "Delete" button
        mod_slot_delete_button = QtWidgets.QPushButton(mod_slot)
        mod_slot_delete_button.setMinimumSize(QtCore.QSize(75, 20))
        mod_slot_delete_button.setMaximumSize(QtCore.QSize(75, 16777215))
        mod_slot_delete_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        mod_slot_delete_button.setStyleSheet("color: rgb(255, 47, 50)")
        mod_slot_delete_button.setObjectName("mod_slot_1_delete_button")
        mod_slot_delete_button.setText("Delete")
        mod_slot_delete_button.clicked.connect(lambda: self.delete_mod(mod))  # Подключение кнопки к функции
        mod_slot_horizontal_layout.addWidget(mod_slot_delete_button)

        return mod_slot

    def apply_button_pressed(self):
        self.stop_threads = True

        data.console_font = str(self.horizontal_slider.value())
        data.save_old_mods = self.save_check_box.isChecked()
        data.dark_mode = self.dark_check_box.isChecked()

        # Сохранение data.py
        save_data_py()

        self.apply_button.hide()

        self.start_initial_thread()

    def reset_settings(self):
        reset_data_py()

        if data.user_mc_path:
            print_console('Minecraft Path set to:\n' + data.user_mc_path)

        self.horizontal_slider.setProperty("value", int(data.console_font))
        self.dark_check_box.setChecked(data.dark_mode)
        self.save_check_box.setChecked(data.save_old_mods)

        self.update_ui()

    def start_initial_thread(self):
        self.stop_threads = False
        threading.Thread(target=self.checker_and_updater).start()

    def checker_and_updater(self):
        while not self.stop_threads:
            # Автосохранение версии MC
            if self.mc_version_select_box.currentText() != data.user_mc_version:
                data.user_mc_version = self.mc_version_select_box.currentText()

                # Сохранение data.py
                save_data_py()

            # Изменение значения рядом со слайдером
            if self.font_size_label.text() != str(self.horizontal_slider.value()):
                # data.console_font = str(self.horizontal_slider.value())
                self.font_size_label.setText(str(self.horizontal_slider.value()))

                # Сохранение data.py
                save_data_py()

            # Пороверка изменения настроек и появление кнопки apply
            if self.save_check_box.isChecked() != data.save_old_mods:
                self.apply_button.show()
            elif self.dark_check_box.isChecked() != data.dark_mode:
                self.apply_button.show()
            elif str(self.horizontal_slider.value()) != data.console_font:
                self.apply_button.show()
            else:
                self.apply_button.hide()

            # Обновление консоли
            if self.console_text_edit.toPlainText() != data.console_text:
                self.console_text_edit.setPlainText(data.console_text)

            # Обновление прогресс бара
            if self.mods_count and self.mods_count != self.mods_done:
                try:
                    progress_bar_max_width = self.progress_bar_widget.width() - 10
                    self.progress_bar.setFixedWidth(progress_bar_max_width / self.mods_count * self.mods_done)
                except:
                    pass

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "Minecraft Mods Updater"))
        self.title.setText(_translate("main_window", "Minecraft Mods Updater"))
        self.program_version.setText(_translate("main_window", "v0.1"))
        self.mods_button.setText(_translate("main_window", "Mods"))
        self.console_button.setText(_translate("main_window", "Console"))
        self.settings_button.setText(_translate("main_window", "Settings"))
        self.mc_version_label.setText(_translate("main_window", "Your MC version"))
        self.refresh_button.setText(_translate("main_window", "Refresh"))
        self.update_all_button.setText(_translate("main_window", "Update all"))
        self.console_text_edit.setPlainText(_translate("main_window", "Console Text"))
        self.path_line_edit.setPlaceholderText(_translate("main_window", "Minecraft Path"))
        self.browse_button.setText(_translate("main_window", "Browse"))
        self.save_check_box.setText(_translate("main_window", "Save old mods"))
        self.dark_check_box.setText(_translate("main_window", "Dark Theme"))
        self.font_label.setText(_translate("main_window", "Console font size"))
        self.font_size_label.setText(_translate("main_window", "8"))
        self.default_button.setText(_translate("main_window", "Default"))
        self.apply_button.setText(_translate("main_window", "Apply"))


if __name__ == "__main__":
    # If data.py is not empty
    try:
        data.dark_mode
    except:
        reset_data_py()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ui = UiMainWindow()
    ui.setup_ui(MainWindow)
    ui.update_ui()
    ui.start_initial_thread()

    MainWindow.show()
    sys.exit(app.exec_())
