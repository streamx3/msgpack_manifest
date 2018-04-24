import os
import re
import logging


def schema2dict(string):
    rv = {}
    # TODO imeplement


def __substrac_morpheme_name(string):
    rv = ''
    #TODO go study regexes and return here
    return rv


def __str2morphemes(string):
    morphemes = string.split('$')
    tmp = {}
    for m in morphemes:
        key = __substrac_morpheme_name(m)
        tmp[key]: m[len(key)]
    #TODO not fully implemented


def __regex_list2list(list):
    return [i.regs[0][0] for i in list]


def __occurences(string, substr):
    return __regex_list2list([n for n in re.finditer(substr, string)])


def __occurences_exclusive(string, substr):
    rv = []
    in_quotes = False
    for i in range(len(string)):
        if string[i] == '"' and (i == 0 or string[i-1] != '\\'):
            in_quotes = not in_quotes
        if in_quotes:
            pass
        elif string[i:].startswith(substr):
            rv.append(i)
    return rv


def __all_less(arr1, arr2):
    rv = True
    if type(arr1) != type(arr2) or type(arr1) not in (bytearray, list, tuple):
        logging.critical('Type error in container comparison: ' + str(type(arr1)) + ', ' + str(type(arr2)) + ';')
        return False
    if len(arr1) != len(arr2):
        logging.critical('Sizes of container must match: ' + str(len(arr1)) + ', ' + str(len(arr2)) + ';')
        return False
    for a, b in zip(arr1, arr2):
        if type(a) != int or type(b) != int:
            logging.critical('Wrong data type in container')
            return False
        if not (a < b):
            rv = False
            break
    return rv


def __all_a_before_all_b_in_c(a, b, c):
    rv = True
    if [type(a), type(b), type(c)] != [str, str, str]:
        logging.critical('Expecting 3 strings!')
        return False
    occ_a = __occurences_exclusive(c, a)
    occ_b = __occurences_exclusive(c, b)
    return __all_less(occ_a, occ_b)


# C and C++ style comments allowed
def __process_comments(string):
    # Removing old C-like comments
    # Expecting same number of comment opening and closing sequences
    opening_comments = __occurences(string, '/\*')
    closing_comments = __occurences(string, '\*/')

    opening_comments.reverse()
    closing_comments.reverse()

    assert len(closing_comments) == len(opening_comments)
    for o, c in zip(opening_comments, closing_comments):
        assert o < c
        string = string[:o] + string[c+2:]

    # Removing old C++-like comments
    opening_comments = __occurences(string, '//')
    next_endls = [string.find('\n', i) for i in opening_comments]
    if next_endls[-1:] == [-1]:
        next_endls = next_endls[:-1] + [len(string)]

    opening_comments.reverse()
    next_endls.reverse()
    for o, nl in zip(opening_comments, next_endls):
        string = string[:o] + string[nl:]

    return string


def __clear_spaces(string):
    symbols_to_get_rid_of = (' ', '\n', '\t')
    tmp = ''
    in_quotes = False
    for i in range(len(string)):
        if string[i] == '"':
            in_quotes = not in_quotes
        if not in_quotes and string[i] in symbols_to_get_rid_of:
            continue
        tmp += string[i]
    return tmp


def __validate(string):
    rv = True
    matching_elements = [['[', ']'], ['(', ')'], ['{', '}']]
    for pair in matching_elements:
        if not __all_a_before_all_b_in_c(pair[0], pair[1], string):
            rv = False
            logging.critical('Mismatching number of ' + pair[0] + ' and ' + pair[1] + '!')
            break
    return rv


def reads(string):
    if type(string) != str:
        raise TypeError('Given ' + str(type(str)) + ' instead of str!')
    string = __process_comments(string)
    string = __clear_spaces(string)
    # if __occurences_exclusive()
    if __validate(string):
        logging.info('Give data is valid.')
    else:
        raise SyntaxError('Give data is invalid!')
    logging.debug(string)


def readf(filename):
    if type(filename) != str:
        raise TypeError('Given ' + str(type(filename)) + ' instead of str!')
    if not os.path.exists(filename) or not os.path.isfile(filename):
        raise IOError('File ' + filename + ' not found!')

    with open(filename) as f:
        return reads(f.read())



# class Schema:
#     def __init__(self, string):
#         self.
