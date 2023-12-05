import requests
from bs4 import BeautifulSoup
import os
import csv
import shutil

class Scraper:
    # Constructor de la clase, inicializa con la URL a raspar.
    def __init__(self, url):
        self.url = url

    # Método para obtener el HTML de la página web.
    def fetch_html(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            formatted_html = soup.prettify()
            return formatted_html
        else:
            raise Exception(f"Error al obtener la página: {response.status_code}")

    # Método para guardar el HTML obtenido en un archivo.
    def save_html(self, html, filename="html_temp.html"):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html)

    # Método para extraer enlaces de noticias de un HTML dado.
    def extract_news_links(self, html, max_links):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.find('ul', {'data-testid': 'topic-promos'}).find_all('li', limit=max_links)
        links = [item.find('a')['href'] for item in news_items]
        return links

    # Método para crear una carpeta si no existe.
    def create_folder(self, nombre_carpeta):
        if not os.path.exists(nombre_carpeta):
            os.makedirs(nombre_carpeta)
        else:
            print(f"La carpeta '{nombre_carpeta}' ya existe.")

    # Método para extraer información relevante de un archivo HTML.
    def extraer_informacion_html(self, archivo_html):
        # Intenta abrir y leer el archivo HTML
        try:
            with open(archivo_html, 'r', encoding='utf-8') as file:
                contenido = file.read()
                soup = BeautifulSoup(contenido, 'html.parser')
                
                # Intenta extraer el título, autor y texto del contenido HTML
                try:
                    elemento_title = soup.select_one("div h1[id='content']")
                    title = elemento_title.get_text().replace('\n', ' ').strip() if elemento_title else "Título no encontrado."

                    elemento_autor = soup.select_one('section[aria-labelledby="article-byline"]')
                    autor = elemento_autor.get_text().replace('\n', '').strip() if elemento_autor else "Autor no encontrado."

                    # Extraer los elementos de texto (párrafos y subtítulos)
                    elementos_texto = soup.select('div[dir="ltr"] div[dir="ltr"] h2, p[dir="ltr"]')

                    # Compilar el texto total a partir de los elementos extraídos
                    texto_total = ""
                    for elem in elementos_texto:
                        texto = elem.get_text().replace('\n', ' ').strip()
                        texto_total = texto_total + "\n"+ texto

                    return title, autor, texto_total 
                    
                except FileNotFoundError:
                    return "Informacion no encontrado"
        
        except FileNotFoundError:
            return "Archivo no encontrado."

    # Método para guardar la información extraída en un archivo CSV.
    def guardar_en_csv(self, datos, nombre_archivo_csv):
        with open(nombre_archivo_csv, mode='w', newline='', encoding='utf-8') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerow(['Título', 'Autor', 'Texto'])
            for dato in datos:
                escritor_csv.writerow(dato)

    # Método para eliminar una carpeta y su contenido.
    def eliminar_carpeta(self, ruta_carpeta):
        if os.path.exists(ruta_carpeta) and os.path.isdir(ruta_carpeta):
            shutil.rmtree(ruta_carpeta)
            print(f"La carpeta '{ruta_carpeta}' ha sido eliminada.")
        else:
            print(f"La carpeta '{ruta_carpeta}' no existe o no es una carpeta.")

    # Método principal que orquesta la ejecución del scraping.
    def run(self, max_links=18):
        if max_links > 18:
            raise Exception(f"Solo se pueden maximos 18.")
        else:
            formatted_html = self.fetch_html()
            #self.save_html(formatted_html,"html_main.py")
            news_links = self.extract_news_links(formatted_html, max_links)
            self.create_folder("noticias")
            
            datos_para_csv = []

            for link in news_links:
                self.url = link
                formatted_html = self.fetch_html()
                self.save_html(formatted_html,"noticias/" + str(link.replace("/","")) + ".html")
                title, autor, texto_total  = self.extraer_informacion_html("noticias/" + str(link.replace("/","")) + ".html")
                datos_para_csv.append([title,autor,texto_total])

            self.guardar_en_csv(datos_para_csv, 'datos_noticias.csv')

            self.eliminar_carpeta("noticias")
