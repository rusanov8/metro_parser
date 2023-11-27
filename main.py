import csv
import json
import requests


def get_request_query(filename: str = None) -> dict:
    """
    Загружает запрос GraphQL из JSON файла.

    Параметры:
    - filename (str): Имя JSON файла с запросом GraphQL.

    Возвращает:
    - dict: Запрос GraphQL в виде словаря.
    """
    with open(filename, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def get_products_total(url: str, headers: dict, data: dict) -> int:
    """
        Получает общее количество товаров из GraphQL API.

        Параметры:
        - url (str): URL GraphQL API.
        - headers (dict): Заголовки для HTTP запроса.
        - data (dict): Данные запроса GraphQL.

        Возвращает:
        - int: Общее количество товаров.
    """
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json().get("data", {}).get("category", {})
        total = response_data['total']
        return total
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")
        return 0


def get_products_data(url: str, headers: dict, data: dict) -> list[dict]:
    """
       Получает данные о товарах из GraphQL API.

       Параметры:
       - url (str): URL GraphQL API.
       - headers (dict): Заголовки для HTTP запроса.
       - data (dict): Данные запроса GraphQL.

       Возвращает:
       - list: Список словарей с данными о товарах.
    """
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        products_data = response.json().get("data", {}).get("category", {}).get("products", [])
        return products_data
    except requests.exceptions.RequestException as e:
            print(f"Error in API request: {e}")
            return []


def save_data_to_csv(data: list[dict], filename: str = None) -> None:
    """
      Сохраняет данные о товарах в CSV файл, исключая товары, которые отсутствуют в наличии.

      Параметры:
      - data (list[dict]): Список словарей с данными о товарах.
      - filename (str): Имя CSV файла.

      Примечание:
      Товары записываются в CSV только в том случае, если они находятся в наличии (stock_value > 0).
      Записываются следующие данные: ID товара, наименование, ссылка на товар, регулярная цена, промо цена, бренд.
      """

    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['ID товара', 'Наименование', 'Ссылка на товар', 'Регулярная цена', 'Промо цена', 'Бренд'])

        for product in data:

            stocks = product.get('stocks', [{}])
            stock_value = stocks[0].get('value', 0)

            if stock_value > 0:

                product_id = product.get('id', '')
                name = product.get('name', '')
                url = 'https://online.metro-cc.ru' + product.get('url', '')

                prices_data = stocks[0].get('prices', {})

                promo_price = prices_data.get('price', '') if prices_data.get('old_price') is not None else ''
                regular_price = prices_data.get('old_price', '') if prices_data.get('old_price') is not None else prices_data.get('price', '')

                brand = product.get('manufacturer', {}).get('name', '')

                csv_writer.writerow([product_id, name, url, regular_price, promo_price, brand])


def main() -> None:

    """
       Основная функция для выполнения запроса к GraphQL API и сохранения данных в CSV файл.
       Выбранная категория для парсинга - чай.
    """

    category_slug = 'chay'

    url = 'https://api.metro-cc.ru/products-api/graph'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    request_variables = {
        "storeId": 10,
        "size": 0,
        "from": 0,
        "slug": category_slug
    }

    query_data = get_request_query(filename='graphql_query.json')
    query_data['variables'] = request_variables

    total = get_products_total(url, headers, query_data)

    query_data['variables']['size'] = total
    products_data = get_products_data(url, headers, query_data)

    filename = 'result.csv'
    save_data_to_csv(products_data, filename)


if __name__ == "__main__":
    main()


