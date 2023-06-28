import os
import logging
import sys

import requests
import urllib.request
import progressbar

pbar = None

exec_dir = f"{os.getcwd()}\\exec"

try:
    os.mkdir(exec_dir)
except FileExistsError:
    pass

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


# DOWNLOAD
def download_executables():
    def progressBar(count_value, block_size, total, filler='◼'):
        percent = count_value/total*block_size
        sys.stdout.write(f"\r{int(percent*10)*filler}{int(percent*10)}")

    logging.info("Downloading Python")
    urllib.request.urlretrieve(PYTHON_URL, f"{exec_dir}\\python_setup.exe", progressBar)

    logging.info("Downloading Pycharm")
    urllib.request.urlretrieve(PYCHARM_URL, f"{exec_dir}\\pycharm_setup.exe", progressBar)

    logging.info("Downloading Git")
    urllib.request.urlretrieve(GIT_URL, f"{exec_dir}\\git_setup.exe", progressBar)

    logging.info("Downloading Firefox")
    urllib.request.urlretrieve(FIREFOX_URL, f"{exec_dir}\\firefox_setup.exe", progressBar)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_executables()
