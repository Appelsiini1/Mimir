"""Mímir constants"""

from os import name as OSname
from os import getenv
from os.path import join
from logging import DEBUG


# Environment spesific variables
# OS = operating system name
# PROGRAM_DATA = path to data/cache folder
ENV = {}
if OSname == "nt":
    ENV["OS"] = "nt"
    ENV["PROGRAM_DATA"] = join(getenv("APPDATA"), "MimirData")
elif OSname == "POSIX":
    ENV["OS"] = "POSIX"
    ENV["PROGRAM_DATA"] = join(getenv("HOME"), "MimirData")


VERSION = "0.0.4"
LOG_LEVEL = DEBUG
