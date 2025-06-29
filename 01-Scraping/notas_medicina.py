from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import UnexpectedAlertPresentException
import time
import pandas as pd
import random
import re
import undetected_chromedriver as uc

def digitar_humanamente(element, texto):
    for letra in texto:
        element.send_keys(letra)
        time.sleep(random.uniform(0.1, 0.3))

# options = uc.ChromeOptions()
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-blink-features=AutomationControlled")
# driver = uc.Chrome(options=options)

# Drivers para o chrome
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

def iniciar():
    driver.get("https://emec.mec.gov.br/emec/nova")

    elemento = driver.find_element(By.TAG_NAME, "body")
    ActionChains(driver)\
        .move_to_element_with_offset(elemento, 100, 100)\
        .pause(1)\
        .perform()

    # Selecionar "Curso de Graduação"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="CURSO"]'))
    ).click()

    time.sleep(2)

    campo_curso = driver.find_element(By.NAME, "data[CONSULTA_AVANCADA][txt_no_curso]")
    digitar_humanamente(campo_curso, "Medicina")

    time.sleep(2)

    # Selecionar UF "SC"
    select_uf = Select(driver.find_element(By.ID, "sel_sg_uf"))
    select_uf.select_by_value("SC")

    time.sleep(20)


    botao_pesquisar = driver.find_element(By.ID, "btnPesqAvancada")
    botao_pesquisar.click()
        
iniciar()
try:
    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.ID, "tbyDados"))
    )
    print("Tabela carregada com sucesso!")
except UnexpectedAlertPresentException:
    print(f"Erro ao carregar tabela:")
    time.sleep(20)
   

# Selecionar 200 itens por página
try:
    dropdown_paginacao = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "paginationItemCountItemdiv_listar_consulta_avancada"))
    )
    
    # Selecionar a opção 200
    Select(dropdown_paginacao).select_by_value("/emec/nova-index/listar-consulta-avancada/list/200")
    
    WebDriverWait(driver, 600).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "tr.linha_tr_body_nova_grid")) >= 50
    )
    time.sleep(10)
except Exception as e:
    print(f"Erro ao selecionar 200 itens por página: {e}")


soup = BeautifulSoup(driver.page_source, 'html.parser')
tabela = soup.find("tbody", {"id": "tbyDados"})

dados = []

if tabela:
    for linha in tabela.find_all("tr", class_=re.compile(r"linha_tr_body_nova_grid(_old)?")):
        celulas = linha.find_all("td")
        if len(celulas) >= 8:
            instituicao = celulas[0].get_text(strip=True)
            sigla = celulas[1].get_text(strip=True)
            curso = celulas[2].get_text(strip=True).split(")")[-1].strip()
            grau = celulas[3].get_text(strip=True)
            modalidade = celulas[4].get_text(strip=True)
            indices = celulas[5].get_text(separator=" | ", strip=True)
            vagas = celulas[6].get_text(strip=True)
            data_inicio = celulas[7].get_text(strip=True)
            
            dados.append([instituicao, sigla, curso, grau, modalidade, indices, vagas, data_inicio])

driver.quit()

df = pd.DataFrame(dados, columns=[
    "Instituição", "Sigla", "Curso", "Grau", "Modalidade", 
    "Índices (CC/CPC/ENADE/IDD)", "Vagas Anuais", "Data Início"
])

df.to_csv("cursos_medicina_sc_200itens.csv", index=False, encoding="utf-8-sig")
print(f"Total de registros extraídos: {len(df)}")
print(df.head())
