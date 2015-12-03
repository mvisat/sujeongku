# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_highscore.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialog_highscore(object):
    def setupUi(self, dialog_highscore):
        dialog_highscore.setObjectName("dialog_highscore")
        dialog_highscore.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(dialog_highscore)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.text_highscore = QtWidgets.QTextEdit(dialog_highscore)
        self.text_highscore.setReadOnly(True)
        self.text_highscore.setObjectName("text_highscore")
        self.verticalLayout.addWidget(self.text_highscore)
        self.buttonBox = QtWidgets.QDialogButtonBox(dialog_highscore)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(dialog_highscore)
        self.buttonBox.accepted.connect(dialog_highscore.accept)
        self.buttonBox.rejected.connect(dialog_highscore.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog_highscore)

    def retranslateUi(self, dialog_highscore):
        _translate = QtCore.QCoreApplication.translate
        dialog_highscore.setWindowTitle(_translate("dialog_highscore", "Highscore"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog_highscore = QtWidgets.QDialog()
    ui = Ui_dialog_highscore()
    ui.setupUi(dialog_highscore)
    dialog_highscore.show()
    sys.exit(app.exec_())

