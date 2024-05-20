import json
import requests
from bs4 import BeautifulSoup


urls = ["https://brandshop.ru/muzhskoe/obuv/krossovki/?page=", "https://brandshop.ru/zhenskoe/obuv/krossovki/?page="]
headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36"
    }
def get_data(url):
    global try_next_page
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    items = soup.find_all("div", class_="product-card")
    try:
        pag_button = soup.find("li", class_="pagination__item pagination__item_arrow pagination__item_next")
    except:
        try_next_page = False
    item_urls = []
    for item in items:
        try:
            item_url = "https://brandshop.ru" + item.find("a", class_="product-card__link").get("href")
        except:
            continue
        item_urls.append(item_url)
    return item_urls

def get_item_info(item_urls):
    item_data_list = []

    for item_url in item_urls:
        descriptions = []
        req = requests.get(item_url, headers=headers)
        src = req.text
        soup = BeautifulSoup(src, "lxml")
        item_data = soup.find("div", class_="page__container container")
        try:
            title = item_data.find("span", class_="product-page__subheader font font_m font_grey").text.strip()
        except:
            title = "The title was not found"
        try:
            store = item_data.find("a", class_="product-page__header font font_title-l").get_text()
        except:
            store = "The store was not found"
        link = item_url
        try:
            price = item_data.find("div", class_="product-order__price_new").get_text().replace("₽", "").strip()
            priceOld = item_data.find("span", class_="product-order__price_old").get_text().replace("₽", "").strip()
        except:
            price = item_data.find("div", class_="product-order__price-wrapper").text.replace("₽", "").strip()
            priceOld = None
        type = "normal"
        if count == 1:
            gender = "Мужское"
        else:
            gender = "Женское"
        try:
            description = soup.find(class_="product-menu__content").text
        except:
            description = "The description was not found"
        try:
            category = soup.find_all("li", itemprop="itemListElement")[3].get_text()
        except:
            category = "The category was not found"
        try:
            size = soup.find("div", class_="product-plate product-page__plate")
            table_size = []
            for sizes in size:
                item_size = sizes.text.split("\n")[1].strip()
                table_size.append(
                    {
                        "title": "Size",
                        "value": item_size
                    }
                )
        except:
            table_size = "The size was not found"
        try:
            class_image = soup.find_all(class_="product-page__img _ibg")
            image_list = []
            for src in class_image:
                image_link = src.img["src"]
                image_list.append(image_link)

        except:
            image_list = "The image was not found"
        try:
            product_data = soup.find_all("div", class_="product-data__name font_m")
            article = product_data[0].text
            code_item = product_data[1].text
        except:
            article = "The article was not found"
            code_item = "The code_item was not found"
        locale = None
        try:
            color_types = []
            colors = item_data.find(class_="product-colors")
            for color in colors:
                color_types.append(
                    {
                        "title": "Color",
                        "value": color.get_text()
                    }
                )
        except:
            color_types = "The color was not found"
        descriptions.append(
            {
                "title" : "color",
                "text" : color_types
            }
        )
        descriptions.append(
            {
                "title" : "description",
                "text" : description
            }
        )
        descriptions.append(
            {
                "title": "article",
                "text": article
            }
        )
        descriptions.append(
            {
                "title": "code_item",
                "text": code_item
            }
        )
        descriptions.append(
            {
                "title": "size",
                "text": "",
                "table": table_size
            }
        )
        descriptions.append(
            {
                "title": "IMG",
                "value": image_list
            }
        )

        item_data_list.append(
            {
                "title" : title,
                "store" : store,
                "link" : link,
                "price" : price,
                "priceOld" : priceOld,
                "type" : type,
                "gender" : gender,
                "description" : descriptions,
                "category" : category,
                "locale" : locale
            }
        )


    return item_data_list

def write_json(item_data_list):
    with open("item_data.json", "a", encoding="utf-8") as file:
        json.dump(item_data_list, file, indent=4,  ensure_ascii=False)

def main():
    global try_next_page, count
    count = 1
    for url in urls:
        try_next_page = True
        for i in range(1, 500):
            if try_next_page == True:
                items_urls_list = get_data(url + f"{i}")
                info = get_item_info(items_urls_list)
                write_json(info)
            else:
                break
        count += 1

if __name__ == "__main__":
    main()
