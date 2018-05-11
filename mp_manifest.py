import os
import re
import logging


def schema2dict(string):
    rv = {}
    # TODO imeplement


def __dump_pydict(dic, depth=0):
    prefix = ''.join(['|' for i in range(depth)])
    for k in dic:
        if type(dic[k]) == dict:
            print(prefix + k)
            __dump_pydict(dic[k], depth+1)
        else:
            print(prefix + str(k) + ':' + str(dic[k]))


def __map_depth(string):
    rv = []
    depth = 0
    for i in range(len(string)):
        if string[i] == '{':
            depth += 1
        rv.append(depth)
        if string[i] == '}':
            depth -= 1
    return rv


def __split_morphemes(string):
    i1 = 0
    tmp = []
    tmp_d = {}
    if not (string.startswith('{') and string.endswith('}')):
        logging.ERROR('Invalid string "' + string + '"')
    string = string[1:-1]
    depth_arr = __map_depth(string)
    commas_arr = __occurences_exclusive(string, ',', ['"', '()'])
    for c in commas_arr:
        if depth_arr[c] == 0:
            i0 = i1
            i1 = c
            itmp = 0 if i0 == 0 else i0 + 1
            tmp.append(string[itmp:i1])
    if not string.endswith(','):                # For dump C-like syntax
        tmp.append(string[i1+1:len(string)])
    for subs in tmp:
        if ':' in subs:
            i = subs.find(':')
            k, v = subs[0:i], subs[i+1:len(subs)]
            tmp_d[k] = v
            if v[0] == '{' and v[-1:] == '}':
                tmp_d[k] = __split_morphemes(v)
        else:
            tmp_d[subs] = None
    return tmp_d


def __str2morphemes(string):
    regex_dictionary = r'[_,a-z,A-Z]{1}[_,a-z,A-Z,0-9]*\:{1}\{.*\}'
    regex_definition = r'[_,a-z,A-Z]{1}[_,a-z,A-Z,0-9]*\:{1}\(.*\)'
    morphemes = string.split('$')[1:]
    dicts = {}
    defs = {}
    for m in morphemes:
        # key = __subtract_morpheme_name(m)
        if re.match(regex_dictionary, m):
            key = m.split(':')[0]
            dicts[key] = m[len(key) + 1:]
        elif re.match(regex_definition, m):
            key = m.split(':')[0]
            defs[key] = m[len(key) + 1:]
    dicts = {k: __split_morphemes(dicts[k]) for k in dicts}
    tmp = {'dicts': dicts, 'defs': defs}
    # __dump_pydict(tmp)
    return tmp


def __regex_list2list(list):
    return [i.regs[0][0] for i in list]


def __occurences(string, substr):
    return __regex_list2list([n for n in re.finditer(substr, string)])


# Resutns numberical locations of substr occurences of substr in string, except for the cases
# when it's inside of a pair of exclchars. If exclchars do not match, they should be given as a
# pair, for example: exclchars=['"', '{}', '[]']
def __occurences_exclusive(string, substr, exclchars=['"']):
    rv = []
    _in = {s: 0 for s in exclchars}
    for i in range(len(string)):
        in_exclchars = False
        for k in _in:
            if len(k) == 1:
                if string[i] == k and (i == 0 or string[i-1] != '\\'):
                    _in[k] = 0 if _in[k] == 1 else 1
            if len(k) == 2:
                if string[i] == k[0]:
                    _in[k] += 1
                if string[i] == k[1]:
                    _in[k] -= 1
        for k in _in:
            if _in[k] > 0:
                in_exclchars = True
        if in_exclchars:
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


# Check if number of opening and closing brackets, braces and parentheses is matching
def __validate_matching_syms(string):
    rv = True
    matching_elements = [['[', ']'], ['(', ')'], ['{', '}']]
    for pair in matching_elements:
        if not __all_a_before_all_b_in_c(pair[0], pair[1], string):
            rv = False
            logging.critical('Mismatching number of ' + pair[0] + ' and ' + pair[1] + '!')
            break
    return rv


def __recursive_extract_variables(dictionary):
    rv = []
    if type(dictionary) is not dict:
        return rv
    for k in dictionary:
        if type(dictionary[k]) == str and '@' in dictionary[k]:
            substr = dictionary[k][dictionary[k].find('@') + 1:]

            cut_syms = __occurences_exclusive(substr, ')') + \
                       __occurences_exclusive(substr, '}') + \
                       __occurences_exclusive(substr, ']')
            cut_syms.sort()
            if len(cut_syms) > 0:
                substr = substr[:cut_syms[0]]
            rv.append(substr)
        elif type(dictionary[k]) == dict:
            branch = __recursive_extract_variables(dictionary[k])
            if len(branch) > 0:
                rv += branch
    return rv


def __validate_variables(morphemes):
    used_vars = __recursive_extract_variables(morphemes)
    print(used_vars)
    used_vars = {k: False for k in used_vars}
    #TODO find user_vars in morphemes as keys!


def reads(string):
    if type(string) != str:
        raise TypeError('Given ' + str(type(str)) + ' instead of str!')
    string = __process_comments(string)
    string = __clear_spaces(string)
    if __validate_matching_syms(string):
        logging.info('Give data is valid.')
    else:
        raise SyntaxError('Give data is invalid!')
    logging.debug(string)
    morphemes = __str2morphemes(string)
    __validate_variables(morphemes)



def readf(filename):
    if type(filename) != str:
        raise TypeError('Given ' + str(type(filename)) + ' instead of str!')
    if not os.path.exists(filename) or not os.path.isfile(filename):
        raise IOError('File ' + filename + ' not found!')

    with open(filename) as f:
        return reads(f.read())

