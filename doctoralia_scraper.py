from selenium import webdriver
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

num_paginas = 50

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

        print({
            'nome': nome,
            'url': url,
            'especialidade': especialidade,
            'nota': nota,
            'opinioes': opinioes,
            'cidade': cidade,
            'registro': registro,
            'imagem_url': imagem_url
        })

driver.quit()
