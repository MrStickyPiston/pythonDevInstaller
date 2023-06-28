import logging
import os
import subprocess
import sys
import urllib.request

import requests


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


pbar = None
exec_dir = resource_path(".\exec\\")

try:
    os.mkdir(exec_dir)
except FileExistsError:
    pass

# ACCOUNT
GIT_EMAIL = "mr.sticky.piston@gmail.com"
GIT_USER = "sticky"

# VERSIONS
git_url = 'https://github.com/git-for-windows/git/releases/latest'
git_r = requests.get(git_url)
git_v = git_r.url.split('/')[-1].split('v')[1].split(".windows")[0]

PYTHON_VERSION = '3.11.4'
PYCHARM_VERSION = '2023.1.3'
GIT_VERSION = git_v
FIREFOX_VERSION = 'latest'

# URLS
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
PYCHARM_URL = f"https://download.jetbrains.com/python/pycharm-community-{PYCHARM_VERSION}.exe"
GIT_URL = f"https://github.com/git-for-windows/git/releases/download/{git_r.url.split('/')[-1]}/Git-{GIT_VERSION}-64-bit.exe"
FIREFOX_URL = "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=nl"

# CONFIG
PYCHARM_CONFIG = resource_path("config\pycharm.config")
GIT_CONFIG = resource_path("config\git.config")


# DOWNLOAD
def download_executables():
    def progress_bar(count_value, block_size, total, size=20, filled='█', empty='░'):
        done = count_value / total * block_size
        sys.stdout.write(f"\r[{round(done * 100)}%] {int(done * size) * filled}{(size - int(done * size)) * empty}")

        if done >= 1:
            sys.stdout.write("\n")

    logging.info("Downloading Python")
    urllib.request.urlretrieve(PYTHON_URL, f"{exec_dir}\\python_setup.exe", progress_bar)

    logging.info("Downloading Pycharm")
    urllib.request.urlretrieve(PYCHARM_URL, f"{exec_dir}\\pycharm_setup.exe", progress_bar)

    logging.info("Downloading Git")
    urllib.request.urlretrieve(GIT_URL, f"{exec_dir}\\git_setup.exe", progress_bar)

    logging.info("Downloading Firefox")
    urllib.request.urlretrieve(FIREFOX_URL, f"{exec_dir}\\firefox_setup.exe", progress_bar)


def install_executables():
    logging.info("Installing collected files")

    subprocess.Popen(
        f'{exec_dir}\python_setup.exe /quiet TargetDir="C:\Python311" AppendPath InstallAllUsers=0 Include_launcher=0')
    subprocess.Popen(f'{exec_dir}\pycharm_setup.exe /S /CONFIG={PYCHARM_CONFIG} /D=c:\Pycharm')
    subprocess.Popen(f'{exec_dir}\\firefox_setup.exe /S /InstallDirectoryPath="C:\Firefox"')
    subprocess.call(f'{exec_dir}\git_setup.exe /VERYSILENT /NORESTART /LOADINF={GIT_CONFIG}')

    logging.info("Configurating Git")
    os.system(f'C:\Git\\bin\git.exe config --global user.email "{GIT_EMAIL}"')
    os.system(f'C:\Git\\bin\git.exe config --global user.name {GIT_USER}')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_executables()
    install_executables()
    input("Press enter to exit")
