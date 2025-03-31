import unidecode

default_charset_replacement_table = { 
                     " ": " ",
                     "!": "!",
                     "\"": "'",
                     "#": "+",
                     "$": "S",
                     "%": "%",
                     "&": "+",
                     "'": "'",
                     "(": "(",
                     ")": ")",
                     "*": "*",
                     "+": "+",
                     ",": ",",
                     "-": "-",
                     ".": ".",
                     "/": "/",
                     "0": "0",
                     "1": "1",
                     "2": "2",
                     "3": "3",
                     "4": "4",
                     "5": "5",
                     "6": "6",
                     "7": "7",
                     "8": "8",
                     "9": "9",
                     ":": ":",
                     ";": ":",
                     "<": "<",
                     "=": "=",
                     ">": ">",
                     "?": "?",
                     "@": "*",
                     "A": "A",
                     "B": "B",
                     "C": "C",
                     "D": "D",
                     "E": "E",
                     "F": "F",
                     "G": "G",
                     "H": "H",
                     "I": "I",
                     "J": "J",
                     "K": "K",
                     "L": "L",
                     "M": "M",
                     "N": "N",
                     "O": "O",
                     "P": "P",
                     "Q": "Q",
                     "R": "R",
                     "S": "S",
                     "T": "T",
                     "U": "U",
                     "V": "V",
                     "W": "W",
                     "X": "X",
                     "Y": "Y",
                     "Z": "Z",
                     "[": "(",
                     "\\": "/",
                     "]": ")",
                     "^": "*",
                     "_": "-",
                     "`": "'",
                     "{": "(",
                     "|": "I",
                     "}": ")",
                     "~": "-"
}


def unicode_to_default_charset(inp):
    # uppercase
    s = inp.upper()
    # crlf -> lf
    s = s.replace('\r\n', '\n')
    # transcode to default-charset
    outp = ''
    for c in s:
        decoded = unidecode.unidecode(c)
        if decoded in default_charset_replacement_table:
            outp += default_charset_replacement_table[decoded]
        elif c in [chr(10), '␛', '␀']:
            outp += c
        else:
            # drop the char
            pass

    return outp

