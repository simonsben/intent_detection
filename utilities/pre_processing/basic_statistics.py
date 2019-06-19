from re import compile, subn, sub

emoji_regex = compile(r'&#\d{4,7};')
express_regex = compile(r'[!?]+')
punctuation_regex = compile(r'[^a-zA-Z0-9]')
partial_clean = compile(r'[^a-zA-Z,.!?\'";:\-]+')
digit_regex = compile(r'[0-9]+')
space_regex = compile(r'\s+(?=\s)|^\s|'
                      r'(?<=\w)\s+(?=[^a-zA-Z0-9])')
image_regex = compile(r'Image:\w[\w\s]+.\w{3}')
repeat_regex = compile(r'(\w)\1{2,}')


def count_upper(document, get_header=False):
    """ Counts number of uppercase characters and converts to lowercase """
    if get_header: return 'upper_count'

    count = sum(1 for ch in document if ch.isupper())
    document = document.lower()

    return count, document


def count_emojis(document, get_header=False):
    """ Counts the number of emojis in the document and removes them """
    if get_header: return 'emoji_count'

    document, count = subn(emoji_regex, ' ', document)
    return count, document


def original_length(document, get_header=False):
    """ Gives the length of the original document """
    if get_header: return 'original_length'

    return len(document), document


def count_express(document, get_header=False):
    """ Counts occurances of expressive punctuation (i.e. ! and ?) """
    if get_header: return 'express_count'

    document, count = subn(express_regex, ' ', document)
    return count, document


# TODO see whether there are more intelligent ways to substitute certain characters (ex. word-embedded @)
def count_punctuation(document, get_header=False):
    """ Counts uncaught/un-important punctuation and removes it """
    if get_header: return 'punctuation_count'

    document, count = subn(punctuation_regex, ' ', document)
    return count, document


# TODO see whether there is a way to detect digits representing words (ex. go2school)
def count_digits(document, get_header=False):
    """ Counts uncaught digits and removes them """
    if get_header: return 'digit_count'

    document, count = subn(digit_regex, ' ', document)
    return count, document


def count_images(document, get_header=False):
    """ Counts embedded images of the form "Image:image name.png" then removes them """
    if get_header: return 'image_count'

    document, count = subn(image_regex, ' image ', document)
    return count, document


def count_repeat_instances(document, get_header=False):
    """ Counts the number of repeated characters (greater than 3) and removes all but one """
    if get_header: return 'repeat_count'

    document, count = subn(repeat_regex, lambda pattern: pattern[0], document)
    return count, document


def remove_spaces(document, get_header=False):
    """ Removes extra spaces added into document by previous filters """
    if get_header: return None

    document = sub(space_regex, '', document)
    return None, document


def run_partial_clean(document, get_header=False):
    """ Partially clean document, meant for SpaCY relatex pre-processing """
    if get_header: return None

    document = sub(partial_clean, ' ', document)
    return None, document
