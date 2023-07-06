import ssl
import logging
import os
import subprocess
import sys
import threading
import urllib.request
import webbrowser
from builtins import function

import requests


class Installer:
    def __init__(self,
                 name: str,
                 version: str,
                 url: str,
                 options: str,
                 post: function = None,
                 config: str = "None"):
        self.name = name

        self.version = version
        self.url = url.replace("{VERSION}", self.version)

        self.options = options.replace("{CONFIG}", config)
        self.config = config

        self.thread = None

        if self.post is not None:
            self.post = post
        else:
            self.post = self._post

    def progress_bar(self, count_value, block_size, total, size=20, filled='█', empty='░'):
        done = count_value / total * block_size
        sys.stdout.write(
            f"\r{'Downloading ' + self.name:<20} [{int(done * size) * filled}{(size - int(done * size)) * empty}] ({round(done * 100)}%)")

        if done >= 1:
            sys.stdout.write("\n")

    def download(self):
        urllib.request.urlretrieve(self.url, f"{exec_dir}\\{self.name}_setup.exe", self.progress_bar)

    def _install_thread(self):
        print(f"Starting the installation of {self.name}")
        subprocess.call(f'{exec_dir}\\{self.name}_setup.exe {self.options}')

        self.post()
        print(f"Finished installing {self.name}")

    def install(self):
        self.thread = threading.Thread(target=self._install_thread())
        self.thread.start()

    def _post(self):
        pass

    def wait(self):
        self.thread.join()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


exec_dir = resource_path(".\exec\\")
ssl._create_default_https_context = ssl._create_unverified_context

try:
    os.mkdir(exec_dir)
except FileExistsError:
    pass

# VERSIONS
git_url = 'https://github.com/git-for-windows/git/releases/latest'
git_r = requests.get(git_url)
git_v = git_r.url.split('/')[-1].split('v')[1].split(".windows")[0]
git_url = f'https://github.com/git-for-windows/git/releases/download/{git_r.url.split("/")[-1]}/Git-{{VERSION}}-64-bit.exe'

python_installer = Installer(name='Python',
                             version='3.11.4',
                             url='https://www.python.org/ftp/python/{VERSION}/python-{VERSION}-amd64.exe',
                             options='/quiet TargetDir="C:\Python311" AppendPath InstallAllUsers=0 Include_launcher=0')

pycharm_installer = Installer(name='Pycharm',
                              version='2023.1.3',
                              url='https://download.jetbrains.com/python/pycharm-community-{VERSION}.exe',
                              options='/S /CONFIG={CONFIG} /D=c:\Pycharm',
                              config=resource_path('config\pycharm.config'))

git_installer = Installer(name='Git',
                          version=git_v,
                          url=git_url,
                          options='/VERYSILENT /NORESTART /LOADINF={CONFIG}',
                          config=resource_path('config\git.config'))

firefox_installer = Installer(name='Firefox',
                              version='latest',
                              url='https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=nl',
                              options='/VERYSILENT /NORESTART /LOADINF={CONFIG}',
                              config=resource_path('config\git.config'))

installers = [python_installer, pycharm_installer, git_installer, firefox_installer]

# ACCOUNT
global GIT_EMAIL
global GIT_USER

DARK_READER_VERSION = '4.9.64'
ADBLOCK_ULTIMATE_VERSION = '3.7.28'

DARK_READER_URL = f"https://addons.mozilla.org/firefox/downloads/file/4128489/darkreader-{DARK_READER_VERSION}.xpi"
ADBLOCK_ULTIMATE_URL = f"https://addons.mozilla.org/firefox/downloads/file/4113999/adblocker_ultimate-{ADBLOCK_ULTIMATE_VERSION}.xpi"


# DOWNLOAD
def download_executables():
    for i in installers:
        i.download()


def install_executables():
    def install_python():
        logging.info("Installing Python")
        subprocess.call(
            f'{exec_dir}\python_setup.exe /quiet TargetDir="C:\Python311" AppendPath InstallAllUsers=0 Include_launcher=0')
        logging.info("Finished installing Python")

    def install_pycharm():
        logging.info("Installing Pycharm")
        subprocess.call(f'{exec_dir}\pycharm_setup.exe /S /CONFIG={PYCHARM_CONFIG} /D=c:\Pycharm')
        logging.info("Finished installing Pycharm")

    def install_firefox():
        logging.info("Installing Firefox")
        subprocess.call(f'{exec_dir}\\firefox_setup.exe /S /InstallDirectoryPath="C:\Firefox"')

        logging.info("Installing Firefox addons")
        with open(resource_path('./assets/addons.html')) as baseHTML:
            addonsHTML = baseHTML.read().replace("{DARK_READER}", DARK_READER_URL).replace("{ADBLOCK_ULTIMATE}",
                                                                                           ADBLOCK_ULTIMATE_URL)
        with open(resource_path('./addons.html'), 'w') as filledHTML:
            filledHTML.write(addonsHTML)

        webbrowser.register('firefox', None, webbrowser.BackgroundBrowser("C:\\firefox\\firefox.exe"))
        webbrowser.get('firefox').open('file://' + resource_path("./addons.html"))

        logging.info("Finished installing Firefox")

    def install_git():
        logging.info("Installing Git")
        subprocess.call(f'{exec_dir}\git_setup.exe /VERYSILENT /NORESTART /LOADINF={GIT_CONFIG}')

        logging.info("Configurating Git")
        os.system(f'C:\Git\\bin\git.exe config --global user.email "{GIT_EMAIL}"')
        os.system(f'C:\Git\\bin\git.exe config --global user.name {GIT_USER}')

        logging.info(f"Finished installing Git (User: {GIT_USER}, Email: {GIT_EMAIL})")

    PYTHON_PROCESS = threading.Thread(target=install_python)
    PYCHARM_PROCESS = threading.Thread(target=install_pycharm)
    GIT_PROCESS = threading.Thread(target=install_git)
    FIREFOX_PROCESS = threading.Thread(target=install_firefox)

    PYTHON_PROCESS.start()
    PYCHARM_PROCESS.start()
    GIT_PROCESS.start()
    FIREFOX_PROCESS.start()


def __main__():
    global GIT_EMAIL
    global GIT_USER

    logging.basicConfig(level=logging.INFO)

    logging.info("##### Collecting data #####")
    GIT_EMAIL = input("Enter git email: ")
    GIT_USER = input("Enter git username: ")

    logging.info("##### Downloading files #####")
    download_executables()

    logging.info("##### Installing collected files #####")
    # install_executables()

    logging.info("Finished installing all tools")
    input("Press enter to exit")


if __name__ == "__main__":
    __main__()
