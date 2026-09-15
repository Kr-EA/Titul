from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QApplication, QVBoxLayout, QHBoxLayout, QWidget
import sys
import subprocess
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Titul cmd popup")
        self.setGeometry(100, 100, 600, 400)
        
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)

        formLayout = QVBoxLayout(mainWidget)
        
        self.fields = [
            "Кафедра",
            "Группа",
            "Имя работы (с номером или без)",
            "Тема работы",
            "Дисциплина",
            "Ваша Фамилия И.О.",
            "Фамилия И.О. препода",
            "Год обучения",
            "Название выходного файла"
        ]

        self.inputs = []

        for field in self.fields:
            field_input = QHBoxLayout()
            field_input_label = QLabel(text=f"{field}")
            field_input_edit = QLineEdit()
            field_input_edit.setPlaceholderText("Оставьте пустым для значения по умолчанию" if field in ['Ваша Фамилия И.О.', 'Год обучения', 'Группа', 'Название выходного файла'] else 'Введите значение')
            field_input.addWidget(field_input_label)
            field_input.addWidget(field_input_edit)
            self.inputs.append([field_input_label, field_input_edit])
            formLayout.addLayout(field_input)

        submit_button = QPushButton()
        submit_button.setText("Ok")
        
        cancel_button = QPushButton()
        cancel_button.setText("Cancel")

        window_controlls = QHBoxLayout()
        window_controlls.addWidget(submit_button)
        window_controlls.addWidget(cancel_button)
        
        formLayout.addLayout(window_controlls)

        cancel_button.clicked.connect(lambda: sys.exit())
        submit_button.clicked.connect(lambda: self.parse_form_data())

    def parse_form_data(self):
        self.data = {_f: "" for _f in self.fields}
        for field in self.inputs:
            self.data[field[0].text()] = field[1].text()
        if len(sys.argv) == 2:
            path = sys.argv[1]
            subprocess.run(["zsh", "-i", "-c", f"titul \"{Path(path)}\" \"{self.data}\""])
            sys.exit()
        else:
            sys.exit()




if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())
