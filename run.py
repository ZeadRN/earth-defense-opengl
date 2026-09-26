"""Create the local environment, install the pinned dependency, and run the game."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)

def main():
    if sys.version_info < (3, 10):
        raise RuntimeError('Install Python 3.10 or newer from python.org.')
    python = ROOT / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    if not python.exists():
        print('Creating the project Python environment...', flush=True)
        run(sys.executable, '-m', 'venv', ROOT / '.venv')
    check = subprocess.run([str(python), '-c', "import OpenGL; assert OpenGL.__version__ == '3.1.10'"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if check.returncode:
        print('Installing PyOpenGL (internet needed for first setup)...', flush=True)
        run(python, '-m', 'pip', 'install', '--disable-pip-version-check', '-r', 'requirements.txt')
    run(python, '-c', "from OpenGL.GLUT import glutInit; assert bool(glutInit), 'FreeGLUT failed to load. See README.md.'")
    if '--setup-only' not in sys.argv:
        run(python, 'main.py')

if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f'Setup or launch failed: {exc}\nSee README.md for troubleshooting.', file=sys.stderr)
        sys.exit(1)
