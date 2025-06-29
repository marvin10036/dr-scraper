import pandas as pd
import re
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def output_to_csv(file_name: str, data: list):
    df = pd.DataFrame(data)
    # If the file already exists
    if os.path.exists(file_name):
        # Append only mode
        df.to_csv(file_name, mode='a', header=False, index=False, encoding="utf-8-sig")
    else:
        # Create the file and headers
        df.to_csv(file_name, index=False, encoding="utf-8-sig")


def extract_uf(line: str):
    UFs = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
           "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
           "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

    pattern = r'\b(' + '|'.join(UFs) + r')\b'
    pattern_matched = re.search(pattern, line)
    if pattern_matched:
        return pattern_matched.group()
    else:
        return None


def extract_CRM_number(line: str):
    pattern = r"[0-9]+\.[0-9]*|[0-9]+"
    pattern_matched = re.search(pattern, line)
    if pattern_matched:
        # Only the first ocurrence
        return pattern_matched.group(0)
    else:
        return None


def extract_page_data():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    medicos = soup.find_all('div', class_='resultado-item')

    page_data = []
    for medico in medicos:
        # CRM
        crm_element = medico.find('b', string='CRM:')
        crm = crm_element.next_sibling.strip() if crm_element else ''

        # Data de Inscrição
        data_inscricao_element = medico.find('b', string='Data de Inscrição:')
        data_inscricao = data_inscricao_element.next_sibling.strip() if data_inscricao_element else ''

        # Tipo de Inscrição
        tipo_inscricao_element = medico.find('b', string='Inscrição:')
        tipo_inscricao = tipo_inscricao_element.next_sibling.strip() if tipo_inscricao_element else ''

        # Situação
        situacao_element = medico.find('b', string='Situação:')
        situacao = situacao_element.next_sibling.strip() if situacao_element else ''

        # Especialidades CFM
        especialidades_element = medico.find('b', string='Especialidades/Areas de Atuação:')
        especialidades = especialidades_element.find_next('span').get_text(strip=True) if especialidades_element else 'Médico sem especialidade registrada.'

        # Endereço
        endereco_element = medico.find('b', string='Endereço:')
        endereco = endereco_element.next_sibling.strip() if endereco_element else ''

        # Telefone
        telefone_element = medico.find('b', string='Telefone:')
        telefone = telefone_element.next_sibling.strip() if telefone_element else ''

        # Instituição de Graduação
        instituicao_element = medico.find('b', string='Instituição de Graduação: ')
        instituicao = instituicao_element.next_sibling.strip() if instituicao_element else ''

        page_data.append({
            'crm': crm,
            'data_inscricao': data_inscricao,
            'tipo_inscricao': tipo_inscricao,
            'situacao': situacao,
            'especialidades_CFM': especialidades,
            'endereco': endereco,
            'telefone': telefone,
            'instituicao': instituicao,
        })

    return page_data


# Thanks GPT
def captcha_is_rendered(timeout=10):
    try:
        # Wait for the div containing the CAPTCHA to be present
        captcha_div = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@style, "visibility") and contains(@style, "opacity")]'))
        )

        # Get the full style attribute of the div
        style = captcha_div.get_attribute('style')

        # Check if visibility is 'visible' and opacity is '1'
        if 'visibility: visible' in style and 'opacity: 1' in style:
            return True  # CAPTCHA is visible
        else:
            return False  # CAPTCHA is not visible

    except Exception as e:
        print(f"Error: {e}")
        return False  # CAPTCHA not found or not visible within the timeout


def save_matched_doctors(medicos: list):
    for medico in medicos:
        current_crm = medico['crm']
        current_crm = current_crm.replace("-", "")
        current_crm = current_crm.replace("/", "")

        current_index = CFM_UF_dict.get(current_crm)
        # If the current doctor is on the doctoralia sample
        if current_index is not None:
            joined_row = index_dict.get(current_index)
            joined_row.update(medico)
            output_to_csv("Output/06_joined.csv", [joined_row])


# Fourth: Reconstruct the index column to enumerate correclty
df = pd.read_csv("./Output/03_accepted.csv")
df.drop('index', axis=1)  # axis=1 to say it's a column

df['index'] = df.index
df = df[['index'] + [col for col in df.columns if col != 'index']]
df.to_csv("./Output/04_accepted_indexed.csv", index=False)

# Fifth: Create a new column with te structured data of CRM and UF together to
# be used as a CFM_UF_key for dictionary matching while scraping the CRM website
df['CFM_UF_key'] = "None"  # Creating new column
df = df[['CFM_UF_key'] + [col for col in df.columns if col != 'CFM_UF_key']]

for line_number, row in df.iterrows():
    current_uf = extract_uf(row['registro'])
    current_CRM = extract_CRM_number(row['registro'])
    df.at[line_number, 'CFM_UF_key'] = current_CRM + current_uf

df.to_csv("./Output/05_CRM_UF_key_column_added.csv", index=False)

# Sixth: Start scraping the CFM website and scrapping CRM and UF for matching
# with the key of the last step. Creating a new joined row on a new .csv. With
# added information when matched.

# { 0: {'index': 0, 'Name': 'Alice', ...}, 1: {'index': 1, 'Name': 'Bob', ...}, ...}
index_dict = df.to_dict(orient="index")
# {CFM_UF_key: index} for matching while scraping
CFM_UF_dict = {}
for line_number, row in df.iterrows():
    CFM_UF_dict[row['CFM_UF_key']] = line_number

# Begin scraping
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

driver.get("https://portal.cfm.org.br/busca-medicos")
wait = WebDriverWait(driver, 10)
time.sleep(5)

lgpd_button = driver.find_element("xpath", "//button[contains(text(), 'Aceito')]")
lgpd_button.click()
print("Botão aceito clicado.")

uf_select = Select(driver.find_element(By.ID, 'uf'))
uf_select.select_by_value('SC')

enviar_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[text()='ENVIAR']")
))
enviar_button.click()
print("Botão ENVIAR clicado.")
time.sleep(5)

if captcha_is_rendered():
    input("There is a captcha, solve it, and then press Enter to proceed")
    print("Proceeding...")

all_data = extract_page_data()

try:
    pagination = driver.find_element(By.CLASS_NAME, 'paginationjs-pages')
    page_links = pagination.find_elements(By.CLASS_NAME, 'J-paginationjs-page')

    last_page = int(page_links[-1].get_attribute('data-num'))

    # The maximum number of pages that I will allow the all_data array to grow
    # through before outputing to the csv.
    memory_treshold = 25
    for page_num in range(2, last_page + 1):
        try:
            page_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//li[@class='paginationjs-page J-paginationjs-page' and @data-num='{page_num}']/a")
            ))

            page_link.click()
            print(f"Acessando página {page_num}...")

            time.sleep(3)
            if captcha_is_rendered():
                input("There is a captcha, solve it, and then press Enter to proceed")
                print("Proceeding...")

            all_data.extend(extract_page_data())
            if page_num % memory_treshold == 0:
                save_matched_doctors(all_data)
                all_data = []

        except Exception as e:
            print(f"Erro ao acessar página {page_num}: {str(e)}")
            continue

    if all_data != []:
        save_matched_doctors(all_data)

except Exception as e:
    print(f"Não foi possível encontrar a paginação ou ocorreu um erro: {str(e)}")

driver.quit()
