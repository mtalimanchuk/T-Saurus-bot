# -*- coding: utf-8 -*-
import requests

from config import MW_DICTIONARY_API_KEY, MW_THESAURUS_API_KEY


class MWThesaurusEntry:
    def __init__(self, headword, pos, sense_dict):
        self._headword = headword
        self._pos = pos
        self._raw_sense_dict = sense_dict   # just in case we need to extract other fields
        self._defining_text_list = sense_dict['dt']
        self._content_dict = self._parse_thesaurus_content()

    def _parse_thesaurus_content(self):
        possible_content_lists = [
            'syn_list',
            'rel_list',
            # 'ant_list',
            # 'near_list',
            'phrase_list'
            ]
        content = {}
        for list_type in possible_content_lists:
            if self._raw_sense_dict.get(list_type):
                content[list_type] = []
                for group in self._raw_sense_dict[list_type]:
                    word_group = [self._parse_word_element(word_element) for word_element in group]
                    content[list_type].append(word_group)
        return content

    def _parse_word_element(self, word_element):
        wd = word_element.get('wd')
        annotated_word = wd
        if word_element.get('wvrs'):
            wvrs_annotation = ', '.join([f"{note['wvl']} {note['wva']}" for note in word_element['wvrs']])
            annotated_word = f"{annotated_word} ({wvrs_annotation})"
        if word_element.get('wsls'):
            wsls_annotation = ', '.join(word_element['wsls'])
            annotated_word = f"{annotated_word} [{wsls_annotation}]"
        if word_element.get('wvbvrs', ''):
            wvbvrs_annotation = ', '.join([f"{note['wvbvl']} {note['wvbva']}" for note in word_element['wvbvrs']])
            annotated_word = f"{annotated_word} ({wvbvrs_annotation})"
        return annotated_word

    @property
    def title(self):
        return f"{self._headword}   ({self._pos})"

    @property
    def examples(self):
        example_elements = []
        for dt_element in self._defining_text_list:
            if dt_element[0] == 'vis':
                for vis_item in dt_element[1]:
                    example_elements.append(f"//{vis_item['t']}")
        return '\n'.join(example_elements)

    @property
    def description(self):
        desc_elements = []
        for dt_element in self._defining_text_list:
            if dt_element[0] == 'text':
                desc_elements.append(dt_element[1])
        return '\n'.join(desc_elements)

    @property
    def message(self):
        msg_elements = [f"`{self._headword}`   _({self._pos})_\n",
                        f"{self.description}",
                        f"_{self.examples}_\n"]
        for list_type, list_content in self._content_dict.items():
            content = '\n'.join([', '.join(group) for group in list_content])
            msg_elements.extend([f"*{list_type.replace('_', ' ').upper()}*", content])
        return '\n'.join(msg_elements)

    # def __str__(self):
    #     header = f"{self._headword}   ({self._pos})"
    #     description = f"{self._defining_text_list}"
    #     formatted_string = f"{header}\n{description}"
    #     for list_type, list_content in self._content_dict.items():
    #         content = '\n'.join([', '.join(group) for group in list_content])
    #         formatted_string = f"{formatted_string}\n{list_type.replace('_', ' ').upper()}\n{content}"
    #     return f"{formatted_string}\n{'-' * 150}"


def lookup_thesaurus(word):
    session = requests.Session()
    url = f"https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word.replace(' ', '%20')}?key={MW_THESAURUS_API_KEY}"
    response = session.get(url)
    word_data = response.json()
    for homograph in word_data:
        headword = homograph['hwi']['hw']
        pos = homograph['fl']
        sseq = homograph['def'][0]['sseq']
        for sense in sseq:
            sense_type = sense[0][0]
            sense_dict = sense[0][1]
            # senses may also be:
            # https://www.dictionaryapi.com/products/json#sec-2.sdsense
            # https://www.dictionaryapi.com/products/json#sec-2.sen
            mwt_entry = MWThesaurusEntry(headword, pos, sense_dict)
            # print(mwt_entry.title)
            # print(mwt_entry.description)
            # print(mwt_entry.message)
            yield mwt_entry


def lookup_dictionary(word):
    session = requests.Session()
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word.replace(' ', '%20')}?key={MW_DICTIONARY_API_KEY}"
    response = session.get(url)
    word_data = response.json()
    for meaning in word_data:
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
    #     wordlist = [w.strip() for w in list(checklist_f)]
    #     for w in wordlist:
    #         lookup_thesaurus(w)

    lookup_thesaurus('absolute')
