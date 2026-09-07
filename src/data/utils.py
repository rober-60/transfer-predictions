from datetime import datetime

def str2date(data_tekst:str):
    data_obiekt = datetime.strptime(data_tekst, "%Y-%m-%d").date()
    return data_obiekt