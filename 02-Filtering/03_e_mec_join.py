import pandas as pd
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import UnexpectedAlertPresentException

import time
import random
import re


def output_to_csv(file_name: str, data: list):
    df = pd.DataFrame(data)
    # If the file already exists
    if os.path.exists(file_name):
        # Append only mode
        df.to_csv(file_name, mode='a', header=False, index=False, encoding="utf-8-sig")
    else:
        # Create the file and headers
        df.to_csv(file_name, index=False, encoding="utf-8-sig")


def format_instituicao_string(instituicao_string: str):
    formatted_string = instituicao_string.upper()
    formatted_string = formatted_string.split("-")[0]
    return formatted_string


def query_e_mec(instituicao_string: str):
    print("Attempting query with string: ", instituicao_string)
    instituicao_field = driver.find_element(By.NAME, "data[CONSULTA_AVANCADA][txt_no_ies]")

    instituicao_field.clear()
    for letter in instituicao_string:
        instituicao_field.send_keys(letter)
        time.sleep(random.uniform(0.1, 0.3))

    botao_pesquisar = driver.find_element(By.ID, "btnPesqAvancada")
    botao_pesquisar.click()

    # Wait for the loading element to appear
    loading_element = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "loading"))
    )

    # Wait for the loading elment to disappear
    WebDriverWait(driver, 120).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "loading"))
    )

    # See if the response has returned
    try:
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "tbyDados"))
        )
        print("Tabela carregada com sucesso!")
    except UnexpectedAlertPresentException:
        print(f"Erro ao carregar tabela:")
        time.sleep(20)

    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabela = soup.find("tbody", {"id": "tbyDados"})

    dados = {}
    if tabela:
        lines = (tabela.find_all("tr", class_=re.compile(r"linha_tr_body_nova_grid(_old)?")))
        if len(lines) > 0:
            first_line = lines[0]
            celulas = first_line.find_all("td")
            if len(celulas) >= 8:
                dados['emec_instituicao'] = celulas[0].get_text(strip=True)
                dados['emec_sigla'] = celulas[1].get_text(strip=True)
                dados['emec_curso'] = celulas[2].get_text(strip=True).split(")")[-1].strip()
                dados['emec_grau'] = celulas[3].get_text(strip=True)
                dados['emec_modalidade'] = celulas[4].get_text(strip=True)
                dados['emec_indices'] = celulas[5].get_text(separator=" | ", strip=True)
                dados['emec_vagas'] = celulas[6].get_text(strip=True)
                dados['emec_data_inicio'] = celulas[7].get_text(strip=True)

    return dados


# Seventh: Reorder by original index
df = pd.read_csv("./Output/06_joined.csv")
ordered_df = df.sort_values(by='index', ascending=True)
ordered_df.to_csv('./Output/07_ordered_CFM_join.csv', index=False)

# Eighth: Getting the rows that weren't scraped on the first run of the join
# Thanks GPT
df_a = pd.read_csv('./Output/05_CRM_UF_key_column_added.csv')
df_b = pd.read_csv('./Output/07_ordered_CFM_join.csv')

# So that both dfs have the same header for merging
columns_to_keep = ['CFM_UF_key', 'index', 'nome', 'url', 'especialidade',
                   'nota', 'opinioes', 'cidade', 'registro', 'imagem_url']

df_a = df_a[columns_to_keep]
df_b = df_b[columns_to_keep]
df_diff = pd.merge(df_a, df_b, how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
# TODO Use it to search for the remaining
df_diff.to_csv('./Output/07_rejected.csv', index=False)


# Ninth: Iterate over the list, and create a dict for saving the info that will
# be scraped from the e-mec website. Thus doing the query only once per unique name
df = pd.read_csv('./Output/07_ordered_CFM_join.csv')
index_dict = df.to_dict(orient="index")

# Scraping initialization
# Chrome drivers
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

driver.get("https://emec.mec.gov.br/emec/nova")

elemento = driver.find_element(By.TAG_NAME, "body")
ActionChains(driver)\
    .move_to_element_with_offset(elemento, 100, 100)\
    .pause(1)\
    .perform()


# Iterating over the list of doctors
instituicao_dict = {}  # {UFRJ: {'sigla': 'UFRJ', 'grau': '...', ...}, USP: {...}, ...}
for index, row in df.iterrows():
    print("current_index: ", index)
    current_instituicao = instituicao_dict.get(row['instituicao'])

    # If this is the first ocurrence
    if current_instituicao is None:
        result = query_e_mec(format_instituicao_string(row['instituicao']))
        instituicao_dict[row['instituicao']] = result

    current_row_dict = index_dict.get(index)
    current_row_dict.update(instituicao_dict[row['instituicao']])
    output_to_csv("./Output/08_join_instituicao.csv", [current_row_dict])

driver.quit()
