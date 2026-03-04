import time
import os
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

TOKEN = "8414648377:AAG7kfPA7wvYAwz5cXqW8gcfXAL7p-RWFoc"
CHAT_ID = "1787584864"

URL = "https://www.idealista.com/venta-viviendas/burgos-burgos/con-precio-hasta_200000,metros-cuadrados-mas-de_80,de-dos-dormitorios,de-tres-dormitorios,de-cuatro-cinco-habitaciones-o-mas/"

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url, data=data)

def obtener_anuncios():
    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get(URL)
    time.sleep(5)

    anuncios = []

    while True:
        items = driver.find_elements(By.CSS_SELECTOR, "a.item-link")

        for item in items:
            enlace = item.get_attribute("href")
            if enlace:
                anuncios.append(enlace)

        try:
            siguiente = driver.find_element(By.CSS_SELECTOR, "li.next a")
            siguiente.click()
            time.sleep(5)
        except:
            break

    driver.quit()
    return list(set(anuncios))

def main():
    archivo = "historico_pisos.xlsx"

    anuncios_actuales = obtener_anuncios()
    df_actual = pd.DataFrame(anuncios_actuales, columns=["enlace"])

    if os.path.exists(archivo):
        df_antiguo = pd.read_excel(archivo)
        nuevos = df_actual[~df_actual["enlace"].isin(df_antiguo["enlace"])]
        df_total = pd.concat([df_antiguo, df_actual]).drop_duplicates()
    else:
        nuevos = df_actual
        df_total = df_actual

    df_total.to_excel(archivo, index=False)

    if len(nuevos) > 0:
        mensaje = f"🏡 {len(nuevos)} nuevos pisos encontrados:\n\n"
        for enlace in nuevos["enlace"].head(5):
            mensaje += enlace + "\n"
        enviar_telegram(mensaje)
    else:
        enviar_telegram("Hoy no hay anuncios nuevos.")

if __name__ == "__main__":
    main()