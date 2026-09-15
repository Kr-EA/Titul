import importlib.util
import os
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'titul_build', Path(__file__).resolve().parents[1] / 'packaging' / 'build.py'
)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class LinuxPackagingTests(unittest.TestCase):
    def test_archive_with_missing_or_lowercase_readme(self):
        for filename in (None, 'readme.md', 'README.md'):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'dist/TitulUtil').mkdir(parents=True)
                (root / 'dist/TitulUtil/TitulUtil').write_text('binary fixture')
                (root / 'packaging').mkdir()
                (root / 'packaging/install-linux.sh').write_text('#!/bin/sh\n')
                if filename:
                    (root / filename).write_text('Project instructions', encoding='utf-8')
                with patch.object(build, 'ROOT', root), patch.object(build, 'DIST', root / 'dist'), patch.object(build.platform, 'system', return_value='Linux'), patch.object(build.platform, 'machine', return_value='x86_64'), patch.object(build, 'run'):
                    build.main()
                with tarfile.open(root / 'dist/installers/TitulUtil-linux-x86_64.tar.gz') as archive:
                    prefix = 'TitulUtil-linux-x86_64/'
                    readme = archive.extractfile(prefix + 'README.md').read().decode('utf-8')
                    self.assertIn('Project instructions' if filename else 'sh install.sh', readme)
                    installer = archive.getmember(prefix + 'install.sh')
                    self.assertTrue(installer.isfile())
                    # Mocking platform.system() does not change host filesystem permissions.
                    # Windows chmod cannot set POSIX executable bits.
                    if os.name == 'posix':
                        self.assertEqual(installer.mode & 0o777, 0o755)
                    self.assertIn(prefix + 'TitulUtil/TitulUtil', archive.getnames())
