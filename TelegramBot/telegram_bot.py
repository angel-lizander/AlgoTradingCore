from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext import (CallbackContext)
from telegram import Bot

#Telegram Bot Token
telegramToken= ""

#List of the allowed chat that can receive notifications
allowedChats= ['']


def sendMessage(message: str, parse_mode:str):
    bot = Bot(telegramToken)

    for chat in allowedChats:
     bot.sendMessage(chat, message, parse_mode)


#BotHandlers
def start(update: Update, context: CallbackContext): update.message.reply_text("Bot Initialized")


def main():
    updater = Updater(telegramToken,
                  use_context=True)


    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.idle()
