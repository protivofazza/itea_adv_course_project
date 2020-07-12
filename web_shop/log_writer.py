from datetime import datetime


def log_clear():
    with open("logs.txt", "w") as logs:
        logs.write("BOT APP LOGS\n")


def log_write(data: str):
    data = data.replace('\n', '. ')
    with open("logs.txt", "a+") as logs:
        logs.write(str(datetime.utcnow()) + ': ' + data + '\n')