from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Configuración
CHROMIUM_PATH = "C:/chrome-win64/chrome-win64/chrome.exe"
CHROMEDRIVER_PATH = "C:/chromedriver-win64/chromedriver-win64/chromedriver.exe"

options = Options()
options.binary_location = CHROMIUM_PATH
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Opciones para parecer humano
options.add_argument("start-maximized")
options.add_argument("disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)


service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


# URLS
first_page_url = "https://www.vivanuncios.com.mx/s-casas-en-venta/zapopan/v1c1293l14828p1"
paged_url_template = "https://www.vivanuncios.com.mx/s-casas-en-venta/zapopan/page-{}/v1c1293l14828p{}"

all_links = []

def scroll_pagina(driver, pasos=20, espera=1.5):
    """Hace scroll paso a paso como un humano"""
    altura_total = driver.execute_script("return document.body.scrollHeight")
    altura_actual = 0
    paso_altura = altura_total // pasos

    for i in range(pasos):
        altura_actual += paso_altura
        driver.execute_script(f"window.scrollTo(0, {altura_actual});")
        time.sleep(espera)

    # Espera final para asegurar que se cargue lo último
    time.sleep(1)

def get_links_from_page(url, page_num):
    driver.get(url)
    time.sleep(1)  # Espera inicial

    if page_num == 2: # Espera adicional para captcha
        time.sleep(20)

    scroll_pagina(driver, pasos=20, espera=0.1)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    page_links = []
    for a in soup.select('a.listing-title, a.tile-title, a[href*="/a-"]'):
        href = a.get("href")
        if href and href.startswith("/"):
            full_url = "https://www.vivanuncios.com.mx" + href
            if full_url not in all_links:
                all_links.append(full_url)
                page_links.append(full_url)

    return page_links

# Página 1
print("🟢 Página 1")
page_links = get_links_from_page(first_page_url, 1)
print(f"🔗 {len(page_links)} propiedades encontradas")

# Páginas 2+
max_pages = 150
for page_num in range(2, max_pages + 1):
    url = paged_url_template.format(page_num, page_num)
    print(f"\n🟢 Página {page_num}: {url}")
    page_links = get_links_from_page(url, page_num)
    print(f"🔗 {len(page_links)} propiedades encontradas")

    if not page_links:
        print("🚫 Fin de resultados.")
        break

driver.quit()

print(f"\n✅ Total de propiedades encontradas: {len(all_links)} de {30*45} esperadas, se perdió un {((30*45/len(all_links))-1)*100}% de propiedades")

# Guardar los links en un archivo .txt
output_filename = "links_casas_zapopan.txt"

with open(output_filename, "w", encoding="utf-8") as f:
    for link in all_links:
        f.write(link + "\n")

print(f"\n📁 Links guardados en: {output_filename}")