import logging

import installer

logging.basicConfig(level=logging.INFO) 
installer.download_executables() 
installer.install_executables() 
input("Press enter to exit")

