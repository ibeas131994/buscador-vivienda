import requests
import pandas as pd
import os
import datetime
from bs4 import BeautifulSoup

TOKEN = "TU_TOKEN"
CHAT_ID = "TU_CHAT_ID"

URL = "https://www.idealista.com/venta-viviendas/burgos-burgos/con-precio-hasta_200000,metros-cuadrados-mas-de_80,de-dos-dormitorios,de-tres-dormitorios,de-cuatro-cinco-habitaciones-o-mas/"

HEADERS = {"User-Agent": "Mozilla/5.0"}

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def obtener_pisos():
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    enlaces = []

    for a in soup.select("a.item-link"):
        enlace = a.get("href")
        if enlace:
            if not enlace.startswith("http"):
                enlace = "https://www.idealista.com" + enlace
            enlaces.append(enlace)

    return list(set(enlaces))

def main():

    archivo = "historico_pisos.xlsx"

    actuales = pd.DataFrame(obtener_pisos(), columns=["enlace"])

    if os.path.exists(archivo):
        historico = pd.read_excel(archivo)

        nuevos = actuales[~actuales["enlace"].isin(historico["enlace"])]
        total = pd.concat([historico, actuales]).drop_duplicates()

    else:
        nuevos = actuales
        total = actuales

    total.to_excel(archivo, index=False)

    if len(nuevos) > 0:
        msg = f"🏡 {len(nuevos)} nuevos pisos encontrados:\n\n"
        for e in nuevos["enlace"].head(5):
            msg += e + "\n"
        enviar_telegram(msg)
    else:
        enviar_telegram("Hoy no hay pisos nuevos")

if __name__ == "__main__":
    main()