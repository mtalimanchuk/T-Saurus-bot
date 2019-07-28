#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
# from telegram.utils.helpers import escape_markdown

import merriam_webster_api as mw


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
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
    query = update.inline_query.query
    if query != '':
        logging.info(f"User @{user} searched \"{query}\"")
        query_results = []
        for mwt_entry in mw.lookup_thesaurus(query):
            text_message_content = InputTextMessageContent(mwt_entry.message, parse_mode=ParseMode.MARKDOWN)
            inline_kb_buttons = [
                [InlineKeyboardButton(f"\"{mwt_entry.headword}\" on Merriam-Webster.com 🌐", url=mwt_entry.headword_url)]
            ]
            inline_kb_markup = InlineKeyboardMarkup(inline_kb_buttons)
            query_results.append(
                InlineQueryResultArticle(id=uuid4(),
                                         title=mwt_entry.title,
                                         description=mwt_entry.description,
                                         input_message_content=text_message_content,
                                         reply_markup=inline_kb_markup))

        update.inline_query.answer(query_results)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    from config import DEV_TOKEN, DEV_KWARGS
    updater = Updater(DEV_TOKEN, use_context=True, request_kwargs=DEV_KWARGS)

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
