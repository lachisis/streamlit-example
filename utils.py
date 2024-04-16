import json
import datetime
import pathlib
import pandas as pd

def save_github_data_to_file(date, github_items, github_fields):
    date_str = date.strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"github_items_{date_str}.json", 'w') as f:
        json.dump(github_items, f)
    with open(f"github_fields_{date_str}.json", 'w') as f:
        json.dump(github_fields, f)

def save_github_prs_data_to_file(date, github_prs):
    date_str = date.strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"github_prs_{date_str}.json", 'w') as f:
        json.dump(github_prs, f)      

def load_existing_data(fileprefix, extension="json"):
    files = [file for file in pathlib.Path('.').glob(f"{fileprefix}_*.{extension}")]
    if len(files) == 0:
        return None
    files.sort()
    latest_file = files[-1]
    latest_date = datetime.datetime.strptime("_".join(files[-1].stem.split('_')[-2:]), "%Y-%m-%d_%H-%M-%S")
    if extension == "json":
        return json.load(open(latest_file)), latest_date
    elif extension == "csv":
        return pd.read_csv(latest_file), latest_date        
    else:
        raise ValueError("Unsupported extension")

def save_data(date, data, fileprefix):
   data.to_csv(f'{fileprefix}_{date.strftime("%Y-%m-%d_%H-%M-%S")}.csv')