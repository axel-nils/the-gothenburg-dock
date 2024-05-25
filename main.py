import re
from shutil import make_archive
from time import sleep
from zipfile import ZipFile

import requests as r
from bs4 import BeautifulSoup
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import dates

import seaborn as sns
sns.set_theme()


URL = ("https://goteborgsvarvet.r.mikatiming.com/2024/?event=GV_9TG4PPOP195&num_results=250&pid=list"
       "&ranking=time_finish_netto&search%5Bsex%5D=W&search%5Bage_class%5D=%25")
PATH = "./data"
YEAR = 2024
PAGES = range(60)


def download_data(pages=PAGES):
    for page in pages:
        with open(f"{PATH}/{YEAR}/{int(page)+1}.html", "w+", encoding="UTF-8") as f:
            response = r.request("GET", URL, params=f"page={int(page)+1}").text
            f.write(response)
        sleep(2)


def zip_data():
    base_dir = PATH + "/2024w"
    make_archive("data_w", "zip", base_dir)


def parse_data():
    times = []

    zip_file_path = "./data_w.zip"

    with ZipFile(zip_file_path) as z:
        for filename in z.namelist():
            print(filename)
            if filename.endswith(".html"):
                with z.open(filename) as fp:
                    soup = BeautifulSoup(fp, features="html.parser")
                    hits = soup.findAll(class_="list-active list-group-item row")
                    for hit in hits:
                        time_pattern = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$")
                        finish_time = hit.find(string=time_pattern)
                        page = filename.split(".")[0]
                        times.append((int(YEAR), int(page), finish_time))

    df = pd.DataFrame.from_records(times, columns=("year", "page", "time"))
    df.sort_values(by=["year", "page"]).reset_index(drop=True).to_csv("times_w.csv", encoding="UTF-8")


def plot_data():

    df = pd.read_csv("times.csv")
    df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S")
    df.drop(df.tail(40).index, inplace=True)

    dfw = pd.read_csv("times_w.csv")
    dfw["time"] = pd.to_datetime(dfw["time"], format="%H:%M:%S")
    dfw.drop(dfw.tail(40).index, inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6), layout="tight")
    fig.suptitle("Göteborgsvarvet 2024")
    sns.histplot(data=df["time"], ax=ax, label="men", color="skyblue")
    sns.histplot(data=dfw["time"], ax=ax, label="women", color="salmon")
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    ax.set(xlabel="Finishing time")
    ax.legend()

    fig.savefig("2024.pdf")
    fig.savefig("2024.png")
    plt.show()


def main():
    #download_data()
    #zip_data()
    #parse_data()
    plot_data()

if __name__ == "__main__":
    main()
