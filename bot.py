#!/usr/bin/env python3
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


def _build_inline_results(query, response_flag, results):
    if response_flag == mw.MWThesaurusResponse.CORRECT:
        for mwt_entry in results:
            text_message_content = InputTextMessageContent(mwt_entry.message,
                                                           parse_mode=ParseMode.MARKDOWN)
            inline_kb_buttons = [
                [InlineKeyboardButton(f"\"{mwt_entry.headword}\" on Merriam-Webster.com 🌐",
                                      url=mwt_entry.headword_url)],
                [InlineKeyboardButton(f"Other meanings of \"{mwt_entry.headword}\"",
                                      switch_inline_query_current_chat=mwt_entry.headword)]
            ]
            inline_kb_markup = InlineKeyboardMarkup(inline_kb_buttons)
            result_article = InlineQueryResultArticle(
                                id=uuid4(),
                                title=mwt_entry.title,
                                description=mwt_entry.description,
                                input_message_content=text_message_content,
                                reply_markup=inline_kb_markup)
            yield result_article
    elif response_flag == mw.MWThesaurusResponse.DID_YOU_MEAN:
        def _build_kb(buttons_list):
            buttons_list = iter(buttons_list)
            for i in buttons_list:
                try:
                    yield [i, next(buttons_list)]
                except StopIteration:
                    yield [i]

        text_message_content = InputTextMessageContent(f"No results for *{query}*\nDid you mean:",
                                                       parse_mode=ParseMode.MARKDOWN)
        inline_kb_buttons = []
        for similar_word in results:
            btn = InlineKeyboardButton(similar_word,
                                       switch_inline_query_current_chat=similar_word)
            inline_kb_buttons.append(btn)
        inline_kb_markup = InlineKeyboardMarkup(_build_kb(inline_kb_buttons))
        result_article = InlineQueryResultArticle(id=uuid4,
                                                  title="Did you mean ...?",
                                                  description="click to see similar words",
                                                  input_message_content=text_message_content,
                                                  reply_markup=inline_kb_markup)
        yield result_article
    elif response_flag == mw.MWThesaurusResponse.NO_MATCH:
        text_message_content = InputTextMessageContent(f"Sorry, there are no possible matches for *{query}*",
                                                       parse_mode=ParseMode.MARKDOWN)
        inline_kb_buttons = []
        btn = [InlineKeyboardButton("Try another query", switch_inline_query_current_chat='')]
        inline_kb_buttons.append(btn)
        inline_kb_markup = InlineKeyboardMarkup(inline_kb_buttons)
        result_article = InlineQueryResultArticle(id=uuid4,
                                                  title="No possible matches",
                                                  description="Try another query",
                                                  input_message_content=text_message_content,
                                                  reply_markup=inline_kb_markup)
        yield result_article


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
        logging.info(f"User @{user} searched \"{query}\"")
        response_flag, results = mw.lookup_thesaurus(query)
        query_results = _build_inline_results(query, response_flag, results)
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
