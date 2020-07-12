from flask_restful import Api
from web_shop.bot.bot_main import app
from .resources import CategoryResource, CartResource, CustomerResource, NewsResource, TextsResource, ProductResource


def start():
    api = Api(app)
    api.add_resource(CategoryResource, '/category', '/category/<category_id>')
    api.add_resource(CustomerResource, '/customer', '/customer/<customer_id>',
                     '/customer/<customer_id>/<property_name>')
    api.add_resource(CartResource, '/cart', '/cart/<cart_id>')
    api.add_resource(ProductResource, '/product', '/product/<product_id>')
    api.add_resource(TextsResource, '/texts', '/texts/<text_id>')
    api.add_resource(NewsResource, '/news', '/news/<news_id>')
