import ssl
import logging
import os
import subprocess
import sys
import threading
import urllib.request
import webbrowser

import requests

global data

base_url = f"{os.environ['USERPROFILE']}\\Tools"

class Data:
    def __init__(self,
                 git_email,
                 git_user,
                 python_version='3.12.0',
                 pycharm_version='2023.2.5',
                 git_version='latest',
                 firefox_version='latest',

                 dark_reader_version='4.9.64',
                 adblock_ultimate_version='3.7.28',

                 python_url='https://www.python.org/ftp/python/{VERSION}/python-{VERSION}-amd64.exe',
                 pycharm_url='https://download.jetbrains.com/python/pycharm-community-{VERSION}.exe',
                 git_url='https://github.com/git-for-windows/git/releases/download/{git_r.url.split("/")[-1]}/Git-{'
                         'git_v}-64-bit.exe',
                 firefox_url='https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=nl',

                 dark_reader_url = "https://addons.mozilla.org/firefox/downloads/file/4128489/darkreader-{dark_reader_version}.xpi",
                 adblock_ultimate_url = "https://addons.mozilla.org/firefox/downloads/file/4113999/adblocker_ultimate-{adblock_ultimate_version}.xpi",

                 python_options=f'/quiet TargetDir="{base_url}\\python\\Python311\\" AppendPath InstallAllUsers=0 Include_launcher=0',
                 pycharm_options=f'/S /CONFIG={{CONFIG}} /D={base_url}\\pycharm\\',
                 git_options=f'/VERYSILENT /NORESTART /CONFIG={{CONFIG}} /DIR={base_url}\\git\\',
                 firefox_options=f'/S /InstallDirectoryPath="{base_url}\\firefox\\"',

                 python_config='None',
                 pycharm_config='config\pycharm.config',
                 git_config='config\git.config',
                 firefox_config='None'
                 ):

        git_r = requests.get('https://github.com/git-for-windows/git/releases/latest')
        git_v = git_r.url.split('/')[-1].split('v')[1].split(".windows")
        git_v = git_v[0] + (git_v[1] if git_v[1] != ".1" else "")

        self.exec_dir = resource_path(".\exec\\")

        self.git_email = git_email
        self.git_user = git_user

        self.python_version = python_version
        self.pycharm_version = pycharm_version
        self.git_version = git_v if git_version == 'latest' else git_version
        self.firefox_version = firefox_version

        self.dark_reader_version = dark_reader_version
        self.adblock_ultimate_version = adblock_ultimate_version

        self.python_url = python_url
        self.pycharm_url = pycharm_url
        self.git_url = eval(f"f'{git_url}'")
        self.firefox_url = firefox_url

        self.dark_reader_url = eval(f"f'{dark_reader_url}'")
        self.adblock_ultimate_url = eval(f"f'{adblock_ultimate_url}'")

        self.python_options = python_options
        self.pycharm_options = pycharm_options
        self.git_options = git_options
        self.firefox_options = firefox_options

        self.python_config = python_config
        self.pycharm_config = pycharm_config
        self.git_config = git_config
        self.firefox_config = firefox_config

        self.python_installer = Installer(name='Python',
                                          version=self.python_version,
                                          url=self.python_url,
                                          options=python_options,
                                          config=resource_path(python_config))

        self.pycharm_installer = Installer(name='Pycharm',
                                           version=self.pycharm_version,
                                           url=self.pycharm_url,
                                           options=pycharm_options,
                                           config=resource_path(pycharm_config))

        self.git_installer = Installer(name='Git',
                                       version=self.git_version,
                                       url=self.git_url,
                                       options=git_options,
                                       post=PostInstall.git,
                                       config=resource_path(git_config))

        self.firefox_installer = Installer(name='Firefox',
                                           version=self.firefox_version,
                                           url=self.firefox_url,
                                           options=firefox_options,
                                           post=PostInstall.firefox,
                                           config=resource_path(git_config))

        self.installers = [self.python_installer, self.pycharm_installer, self.git_installer, self.firefox_installer]


class Installer:
    def __init__(self,
                 name: str,
                 version: str,
                 url: str,
                 options: str,
                 post: object = None,
                 config: str = "None"):
        self.name = name

        self.version = version
        self.url = url.replace("{VERSION}", self.version)

        self.options = options.replace("{CONFIG}", config)
        self.config = config

        self.thread = None

        if post is not None:
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
        urllib.request.urlretrieve(self.url, f"{data.exec_dir}\\{self.name}_setup.exe", self.progress_bar)

    def _install_thread(self):
        print(f"Starting the installation of {self.name}")
        subprocess.call(f'{data.exec_dir}\\{self.name}_setup.exe {self.options}')

        self.post()
        print(f"Finished installing {self.name}")

    def install(self):
        self.thread = threading.Thread(target=self._install_thread)
        self.thread.start()

    def _post(self):
        pass

    def wait(self):
        self.thread.join()


class PostInstall:
    @staticmethod
    def firefox():
        with open(resource_path('./assets/addons.html')) as baseHTML:
            addonsHTML = baseHTML.read().replace("{DARK_READER}", data.dark_reader_url).replace("{ADBLOCK_ULTIMATE}",
                                                                                           data.adblock_ultimate_url)
        with open(resource_path('./addons.html'), 'w') as filledHTML:
            filledHTML.write(addonsHTML)

        webbrowser.register('firefox', None, webbrowser.BackgroundBrowser("C:\\firefox\\firefox.exe"))
        webbrowser.get('firefox').open('file://' + resource_path("./addons.html"))

    @staticmethod
    def git():
        os.system(f'C:\Git\\bin\git.exe config --global user.email "{data.git_email}"')
        os.system(f'C:\Git\\bin\git.exe config --global user.name {data.git_user}')

        print(f"Set Git user to {data.git_user}\nSet Git email to {data.git_email}")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def setup(exec_dir):
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        os.mkdir(exec_dir)
    except FileExistsError:
        pass


def download_executables():
    for i in data.installers:
        i.download()


def install_executables():
    for i in data.installers:
        i.install()


def await_executables():
    for i in data.installers:
        i.wait()


def __main__():
    global data
    logging.basicConfig(level=logging.INFO)

    logging.info("##### Collecting data #####")
    git_email = input("Enter git email: ")
    git_user = input("Enter git username: ")

    data = Data(git_email, git_user)

    logging.info("##### Downloading files #####")
    download_executables()

    logging.info("##### Installing collected files #####")
    install_executables()
    await_executables()

    input("Finished installing all tools, press enter to exit.")


setup(resource_path(".\exec\\"))

if __name__ == "__main__":
    __main__()
