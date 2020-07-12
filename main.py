from web_shop.bot.bot_main import app, set_webhook, bot
from web_shop.db.seeder import seed, generate
from web_shop.bot import config
from web_shop.db.models import is_db_empty
from web_shop.api.api_main import start as startAPI
from web_shop.log_writer import log_write, log_clear

from flask import Flask, request, abort
from telebot.types import Update


app = Flask(__name__)


@app.route(config.WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') =='application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(status=403)


if __name__ == '__main__':
    bot.set_webhook(config.WEBHOOK_URL,
                    certificate=open('webhook_cert.pem', 'r')
                    )


# log_write("\n\nRESTARTING BOT..\n\n")
# log_write("STARTING LOGGING..")
# if is_db_empty():
#     generate(category=20, product=46, news=8)
# if not DEBUG:
#     log_write("STARTING API")
#     startAPI()
#     log_write("API STARTED SUCCESSFULLY")
#     set_webhook()
#     log_write("WEBHOOK SET SUCCESSFULLY")
#     log_write("STARTING SERVER")
#     app.run(port=8000)
# else:
#     bot.polling()
#     startAPI()
#     log_write("API STARTED SUCCESSFULLY")
#     app.run(port=8000)




