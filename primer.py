# primer.py
import sys
import os
import random

from vichesleniya import EquationGenerator

from resh_prim import Ui_mainwindow_1
from PyQt5 import QtCore, QtGui, QtWidgets ,uic 

class primer(QtWidgets.QMainWindow, Ui_mainwindow_1):
    def __init__(self, rezh, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.label_5.hide()
        self.parent = parent
        self.re = rezh
        self.label_4.hide()
        self.showFullScreen()
        self.pushButton_2.clicked.connect(self.exit)
        self.pushButton.clicked.connect(self.prov_resh)
        self.pushButton_4.clicked.connect(self.start)
        
        self.correct_answers = 0
        self.total_attempts = 0
        
        self.label_3.hide()
        self.pushButton_4.show()
        
        self.start()

    def start(self):
        generator = EquationGenerator()
        self.lineEdit.clear()
        self.lineEdit.setFocus() 
        self.rezh = self.re
        equation, steps, answer = generator.generate_from_extended_mode(self.rezh)
        self.answer = answer
        print(f"Уравнение: {equation}, Ответ: {answer}")
        self.label.setText(str(equation))

    def prov_resh(self):
        otvet = self.lineEdit.text()
        
        try:
            otvet = int(otvet)
        except ValueError:
            try:
                otvet = float(otvet)
            except ValueError:
                self.show_message('!НЕ ЧИСЛО! Введите число', '#3498db')
                self.lineEdit.clear()
                self.lineEdit.setFocus()
                return
        
        self.total_attempts += 1
        
        if otvet == self.answer:
            self.show_message('!ВЕРНО!', '#2ecc71')
            self.correct_answers += 1
        else:
            self.show_message(f'!НЕВЕРНО! Правильный ответ: {self.answer}', '#e74c3c')
        self.start()

    def show_message(self, text, color):
        self.label_3.show()
        self.label_3.setText(text)
        self.label_3.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {color};
                font-size: 25px;
                font-weight: bold;
                border: none;
                text-align: center;
            }}
        """)


    def exit(self):
        if self.parent:
            self.parent.show()
        self.close()

    def closeEvent(self, event):
        if self.parent:
            self.parent.show()
        event.accept()