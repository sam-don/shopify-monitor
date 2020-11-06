import requests
import time
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

webhook = DiscordWebhook(url=WEBHOOK_URL)

# URL of Shopify store to monitor
url = 'https://happyvalleyshop.com/collections/vinyl/'

# Add required url bits if necessary
if 'https' not in url:
    url = 'https://' + url

if url[-1] != '/':
    url += '/'

shopify_url = url + 'products.json'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
    'Connection': 'keep-alive'
}

print("Starting Shopify Monitor...")

r = requests.get(shopify_url, headers=headers)

# Initial list of products, the next request will compare against this
old_product_list = r.json()['products']

while True:
    # 5 minute wait between requests, to avoid being blocked by bot prevention
    time.sleep(300)

    try:
        r = requests.get(shopify_url, headers=headers)

        # Get product list again
        new_product_list = r.json()['products']

        # Check for difference between the two product lists, should update to only check product IDs
        diff = [i for i in old_product_list + new_product_list if i not in old_product_list or i not in new_product_list]

        if not diff:
            print("No new products")

        for product in diff:
            print(f"New product found! {product['title']}")

            # Create embed object for webhook with product title, and link to product in description
            embed = DiscordEmbed(title=f"{product['title']}",
                                description=f"[Product Link]({url}/products/{product['handle']})",
                                color=242424)

            # Add product image to embed if available
            if product['images'][0]:
                embed.set_image(url=product['images'][0]['src'])

            # Create add to cart links for all the variants of the product
            # These links automatically add one of the product variant to the cart and takes the user to checkout
            atc_links = ""
            for variant in product['variants']:
                atc_links += f"[ [{variant['title']} - ${variant['price']}]({url}cart/{variant['id']}:1) ]"
            
            embed.add_embed_field(
                name="ATC Links", 
                value=atc_links)

            # Add embed object to webhook, execute to send to discord, and remove the embed from the list
            webhook.add_embed(embed)
            response = webhook.execute()
            webhook.remove_embed(0)

        # Make the new product list the old product list, ready for comparison on next request
        old_product_list = new_product_list

    # Not the greatest error handling, but will keep the monitor running if anything goes wrong
    except Exception as error:
        print("Something went wrong!", error)
        continue
