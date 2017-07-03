def scrub(text):
    """ return a string with targeted non-ascii characters replaced, all others replaced with *, white space trimmed """
    # """ return a string with non-ascii characters and consecutive spaces converted to one space """
    # if not text:
    #     return ''
    # # text = ''.join([i if 31 < ord(i) < 127 else ' ' for i in text])
    # # convert consecutive non-ascii characters to one space & clean up html characters
    # text = re.sub(r'[^\x1F-\x7F]+', ' ', text) \
    #     .replace('&amp;', '&').replace('&quot;', '"').replace('<p>', '').replace('</p>', '')
    # # remove leading, trailing, and repeated spaces
    # return ' '.join(text.split())

    # pairs = {
    #     '&amp;': '&',
    #     '&quot;': '"',
    #     '<p>': '',
    #     '</p>': ''
    #     '\u00E2\u0080\u0099': "'",
    #     '\u0009': ' ',    # tab
    #     '\u002D': '-',    # -
    #     '\u00AB': '"',    # �
    #     '\u00BB': '"',    # �
    #     '\u2013': '-',    # �
    #     '\u2014': '-',    # �
    #     '\u2018': "'",    # �
    #     '\u2019': "'",    # �
    #     '\u201A': "'",    # �
    #     '\u201B': "'",    # ?
    #     '\u201C': '"',    # �
    #     '\u201D': '"',    # �
    #     '\u201E': '"',    # �
    #     '\u201F': '"',    # ?
    #     '\u2022': '',     # �
    #     '\u2026': '...',  # �
    #     '\u2039': '<',    # �
    #     '\u203A': '>',    # �
    #     '\u2264': '<='    # ?
    # bullets?
    # }
    # scrubbed = text
    # for crap in pairs:
    #     scrubbed = scrubbed.replace(crap, pairs[crap])
    # scrubbed = re.sub(r'[^\x1F-\x7F]+', '*', scrubbed)
    return ' '.join(text.replace('&amp;', '&').replace('&quot;', '"').replace('<p>', '').replace('</p>', '').split())


def quote(text):
    return '"{}"'.format(text)


def make_leader(program, course_sis_id):
    return '{: <12}{: <40}'.format(program, course_sis_id)


class DictDiffer(object):
    """
    A dictionary difference calculator from http://www.stackoverflow.com/questions/1165352#1165552

    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items deleted
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [set(d.keys()) for d in (current_dict, past_dict)]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def deleted(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
