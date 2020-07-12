from flask_restful import Resource
from flask import request, jsonify
import web_shop.db.models as m
from web_shop.api import schemas as s
from web_shop.log_writer import log_write


class GlobalResource:

    @staticmethod
    def get(model, schema, name, param):
        if param is not None:
            try:
                obj = model.objects.get(id=param)
                result = schema().dump(obj)
                log_write(f"Successful attempt to reach REST API GET -> '{name}' with id {param}")
            except (s.ValidationError, m.ValidationError, m.DoesNotExist) as e:
                log_write(
                    f"Unsuccessful attempt to reach REST API GET -> '{name}' with id {param}. Error: {str(e)}")
                result = str(e)
        else:
            objs = model.objects
            try:
                result = schema().dump(objs, many=True)
                log_write(f"Successful attempt to reach REST API GET -> '{name}'")
            except s.ValidationError as e:
                log_write(f"Unsuccessful attempt to reach REST API GET -> '{name}'. Error: {str(e)}")
                result = str(e)
        return jsonify(result)

    @staticmethod
    def post(model, schema, name):
        try:
            json = schema().load(request.get_json())
            result = schema().dump(model.objects.create(**json))
            log_write(f"Successful attempt to reach REST API POST -> '{name}'")
        except (s.ValidationError, m.NotUniqueError) as e:
            log_write(f"Unsuccessful attempt to reach REST API POST -> '{name}'. Error: {str(e)}")
            result = str(e)
        return jsonify(result)

    @staticmethod
    def put(model, schema, name, param):
        try:
            obj = model.objects.get(id=param)
            json: dict = schema().dump(obj)
            json.update(request.get_json())

            njson = {}
            for key, value in json.items():
                if json[key]:
                    njson[key] = value
            json = njson

            json = schema().load(json)
            obj.update(**json)
            obj.reload()
            result = schema().dump(obj)
            log_write(f"Successful attempt to reach REST API PUT -> '{name}' with id {param}")
        except (s.ValidationError, m.ValidationError, m.NotUniqueError, m.DoesNotExist) as e:
            log_write(
                f"Unsuccessful attempt to reach REST API PUT -> '{name}' with id {param}. Error: {str(e)}")
            result = str(e)
        return jsonify(result)

    @staticmethod
    def delete(model, name, param):
        if param:
            try:
                obj = model.objects.get(id=param)
                obj.delete()
                result = {'status': 'OK'}
            except (m.OperationError, m.ValidationError, m.DoesNotExist) as e:
                log_write(
                    f"Unsuccessful attempt to reach REST API DELETE -> '{name}' with id {param}. Error: {str(e)}")
                result = str(e)
        else:
            log_write(
                f"Unsuccessful attempt to reach REST API DELETE -> '{name}'. Error: parameter 'id' not specified!")
            result = {'status': 'Error'}
        return jsonify(result)


class CategoryResource(Resource):

    def get(self, category_id=None):
        return GlobalResource.get(m.Category, s.CategorySchema, 'category', category_id)

    def post(self):
        return GlobalResource.post(m.Category, s.CategorySchema, 'category')

    def put(self, category_id=None):
        return GlobalResource.put(m.Category, s.CategorySchema, 'category', category_id)

    def delete(self, category_id=None):
        return GlobalResource.delete(m.Category, 'category', category_id)


class CustomerResource(Resource):

    def get(self, customer_id=None, property_name=None):
        if property_name is None:
            return GlobalResource.get(m.Customer, s.CustomerSchema, 'customer', customer_id)
        else:
            if property_name == 'carts':
                try:
                    customer = m.Customer.objects.get(id=customer_id)
                    carts = m.Cart.objects.filter(customer=customer)
                    result = s.CartSchema().dump(carts, many=True)
                    log_write(f"Successful attempt to reach REST API GET -> 'customer' with id {customer_id}")
                except (s.ValidationError, m.ValidationError, m.DoesNotExist) as e:
                    log_write(
                        f"Unsuccessful attempt to reach REST API GET -> 'customer' with id {customer_id}. Error: {str(e)}")
                    result = str(e)
                return jsonify(result)
            else:
                log_write(
                    f"Unsuccessful attempt to reach REST API GET -> 'customer' with id {customer_id}. Property {property_name} is invalid")
                result = {"Status": "Error"}
                return jsonify(result)

    def post(self):
        return GlobalResource.post(m.Customer, s.CustomerSchema, 'customer')

    def put(self, customer_id=None):
        return GlobalResource.put(m.Customer, s.CustomerSchema, 'customer', customer_id)

    def delete(self, customer_id=None):
        return GlobalResource.delete(m.Customer, 'customer', customer_id)


class CartResource(Resource):

    def get(self, cart_id=None):
        return GlobalResource.get(m.Cart, s.CartSchema, 'cart', cart_id)

    def post(self):
        return GlobalResource.post(m.Cart, s.CartSchema, 'cart')

    def put(self, cart_id=None):
        return GlobalResource.put(m.Cart, s.CartSchema, 'cart', cart_id)

    def delete(self, cart_id=None):
        return GlobalResource.delete(m.Cart, 'cart', cart_id)


class ProductResource(Resource):

    def get(self, product_id=None):
        return GlobalResource.get(m.Product, s.ProductSchema, 'product', product_id)

    def post(self):
        return GlobalResource.post(m.Product, s.ProductSchema, 'product')

    def put(self, product_id=None):
        return GlobalResource.put(m.Product, s.ProductSchema, 'product', product_id)

    def delete(self, product_id=None):
        return GlobalResource.delete(m.Product, 'product', product_id)


class TextsResource(Resource):

    def get(self, text_id=None):
        return GlobalResource.get(m.Texts, s.TextsSchema, 'text', text_id)

    def post(self):
        return GlobalResource.post(m.Texts, s.TextsSchema, 'text')

    def put(self, text_id=None):
        return GlobalResource.put(m.Texts, s.TextsSchema, 'text', text_id)

    def delete(self, text_id=None):
        return GlobalResource.delete(m.Texts, 'text', text_id)


class NewsResource(Resource):

    def get(self, news_id=None):
        return GlobalResource.get(m.News, s.NewsSchema, 'news', news_id)

    def post(self):
        return GlobalResource.post(m.News, s.NewsSchema, 'news')

    def put(self, news_id=None):
        return GlobalResource.put(m.News, s.NewsSchema, 'news', news_id)

    def delete(self, news_id=None):
        return GlobalResource.delete(m.News, 'news', news_id)
