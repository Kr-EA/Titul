#!/usr/bin/env python3
"""Графическое создание титульного листа: python3 titul_util.py [папка]."""

import argparse
import json
import os
import shutil
import tempfile
import re
import sys
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate
from PyQt6.QtCore import QStandardPaths
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QComboBox, QSpinBox, QFileDialog, QLabel,
    QApplication, QFormLayout, QHBoxLayout, QInputDialog, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)


RESOURCE_DIR = Path(__file__).resolve().parent
FIELDS = {
    "caf": "Кафедра",
    "group": "Группа",
    "w_title": "Имя работы (с номером или без)",
    "theme": "Тема работы",
    "subject": "Дисциплина",
    "author": "Ваша Фамилия И.О.",
    "tutor": "Фамилия И.О. преподавателя",
    "year": "Год обучения",
    "output_file": "Название выходного файла",
}


class TitulGenerator:
    def __init__(self, resource_dir=RESOURCE_DIR, config_path=None):
        self.resource_dir = Path(resource_dir)
        if config_path is None:
            if getattr(sys, "frozen", False):
                config_path = Path(QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.AppConfigLocation
                )) / "config.json"
            else:
                config_path = self.resource_dir / "config.json"
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.resource_dir / "config.json", self.config_path)
        with self.config_path.open(encoding="utf-8") as source:
            config = json.load(source)
        with (self.resource_dir / "faculties_cafedrals_shortcuts.json").open(
            encoding="utf-8"
        ) as source:
            self.reference = json.load(source)

        self.apply_config(config)
        self.teachers = {}
        with (self.resource_dir / "teachers.txt").open(encoding="utf-8") as source:
            for line in source:
                parts = line.split()
                if len(parts) < 3:
                    continue
                surname, first, patronymic = parts[:3]
                initials = (surname[0] + first[0] + patronymic[0]).upper()
                name = f"{surname} {first[0]}.{patronymic[0]}."
                candidates = self.teachers.setdefault(initials, [])
                if name not in candidates:
                    candidates.append(name)

    def validate_config(self, config):
        result = dict(config)
        for key in ("me", "my_caf", "degree"):
            if not isinstance(result.get(key), str) or not result[key].strip():
                raise ValueError(f"Настройка {key} не должна быть пустой.")
            result[key] = result[key].strip()
        result["my_caf"] = result["my_caf"].upper()
        if result["my_caf"] not in self.reference["cafedrals"]:
            raise ValueError("Выберите кафедру из справочника.")
        for key, minimum, maximum in (
            ("year_of_arrive", 1900, datetime.now().year),
            ("AH_count", 0, 100), ("group_num", 1, 99),
        ):
            value = result.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
                raise ValueError(f"Настройка {key}: введите целое число от {minimum} до {maximum}.")
        if result["AH_count"] > datetime.now().year - result["year_of_arrive"]:
            raise ValueError("Академический отпуск не может превышать срок обучения.")
        return result

    def apply_config(self, config):
        config = self.validate_config(config)
        self.config = config
        now = datetime.now()
        semester = (
            (now.year - int(config["year_of_arrive"]) - int(config["AH_count"])) * 2
            + (1 if now.month >= 9 else 0)
        )
        self.defaults = {
            "author": config["me"],
            "group": f'{config["my_caf"]}-{semester}{config["group_num"]}{config["degree"][0]}',
            "year": str(now.year),
        }
        self.defaults["caf"] = config["my_caf"]

    def save_config(self, config):
        config = self.validate_config(config)
        # Замена целого файла не оставляет обрезанный JSON при ошибке записи.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.config_path.parent,
                prefix=".config-", suffix=".tmp", delete=False,
            ) as source:
                temporary = Path(source.name)
                json.dump(config, source, ensure_ascii=False, indent=4)
                source.write("\n")
                source.flush()
                os.fsync(source.fileno())
            os.replace(temporary, self.config_path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        self.apply_config(config)

    def prepare_data(self, raw_data):
        data = {key: raw_data.get(key, "").strip() for key in FIELDS}
        for key, value in self.defaults.items():
            if not data[key]:
                data[key] = value
        for key in ("caf", "w_title", "subject", "author", "tutor", "group", "year"):
            if not data[key]:
                raise ValueError(f'Заполните поле «{FIELDS[key]}».')

        department = data["caf"].upper()
        match = re.match(r"^[^\d]+", department)
        faculty = match.group() if match else ""
        if department not in self.reference["cafedrals"]:
            raise ValueError(f"Неизвестная кафедра: {department}.")
        if faculty not in self.reference["faculties"]:
            raise ValueError(f"Неизвестный факультет: {faculty}.")
        data["faculty"] = f'{faculty} "{self.reference["faculties"][faculty]}"'
        data["caf"] = f'{department} "{self.reference["cafedrals"][department]}"'

        if data["theme"]:
            data["theme"] = f'«{data["theme"].strip("«»")}»'
        shortcut = data["w_title"][:2].upper()
        if shortcut in self.reference["titles_shortcuts"]:
            number = data["w_title"][2:].replace("№", "").strip()
            data["w_title"] = self.reference["titles_shortcuts"][shortcut]
            if number:
                data["w_title"] += f" №{number}"
        return data

    def output_path(self, data, output_dir):
        filename = data["output_file"]
        if not filename:
            words = data["subject"].split()
            subject = "".join(word[0] for word in words).upper() if len(words) > 1 else words[0]
            title = "".join(word[0] for word in data["w_title"].replace("№", "").split()).upper()
            filename = f'{data["author"].replace(" ", "_")}_{data["group"]}_{subject}_{title}_{data["year"]}г.docx'
            filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)
        elif re.search(r'[<>:"/\\|?*\x00-\x1f]', filename) or filename in (".", ".."):
            raise ValueError("Укажите имя файла без пути и символов <>:\"/\\|?*.")
        if not filename.lower().endswith(".docx"):
            filename += ".docx"
        directory = Path(output_dir).expanduser().resolve()
        if not directory.is_dir():
            raise ValueError(f"Папка для сохранения не существует: {directory}")
        return directory / filename

    def fill_template(self, data, output_path):
        document = DocxTemplate(self.resource_dir / "template.docx")
        document.render(data)
        document.save(output_path)


