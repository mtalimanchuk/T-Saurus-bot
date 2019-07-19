#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown

import nlp_util


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

INFO_MESSAGES = {'start': 'Hi!\nThis bot currently supports only inline mode. Try it out in any chat!',
                 'help': "Use this bot via inline mode. Type @"}


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(INFO_MESSAGES['start'])


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(INFO_MESSAGES['help'])


def inlinequery(update, context):
    """Handle the inline query."""
    user = update.inline_query.from_user['username']
    query = update.inline_query.query.replace(' ', '_')
    logging.info(f"User @{user} asked for \"{query}\"")
    synonyms = nlp_util.find_synsets(query)

    query_results = []
    for synonym in synonyms:
        result_id = uuid4()
        word = synonym['word']
        pos = synonym['pos']
        result_title = f"{word} ({pos})"
        result_description = synonym['definition']
        formatted_content = f"*{word}* _{pos}_\n{result_description}"
        examples = '\n'.join(synonym['examples'])
        if examples:
            formatted_content = f"{formatted_content}\n\n_{examples}_"
        related_words = ', '.join(synonym['related'])
        if related_words:
            formatted_content = f"{formatted_content}\n\nSee also: {related_words}"

        query_results.append(
            InlineQueryResultArticle(id=result_id,
                                     title=result_title,
                                     description=result_description,
                                     input_message_content=InputTextMessageContent(formatted_content,
                                                                                   parse_mode=ParseMode.MARKDOWN)))

    update.inline_query.answer(query_results)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    from config import TOKEN
    updater = Updater(TOKEN, use_context=True)

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
