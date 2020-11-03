import requests
import time
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

webhook = DiscordWebhook(url=WEBHOOK_URL)


url = 'culturekings.com'

if 'https' not in url:
    url = 'https://' + url

if url[-1] != '/':
    url += '/'


shopify_url = url + 'products.json'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
    'Connection': 'keep-alive'
}

r = requests.get(shopify_url, headers=headers)

print(r.json()['products'])

print("Starting Shopify Monitor...")

old_product_list = r.json()['products']
time.sleep(300)

while True:

    try:
        r = requests.get(shopify_url, headers=headers)
    
        new_product_list = r.json()['products']

        diff = [i for i in old_product_list + new_product_list if i not in old_product_list or i not in new_product_list]

        if not diff:
            print("No new products")

        for product in diff:
            print(f"New product found! {product['title']}")

            # create embed object for webhook
            embed = DiscordEmbed(title=f"{product['title']}",
                                description=f"[Product Link]({url}/products/{product['handle']})",
                                color=242424)

            embed.set_image(url=product['images'][0]['src'])

            atc_links = ""
            for variant in product['variants']:
                atc_links += f"[ [{variant['title']}]({url}cart/{variant['id']}:1) ]"
            
            embed.add_embed_field(
                name="ATC Links", 
                value=atc_links)

            # add embed object to webhook
            webhook.add_embed(embed)

            response = webhook.execute()

            webhook.remove_embed(0)

        old_product_list = new_product_list

    except Exception as error:
        print("Something went wrong!", error)

    time.sleep(300)
