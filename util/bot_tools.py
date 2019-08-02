from uuid import uuid4

from telegram import (InlineQueryResultArticle, InputTextMessageContent,
                      InlineKeyboardButton, InlineKeyboardMarkup, ParseMode)

from . import merriam_webster_api as mw


def article_factory(title, desc, text_msg, kb_buttons=None, ncolumns=3):
    msg_content = InputTextMessageContent(text_msg, parse_mode=ParseMode.MARKDOWN)
    buttons_list = kb_buttons
    # btn is {'text': 'hello', 'switch_inline_query_current_chat': 'aaa'}
    buttons_grid = [buttons_list[n:n+ncolumns] for n in range(0, len(buttons_list), ncolumns)]
    inline_kb_markup = InlineKeyboardMarkup(buttons_grid)
    return InlineQueryResultArticle(id=uuid4(),
                                    title=title,
                                    description=desc,
                                    input_message_content=msg_content,
                                    reply_markup=inline_kb_markup)


def ask_mw_thesaurus(query):
    mw_response_type, content = mw.lookup_thesaurus(query)
    if mw_response_type == mw.MWThesaurusResponse.CORRECT:
        for word_sense in content:
            title = word_sense.headword
            desc = word_sense.description
            text_msg = word_sense.message
            kb_buttons = [
                InlineKeyboardButton(f"{word_sense.headword} on Merriam-Webster.com 🌐", url=word_sense.headword_url),
                InlineKeyboardButton(f"Other meanings of {word_sense.headword}", switch_inline_query_current_chat=word_sense.headword)
            ]
            yield article_factory(title, desc, text_msg, kb_buttons, ncolumns=1)
    elif mw_response_type == mw.MWThesaurusResponse.DID_YOU_MEAN:
        title = "Did you mean ...?"
        desc = "click to see similar words"
        text_msg = f"No results for *{query}*\nDid you mean:"
        kb_buttons = []
        for similar_word in content:
            btn = InlineKeyboardButton(similar_word, switch_inline_query_current_chat=similar_word)
            kb_buttons.append(btn)
        yield article_factory(title, desc, text_msg, kb_buttons, ncolumns=4)
    elif mw_response_type == mw.MWThesaurusResponse.NO_MATCH:
        title = "No matches found"
        desc = "let's try another query!"
        text_msg = f"Sorry, there are no possible matches for *{query}*"
        kb_buttons = [InlineKeyboardButton("Try another query", switch_inline_query_current_chat='')]
        yield article_factory(title, desc, text_msg, kb_buttons, ncolumns=1)
