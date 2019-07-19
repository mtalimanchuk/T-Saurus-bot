from nltk.corpus import wordnet as wn


# https://www.nltk.org/_modules/nltk/corpus/reader/wordnet.html
def find_synsets(word):
    results = []
    all_synsets = wn.synsets(word)
    for s in all_synsets:
        result = {"name": s.name(),
                  "lemmas": s.lemmas(),
                  "def": s.definition(),
                  "lexname": s.lexname(),
                  "examples": s.examples()}

        results.append(result)

    return results


if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter()

    synonyms = find_synsets("good")
    pp.pprint(synonyms)
