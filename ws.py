import time
# pip install txml something like that
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager import chrome

URL = 'https://br.investing.com/economic-calendar/'
HEADERS = ('Hora', 'Moeda', 'Import', 'Evento', 'Atual', 'Projecao', 'Previo')

scraping_time = time.time()

driver = webdriver.Chrome(chrome.ChromeDriverManager().install())

print("Opening URL...")
driver.get(URL)

print("Delay...")
time.sleep(5)

print("Setting weekly table...")
button = driver.find_element_by_id('timeFrame_thisWeek')
driver.execute_script("arguments[0].click();", button)

print("Delay...")
time.sleep(5)

print("Formatting HTML data...")
soup = BeautifulSoup(driver.page_source, 'html.parser')
formatted_rows = []

table = soup.find("table", {"id": "economicCalendarData"})
for row in table.findAll('tr', class_=lambda attr: attr is not None):
    row_cells = row.findAll('td')

    cols = [td.text.replace('\n', ' ').strip() for td in row_cells]
    cols[2] = row_cells[2].get('data-img_key')[4:]

    formatted_rows.append({HEADERS[i]:cols[i] for i in range(len(HEADERS))})

print("Storing data into dataframe...")
df = pd.DataFrame(formatted_rows, columns = HEADERS)

print("Filtering dataframe...")
df_old_len = len(df.index)
df = df.loc[(df.Moeda == 'BRL') | (df.Moeda == 'USD')]
print(f"Size before: {df_old_len}, size now: {len(df.index)}.")

print("Writing dataframe into .csv...")
# UTF-8-SIG to deal with byte order mark
df.to_csv(
    'data_economic_calendar.csv', 
    header=['Hora', 'Moeda', 'Import.', 'Evento', 'Atual', 'Projeção', 'Prévio'], 
    encoding='utf-8-sig', 
    index=False
)

print("Closing browser...")
driver.quit()

print(f"Scraping took {time.time() - scraping_time} second(s).")