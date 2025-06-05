from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Drivers para o chrome
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

def extract_page_data():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    medicos = soup.find_all('div', class_='resultado-item')
    
    page_data = []
    for medico in medicos:
        # Nome
        nome = medico.find('h4').get_text(strip=True) if medico.find('h4') else ''
        
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
        
        # Inscrição em outro estado
        outro_estado_element = medico.find('b', string='Inscrição em outro estado:')
        outro_estado = outro_estado_element.find_next('span').get_text(strip=True) if outro_estado_element else ''
        
        # Especialidades
        especialidades_element = medico.find('b', string='Especialidades/Areas de Atuação:')
        especialidades = especialidades_element.find_next('span').get_text(strip=True) if especialidades_element else 'Médico sem especialidade registrada.'
        
        # Endereço
        endereco_element = medico.find('b', string='Endereço:')
        endereco = endereco_element.next_sibling.strip() if endereco_element else ''
        
        # Telefone
        telefone_element = medico.find('b', string='Telefone:')
        telefone = telefone_element.next_sibling.strip() if telefone_element else ''
        
        page_data.append({
            'nome': nome,
            'crm': crm,
            'data_inscricao': data_inscricao,
            'tipo_inscricao': tipo_inscricao,
            'situacao': situacao,
            'especialidades': especialidades,
            'endereco': endereco,
            'telefone': telefone,
        })
    
    return page_data

all_data = extract_page_data()

try:
    pagination = driver.find_element(By.CLASS_NAME, 'paginationjs-pages')
    page_links = pagination.find_elements(By.CLASS_NAME, 'J-paginationjs-page')
    
    last_page = int(page_links[-1].get_attribute('data-num'))
    
    max_pages = 10
    for page_num in range(2, last_page + 1):
        try:
            
            page_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//li[@class='paginationjs-page J-paginationjs-page' and @data-num='{page_num}']/a")
            ))
            page_link.click()
            print(f"Acessando página {page_num}...")
            
            time.sleep(3)
            
            all_data.extend(extract_page_data())
            
            if page_num >= max_pages:
                break
                
        except Exception as e:
            print(f"Erro ao acessar página {page_num}: {str(e)}")
            continue
            
except Exception as e:
    print(f"Não foi possível encontrar a paginação ou ocorreu um erro: {str(e)}")

print(f"Total de médicos coletados: {len(all_data)}")

for i, medico in enumerate(all_data[:5]):
    print(f"\nMédico {i+1}:")
    for key, value in medico.items():
        print(f"{key}: {value}")

driver.quit()
