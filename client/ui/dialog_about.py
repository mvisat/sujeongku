# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_about.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialog_about(object):
    def setupUi(self, dialog_about):
        dialog_about.setObjectName("dialog_about")
        dialog_about.resize(518, 384)
        self.verticalLayout = QtWidgets.QVBoxLayout(dialog_about)
        self.verticalLayout.setContentsMargins(9, 0, 9, 9)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image_sujeong = QtWidgets.QLabel(dialog_about)
        self.image_sujeong.setText("")
        self.image_sujeong.setPixmap(QtGui.QPixmap(":/image/sujeongku.png"))
        self.image_sujeong.setScaledContents(False)
        self.image_sujeong.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.image_sujeong.setObjectName("image_sujeong")
        self.verticalLayout.addWidget(self.image_sujeong)
        self.buttonBox = QtWidgets.QDialogButtonBox(dialog_about)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dialog_about)
        self.buttonBox.accepted.connect(dialog_about.accept)
        self.buttonBox.rejected.connect(dialog_about.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog_about)

    def retranslateUi(self, dialog_about):
        _translate = QtCore.QCoreApplication.translate
        dialog_about.setWindowTitle(_translate("dialog_about", "About Sujeongku <3"))

from client.ui import resource_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog_about = QtWidgets.QDialog()
    ui = Ui_dialog_about()
    ui.setupUi(dialog_about)
    dialog_about.show()
    sys.exit(app.exec_())

