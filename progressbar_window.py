from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import data
import subprocess
import os
from time import sleep
import threading

# noinspection PyAttributeOutsideInit

mods_from_main_py = ['adsgf.jar', 'asdfgafdg.jar', '34rtdsf.jar', '4sedfadsfasdf.jar',
                     'adsfava .jar', 'asd dasfasd fasdasd.jar','supermsa fsad fods123.jar', 'teste asds fdstets.jar',
                     'sdaf sadf saf.jar', 'asdasad fdafasddasd.jar', ' adfsasasdfsdff.jar', 'asd asad.jar']


class UiMainWindow(object):
    def __init__(self):
        self.mods = {}
        self.progress_bar_size = 0
        self.window_size = 0


    def setup_ui(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(0, 0)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
        main_window.setSizePolicy(size_policy)
        main_window.setMinimumSize(QtCore.QSize(0, 0))
        main_window.setMaximumSize(QtCore.QSize(16777215, 16777215))
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
        self.mods_widget.setStyleSheet("")
        self.mods_widget.setObjectName("mods_widget")
        self.mods_widget_vertical_layout = QtWidgets.QVBoxLayout(self.mods_widget)
        self.mods_widget_vertical_layout.setContentsMargins(0, 6, 0, 6)
        self.mods_widget_vertical_layout.setSpacing(2)
        self.mods_widget_vertical_layout.setObjectName("mods_widget_vertical_layout")

        # main_widget -> inside_widget -> mods_widget -> mod_slot_wait

        # self.mod_slot_wait = QtWidgets.QWidget(self.mods_widget)
        # size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        # size_policy.setHeightForWidth(self.mod_slot_wait.sizePolicy().hasHeightForWidth())
        # self.mod_slot_wait.setSizePolicy(size_policy)
        # self.mod_slot_wait.setObjectName("mod_slot_wait")
        # self.mod_slot_wait_horizontal_layout = QtWidgets.QHBoxLayout(self.mod_slot_wait)
        # self.mod_slot_wait_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        # self.mod_slot_wait_horizontal_layout.setObjectName("mod_slot_wait_horizontal_layout")
        #
        # self.mod_wait = QtWidgets.QPushButton(self.mod_slot_wait)
        # self.mod_wait.setMinimumSize(QtCore.QSize(0, 10))
        # self.mod_wait.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.mod_wait.setStyleSheet("* {\n"
        #                             "    background-color: none;\n"
        #                             "    border: none;\n"
        #                             "    color: rgb(70, 70, 70);\n"
        #                             "}")
        # self.mod_wait.setObjectName("mod_wait")
        # self.mod_slot_wait_horizontal_layout.addWidget(self.mod_wait)
        #
        # self.mods_widget_vertical_layout.addWidget(self.mod_slot_wait)
        #
        # # main_widget -> inside_widget -> mods_widget -> mod_slot_processing
        #
        # self.mod_slot_processing = QtWidgets.QWidget(self.mods_widget)
        # size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        # size_policy.setHeightForWidth(self.mod_slot_processing.sizePolicy().hasHeightForWidth())
        # self.mod_slot_processing.setSizePolicy(size_policy)
        # self.mod_slot_processing.setObjectName("mod_slot_processing")
        # self.mod_slot_processing_horizontal_layout = QtWidgets.QHBoxLayout(self.mod_slot_processing)
        # self.mod_slot_processing_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        # self.mod_slot_processing_horizontal_layout.setObjectName("mod_slot_processing_horizontal_layout")
        #
        # self.mod_processing = QtWidgets.QPushButton(self.mod_slot_processing)
        # self.mod_processing.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.mod_processing.setStyleSheet("* {\n"
        #                                   "    background-color: none;\n"
        #                                   "    border: none;\n"
        #                                   "    color: white;\n"
        #                                   "}\n"
        #                                   "\n"
        #                                   "*:hover {\n"
        #                                   "    background-color: none;\n"
        #                                   "    color: rgb(165, 165, 165)\n"
        #                                   "}")
        # self.mod_processing.setObjectName("mod_processing")
        # self.mod_slot_processing_horizontal_layout.addWidget(self.mod_processing)
        #
        # self.mods_widget_vertical_layout.addWidget(self.mod_slot_processing)
        #
        # # main_widget -> inside_widget -> mods_widget -> mod_slot_accepted
        #
        # self.mod_slot_accepted = QtWidgets.QWidget(self.mods_widget)
        # size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        # size_policy.setHeightForWidth(self.mod_slot_accepted.sizePolicy().hasHeightForWidth())
        # self.mod_slot_accepted.setSizePolicy(size_policy)
        # self.mod_slot_accepted.setObjectName("mod_slot_accepted")
        # self.mod_slot_accepted_horizontal_layout = QtWidgets.QHBoxLayout(self.mod_slot_accepted)
        # self.mod_slot_accepted_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        # self.mod_slot_accepted_horizontal_layout.setObjectName("mod_slot_accepted_horizontal_layout")
        #
        # self.tick_label = QtWidgets.QLabel(self.mod_slot_accepted)
        # self.tick_label.setStyleSheet("color: rgb(0, 255, 0)")
        # self.tick_label.setObjectName("tick_label")
        # self.mod_slot_accepted_horizontal_layout.addWidget(self.tick_label)
        #
        # self.mod_accepted = QtWidgets.QPushButton(self.mod_slot_accepted)
        # self.mod_accepted.setMinimumSize(QtCore.QSize(0, 10))
        # self.mod_accepted.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.mod_accepted.setStyleSheet("* {\n"
        #                                 "    background-color: none;\n"
        #                                 "    border: none;\n"
        #                                 "    color: white;\n"
        #                                 "}\n"
        #                                 "\n"
        #                                 "*:hover {\n"
        #                                 "    background-color: none;\n"
        #                                 "    color: rgb(165, 165, 165)\n"
        #                                 "}")
        # self.mod_accepted.setObjectName("mod_accepted")
        # self.mod_slot_accepted_horizontal_layout.addWidget(self.mod_accepted)
        #
        # self.mods_widget_vertical_layout.addWidget(self.mod_slot_accepted)
        #
        # # main_widget -> inside_widget -> mods_widget -> mod_slot_denied
        #
        # self.mod_slot_denied = QtWidgets.QWidget(self.mods_widget)
        # size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        # size_policy.setHeightForWidth(self.mod_slot_denied.sizePolicy().hasHeightForWidth())
        # self.mod_slot_denied.setSizePolicy(size_policy)
        # self.mod_slot_denied.setObjectName("mod_slot_denied")
        # self.mod_slot_denied_horizontal_layout = QtWidgets.QHBoxLayout(self.mod_slot_denied)
        # self.mod_slot_denied_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        # self.mod_slot_denied_horizontal_layout.setObjectName("mod_slot_denied_horizontal_layout")
        #
        # self.cross_label = QtWidgets.QLabel(self.mod_slot_denied)
        # self.cross_label.setStyleSheet("color: rgb(255, 47, 50);")
        # self.cross_label.setObjectName("cross_label")
        # self.mod_slot_denied_horizontal_layout.addWidget(self.cross_label)
        #
        # self.mod_denied = QtWidgets.QPushButton(self.mod_slot_denied)
        # self.mod_denied.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.mod_denied.setStyleSheet("* {\n"
        #                               "    background-color: none;\n"
        #                               "    border: none;\n"
        #                               "    color: white;\n"
        #                               "}\n"
        #                               "\n"
        #                               "*:hover {\n"
        #                               "    background-color: none;\n"
        #                               "    color: rgb(165, 165, 165)\n"
        #                               "}")
        # self.mod_denied.setObjectName("mod_denied")
        # self.mod_slot_denied_horizontal_layout.addWidget(self.mod_denied)
        #
        # self.mods_widget_vertical_layout.addWidget(self.mod_slot_denied)
        #
        # spacer_item1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.mods_widget_vertical_layout.addItem(spacer_item1)

        self.inside_widget_horizontal_layout.addWidget(self.mods_widget)

        spacer_item2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.inside_widget_horizontal_layout.addItem(spacer_item2)

        self.main_widget_vertical_layout.addWidget(self.inside_widget)

        main_window.setCentralWidget(self.main_widget)

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def init_mods(self, mods):
        self.progress_bar_size = len(mods) * 15

        self.progress_bar_widget.setMinimumSize(QtCore.QSize(22, self.progress_bar_size + 13))
        self.window.setMaximumSize(QtCore.QSize(16777215, self.progress_bar_size + 13))

        self.progress_bar.hide()
        self.progress_bar.setMinimumSize(QtCore.QSize(10, 0))

        self.progress_bar.setMinimumSize(QtCore.QSize(10, 0))

        for mod in mods:
            slot = self.create_slot(mod)

            self.mods[mod] = slot

            self.mods_widget_vertical_layout.addWidget(slot)

        spacer_item1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mods_widget_vertical_layout.addItem(spacer_item1)

    def create_slot(self, mod):
        mod_slot = QtWidgets.QWidget(self.mods_widget)
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

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "MainWindow"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ui = UiMainWindow()
    ui.setup_ui(MainWindow)

    ui.init_mods(mods_from_main_py)

    for i in range(12):
        ui.activate_slot(mods_from_main_py[i])
        ui.accept_slot(mods_from_main_py[i])

    MainWindow.show()
    sys.exit(app.exec_())
