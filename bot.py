#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def inlinequery(update, context):
    """Handle the inline query."""
    import nlp_util

    query = update.inline_query.query
    synonyms = nlp_util.find_synsets(query)

    query_results = []
    for synonym in synonyms:
        _id = uuid4()
        _title = synonym['name'].split('.')[0]
        _desc = synonym['def']
        _lemmas = str([l.name() for l in synonym['lemmas']])
        _examples = '\n'.join(synonym['examples'])
        _content = f"{_title}\n{_desc}\n\n{_examples}\n\nLemmas: {_lemmas}"

        query_results.append(
            InlineQueryResultArticle(id=_id,
                                     title=_title,
                                     description=_desc,
                                     input_message_content=InputTextMessageContent(_content)))

    # results = [
    #     InlineQueryResultArticle(
    #         id=uuid4(),
    #         title="Caps",
    #         input_message_content=InputTextMessageContent(
    #             query.upper())),
    #     InlineQueryResultArticle(
    #         id=uuid4(),
    #         title="Bold",
    #         input_message_content=InputTextMessageContent(
    #             "*{}*".format(escape_markdown(query)),
    #             parse_mode=ParseMode.MARKDOWN)),
    #     InlineQueryResultArticle(
    #         id=uuid4(),
    #         title="Italic",
    #         input_message_content=InputTextMessageContent(
    #             "_{}_".format(escape_markdown(query)),
    #             parse_mode=ParseMode.MARKDOWN))]

    update.inline_query.answer(query_results)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    from config import TOKEN
    updater = Updater(TOKEN, use_context=True, request_kwargs={'proxy_url': 'socks5h://163.172.152.192:1080'})

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)

    updater.start_polling()
    logger.info("BOT DEPLOYED. Ctrl+C to terminate")

    updater.idle()


if __name__ == '__main__':
    main()
