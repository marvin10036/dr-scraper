from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import os


def output_to_csv(data):
    df = pd.DataFrame(data)
    # If the file already exists
    if os.path.exists("doctoralia.csv"):
        # Append only mode
        df.to_csv("doctoralia.csv", mode='a', header=False, index=False, encoding="utf-8-sig")
    else:
        # Create the file and headers
        df.to_csv("doctoralia.csv", index=False, encoding="utf-8-sig")


options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
num_paginas = 150

memory_treshold = 5
all_data = []

for pagina in range(1, num_paginas + 1):
    url = f"https://www.doctoralia.com.br/pesquisa?q=&loc=Santa%20Catarina&page={pagina}"
    print(f"Acessando página {pagina}: {url}")
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    doctors = soup.find_all('div', {'data-id': 'result-item'})

    if not doctors:
        print("Nenhum resultado encontrado nesta página.")
        break

    for doc in doctors:
        nome = doc.get('data-doctor-name', '').strip()
        url = doc.get('data-doctor-url', '')
        especialidade = doc.get('data-eec-specialization-name', '')
        nota = doc.get('data-eec-stars-rating', '')
        opinioes = doc.get('data-eec-opinions-count', '')
        cidade = doc.get('data-eec-address-cities', '')
        registro_tag = doc.find('span', class_='h5 font-weight-normal mb-0')
        registro = registro_tag.get_text(strip=True) if registro_tag else ''
        img_tag = doc.find('img')
        imagem_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else ''

        all_data.append({
            'nome': nome,
            'url': url,
            'especialidade': especialidade,
            'nota': nota,
            'opinioes': opinioes,
            'cidade': cidade,
            'registro': registro,
            'imagem_url': imagem_url,
        })

    if pagina % memory_treshold == 0:
        output_to_csv(all_data)
        all_data = []

# Outputing the remaining entries
output_to_csv(all_data)

driver.quit()
