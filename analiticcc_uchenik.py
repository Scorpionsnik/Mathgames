import sys
import os
import shutil

from analitic_uchenik import Analitic_uchenik_window
from try_table import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

class Analitic_uchen(QtWidgets.QMainWindow, Analitic_uchenik_window):
	def __init__(self,dannie ,parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.setStyleSheet("""
			QMainWindow {
				background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
			}
			QFrame {
				background: rgba(255, 255, 255, 0.95);
				border-radius: 20px;
				border: 2px solid rgba(255, 255, 255, 0.3);
			}
			QLabel {
				color: red
			}
			QPushButton {
				background: #e74c3c; 
				color: white;
				border: none;
				border-radius: 15px;
				font-size: 18px;
				font-weight: bold;
				padding: 12px 25px;
			}
		""")
		self.centralWidget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.titleLabel.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.studentInfo.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setWindowTitle("АНАЛИТИКА")
		self.showFullScreen()
		self.parent_window = parent
		self.dannie = dannie
		self.backButton.clicked.connect(self.exit)
		self.analitic()

	def analitic(self):
		self.titleLabel.setStyleSheet("""QLabel {
				color: #C00000
			}""")
		self.studentInfo.setStyleSheet("""QLabel {
				color: #C00000
			}""")
		info = str(str(self.dannie[1]) + ' | ')
		cclass = find_student_in_classes(self.dannie[1])
		info = info + str(cclass)
		self.studentInfo.setText(info)
		grades = get_student_grades(self.dannie[1])
		gr = ''
		for i in range(0, len(grades)):
			if i < (len(grades)-1):
				gr = gr + str(grades[i]) + ', '
			else:
				gr = gr + str(grades[i])
		sr = 0
		for i in range(0, len(grades)):
			sr = sr + grades[i]
		try:
			sr = sr / (len(grades))
			sr = f'{sr:.1f}'
			if float(sr) > 4.5:
				ost = 5 - float(sr)
			else:
				ost = 4.5 - float(sr)
		except:
			sr = 'Нет выставленных оценок!'
			ost = 'Нет выставленных оценок!'
		self.progressValue.hide()
		self.progressLabel.hide()
		o5 = 0
		for i in range(0, len(grades)):
			if grades[i] == 5:
				o5 = o5 + 1
		o4 = 0
		for i in range(0, len(grades)):
			if grades[i] == 4:
				o4 = o4 + 1
		o3 = 0
		for i in range(0, len(grades)):
			if grades[i] == 3:
				o3 = o3 + 1
		o2 = 0
		for i in range(0, len(grades)):
			if grades[i] == 2:
				o2 = o2 + 1
		stats = get_student_statistics(self.dannie[1])
		if stats:
			print(f"Место в классе: {stats['place']} из {stats['total_students']}")
			print(f"Лучше {stats['better_than_percent']}% класса")
			print(f"Успеваемость: {stats['success_rate']}%")
			print(f"Средний балл: {stats['average_grade']}")

		self.avgGradeValue.setText(str(sr))
		self.fivesCount.setText(str(o5))
		self.foursCount.setText(str(o4))
		self.threesCount.setText(str(o3))
		self.label.setText(str(o2))
		self.successRate.setText(str(str(stats['success_rate']) + '%'))
		self.rankValue.setText(str(str(stats['place']) + ' место из ' + str(stats['total_students'])))
		self.rankText.setText(f"Вы лучше {stats['better_than_percent']}% класса")
		# self.progressValue.setText("+0.3 балла 📈")
		self.targetValue.setText(str('-' + str(ost)))
		self.gradesText.setText(gr)

	def exit(self):
		if self.parent_window:
			self.parent_window.show()
		self.close()