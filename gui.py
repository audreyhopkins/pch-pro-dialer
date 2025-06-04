from PyQt5 import QtWidgets, QtGui
import pandas as pd
import os
from campaign_runner import start_campaign

def run_gui():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QWidget()
    window.setWindowTitle("PCH PRO DIALER")
    window.setFixedSize(600, 400)

    layout = QtWidgets.QVBoxLayout()

    label = QtWidgets.QLabel("Upload Contact CSV to Start Campaign")
    label.setFont(QtGui.QFont("Arial", 14))
    layout.addWidget(label)

    table = QtWidgets.QTableWidget()
    layout.addWidget(table)

    def load_csv():
        path, _ = QtWidgets.QFileDialog.getOpenFileName(window, "Open CSV", "", "CSV Files (*.csv)")
        if path:
            df = pd.read_csv(path)
            table.setRowCount(len(df))
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)
            for i, row in df.iterrows():
                for j, value in enumerate(row):
                    table.setItem(i, j, QtWidgets.QTableWidgetItem(str(value)))
            start_campaign(path)

    button = QtWidgets.QPushButton("Upload & Start")
    button.clicked.connect(load_csv)
    layout.addWidget(button)

    window.setLayout(layout)
    window.show()
    app.exec_()
