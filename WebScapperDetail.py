from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
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

ciudad = "zapopan"

with open(f"Data/{ciudad}/links_casas_{ciudad}.txt", "r", encoding="utf-8") as f:
    all_links = [line.strip() for line in f if line.strip()]

all_links = all_links[2690+581:]  # Solo procesa el primer link

# def extraer_direccion(soup):
#     h4_tags = soup.find_all("h4")
#     for h4 in h4_tags:
#         texto = h4.get_text(strip=True).lower()
#         if any(palabra in texto for palabra in ["tlajomulco", "guadalajara", "zapopan", "tlaquepaque", "tonalá", "fraccionamiento", "colonia"]):
#             return h4.get_text(strip=True)
#     return None

def extraer_direccion(soup):
    # Dirección desde <h4> en #map-section
    direccion_tag = soup.select_one("section#map-section h4")
    if direccion_tag:
        direccion = direccion_tag.get_text(strip=True)

    return direccion

def extraer_caracteristicas(soup):
    datos = {
        "m2_lote": None,
        "m2_construccion": None,
        "banos": None,
        "medio_banos": None,
        "estacionamientos": None,
        "recamaras": None,
        "antiguedad": None,
        "direccion": extraer_direccion(soup)
    }

    iconos = soup.select("ul#section-icon-features-property li.icon-feature")

    for li in iconos:
        icono = li.find("i")
        texto = li.get_text(strip=True).lower()
        valor = ''.join(filter(str.isdigit, texto))  # Extrae solo el número

        if not icono or not valor:
            continue

        clase_icono = icono.get("class", [""])[0]

        if "icon-stotal" in clase_icono:
            datos["m2_lote"] = valor
        elif "icon-scubierta" in clase_icono:
            datos["m2_construccion"] = valor
        elif "icon-bano" in clase_icono:
            datos["banos"] = valor
        elif "icon-toilete" in clase_icono:
            datos["medio_banos"] = valor
        elif "icon-cochera" in clase_icono:
            datos["estacionamientos"] = valor
        elif "icon-dormitorio" in clase_icono:
            datos["recamaras"] = valor
        elif "icon-antiguedad" in clase_icono:
            datos["antiguedad"] = valor

    return datos

def extraer_datos_propiedad(url):
    driver.get(url)
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    datos = {"url": url}

    # Título
    titulo = soup.find("h1")
    datos["titulo"] = titulo.get_text(strip=True) if titulo else None

    # Precio
    datos["precio"] = None
    for span in soup.find_all("span"):
        texto = span.get_text(strip=True)
        if "MN" in texto or "$" in texto:
            datos["precio"] = texto
            break

    # Características adicionales
    datos.update(extraer_caracteristicas(soup))

    return datos


todos_los_datos = []

for i, link in enumerate(all_links):
    if i == 2:
        time.sleep(30)
    print(f"🔎 {i+1}/{len(all_links)} Procesando: {link}")
    try:
        datos = extraer_datos_propiedad(link)
        todos_los_datos.append(datos)

    except Exception as e:
        print(f"❌ Error en {link}: {e}")

# Guardar en CSV
df = pd.DataFrame(todos_los_datos)
df.to_csv(f"Data/{ciudad}/propiedades_{ciudad}7.csv", index=False, encoding="utf-8")

driver.quit()
print(f"✅ Extracción finalizada. Archivo guardado como 'propiedades_{ciudad}7.csv'")
