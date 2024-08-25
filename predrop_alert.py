from time import sleep
import requests as req
import json
from utils import read_message_from_file, get_json
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import re
from keep_alive import keep_alive
load_dotenv()

MY_ID = 2063066217
PRODUCTS_PAGE_URL = 'https://www.dzrt.com/ar/our-products.html'
product_details = get_json('./product_details.json')

# BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_TOKEN = '7304572629:AAHGVsU9cvm0eGBMyMe2PkmwHZT5Os5DEyY' #main test features token
MAIN_CHANNEL_ID = -1002022588564
ALL_NOTIFICATIONS_CHANNEL = -1002103841630
TEST_FEATURES_CHANNEL = -1002173791007

BOT_SEND_MESSAGE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
BOT_SEND_PHOTO_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
BOT_EDIT_MESSAGE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption'
NOTIFICATION_MSG_TEMPLATE = read_message_from_file('./available_notification_msg.txt')

LOGIN_URL = 'https://www.dzrt.com/ar/customer/account/login/referer/aHR0cHM6Ly93d3cuZHpydC5jb20vYXIvY2hlY2tvdXQvY2FydC9pbmRleC8%2C/'
CART_URL = 'https://www.dzrt.com/ar/checkout/cart/'

EMAIL = 'Felks106@gmail.com'
PWD = 'saud1288-'

previous_predrop_notifications = []

TWO_LINE_UNAVAILABLE = 2
ONE_LINE_PREDROP = 1
ZERO_LINE_AVAILABLE = 0

previous_product_statuses = {
    "HIGHLAND BERRIES 10MG": None,
    "HIGHLAND BERRIES 6MG": None,
    "PURPLE MIST 6MG": None,
    "PURPLE MIST 3MG": None,
    "ICY RUSH 10MG": None,
    "GARDEN MINT 6MG": None,
    "MINT FUSION 6MG": None,
    "SEASIDE FROST 10MG": None,
    "EDGY MINT 6MG": None,
    "SAMRA 10MG": None,
    "TAMRA 6MG": None,
    "HAILA 10MG": None
}

nicotine_strength_en = {
    '٣ ملغ': '3MG',
    '٦ ملغ': '6MG',
    '١٠ ملغ': '10MG',
}

def delete_predrop_msg(msg_id):
    
    sleep(3)
    req.post(
        url='https://api.telegram.org/bot7304572629:AAHGVsU9cvm0eGBMyMe2PkmwHZT5Os5DEyY/deleteMessage',
        data={
            'chat_id' : MAIN_CHANNEL_ID,
            'message_id': msg_id
        }
    )

def send_tg_text_msg(chat_id, msg_text, bot_token):
    
    return req.post(
        url=f'https://api.telegram.org/bot{bot_token}/sendMessage',
        data={
            'chat_id' : chat_id,
            'text': msg_text,
            'parse_mode': 'Markdown',
        }
    )

def check_predrop(page):

    global previous_product_statuses
    cart_items = page.locator('tbody.cart.item').all()

    for i, item in enumerate(cart_items):
        product_name = item.locator('.product-item-name').text_content().strip()
        lines_num = item.locator('.message.error').count()
        nicotine_strength_txt = item.locator('.item-options dd').text_content().strip()
        nicotine_strength = nicotine_strength_txt if not 'ملغ' in nicotine_strength_txt else nicotine_strength_en[nicotine_strength_txt]
        name_nicotine = product_details[product_name]['en'] + ' ' + nicotine_strength
        print(name_nicotine, ':', lines_num, flush=True)

        if previous_product_statuses[name_nicotine] == TWO_LINE_UNAVAILABLE and lines_num == ONE_LINE_PREDROP:
            if (product_name == 'هايلاند بيريز' and nicotine_strength == '10MG')\
                or (product_name == 'بيربل مست' and nicotine_strength == '6MG')\
                and cart_items[i-1].locator('.message.error').count() == 0:
                continue
            
            msg_product_name = product_name + (f' {nicotine_strength_txt}' if product_name in ['هايلاند بيريز', 'بيربل مست'] else '')
            req.post(
                url=f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                data={
                    # 'chat_id' : product_details[product_name]['channel_id'],
                    'chat_id' : TEST_FEATURES_CHANNEL,
                    'text': f'🔔 {msg_product_name} سيتوفر قريباً استعد للصيد👑🏹',
                    'parse_mode': 'Markdown',
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{'text': '⚡️ اضغط لتسجيل الدخول ⚡️', 'url': LOGIN_URL}],
                        ]
                    }),
                }
            )
            print(name_nicotine, ' sent!', flush=True)
            
        previous_product_statuses[name_nicotine] = lines_num

    print('====================\n', flush=True)

def start_predrop_check():
    print('started predrop alert script!')

    with sync_playwright() as pl:
        firefox = pl.firefox.launch()
        context = firefox.new_context()
        page = context.new_page()
        page.route(re.compile(r"\.(jpg|png|svg|webp|jpeg)$"), lambda route: route.abort()) 
        login_tries = 0
        while login_tries < 5:
            try:
                page.goto(LOGIN_URL, timeout=60000)
                print('opened login page')
                page.wait_for_selector('.age-verification-popup-text.arabic .upper-age').click(timeout=60000)
                page.locator('.m-button.m-accept').click(timeout=60000)
                page.locator('#rememberuser').click(timeout=60000)
                sleep(5)
                page.locator('#email').type(EMAIL, delay=300)
                page.locator('#pass.password-input-field').type(PWD, delay=400)
                page.wait_for_selector('#send2.primary').click(timeout=60000)
                print('sent sign in')
                sleep(15)
                page.screenshot(path='f.png')
                req.post(
                    url=BOT_SEND_PHOTO_URL,
                    data={
                        'chat_id' : MY_ID,
                    },
                    files={'photo': open('f.png', 'rb')}
                )
                page.wait_for_url('https://www.dzrt.com/ar/checkout/cart/index/', timeout=60000)
                break
            except Exception as e:
                print(f'Predrop bot error: {e.with_traceback}')
            login_tries += 1
        else:
            print("Logging in didn't work after 5 tries...")
            return
        
        print('started predrop checking...')
        
        while True:
            try:
                check_predrop(page)
                sleep(3)
                page.reload()
            except Exception as e:
                print(f'Predrop bot error: {e}')
                # send_tg_text_msg(MY_ID, f'``` Predrop bot error: {e}```', '7006391375:AAGuA2TqB2vi1fumHMMj6aN_SHBH67N2VrM')

if __name__ == '__main__':
    keep_alive()
    start_predrop_check()
