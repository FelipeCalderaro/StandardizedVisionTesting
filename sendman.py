class chatIds:
    calderaro = 277634087
    galende = 340707674


def send(id, message, botInstance):
    botInstance.sendMessage(chat_id=id, text=message)


def sendPhoto(id, file, botInstance):
    botInstance.sendDocument(chat_id=id, photo=file)
