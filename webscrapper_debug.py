from webscrapper import fetch_page, debug_soup
from bs4 import BeautifulSoup

if __name__ == "__main__":
    # URL de exemplo
    url = 'https://www.mercadolivre.com.br/tnis-fila-float-maxxi-2-pro-color-esmeralda-adulto-41-br/p/MLB37880234?attributes=COLOR%3AEsmeralda%2CSIZE%3A41%20BR'

    # Obtenha o HTML da página
    html_content = fetch_page(url)

    # Use a função debug_soup para processar o HTML
    soup_debug = debug_soup(html_content)

    # Exibe o conteúdo formatado do soup
    print(soup_debug.prettify())

    # A partir do debug, você pode acessar as variáveis de interesse:
    # 1. Encontra o título do produto
    product_name = soup_debug.find('h1', class_='ui-pdp-title')
    if product_name:
        print("Product Name:", product_name.get_text(strip=True))

    # 2. Encontra o container de preços dentro do título do produto
    price_container = soup_debug.find('div', class_='ui-pdp-price__main-container')
    if price_container:
        # 3. Encontra o preço original
        old_price = price_container.find('span', class_='andes-money-amount__fraction')
        if old_price:
            old_price_value = old_price.get_text(strip=True)
            print("Old Price:", old_price_value)

        # 4. Encontra o preço atual
        new_price_container = soup_debug.find('div', class_='ui-pdp-price__second-line')
        if new_price_container:
            new_price = new_price_container.find('span', class_='andes-money-amount__fraction')
            if new_price:
                new_price_value = new_price.get_text(strip=True)
                print("New Price (without cents):", new_price_value)

            # 5. Encontra os centavos do preço atual (caso exista)
            cents = new_price_container.find('span', class_='andes-money-amount__cents')
            if cents:
                cents_value = cents.get_text(strip=True)
                # Concatenate cents to the new_price, ensuring the correct format (e.g., 1018.36)
                new_price_value = new_price_value.replace('.', '')  # Remove dot if exists
                new_price_value = new_price_value + '.' + cents_value  # Add dot and cents
                print("New Price (with cents):", new_price_value)
    else:
        print("Price container not found.")
