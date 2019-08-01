from uuid import uuid4

from telegram import (InlineQueryResultArticle, InputTextMessageContent,
                      InlineKeyboardButton, InlineKeyboardMarkup, ParseMode)

from . import merriam_webster_api as mw
inline_result_list = []


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
