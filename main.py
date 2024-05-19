import os
import re
from shutil import make_archive
import sys
from time import sleep
from zipfile import ZipFile

import requests as r
from bs4 import BeautifulSoup
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import dates

URL = ("https://goteborgsvarvet.r.mikatiming.com/2024/?event=GV_9TG4PPOP195&num_results=250&pid=list"
       "&ranking=time_finish_netto&search%5Bsex%5D=M&search%5Bage_class%5D=%25")
PATH = "./data"
YEAR = 2024
PAGES = range(100)


def download_data(pages=PAGES):
    for page in pages:
        with open(f"{PATH}/{YEAR}/{int(page)+1}.html", "w+", encoding="UTF-8") as f:
            response = r.request("GET", URL, params=f"page={int(page)+1}").text
            f.write(response)
        sleep(2)


def zip_data():
    base_dir = PATH
    make_archive("data", "zip", base_dir)


def parse_data():
    times = []

    zip_file_path = "./data.zip"

    with ZipFile(zip_file_path) as z:
        for filename in z.namelist():
            if filename.endswith(".html"):
                with z.open(filename) as fp:
                    soup = BeautifulSoup(fp, features="html.parser")
                    hit = soup.find(class_="list-active list-group-item row")
                    time_pattern = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$")
                    finish_time = hit.find(string=time_pattern)
                    page = filename.split("/")[1].split(".")[0]
                    times.append((int(YEAR), int(page), finish_time))

    df = pd.DataFrame.from_records(times, columns=("year", "page", "time"))
    df.sort_values(by=["year", "page"]).reset_index(drop=True).to_csv("times.csv", encoding="UTF-8")


def plot_data():
    df = pd.read_csv("times.csv")
    df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S")

    fig, ax = plt.subplots()
    ax.scatter(df["time"], df["page"])
    ax.set(xlabel="time", ylabel="percentile")
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    plt.show()


if __name__ == '__main__':
    globals()[sys.argv[1]]()
