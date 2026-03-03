import requests
from bs4 import BeautifulSoup
import csv
import urllib3
import time
from urllib.parse import urljoin

# Desactivamos advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extraer_mails_hcdn():
    url_base = "https://www.diputados.gov.ar"
    url_index = f"{url_base}/diputados/index.html"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    print("Paso 1: Obteniendo el directorio de perfiles desde el índice...")

    try:
        res_index = requests.get(url_index, headers=headers, verify=False, timeout=15)
        if res_index.status_code != 200:
            print(f"Error al acceder al índice. Código HTTP: {res_index.status_code}")
            return

        sopa_index = BeautifulSoup(res_index.text, 'html.parser')
        enlaces_perfiles = set()

        # Recolectamos todos los enlaces de la grilla principal
        for enlace in sopa_index.find_all('a', href=True):
            href = enlace['href']
            url_completa = urljoin(url_index, href)

            # Filtramos para quedarnos con los que son perfiles (evitamos el index, redes sociales externas, o PDFs)
            if 'diputados.gov.ar/diputados/' in url_completa and url_completa != url_index and not url_completa.endswith(
                    ('.pdf', '.png', '.jpg')):
                enlaces_perfiles.add(url_completa)

        if not enlaces_perfiles:
            print("No se encontraron enlaces a perfiles en el índice.")
            return

        print(f"Se detectaron {len(enlaces_perfiles)} perfiles. Iniciando extracción de correos...")
        print("Esto puede demorar unos minutos (se procesa uno por uno para evitar bloqueos del servidor).\n")

        diputados_mails = set()

        # Paso 2: Entrar a cada perfil y extraer el correo
        for i, url_perfil in enumerate(enlaces_perfiles, 1):
            try:
                res_perfil = requests.get(url_perfil, headers=headers, verify=False, timeout=10)
                sopa_perfil = BeautifulSoup(res_perfil.text, 'html.parser')

                # Buscamos específicamente los enlaces mailto: en el bloque de contacto
                for a in sopa_perfil.find_all('a', href=True):
                    if 'mailto:' in a['href']:
                        # Lo limpiamos y lo pasamos a minúsculas
                        mail = a['href'].replace('mailto:', '').strip().lower()
                        diputados_mails.add(mail)
                        print(f"[{i}/{len(enlaces_perfiles)}] Éxito: {mail}")
                        break

            except requests.exceptions.RequestException as e:
                print(f"[{i}/{len(enlaces_perfiles)}] Error al cargar {url_perfil}: {e}")

            # Pausa obligatoria de 0.5 segundos para cuidar la conexión
            time.sleep(0.5)

        if not diputados_mails:
            print("Finalizó el escaneo pero no se pudieron extraer correos.")
            return

        # Paso 3: Exportar el resultado final
        with open('mails_diputados.csv', mode='w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(['Email Institucional'])
            # Los guardamos ordenados alfabéticamente
            for mail in sorted(diputados_mails):
                escritor.writerow([mail])

        print(f"\n¡Proceso finalizado! Se guardaron {len(diputados_mails)} correos únicos en 'mails_diputados.csv'.")

    except Exception as e:
        print(f"Ocurrió un error inesperado de conexión: {e}")


if __name__ == "__main__":
    extraer_mails_hcdn()