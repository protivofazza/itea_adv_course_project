from web_shop.bot.bot_main import start_bot, bot
from web_shop.bot import config
from flask import Flask, request, abort

from telebot.types import Update

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


if __name__ == '__main__':
    import time
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(
        config.WEBHOOK_URL,
        certificate=open('webhook_cert.pem', 'r')
    )
    app.run(debug=True, port=8000)




# from web_shop.bot.bot_main import bot, set_webhook, app
# from web_shop.db.seeder import seed, generate
# from web_shop.bot import config
# from web_shop.db.models import is_db_empty
# from web_shop.api.api_main import start as startAPI
# from web_shop.log_writer import log_write, log_clear
#
# from flask import Flask, request, abort
# from telebot.types import Update
#
#
# app = Flask(__name__)
#
#
# @app.route(config.WEBHOOK_PATH, methods=['POST'])
# def webhook():
#     if request.headers.get('content-type') =='application/json':
#         json_string = request.get_data().decode('utf-8')
#         update = Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return ''
#     else:
#         abort(status=403)
#
#
# if __name__ == '__main__':
#     print("Mark 1")
#     set_webhook()
#     print("Mark 2")
#     # import time
#     # bot.remove_webhook()
#     # time.sleep(1)
#     # bot.set_webhook(url=config.WEBHOOK_URL,
#     #                 certificate=open('webhook_cert.pem', 'r')
#     #                 )
#     print("Mark 3")
#     startAPI()
#     print("Mark 4")
#     app.run(debug=True, port=8000)
#
#
# # log_write("\n\nRESTARTING BOT..\n\n")
# # log_write("STARTING LOGGING..")
# # if is_db_empty():
# #     generate(category=20, product=46, news=8)
# # if not config.DEBUG:
# #     log_write("STARTING API")
# #     startAPI()
# #     log_write("API STARTED SUCCESSFULLY")
# #     set_webhook()
# #     log_write("WEBHOOK SET SUCCESSFULLY")
# #     log_write("STARTING SERVER")
# #     app.run(port=8000)
# # else:
# #     bot.polling()
# #     startAPI()
# #     log_write("API STARTED SUCCESSFULLY")
# #     app.run(port=8000)




