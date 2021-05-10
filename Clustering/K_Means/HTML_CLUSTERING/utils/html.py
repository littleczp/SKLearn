import re
from collections import OrderedDict
from copy import deepcopy
from enum import Enum

_ATTR = "((?:[^=/<>\s]|/(?!>))+)(?:\s*=(?:\s*\"(.*?)\"|\s*'(.*?)'|([^>\s]+))?)?"
_TAG = "<(\/?)(\w+(?::\w+)?)((?:\s*" + _ATTR + ")+\s*|\s*)(\/?)>?"
_DOCTYPE = r"<!DOCTYPE.*?>"
_SCRIPT = "(<script.*?>)(.*?)(</script.*?>)"
_COMMENT = "(<!--.*?--!?>|<\?.+?>|<!>)"

_ATTR_REGEXP = re.compile(_ATTR, re.I | re.DOTALL)
_HTML_REGEXP = re.compile("%s|%s|%s" % (_COMMENT, _SCRIPT, _TAG), re.I | re.DOTALL)
_DOCTYPE_REGEXP = re.compile("(?:%s)" % _DOCTYPE)
_COMMENT_REGEXP = re.compile(_COMMENT, re.DOTALL)


class TagType(Enum):
    OPEN = 1
    CLOSE = 2
    UNPAIRED = 3


class HtmlDataFragment:
    __slots__ = ('start', 'end', 'is_text_content')

    def __init__(self, start, end, is_text_content=False):
        self.start = start
        self.end = end
        self.is_text_content = is_text_content


class HtmlTag(HtmlDataFragment):
    __slots__ = ('tag_type', 'tag', '_attributes', '_attr_text')
    _ATTR_REGEXP = re.compile(
        "((?:[^=/<>\s]|/(?!>))+)(?:\s*=(?:\s*\"(.*?)\"|\s*'(.*?)'|([^>\s]+))?)?",
        re.I | re.DOTALL
    )

    def __init__(self, tag_type, tag, attr_text, start, end):
        super().__init__(self, start, end)
        self.tag_type = tag_type
        self.tag = tag
        if isinstance(attr_text, dict):
            self._attributes = attr_text
            self._attr_text = None
        else:
            self._attributes = OrderedDict()
            self._attr_text = attr_text

    @property
    def attributes(self):
        if not self._attributes and self._attr_text:
            for attr_match in self._ATTR_REGEXP.findall(self._attr_text):
                name = attr_match[0].lower()
                values = [v for v in attr_match[1:] if v]
                if name not in self._attributes:
                    self._attributes[name] = values[0] if values else None
        return self._attributes


class HtmlPage:
    def __init__(self, body, headers=None):
        self.body = body
        self.parsed_body = list(parse(body))
        self.headers = headers or {}

    def subregion(self, start=0, end=None):
        """HtmlPageRegion constructed from the start and end index (inclusive)
        into the parsed page
        """
        return HtmlPageParsedRegion(self, start, end)

    def fragment_data(self, dataframe):
        """portion of the body corresponding to the HtmlDataFragment"""
        return self.body[dataframe.start:dataframe.end]


class TextPage(HtmlPage):
    """An HtmlPage with one unique HtmlDataFragment, needed to have a
    convenient text with same interface as html page but avoiding unnecesary
    reparsing"""
    def __init__(self, body, headers=None):
        super().__init__(body, headers)
        self.parsed_body = [HtmlDataFragment(0, len(self.body), True)]


class HtmlPageRegion:
    """A Region of an HtmlPage that has been extracted"""

    def __new__(cls, htmlpage, data):
        return str(data)

    def __init__(self, htmlpage, _):
        """
        Construct a new HtmlPageRegion object.
        htmlpage is the original page and data is the raw html
        """
        self.htmlpage = htmlpage

    @property
    def text_content(self):
        return self


class HtmlPageParsedRegion:
    """A region of an HtmlPage that has been extracted

    This has a parsed_fragments property that contains the parsed html
    fragments contained within this region
    """

    def __new__(cls, htmlpage, start_index, end_index):
        text = htmlpage.body
        if text:
            text_start = htmlpage.parsed_body[start_index].start
            text_end = htmlpage.parsed_body[end_index or -1].end
            text = htmlpage.body[text_start:text_end]

        return HtmlPageRegion(htmlpage, text)

    def __init__(self, htmlpage, start_index, end_index):
        self.htmlpage = htmlpage
        self.start_index = start_index
        self.end_index = end_index

    def __copy__(self, page=None):
        page = page or self.htmlpage
        return HtmlPageParsedRegion(page, self.start_index, self.end_index)

    def __deepcopy__(self, memo):
        page = deepcopy(self.htmlpage)
        return self.__copy__(page)

    @property
    def parsed_fragments(self):
        """HtmlDataFragment or HtmlTag objects for this parsed region"""
        end = self.end_index + 1 if self.end_index is not None else None
        return self.htmlpage.parsed_body[self.start_index:end]

    @property
    def text_content(self):
        """Text content of this parsed region"""
        return TextPage(self.htmlpage.url, self.htmlpage.headers).subregion()


def parse(text):
    start_pos = 0
    match = _DOCTYPE_REGEXP.match(text)
    if match:
        start_pos = match.end()
    prev_end = start_pos
    for match in _HTML_REGEXP.finditer(text, start_pos):
        start = match.start()
        end = match.end()

        if start > prev_end:
            yield HtmlDataFragment(prev_end, start, True)

        if match.groups()[0] is not None:  # comment
            yield HtmlDataFragment(start, end)
        elif match.groups()[1] is not None:  # <script>...</script>
            for e in _parse_script(match):
                yield e
        else:  # tag
            yield _parse_tag(match)

        prev_end = end
    textlen = len(text)
    if prev_end < textlen:
        yield HtmlDataFragment(prev_end, textlen, True)


def _parse_script(match):
    """parse a <script>...</script> region matched by _HTML_REGEXP"""
    open_text, content, close_text = match.groups()[1:4]

    open_tag = _parse_tag(_HTML_REGEXP.match(open_text))
    open_tag.start = match.start()
    open_tag.end = match.start() + len(open_text)

    close_tag = _parse_tag(_HTML_REGEXP.match(close_text))
    close_tag.start = match.end() - len(close_text)
    close_tag.end = match.end()

    yield open_tag
    if open_tag.end < close_tag.start:
        start_pos = 0
        for m in _COMMENT_REGEXP.finditer(content):
            if m.start() > start_pos:
                yield HtmlDataFragment(open_tag.end + start_pos, open_tag.end + m.start())

            yield HtmlDataFragment(open_tag.end + m.start(), open_tag.end + m.end())
            start_pos = m.end()
        if open_tag.end + start_pos < close_tag.start:
            yield HtmlDataFragment(open_tag.end + start_pos, close_tag.start)
    yield close_tag


def _parse_tag(match):
    """
    parse a tag matched by _HTML_REGEXP
    """
    data = match.groups()
    closing, tag, attr_text = data[4:7]
    # if tag is None then the match is a comment
    if tag is not None:
        unpaired = data[-1]
        if closing:
            tag_type = TagType.CLOSE
        elif unpaired:
            tag_type = TagType.UNPAIRED
        else:
            tag_type = TagType.OPEN
        return HtmlTag(tag_type, tag.lower(), attr_text, match.start(), match.end())
