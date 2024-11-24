import asyncio
import os
import time
from datetime import datetime, timezone

import nest_asyncio
import pytz
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot

# Determina ambiente: staging — usado localmente com ‘ids’ de teste / prod — usado no git
enviroment = "staging"

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
    prices = soup.find_all('span', class_='andes-money-amount__fraction')
    old_price = int(prices[0].get_text(strip=True).replace('.', ''))
    new_price = int(prices[1].get_text(strip=True).replace('.', ''))
    installment_price = int(prices[2].get_text(strip=True).replace('.', ''))

    timestamp = get_brt_timestamp()

    return {
        'product_name': product_name,
        'old_price': old_price,
        'new_price': new_price,
        'installment_price': installment_price,
        'timestamp': timestamp
    }


async def send_telegram_message(text, chat_ids):
    """Envia uma mensagem para múltiplos chats do Telegram."""
    for chat_id in chat_ids:  # Itera sobre a lista de chat_ids
        await bot.send_message(chat_id=chat_id, text=text)  # Change CHAT_ID to chat_id


async def main():
    # Lista de URLs dos produtos
    product_urls = [
        'https://www.mercadolivre.com.br/fila-float-maxxi-2-pro-masculino-adultos-esmeralda/p/MLB37880230?product_trigger_id=MLB37880234&attributes=COLOR%3AEsmeralda%2CSIZE%3A40+BR&pdp_filters=item_id%3AMLB3905376889&applied_product_filters=MLB37880234&quantity=1',
        'https://www.mercadolivre.com.br/samsung-galaxy-buds3-fone-de-ouvido-sem-fio-galaxy-ai-cinza/p/MLB38059088?pdp_filters=deal%3AMLB1184464-1#polycard_client=search-nordic&wid=MLB3797351091&sid=search&searchVariation=MLB38059088&position=2&search_layout=grid&type=product&tracking_id=c27e8a5b-7ba4-47e3-91c4-6d85a17bd833',
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

            # Aguarda alguns segundos entre as requisições para evitar bloqueios
            time.sleep(5)

    except KeyboardInterrupt:
        print("Parando a execução...")
    finally:
        print("Execução finalizada com sucesso")


nest_asyncio.apply()

asyncio.run(main())
