from re import compile
from numpy import zeros
import config

# Run clean on contexts
non_char = compile(r'[^a-zA-Z ]')    # Replace non-alphabetic characters
extra_space = compile(r'\s{2,}')     # Replace repeat spaces
repeats = compile(r'(.)(\1{2,})')
acronym = compile(r'(\w\.){2,}')
split_pattern = compile(r'[.?!;]+')
apostrophe_regex = compile(r'(\w+)\\?\'(\w+)')


def clean_acronym(document):
    """ Removes periods from acronyms (ex. U.S.A. -> USA) """
    return acronym.sub(lambda match: match[0].replace('.', '') + ' ', document)


def clean_apostrope(document):
    """ Removes apostrophes without splitting letters (ex. i'm -> im instead of i m) """
    return apostrophe_regex.sub(lambda match: match[1] + match[2], document)


def pre_intent_clean(document):
    """ Perform final clean on contexts before saving and exporting. """
    document = repeats.sub(lambda match: match[0][0], document)     # Remove repeat characters
    return extra_space.sub(' ', document)                          # Remove extra spaces


def final_clean(document):
    """ Final clean after context splitting """
    return extra_space.sub(' ', non_char.sub(' ', document))     # Run post clean regex


def simulated_runtime_clean(documents):
    """ Simulates the cleaning process from partial to saved contexts """
    for index, document in enumerate(documents):
        if not isinstance(document, str):
            documents[index] = ''
            continue

        documents[index] = extra_space.sub(' ', non_char.sub(
            ' ',
            pre_intent_clean(clean_apostrope(clean_acronym(document)))
        ))

    return documents


def runtime_clean(documents):
    """ Last function to be executed before training (mainly used when executing on Google Colab) """
    for ind, document in enumerate(documents):
        if not isinstance(document, str):
            documents[ind] = ''
            continue

        documents[ind] = extra_space.sub(' ', non_char.sub(' ', document))

    return documents


def token_to_index(raw_documents, embedding_tokens, return_mapping=False):
    """ Takes documents and replaces their tokens with the index within the word embeddings """
    # Enumerate embedding tokens
    token_mapping = {token: index for index, token in enumerate(embedding_tokens)}
    max_tokens = config.max_tokens

    # Convert documents to arrays of token indexes
    doc_arrays = zeros((len(raw_documents), max_tokens), dtype=int)    # Allocate matrix
    for index, document in enumerate(raw_documents):
        if not isinstance(document, str): continue

        indexed_document = []                                           # Temp list of enumerated indexes
        for token_index, token in enumerate(document.split(' ')):       # Split document into tokens
            if token_index > max_tokens: break                          # Don't translate past max document length
            if len(token) == 0: continue                                # Don't convert null strings
            elif token in token_mapping:                                       # Add token index to temp list
                indexed_document.append(token_mapping[token])

        # Push indexes to matrix
        num_tokens = min([max_tokens, len(indexed_document)])
        doc_arrays[index, :num_tokens] = indexed_document[:num_tokens]

    if return_mapping:
        return doc_arrays, token_mapping
    return doc_arrays
