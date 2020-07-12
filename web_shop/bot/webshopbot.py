from telebot import TeleBot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from .texts import set_params_text, success_texts
from ..db.data_validators import is_phone_valid, is_age_valid

from typing import List, Union


class WebShopBot(TeleBot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_inline_keyboard(self, buttons: List[InlineKeyboardButton], row_width=3):
        kb = InlineKeyboardMarkup(row_width=row_width)
        kb.add(*buttons)
        return kb

    def generate_reply_keyboard(self, buttons: List[KeyboardButton]):
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(*buttons)
        return kb

    def send_message_or_photo(self, chat_id: int, text: str,
                              kb: Union[ReplyKeyboardMarkup, InlineKeyboardMarkup] = None,
                              photo_bytes=None
                              ):
        if photo_bytes:
            self.send_photo(chat_id=chat_id, caption=text, photo=photo_bytes, reply_markup=kb)
        else:
            self.send_message(chat_id=chat_id, text=text, reply_markup=kb)

    def edit_message(self, chat_id: int, text: str, message_id: int,
                     kb: Union[InlineKeyboardMarkup] = None
                     ):
        self.edit_message_text(chat_id=chat_id, text=text, reply_markup=kb, message_id=message_id)

    def load_products(self, products, chat_id):
        for product in products:
            buttons = [InlineKeyboardButton(text="В корзину", callback_data=f"product-{product.id}")]
            self.send_message_or_photo(chat_id,
                                       f"{product.title}\n{product.description}\n"
                                       f"Товар в категории: {product.category.title}\n"
                                       f"Цена: {product.get_price()} грн" +
                                       (f" акционная, вместо изначальной {product.price} грн!"
                                        if product.get_price() != product.price else f""),
                                       self.generate_inline_keyboard(buttons),
                                       product.image.read() if product.image else None)
        if len(products) == 0:
            self.send_message_or_photo(chat_id,
                                       f"Все распродано! В этой категории пока нет товаров")

    def load_subcategories(self, category, chat_id, message_id):
        buttons = []
        if category.parent:
            buttons += [InlineKeyboardButton(text='<-<- Назад', callback_data=f"category-{category.parent.id}")]
        buttons += [InlineKeyboardButton(text=category.title, callback_data=f"category-{category.id}") for category in
                    category.subcategories]
        self.edit_message(chat_id, category.title, message_id,
                          self.generate_inline_keyboard(buttons, row_width=2))

    def load_category_products(self, category, chat_id):
        self.load_products(category.products, chat_id)

    def generate_cart_message_data(self, cart, load_buttons=True):
        text = "Покупки в корзине:\n"
        total = 0
        buttons = []
        for item in cart.cart_items:
            text += f"{item.product.title} - {item.count}\n"
            total += item.product.get_price() * item.count
            buttons += [InlineKeyboardButton(text='-', callback_data=f"minus-{item.product.id}"),
                        InlineKeyboardButton(text=f'{item.product.title}', callback_data="unreal_data"),
                        InlineKeyboardButton(text='+', callback_data=f"plus-{item.product.id}")]
        text += f"Общая цена: {total} грн"
        buttons += [InlineKeyboardButton(text="Заказать", callback_data='order-goods')]
        kb = self.generate_inline_keyboard(buttons) if load_buttons else None
        return text, kb

    def load_cart_data(self, customer, chat_id):
        cart = customer.get_or_create_current_cart()[1]
        text, kb = self.generate_cart_message_data(cart)
        self.send_message_or_photo(chat_id, text, kb)

    def update_cart_data(self, customer, chat_id, message_id):
        cart = customer.get_or_create_current_cart()[1]
        text, kb = self.generate_cart_message_data(cart)
        self.edit_message(chat_id, text, message_id, kb)

    def add_product_to_cart(self, product_id, customer):
        cart = customer.get_or_create_current_cart()[1]
        for item in cart.cart_items:
            if str(item.product.id) == product_id:
                item.count += 1
                break
        cart.save()

    def remove_product_from_cart(self, product_id, customer):
        cart = customer.get_or_create_current_cart()[1]
        pop = None
        for i, item in enumerate(cart.cart_items):
            if str(item.product.id) == product_id:
                item.count -= 1
                if item.count == 0:
                    pop = i
                break
        if pop is not None:
            cart.cart_items.pop(pop)
        cart.save()

    def set_customer_data(self, customer, param, param_data, chat_id):
        if not param_data:
            self.send_message_or_photo(chat_id, set_params_text)
            return None
        if param == 'name':
            customer.name = param_data
        elif param == 'surname':
            customer.surname = param_data
        elif param == 'address':
            customer.address = param_data
        elif param == 'phone_number':
            if is_phone_valid(param_data):
                customer.phone_number = param_data
            else:
                self.send_message_or_photo(chat_id, "Неверный формат, шаблон: +380xxxxxxxxx")
                return None
        elif param == 'age':
            if is_age_valid(param_data):
                customer.age = param_data
            else:
                self.send_message_or_photo(chat_id, "Возраст надо ввести числом")
                return None
        customer.save()
        self.send_message_or_photo(chat_id, success_texts[param])
        if param == 'age' :
            self.send_message_or_photo(chat_id, f"Если вы внесли все данные, можете перейти в корзину")

    def is_customer_data_valid(self, customer):
        name = True if customer.name is not None else False
        surname = True if customer.surname is not None else False
        address = True if customer.address is not None else False
        phone_number = True if customer.phone_number is not None else False
        age = True if customer.age is not None else False
        if not all([name, surname, address, phone_number, age]):
            return False, f"Для обработки заказа, надо заполнить учетную запись. " \
                          f"В данный момент не заполнены такие поля: \n" \
                          f"{'Имя, ' if not name else ''}" \
                          f"{'фамилия, ' if not surname else ''}" \
                          f"{'адрес, ' if not address else ''}" \
                          f"{'телефон, ' if not phone_number else ''}" \
                          f"{'возраст' if not age else ''}.\n\n" + set_params_text
        return True, ''
