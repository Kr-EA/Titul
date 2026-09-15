#!/bin/sh
set -eu
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
install_dir="$HOME/.local/opt/titul-util"
applications_dir="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$install_dir" "$applications_dir"
cp -R "$source_dir/TitulUtil/." "$install_dir/"
chmod +x "$install_dir/TitulUtil"
# Escape the executable path according to the desktop-entry Exec syntax.
exec_path=$(printf '%s' "$install_dir/TitulUtil" | sed 's/\\/\\\\/g; s/"/\\"/g; s/`/\\`/g; s/\$/\\$/g; s/%/%%/g')
cat > "$applications_dir/titul-util.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Titul Util
Comment=Создание титульного листа
Exec="$exec_path"
Terminal=false
Categories=Office;
DESKTOP
printf 'Titul Util установлен. Запустите его из меню приложений или: %s\n' "$install_dir/TitulUtil"
