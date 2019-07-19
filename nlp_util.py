from nltk.corpus import wordnet as wn

WN2HUMAN_POS_MAP = {'n': 'noun',
                    'v': 'verb',
                    'a': 'adj.',
                    's': 'adj. sat.',
                    'r': 'adv.'}


# https://www.nltk.org/_modules/nltk/corpus/reader/wordnet.html
def find_synsets(word):
    results = []
    all_synsets = wn.synsets(word)
    for s in all_synsets:
        result = {"_wn_name": s.name(),
                  "_wn_lexname": s.lexname(),
                  "word": s.name().split('.')[0].replace('_', ' '),
                  "pos": WN2HUMAN_POS_MAP.get(s.pos(), 'UNKNOWN PoS'),
                  "related": [l.name().replace('_', ' ') for l in s.lemmas() if l.name().split('.')[-1] != s.name().split('.')[0]],
                  # we don't need any other lemma data except for the name. or do we?
                  "definition": s.definition().replace("`", "'"),
                  "examples": [e.capitalize() for e in s.examples()]}

        results.append(result)

    return results


if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter()

    synonyms = find_synsets("pick_up")
    pp.pprint(synonyms)
