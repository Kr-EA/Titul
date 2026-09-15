**Titul Util**  
Графическое приложение для создания титульного листа Word из template.docx.  
**Использование**  
1. Откройте приложение и нажмите **Настройки**.  
2. Укажите ФИО, кафедру, год поступления, номер группы, ступень образования и количество лет академического отпуска. Группа рассчитывается автоматически, как в исходном main.py.  
3. Нажмите **Сохранить**. Новые значения по умолчанию действуют сразу. Явно введённые значения в основной форме имеют приоритет.  
4. Заполните название работы, дисциплину и преподавателя. Тема необязательна. Поддерживаются сокращения работ (ЛР1) и инициалы преподавателей.  
5. При необходимости выберите **Папка сохранения** и нажмите  **Создать лист**.  
Настройки читаются из config.json. При запуске из исходников изменяется файл рядом с titul_util.py. В установленном приложении при первом запуске создаётся отдельная копия конфига в пользовательской папке Qt AppConfigLocation:  
- Windows: %LOCALAPPDATA%\TitulUtil\TitulUtil\config.json.  
- macOS: ~/Library/Preferences/TitulUtil/TitulUtil/config.json.  
- Linux: ${XDG_CONFIG_HOME:-~/.config}/TitulUtil/TitulUtil/config.json.  
Обновление приложения не перезаписывает пользовательский конфиг. Шаблон, teachers.txt, faculties_cafedrals_shortcuts.json и исходный config.json включены в сборку. Включённый конфиг содержит текущие данные из проекта; для распространения среди других людей замените их перед сборкой.  
**Установка**  
Python на компьютере пользователя не требуется.  
- **macOS:** откройте TitulUtil-macos-arm64.dmg и перетащите TitulUtil.app в Applications. Эта сборка предназначена для Apple Silicon. Для Intel нужно выполнить сборку на Intel Mac. Пакет без Developer ID и notarization: macOS может потребовать разрешение запуска в настройках конфиденциальности и безопасности.  
- **Windows x64:** запустите TitulUtil-windows-x64-setup.exe. Установка в профиль пользователя, ярлык в меню «Пуск», удаление через стандартный список приложений. Установщик не подписан.  
- **Linux x64:** распакуйте TitulUtil-linux-x86_64.tar.gz, откройте терминал в распакованной папке и выполните sh install.sh. Приложение появится в меню. Удаление: удалите ~/.local/opt/titul-util и ${XDG_DATA_HOME:-~/.local/share}/applications/titul-util.desktop. Пользовательский конфиг сохраняется.  
Linux-сборка из CI рассчитана на Ubuntu 22.04+ и совместимые дистрибутивы с графической сессией; это не гарантия работы на любом Linux. Для Qt/X11 могут потребоваться пакеты libegl1 libopengl0 libxkbcommon-x11-0 libxcb-cursor0 (названия для Ubuntu).  
**Запуск из исходников**  
Требуется Python 3.10+ (сборка проверяется на 3.12).  
python -m pip install -r requirements.txt  
 python titul_util.py  
 python titul_util.py "/путь/к/папке"  
   
**Сборка установщиков**  
Собирать нужно на целевой ОС: [PyInstaller не является кросс-компилятором.](https://www.pyinstaller.org/en/stable/ "https://www.pyinstaller.org/en/stable/")  
python -m venv .venv-build  
 # macOS / Linux  
 source .venv-build/bin/activate  
 # Windows PowerShell: .venv-build\Scripts\Activate.ps1  
 python -m pip install -r requirements-build.txt  
 python -m unittest discover -s tests -v  
 python packaging/build.py  
   
На Windows предварительно установите [Inno Setup 6. На macOS используется системный hdiutil, на Linux создаётся архив с установочным скриптом. Результаты находятся в dist/installers/.](https://jrsoftware.org/isinfo.php "https://jrsoftware.org/isinfo.php")  
