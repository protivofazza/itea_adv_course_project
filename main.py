from web_shop.bot.bot_main import app, set_webhook, bot
from web_shop.db.seeder import seed, generate
from web_shop.bot.config import DEBUG
from web_shop.db.models import is_db_empty
from web_shop.api.api_main import start as startAPI
from web_shop.log_writer import log_write, log_clear


if __name__ == '__main__':
    log_write("\n\nRESTARTING BOT..\n\n")
    log_write("STARTING LOGGING..")
    if is_db_empty():
        generate(category=20, product=46, news=8)
    if not DEBUG:
        log_write("STARTING API")
        startAPI()
        log_write("API STARTED SUCCESSFULLY")
        set_webhook()
        log_write("WEBHOOK SET SUCCESSFULLY")
        log_write("STARTING SERVER")
        app.run(debug=True)
        log_write("STOP RUNNING")
        print("Mark: everything stopped")
    else:
        startAPI()
        print("Mark 1: startAPI() success")
        log_write("API STARTED SUCCESSFULLY")
        bot.polling()
        print("Mark 2: bot.polling() success")
        app.run(debug=True)
        print("Mark 3: app.run(debug=True0)")
