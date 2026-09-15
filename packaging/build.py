"""Build on the target OS: python packaging/build.py."""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def main():
    system = platform.system()
    if system not in ("Windows", "Darwin", "Linux"):
        raise SystemExit(f"Unsupported platform: {system}")
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
               "--windowed", "--name", "TitulUtil", "--onedir",
               "--collect-all", "docxcompose", "--collect-all", "docxtpl",
               "--osx-bundle-identifier", "org.titulutil.app"]
    for name in ("config.json", "teachers.txt", "faculties_cafedrals_shortcuts.json", "template.docx"):
        command.extend(["--add-data", f"{ROOT / name}{os.pathsep}."])
    command.append(str(ROOT / "titul_util.py"))
    run(*command)
    installers = DIST / "installers"
    installers.mkdir(parents=True, exist_ok=True)
    arch = platform.machine().lower()
    if system == "Darwin":
        stage = ROOT / "build" / "dmg"
        if stage.exists():
            shutil.rmtree(stage)
        stage.mkdir(parents=True)
        shutil.copytree(DIST / "TitulUtil.app", stage / "TitulUtil.app", symlinks=True)
        (stage / "Applications").symlink_to("/Applications")
        run("hdiutil", "create", "-volname", "Titul Util", "-srcfolder", stage,
            "-ov", "-format", "UDZO", installers / f"TitulUtil-macos-{arch}.dmg")
    elif system == "Windows":
        compiler = shutil.which("ISCC") or shutil.which("ISCC.exe")
        if compiler is None:
            for env in ("ProgramFiles(x86)", "ProgramFiles"):
                candidate = Path(os.environ.get(env, "C:/Program Files (x86)")) / "Inno Setup 6" / "ISCC.exe"
                if candidate.is_file():
                    compiler = str(candidate)
                    break
        if compiler is None:
            raise SystemExit("Install Inno Setup 6, then run this script again.")
        run(compiler, ROOT / "packaging" / "windows.iss")
    else:
        stage = ROOT / "build" / f"TitulUtil-linux-{arch}"
        if stage.exists():
            shutil.rmtree(stage)
        stage.mkdir(parents=True)
        shutil.copytree(DIST / "TitulUtil", stage / "TitulUtil", symlinks=True)
        shutil.copy2(ROOT / "packaging" / "install-linux.sh", stage / "install.sh")
        (stage / "install.sh").chmod(0o755)
        readme = next((path for path in ROOT.iterdir()
                       if path.is_file() and path.name.lower() == "readme.md"), None)
        if readme is not None:
            shutil.copy2(readme, stage / "README.md")
        else:
            (stage / "README.md").write_text(
                "# Titul Util\n\n"
                "Распакуйте архив и выполните `sh install.sh`.\n"
                "Приложение появится в меню приложений.\n",
                encoding="utf-8",
            )
        shutil.make_archive(str(installers / stage.name), "gztar", stage.parent, stage.name)
    print(f"Installers: {installers}")


if __name__ == "__main__":
    main()
