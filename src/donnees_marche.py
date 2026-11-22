
import io
import pandas as pd
import requests


url = "https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
url_NBER = "https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions"


def charger_vix():
    vix = pd.read_csv(url)

    vix["DATE"] = pd.to_datetime(vix["DATE"])
    vix = vix[["DATE", "CLOSE"]]
    vix = vix.rename(columns={"CLOSE": "vix"})
    vix = vix.set_index("DATE")
    return vix


def charger_récessions():
    response = requests.get(url_NBER)
    html = response.text
    dfs = pd.read_html(io.StringIO(html))
    récession = dfs[0]

    récession = récession.iloc[2:-5]
    récession = récession[[0, 1]]
    récession.columns = ["start", "end"]
    
    récession[["start", "end"]] = récession[["start", "end"]].apply(lambda x : x.str.strip())
    récession[["start", "end"]]= récession[["start", "end"]].apply(lambda x : x.str.split("(").str[0].str.strip())
    récession[["start", "end"]] = récession[["start","end"]].apply(pd.to_datetime, format = "%B %Y")

    récession = récession.dropna(subset = ["start", "end"])

    return récession


def charger_marché():
    vix = charger_vix()
    récession = charger_récessions()

    vix["récession"] = 0

    for i in range(len(récession)):
        debut = récession["start"].iloc[i] + pd.DateOffset(months=1) 
        fin = récession["end"].iloc[i] + pd.offsets.MonthEnd(0)  

    for date in vix.index:
        if date >= debut and date <= fin:
            vix.loc[date, "récession"] = 1

    vix["stress"] = pd.qcut(vix["vix"],q = 3, labels=["bas", "moyen", "haut"])

    marché = vix.reset_index("DATE")
    marché = marché.rename(columns={"DATE": "date"})
    marché = marché[["date", "vix", "récession", "stress"]]

    return marché

