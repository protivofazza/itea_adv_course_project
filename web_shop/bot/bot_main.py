from web_shop.bot.webshopbot import WebShopBot
from web_shop.bot.config import TOKEN
from web_shop.db.models import Category, Texts, News, Product, Customer, Cart
from web_shop.bot.keyboard import START_KB, ACCOUNT_KB
from telebot.types import (KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update)
from flask import Flask, request, abort
from .texts import set_params_text

bot = WebShopBot(TOKEN)
app = Flask(__name__)


@app.route('/', methods=['POST'])
def process_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(status=403)


# START
@bot.message_handler(commands=['start'])
def start(message):
    customer = Customer.objects.filter(user_id=message.chat.id)
    if not customer:
        Customer.objects.create(user_id=message.chat.id)

    buttons = [KeyboardButton(value) for value in START_KB.values()]
    text = Texts.objects.filter(text='Greeting')[0].body
    bot.send_message_or_photo(chat_id=message.chat.id, text=text, kb=bot.generate_reply_keyboard(buttons))


# START -> CART
@bot.message_handler(func=lambda msg: msg.text == START_KB['cart'])
def show_cart(message):
    customer = Customer.objects.filter(user_id=message.chat.id)
    if not customer:
        customer = Customer.objects.create(user_id=message.chat.id)
    else:
        customer = customer[0]
    bot.load_cart_data(customer, message.chat.id)


# START -> CART -> remove
@bot.callback_query_handler(func=lambda call: call.data.startswith('minus-'))
def remove_product(call):
    product_id = ''.join(call.data.split('-')[1::])
    customer = Customer.objects.filter(user_id=call.message.chat.id)[0]
    bot.remove_product_from_cart(product_id, customer)
    bot.update_cart_data(customer, call.message.chat.id, call.message.message_id)


# START -> CART -> add
@bot.callback_query_handler(func=lambda call: call.data.startswith('plus-'))
def add_product(call):
    product_id = ''.join(call.data.split('-')[1::])
    customer = Customer.objects.filter(user_id=call.message.chat.id)[0]
    bot.add_product_to_cart(product_id, customer)
    bot.update_cart_data(customer, call.message.chat.id, call.message.message_id)


# START -> CART -> order goods
@bot.callback_query_handler(func=lambda call: call.data.startswith('order-goods'))
def order_goods(call):
    customer = Customer.objects.filter(user_id=call.message.chat.id)[0]
    cart = customer.get_or_create_current_cart()[1]
    if len(cart.cart_items):
        is_valid, text = bot.is_customer_data_valid(customer)
        if not is_valid:
            bot.send_message_or_photo(call.message.chat.id, text)
        else:
            cart.archive()
            bot.edit_message(call.message.chat.id, "Заказ оформлен", call.message.message_id)
    else:
        bot.edit_message(call.message.chat.id, "Вы не выбрали ничего для оформления заказа", call.message.message_id)


# START -> OLD ORDERS
@bot.message_handler(func=lambda msg: msg.text == START_KB['history'])
def get_categories(message):
    customer = Customer.objects.filter(user_id=message.chat.id)[0]
    old_orders = Cart.objects.filter(customer=customer, is_archived=True)
    if len(old_orders):
        for old_cart in old_orders:
            text, kb = bot.generate_cart_message_data(old_cart, False)
            bot.send_message_or_photo(message.chat.id, text)
    else:
        bot.send_message_or_photo(message.chat.id, "У вас еще нет оформленных заказов")


# START -> CATEGORIES
@bot.message_handler(func=lambda msg: msg.text == START_KB['categories'])
def get_categories(message):
    categories = Category.get_root()
    buttons = [InlineKeyboardButton(text=category.title, callback_data=f"category-{category.id}") for category in
               categories]
    bot.send_message_or_photo(chat_id=message.chat.id, text="Выберите Категорию",
                              kb=bot.generate_inline_keyboard(buttons, row_width=2))


