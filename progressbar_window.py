from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import data
import subprocess
import os
from time import sleep
import threading

# noinspection PyAttributeOutsideInit

mods_from_main_py = ['adsgf.jar']


class UiProgressBarWindow(object):
    def __init__(self):
        self.mods = {}
        self.progress_bar_size = 0
        self.window_size = 0

    def setup_ui(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(0, 0)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
        main_window.setSizePolicy(size_policy)
        main_window.setMinimumSize(QtCore.QSize(0, 0))
        main_window.setMaximumSize(QtCore.QSize(16777215, 16777215))
        main_window.setWindowTitle('Updating...')
        self.window = main_window

        main_window.setStyleSheet("#main_widget {\n"
                                  "    border-radius: 0px;\n"
                                  "    background-color: rgb(50, 50, 50);\n"
                                  "}\n"
                                  "\n"
                                  ".QWidget {\n"
                                  "    background-color: rgb(37, 37, 37);\n"
                                  "    border-radius:10px;\n"
                                  "}\n"
                                  "\n"
                                  ".QProgressBar {\n"
                                  "    background: #333;\n"
                                  "    border-radius: 13px;\n"
                                  "    padding: 3px;\n"
                                  "}\n"
                                  "\n"
                                  ".QProgressBar:after {\n"
                                  "    background: orange;\n"
                                  "}\n"
                                  "\n"
                                  "#progress_bar_widget {\n"
                                  "    background-color: rgb(50, 50, 50);\n"
                                  "    border-radius: 11px;\n"
                                  "}\n"
                                  "\n"
                                  "#progress_bar {\n"
                                  "    background-color: rgb(255, 47, 50);\n"
                                  "    border-radius: 5px;\n"
                                  "}")

        # main_widget

        self.main_widget = QtWidgets.QWidget(main_window)
        self.main_widget.setObjectName("main_widget")
        self.main_widget_vertical_layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.main_widget_vertical_layout.setContentsMargins(15, 15, 15, 15)
        self.main_widget_vertical_layout.setSpacing(15)
        self.main_widget_vertical_layout.setObjectName("verticalLayout_2")

        # main_widget -> inside_widget

        self.inside_widget = QtWidgets.QWidget(self.main_widget)
        self.inside_widget.setObjectName("inside_widget")
        self.inside_widget_horizontal_layout = QtWidgets.QHBoxLayout(self.inside_widget)
        self.inside_widget_horizontal_layout.setContentsMargins(15, 15, 15, 15)
        self.inside_widget_horizontal_layout.setSpacing(15)
        self.inside_widget_horizontal_layout.setObjectName("inside_widget_horizontal_layout")

        # main_widget -> inside_widget -> progress_bar_widget

        self.progress_bar_widget = QtWidgets.QFrame(self.inside_widget)
        self.progress_bar_widget.setMinimumSize(QtCore.QSize(22, 0))
        self.progress_bar_widget.setMaximumSize(QtCore.QSize(22, 16777215))
        self.progress_bar_widget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.progress_bar_widget.setFrameShadow(QtWidgets.QFrame.Raised)
        self.progress_bar_widget.setObjectName("progress_bar_widget")
        self.progress_bar_widget_vertical_layout = QtWidgets.QVBoxLayout(self.progress_bar_widget)
        self.progress_bar_widget_vertical_layout.setContentsMargins(6, 6, 6, 6)
        self.progress_bar_widget_vertical_layout.setSpacing(0)
        self.progress_bar_widget_vertical_layout.setObjectName("progress_bar_widget_vertical_layout")

        # main_widget -> inside_widget -> progress_bar_widget -> progress_bar

        self.progress_bar = QtWidgets.QWidget(self.progress_bar_widget)
        self.progress_bar.setMinimumSize(QtCore.QSize(10, 0))
        self.progress_bar.setMaximumSize(QtCore.QSize(10, 16777215))
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar_vertical_layout = QtWidgets.QVBoxLayout(self.progress_bar)
        self.progress_bar_vertical_layout.setObjectName("progress_bar_vertical_layout")

        self.nothing_frame = QtWidgets.QFrame(self.progress_bar)
        self.nothing_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.nothing_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.nothing_frame.setObjectName("nothing_frame")
        self.progress_bar_vertical_layout.addWidget(self.nothing_frame)

        self.progress_bar_widget_vertical_layout.addWidget(self.progress_bar)

        spacer_item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.progress_bar_widget_vertical_layout.addItem(spacer_item)

        self.inside_widget_horizontal_layout.addWidget(self.progress_bar_widget)

        # main_widget -> inside_widget -> mods_widget

        self.mods_widget = QtWidgets.QWidget(self.inside_widget)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.mods_widget.sizePolicy().hasHeightForWidth())
        self.mods_widget.setSizePolicy(size_policy)
        self.mods_widget.setStyleSheet("background-color: red")
        self.mods_widget.setObjectName("mods_widget")
        self.mods_widget_vertical_layout = QtWidgets.QVBoxLayout(self.mods_widget)
        self.mods_widget_vertical_layout.setContentsMargins(0, 6, 0, 6)
        self.mods_widget_vertical_layout.setSpacing(2)
        self.mods_widget_vertical_layout.setObjectName("mods_widget_vertical_layout")

        self.inside_widget_horizontal_layout.addWidget(self.mods_widget)

        spacer_item2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.inside_widget_horizontal_layout.addItem(spacer_item2)

        self.main_widget_vertical_layout.addWidget(self.inside_widget)

        main_window.setCentralWidget(self.main_widget)

        QtCore.QMetaObject.connectSlotsByName(main_window)

    def init_mods(self, mods):
        self.progress_bar_size = len(mods) * 15

        self.progress_bar_widget.setMinimumSize(QtCore.QSize(22, self.progress_bar_size + 13))

        self.window.setMaximumSize(QtCore.QSize(16777215, self.window.height()))

        self.progress_bar.hide()
        self.progress_bar.setMinimumSize(QtCore.QSize(10, 0))

        for mod in mods:
            slot = self.create_slot(mod)

            self.mods[mod] = slot

            self.mods_widget_vertical_layout.addWidget(slot)

        spacer_item1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mods_widget_vertical_layout.addItem(spacer_item1)

    def create_slot(self, mod):
        print(self.mods_widget.children())

        mod_slot = QtWidgets.QWidget(self.mods_widget)
        print(self.mods_widget.children())

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(mod_slot.sizePolicy().hasHeightForWidth())
        mod_slot.setSizePolicy(size_policy)
        mod_slot.setObjectName("mod_slot")
        mod_slot_horizontal_layout = QtWidgets.QHBoxLayout(mod_slot)
        mod_slot_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        mod_slot_horizontal_layout.setObjectName("mod_slot_horizontal_layout")

        button = QtWidgets.QPushButton(mod_slot)
        button.setMinimumSize(QtCore.QSize(0, 10))
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setStyleSheet("* {\n"
                             "    background-color: none;\n"
                             "    border: none;\n"
                             "    color: rgb(70, 70, 70);\n"
                             "}")
        button.setObjectName("button")
        button.setText(mod)
        button.clicked.connect(
            lambda: subprocess.Popen(r'explorer /select,"{}"'.format(os.path.join(data.user_mc_path, mod))))
        mod_slot_horizontal_layout.addWidget(button)

        return mod_slot

    def activate_slot(self, mod):
        slot = self.mods[mod]
        button = slot.children()[1]
        button.setStyleSheet("* {\n"
                             "    background-color: none;\n"
                             "    border: none;\n"
                             "    color: white;\n"
                             "}\n"
                             "\n"
                             "*:hover {\n"
                             "    background-color: none;\n"
                             "    color: rgb(165, 165, 165)\n"
                             "}")

    def accept_slot(self, mod):
        self.progress_bar.show()
        self.progress_bar.setMinimumSize(QtCore.QSize(10, self.progress_bar.minimumHeight() + 15))

        slot = self.mods[mod]
        layout = slot.children()[0]
        tick = QtWidgets.QLabel(slot)
        tick.setStyleSheet("color: rgb(0, 255, 0)")
        tick.setObjectName("tick")
        tick.setText('✔')
        layout.insertWidget(0, tick)

    def deny_slot(self, mod):
        self.progress_bar.show()
        if self.progress_bar.minimumHeight() >= 30:
            self.progress_bar.setMinimumSize(QtCore.QSize(10, self.progress_bar.height() + 15))

        slot = self.mods[mod]
        layout = slot.children()[0]
        cross = QtWidgets.QLabel(slot)
        cross.setStyleSheet("color: rgb(255, 47, 50)")
        cross.setObjectName("cross")
        cross.setText('✖')
        layout.insertWidget(0, cross)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ui = UiProgressBarWindow()
    ui.setup_ui(MainWindow)
    MainWindow.show()

    ui.init_mods(mods_from_main_py)

    # ui.activate_slot(mods_from_main_py[i])
    # ui.accept_slot(mods_from_main_py[i])

    sys.exit(app.exec_())
