#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from telegram import ParseMode
from telegram.ext import Updater, InlineQueryHandler, CommandHandler

import util.bot_tools as bt


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename="main.log")
logger = logging.getLogger(__name__)

INFO_MESSAGES = {'start': 'Hi!\nThis bot currently supports only inline mode. Try it out in any chat!',
                 'help': "Use this bot via inline mode. Type\n@TsaurusBot _word or phrase_\nin any chat"}


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(INFO_MESSAGES['start'])


def show_help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(INFO_MESSAGES['help'], parse_mode=ParseMode.MARKDOWN)


def inlinequery(update, context):
    """Handle the inline query."""
    user = update.inline_query.from_user['username']
    query = ''.join(c for c in update.inline_query.query if c.isalnum() or c is ' ')
    if query.strip() != '':
        logger.info(f"User @{user} searched \"{query}\"")
        query_results = bt.ask_mw_thesaurus(query)
        update.inline_query.answer(query_results)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    from config import BOT_TOKEN
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", show_help))
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_error_handler(error)

    updater.start_polling()
    logger.info("BOT DEPLOYED. Ctrl+C to terminate")

    updater.idle()


if __name__ == '__main__':
    main()