# START -> CATEGORIES -> category (recursive)
@bot.callback_query_handler(func=lambda call: call.data.startswith('category-'))
def category_handler(call):
    category_id = ''.join(call.data.split('-')[1::])
    category = Category.objects.get(id=category_id)
    if category.subcategories:
        bot.load_subcategories(category, call.message.chat.id, call.message.message_id)
    elif category.is_leaf:
        bot.load_category_products(category, call.message.chat.id)


# START -> NEWS
@bot.message_handler(func=lambda msg: msg.text == START_KB['news'])
def get_news(message):
    news = News.objects.filter()
    buttons = [InlineKeyboardButton(text=i.title, callback_data=f"news-{i.id}") for i in news[:4]]
    bot.send_message_or_photo(message.chat.id, START_KB['news'], bot.generate_inline_keyboard(buttons, row_width=1))


# START -> NEWS -> news
@bot.callback_query_handler(func=lambda call: call.data.startswith('news-'))
def get_certain_news(call):
    news_id = ''.join(call.data.split('-')[1::])
    news = News.objects.get(id=news_id)
    bot.send_message_or_photo(call.from_user.id, f"{news.title}\n\n{news.body}")


# START -> DISCOUNTS
@bot.message_handler(func=lambda msg: msg.text == START_KB['discount_products'])
def get_discount_products(message):
    products = Product.get_discount_products()
    bot.load_products(products, message.chat.id)


# START -> DISCOUNTS -> product
# START -> CATEGORIES -> category -> product
@bot.callback_query_handler(func=lambda call: call.data.startswith('product-'))
def get_certain_product(call):
    product_id = call.data.split('-')[-1]
    product = Product.objects.get(id=product_id)

    customer = Customer.objects.filter(user_id=call.from_user.id)
    if customer:
        customer = customer[0]
        cart = customer.get_or_create_current_cart()[1]
        cart.add_item(product)
        bot.send_message_or_photo(call.from_user.id, f"{product.title} добавлен в корзину")
    else:
        bot.send_message_or_photo(call.from_user.id, f"Нажмите /start для выбора действий")


# START -> SHOP INFO
@bot.message_handler(func=lambda msg: msg.text == START_KB['Shop_info'])
def shop_info(message):
    text = Texts.objects.filter(text='Shop_info')[0].body
    bot.send_message_or_photo(chat_id=message.chat.id, text=text)


# START -> NAVIGATION
@bot.message_handler(func=lambda msg: msg.text == START_KB['Navigation'])
def navigation_info(message):
    text = Texts.objects.filter(text='Navigation')[0].body
    bot.send_message_or_photo(chat_id=message.chat.id, text=text)


# START -> ACCOUNT
@bot.message_handler(func=lambda msg: msg.text == START_KB['Account'])
def account_info(message):
    try:
        text = "В данный момент в вашей учетной записи хранится такая информация:\n\n" + \
               str(Customer.objects.filter(user_id=message.chat.id)[0]) + \
               "\n\n\nЕсли надо изменить данные, следуйте инструкциям по шаблону:\n- д" \
               + set_params_text[1:]
    except IndexError:
        text = "Вы не создавали учетную запись"
    bot.send_message_or_photo(chat_id=message.chat.id, text=text)


# SET_[NAME/SURNAME/ADDRESS/PHONE_NUMBER/AGE] param_data
@bot.message_handler(commands=['set_name', 'set_surname', 'set_address', 'set_phone_number', 'set_age'])
def set_data(message):
    customer = Customer.objects.filter(user_id=message.chat.id)[0]
    param: str = '_'.join(message.text.split('_')[1:]).split(' ')[0]
    param_data: str = ' '.join(message.text.split(' ')[1:])
    bot.set_customer_data(customer, param, param_data, message.chat.id)


def set_webhook():
    import time
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(
        url='https://216.250.119.29/tg',
        certificate=open('web_shop/bot/webhook_cert.pem', 'r')
    )