class SettingsDialog(QDialog):
    def __init__(self, generator, parent=None):
        super().__init__(parent)
        self.generator = generator
        self.setWindowTitle("Настройки")
        self.resize(540, 320)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        layout.addLayout(form)
        self.fields = {}
        labels = {
            "me": "Фамилия И.О.", "my_caf": "Кафедра",
            "year_of_arrive": "Год поступления", "group_num": "Номер группы",
            "degree": "Ступень образования", "AH_count": "Академический отпуск (лет)",
        }
        for key, label in labels.items():
            value = generator.config[key]
            if key in ("year_of_arrive", "group_num", "AH_count"):
                field = QSpinBox()
                field.setRange(1900 if key == "year_of_arrive" else (1 if key == "group_num" else 0),
                               datetime.now().year if key == "year_of_arrive" else (99 if key == "group_num" else 100))
                field.setValue(value)
            elif key in ("my_caf", "degree"):
                field = QComboBox()
                options = list(generator.reference["cafedrals"]) if key == "my_caf" else ["Бакалавр", "Магистр", "Специалист"]
                if value not in options:
                    options.append(value)
                field.addItems(options)
                field.setCurrentText(value)
            else:
                field = QLineEdit(value)
            self.fields[key] = field
            form.addRow(label, field)
        self.preview = QLabel()
        layout.addWidget(self.preview)
        for field in self.fields.values():
            signal = field.valueChanged if isinstance(field, QSpinBox) else (field.currentTextChanged if isinstance(field, QComboBox) else field.textChanged)
            signal.connect(self.update_preview)
        self.update_preview()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        config = dict(self.generator.config)
        for key, field in self.fields.items():
            config[key] = field.value() if isinstance(field, QSpinBox) else (field.currentText() if isinstance(field, QComboBox) else field.text())
        return config

    def update_preview(self):
        config = self.values()
        now = datetime.now()
        semester = (now.year - config["year_of_arrive"] - config["AH_count"]) * 2 + (now.month >= 9)
        self.preview.setText(f'Группа: {config["my_caf"]}-{semester}{config["group_num"]}{config["degree"][:1]}')

    def save(self):
        try:
            self.generator.save_config(self.values())
        except Exception as error:
            QMessageBox.critical(self, "Не удалось сохранить настройки", str(error))
            return
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, generator, output_dir):
        super().__init__()
        self.generator = generator
        self.output_dir = output_dir
        self.setWindowTitle("Создание титульного листа")
        self.resize(700, 420)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        layout.addLayout(form)
        self.inputs = {}
        for key, label in FIELDS.items():
            field = QLineEdit()
            if key in generator.defaults:
                field.setPlaceholderText(f"По умолчанию: {generator.defaults[key]}")
            elif key == "output_file":
                field.setPlaceholderText("Оставьте пустым для автоматического имени")
            elif key == "theme":
                field.setPlaceholderText("Необязательно")
            else:
                field.setPlaceholderText("Введите значение")
            self.inputs[key] = field
            form.addRow(label, field)
        buttons = QHBoxLayout()
        submit = QPushButton("Создать лист")
        submit.clicked.connect(self.create_document)
        cancel = QPushButton("Закрыть")
        cancel.clicked.connect(self.close)
        settings = QPushButton("Настройки")
        settings.clicked.connect(self.open_settings)
        folder = QPushButton("Папка сохранения")
        folder.clicked.connect(self.choose_output_dir)
        buttons.addWidget(settings)
        buttons.addWidget(folder)
        buttons.addWidget(submit)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)
        self.statusBar().showMessage(f"Папка сохранения: {output_dir}")

    def open_settings(self):
        if SettingsDialog(self.generator, self).exec() == QDialog.DialogCode.Accepted:
            for key, value in self.generator.defaults.items():
                self.inputs[key].setPlaceholderText(f"По умолчанию: {value}")

    def choose_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Папка сохранения", str(self.output_dir))
        if directory:
            self.output_dir = Path(directory)
            self.statusBar().showMessage(f"Папка сохранения: {directory}")

    def create_document(self):
        try:
            data = self.generator.prepare_data({key: field.text() for key, field in self.inputs.items()})
            candidates = self.generator.teachers.get(data["tutor"].upper(), [])
            if len(candidates) == 1:
                data["tutor"] = candidates[0]
            elif len(candidates) > 1:
                tutor, accepted = QInputDialog.getItem(
                    self, "Выбор преподавателя", "Выберите преподавателя:", candidates, 0, False
                )
                if not accepted:
                    return
                data["tutor"] = tutor
            output_path = self.generator.output_path(data, self.output_dir)
            if output_path.exists():
                answer = QMessageBox.question(
                    self, "Файл уже существует", f"Заменить файл?\n{output_path}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
            self.generator.fill_template(data, output_path)
        except Exception as error:
            QMessageBox.critical(self, "Не удалось создать лист", str(error))
            return
        QMessageBox.information(self, "Лист создан", f"Файл сохранён:\n{output_path}")


def main():
    parser = argparse.ArgumentParser(description="Создание титульного листа из template.docx")
    parser.add_argument("output_dir", nargs="?", default=None, help="Папка сохранения")
    args = parser.parse_args()
    app = QApplication([sys.argv[0]])
    app.setApplicationName("TitulUtil")
    app.setOrganizationName("TitulUtil")
    try:
        generator = TitulGenerator()
        default_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation) if getattr(sys, "frozen", False) else str(Path.cwd())
        output_dir = Path(args.output_dir or default_dir or Path.home()).expanduser().resolve()
        if args.output_dir is None and not output_dir.is_dir():
            output_dir = Path.home()
        if not output_dir.is_dir():
            raise ValueError(f"Папка для сохранения не существует: {output_dir}")
        window = MainWindow(generator, output_dir)
    except Exception as error:
        QMessageBox.critical(None, "Ошибка запуска", str(error))
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
