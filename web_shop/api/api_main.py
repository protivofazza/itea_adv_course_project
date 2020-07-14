from flask_restful import Api
from web_shop.bot.bot_main import app
from .resources import CategoryResource, CartResource, CustomerResource, NewsResource, TextsResource, ProductResource


def start():
    api = Api(app)
    api.add_resource(CategoryResource, '/tg/category', '/tg/category/<category_id>')
    api.add_resource(CustomerResource, '/tg/customer', '/tg/customer/<customer_id>',
                     '/tg/customer/<customer_id>/<property_name>')
    api.add_resource(CartResource, '/tg/cart', '/tg/cart/<cart_id>')
    api.add_resource(ProductResource, '/tg/product', '/tg/product/<product_id>')
    api.add_resource(TextsResource, '/tg/texts', '/tg/texts/<text_id>')
    api.add_resource(NewsResource, '/tg/news', '/tg/news/<news_id>')
