# -*- coding: utf-8 -*-
from enum import Enum, auto

import requests

from config import MW_DICTIONARY_API_KEY, MW_THESAURUS_API_KEY


class MWThesaurusResponse(Enum):
    CORRECT = auto()
    DID_YOU_MEAN = auto()
    NO_MATCH = auto()


class MWThesaurusWordSenseEntry:
    content_list_map = {
        'syn_list': 'Synonyms',
        'rel_list': 'Related Words',
        'phrase_list': 'Phrases',
        'near_list': 'Near Antonyms',
        'ant_list': 'Antonyms'
        }

    def __init__(self, headword, pos, sense_dict):
        self._headword = headword
        self._pos = pos
        self._raw_sense_dict = sense_dict   # just in case we need to extract other fields
        self._defining_text_list = sense_dict['dt']
        self._content_dict = self._parse_related_wordlists()

    def _parse_related_wordlists(self):
        content = {}
        for list_type in self.content_list_map.keys():
            if self._raw_sense_dict.get(list_type):
                content[list_type] = []
                for group in self._raw_sense_dict[list_type]:
                    word_group = [self._parse_word_element(word_element) for word_element in group]
                    content[list_type].append(word_group)
        return content

    @staticmethod
    def _parse_word_element(word_element):
        wd = word_element.get('wd')
        annotated_word = wd
        if word_element.get('wvrs'):
            wvrs_annotation = ', '.join([f"{note['wvl']} {note['wva']}" for note in word_element['wvrs']])
            annotated_word = f"{annotated_word} ({wvrs_annotation})"
        if word_element.get('wsls'):
            wsls_annotation = ', '.join(word_element['wsls'])
            annotated_word = f"{annotated_word} [[{wsls_annotation}]]"
            # double [[]] due to telegram not showing [] for some reason
        if word_element.get('wvbvrs', ''):
            wvbvrs_annotation = ', '.join([f"{note['wvbvl']} {note['wvbva']}" for note in word_element['wvbvrs']])
            annotated_word = f"{annotated_word} ({wvbvrs_annotation})"
        return annotated_word

    def cleanup_mw_tags(property_getter):
        def cleaner(*args, **kwargs):
            replacements = [('{it}', ''),
                            ('{/it}', ''),
                            ('{ldquo}', '“'),
                            ('{rdquo}', '”')]
            result = property_getter(*args, **kwargs)
            for rule in replacements:
                result = result.replace(*rule)
            return result
        return cleaner

    @property
    def headword(self):
        return self._headword

    @property
    def pos(self):
        return self._pos

    @property
    def title(self):
        return f"{self.headword}   ({self.pos})"

    @property
    def description(self):
        desc_elements = []
        for dt_element in self._defining_text_list:
            if dt_element[0] == 'text':
                desc_elements.append(dt_element[1])
        return '\n'.join(desc_elements)

    @property
    @cleanup_mw_tags
    def examples(self):
        example_elements = []
        for dt_element in self._defining_text_list:
            if dt_element[0] == 'vis':
                for vis_item in dt_element[1]:
                    example_elements.append(f"//{vis_item['t']}")
        return '\n'.join(example_elements)

    @property
    def message(self):
        msg_elements = [f"*{self.headword}*   _{self.pos}_\n",
                        f"{self.description}",
                        f"_{self.examples}_\n"]
        for list_type, list_content in self._content_dict.items():
            list_name = self.content_list_map[list_type]
            content = ';\n'.join([', '.join(word_group) for word_group in list_content])
            msg_elements.extend([f"\n*{list_name}*", content])
        return '\n'.join(msg_elements)

    @property
    def headword_url(self):
        return f"https://www.merriam-webster.com/thesaurus/{self.headword.replace(' ', '%20')}"


def lookup_thesaurus(word):
    session = requests.Session()
    url = f"https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word.replace(' ', '%20')}?key={MW_THESAURUS_API_KEY}"
    response = session.get(url)
    response_data = response.json()
    if not response_data:
        return MWThesaurusResponse.NO_MATCH, []
    elif all([isinstance(r, str) for r in response_data]):
        return MWThesaurusResponse.DID_YOU_MEAN, response_data
    else:
        return MWThesaurusResponse.CORRECT, parse_response_dict(response_data)


def parse_response_dict(response_data):
    for homograph in response_data:
        headword = homograph['hwi']['hw']
        pos = homograph['fl']
        sseq = homograph['def'][0]['sseq']
        for sense in sseq:
            sense_type = sense[0][0]
            sense_dict = sense[0][1]
            # senses may also be:
            # https://www.dictionaryapi.com/products/json#sec-2.sdsense
            # https://www.dictionaryapi.com/products/json#sec-2.sen
            mwt_entry = MWThesaurusWordSenseEntry(headword, pos, sense_dict)
            yield mwt_entry


def lookup_dictionary(word):
    session = requests.Session()
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word.replace(' ', '%20')}?key={MW_DICTIONARY_API_KEY}"
    response = session.get(url)
    response_data = response.json()
    for meaning in response_data:
        syns = meaning.get('syns')
        if syns:
            for syn in syns:
                for s in syn['pt']:
                    if s[0] == 'text':
                        discussion_text = s[1]
                        print(f"{discussion_text}")
                    elif s[0] == 'vis':
                        for vis_example in s[1]:
                            verbal_illustration = vis_example['t']
                            print(f"{verbal_illustration}")
            additional_references = syn.get('sarefs')
            if additional_references:
                print(f"Additional references: {additional_references}")


if __name__ == '__main__':
    # with open('wordlist.txt', 'r', encoding='utf-8') as checklist_f:
    #     wordlist = [w.strip('\n') for w in list(checklist_f)]
    #     for w in wordlist:
    result, entries = lookup_thesaurus('fhkfkfj')
    if result == MWThesaurusResponse.CORRECT:
        for mwt_entry in entries:
            print(mwt_entry.title)
            print(mwt_entry.description)
            print(mwt_entry.examples)
            print("-" * 10)
            print(mwt_entry.message)
            print("=" * 150)
    elif result == MWThesaurusResponse.DID_YOU_MEAN:
        print(f"Did you mean: {', '.join(entries)}?")
    elif result == MWThesaurusResponse.NO_MATCH:
        print(f"No matches found. Try again!")
