import asyncio
import os
import sqlite3
import time
from datetime import datetime, timezone

import nest_asyncio
import pandas as pd
import pytz
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot

# Determina ambiente: staging — usado localmente com ‘ids’ de teste / prod — usado no github
enviroment = "prod"

if enviroment == "staging":
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN_STAGING")
    TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS_STAGING").split(",")
    bot = Bot(token=TELEGRAM_TOKEN)

elif enviroment == "prod":
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TOKEN = TELEGRAM_TOKEN
    TELEGRAM_CHAT_IDS = [chat_id.strip() for chat_id in os.getenv("TELEGRAM_CHAT_IDS").split(",")]
    bot = Bot(token=TOKEN)

else:
    print("Verifique se o ambiente está correto")


def fetch_page(url):
    response = requests.get(url)
    return response.text


def get_brt_timestamp():
    utc_now = datetime.now(timezone.utc)
    brt_timezone = pytz.timezone('America/Sao_Paulo')
    brt_time = utc_now.astimezone(brt_timezone)
    timestamp = brt_time.strftime('%d-%m-%Y - %H:%M:%S')

    return timestamp


def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    product_name = soup.find('h1', class_='ui-pdp-title').get_text(strip=True)

    price_container = soup.find('div', class_='ui-pdp-price__main-container')

    old_price = None
    new_price = None
    installment_price = None

    if price_container:
        old_price_element = price_container.find('span', class_='andes-money-amount__fraction')
        if old_price_element:
            old_price = old_price_element.get_text(strip=True).replace('.', '')

        new_price_container = soup.find('div', class_='ui-pdp-price__second-line')
        if new_price_container:
            new_price_element = new_price_container.find('span', class_='andes-money-amount__fraction')
            if new_price_element:
                new_price = new_price_element.get_text(strip=True).replace('.', '')  # Remove ponto de milhares

        installment_price_element = price_container.find_all('span', class_='andes-money-amount__fraction')
        if len(installment_price_element) > 2:
            installment_price = installment_price_element[2].get_text(strip=True).replace('.', '')

    timestamp = get_brt_timestamp()

    return {
        'product_name': product_name,
        'old_price': int(old_price) if old_price else 0,
        'new_price': int(new_price) if new_price else 0,
        'installment_price': int(installment_price) if installment_price else 0,
        'timestamp': timestamp
    }

def debug_soup(html):
    #Retorna o conteúdo do objeto BeautifulSoup para debug
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def create_connection(db_name = 'scrapper.db'):
    conn = sqlite3.connect(db_name)
    return conn

def setup_database(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrapper_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            old_price INTEGER,
            new_price INTEGER,
            installment_price INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()

def save_to_database(conn, data):
    df = pd.DataFrame([data])
    df.to_sql('scrapper_prices', conn, if_exists='append', index=False)


async def send_telegram_message(text, chat_ids):
    """Envia uma mensagem para múltiplos chats do Telegram."""
    for chat_id in chat_ids:  # Itera sobre a lista de chat_ids
        await bot.send_message(chat_id=chat_id, text=text)  # Change CHAT_ID to chat_id


async def main():
    conn = create_connection()
    setup_database(conn)

    # Lista de URLs dos produtos
    product_urls = [
        'https://www.mercadolivre.com.br/tnis-fila-float-maxxi-2-pro-color-esmeralda-adulto-41-br/p/MLB37880234?attributes=COLOR%3AEsmeralda%2CSIZE%3A41%20BR',
        'https://www.mercadolivre.com.br/samsung-galaxy-buds3-fone-de-ouvido-sem-fio-galaxy-ai-cinza/p/MLB38059088?pdp_filters=deal%3AMLB1184464-1#polycard_client=search-nordic&wid=MLB3797351091&sid=search&searchVariation=MLB38059088&position=2&search_layout=grid&type=product&tracking_id=c27e8a5b-7ba4-47e3-91c4-6d85a17bd833',
        'https://www.mercadolivre.com.br/samsung-galaxy-buds3-fone-de-ouvido-sem-fio-galaxy-ai-cor-branco-luz-branco/p/MLB38087949?product_trigger_id=MLB38059088&pdp_filters=deal%3AMLB1184464-1&applied_product_filters=MLB38059088&quantity=1',
        'https://www.mercadolivre.com.br/galaxy-buds-2-branco-samsung/p/MLB37005100?pdp_filters=official_store%3A2962#reco_item_pos=0&reco_backend=same-seller-odin&reco_backend_type=low_level&reco_client=pdp-seller_items-above&reco_id=a555107b-cda4-4620-8afb-f0cc3e421582&reco_model=machinalis-sellers-baseline',
        'https://www.mercadolivre.com.br/samsung-bluetooth-sm-r400nzapzto-branco-1/p/MLB27932663?product_trigger_id=MLB29595951&pdp_filters=official_store%3A2962&applied_product_filters=MLB27932663&quantity=1',
        'https://www.mercadolivre.com.br/lava-loucas-8-servicos-blf08bb-brastemp-cor-branco-220v/p/MLB19714945#polycard_client=search-nordic&wid=MLB2894978352&sid=search&searchVariation=MLB19714945&position=4&search_layout=stack&type=product&tracking_id=96110f96-2ced-4601-8c3a-cf4ea3ca0478',
        'https://www.mercadolivre.com.br/geladeira-frost-free-duplex-400-l-brm54jb-branca-brastemp-cor-branco-110v/p/MLB26852314#polycard_client=search-nordic&wid=MLB3005552935&sid=search&searchVariation=MLB26852314&position=2&search_layout=stack&type=product&tracking_id=91050e17-9554-4bec-ae80-c8de4145759c',
        'https://produto.mercadolivre.com.br/MLB-2749470194-lava-e-seca-brastemp-101kg6kg-branca-agua-quente-com-ciclo-_JM?searchVariation=174982136117#polycard_client=search-nordic&searchVariation=174982136117&position=7&search_layout=stack&type=item&tracking_id=0f13c8cb-925b-4447-b606-de613de30817',
        'https://produto.mercadolivre.com.br/MLB-2749184146-micro-ondas-brastemp-32-litros-branco-com-menu-gourmet-bms-_JM?searchVariation=174981147827#polycard_client=search-nordic&searchVariation=174981147827&position=11&search_layout=stack&type=item&tracking_id=ab67c270-ac41-40bd-90a7-b5a8055b575a'

    ]

    try:
        for product_url in product_urls:
            # Faz a requisição e parseia a página
            page_content = fetch_page(product_url)
            product_info = parse_page(page_content)

            # Obtém informações do produto
            new_price = product_info['new_price']
            product_name = product_info['product_name']
            timestamp = product_info['timestamp']

            # Formata a mensagem com o link
            message = (
                f"{product_name}\n"
                f"R$ {new_price},00 em {timestamp}.\n"
                f"[Link]({product_url})"
            )

            # Envia a mensagem para os chats com parse_mode='Markdown'
            chat_ids = TELEGRAM_CHAT_IDS
            for chat_id in chat_ids:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

            save_to_database(conn, product_info)
            print("Dados salvos no banco:", product_info)

            # Aguarda alguns segundos entre as requisições para evitar bloqueios
            time.sleep(5)

    except KeyboardInterrupt:
        print("Parando a execução...")
    finally:
        print("Execução finalizada com sucesso")


if __name__ == "__main__":
    asyncio.run(main())

