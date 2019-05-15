from re import compile, subn, search
from unidecode import unidecode


special_regex = compile(r'&\S+;')
special_regex_parser = compile(r'(&amp;)|(&lt;|&le;)|(&gt;|&ge;)|(&160;)|'  # Special characters
                               r'((?<=&)\d+(?=;))')                         # Accented characters
group_map = {
    0: 'and',
    1: 'less than',
    2: 'greater than',
    3: ' '
}


def manage_special_characters(document):
    """ Locates special characters and intelligently replaces (or removes) them """
    def replace(_match):
        character = _match.group(0)
        parsed = search(special_regex_parser, character)
        if parsed is not None:
            group_id = get_symbol_index(parsed.groups())

            if group_id < 4:
                return group_map.get(group_id)
            return get_ascii_char(parsed.group(0))

        print(character)
        return ''

    document, num_special = subn(special_regex, replace, document)

    return num_special, document


def get_symbol_index(groups):
    for ind, val in enumerate(groups):
        if val is not None:
            return ind
    raise ValueError('Group does not exist')


def get_ascii_char(unicode):
    """ Takes decimal unicode and returns closest ascii character """
    if type(unicode) == str:
        unicode = int(unicode)

    return unidecode(chr(unicode))
