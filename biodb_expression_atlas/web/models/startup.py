import os
import requests
from pathlib import Path
from getpass import getpass
import pymysql
import cryptography

## Change folder name
home_dir = Path.home()
PROJECT_DIR = home_dir.joinpath(".Biodb_expression_atlas")
DATA_DIR = PROJECT_DIR.joinpath("data")

# create data folder if not exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# download data files
atlas_ftp = "http://ftp.ebi.ac.uk/pub/databases/microarray/data/atlas/experiments/"
experiments = [
    "E-GEOD-7307/E-GEOD-7307_A-AFFY-44-analytics.tsv",
    "E-MEXP-1416/E-MEXP-1416_A-AFFY-54-analytics.tsv",
    "E-GEOD-7621/E-GEOD-7621_A-AFFY-44-analytics.tsv",
    "E-GEOD-20168/E-GEOD-20168_A-AFFY-33-analytics.tsv",
    "E-GEOD-20333/E-GEOD-20333_A-AFFY-41-analytics.tsv"]

datafile_paths = [] # store data files path

for exp in experiments:
    filename = exp.split('/')[1]
    path = os.path.join(DATA_DIR, filename)
    datafile_paths.append(path)
    if not os.path.exists(path):
        url = atlas_ftp + exp
        req = requests.get(url)
        open(path, 'wb').write(req.content)
