import re
from copy import deepcopy
from enum import Enum

from Clustering.K_Means.HTML_CLUSTERING.utils.parser import CommentParser, ScriptParser


class Tag(Enum):
    OPEN = 1
    CLOSE = 2
    UNPAIRED = 3


class HTMLOffset:
    __slots__ = ('start', 'end', 'is_text_content')

    def __init__(self, start, end, is_text_content=False):
        self.start = start
        self.end = end
        self.is_text_content = is_text_content

    def __repr__(self):
        return str(self)


class HtmlTag(HTMLOffset):
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
            self._attributes = {}
            self._attr_text = attr_text

    @property
    def attributes(self):
        if not self._attributes and self._attr_text:
            for attr_match in self._ATTR_REGEXP.findall(self._attr_text):
                name = attr_match[0].lower()
                values = [v for v in attr_match[1:] if v]
                # According to HTML spec if attribute name is repeated only the
                # first one is taken into account
                if name not in self._attributes:
                    self._attributes[name] = values[0] if values else None
        return self._attributes


class HTMLDataFrame:
    def __init__(self, body):
        self.body = body
        self.comment_parser = CommentParser()
        self.script_parser = ScriptParser()

    def parse(self):
        parsed_result = []

        tag_start = -1
        tag_end = -1
        script = False
        open_tag = False
        quote_single = False
        quote_double = False

        reset_tag = True
        slash = False
        has_attributes = False
        yield_tag = False

        tag_name = ""
        tag_attributes = ""

        prev_char = ""
        i = 0

        for char in self.body:
            if reset_tag:
                reset_tag = False
                slash = False
                has_attributes = False
                tag_name = ""
                tag_attributes = ""
                yield_tag = False

            if open_tag or script:
                if char == '"' and not quote_single:
                    quote_double = not quote_double
                if char == "'" and not quote_double:
                    quote_single = not quote_single
            else:
                quote_single = quote_double = False
            quoted = quote_double or quote_single

            if not quoted:
                if self.comment_parser.parse(char, i):
                    if (tag_end + 1) < self.comment_parser.start:
                        parsed_result.append(HTMLOffset(tag_end + 1, self.comment_parser.start, not script))
                    tag_end = self.comment_parser.end
                    parsed_result.append(HTMLOffset(self.comment_parser.start, tag_end + 1, False))
                    reset_tag = True
                    if (self.comment_parser.end - self.comment_parser.start) == 2:
                        open_tag = False

                if self.comment_parser.inside_comment:
                    open_tag = False
                else:
                    if script:
                        open_tag = False
                        if self.script_parser.parse(char, i):
                            script = False
                            if (tag_end + 1) < self.script_parser.start:
                                parsed_result.append(HTMLOffset(tag_end + 1, self.script_parser.start, False))
                            tag_end = self.script_parser.end
                            parsed_result.append(HtmlTag(Tag.CLOSE, "script", "", self.script_parser.start, tag_end + 1))
                    elif open_tag:
                        if quoted:
                            if has_attributes:
                                tag_attributes += char
                        elif char == "<":
                            tag_end = i - 1
                            yield_tag = True
                        elif char == ">":
                            if prev_char == "/":
                                slash = True
                            tag_end = i
                            yield_tag = True
                            open_tag = False
                        elif char == "/":
                            if prev_char == "<":
                                slash = True
                        elif char.isspace():
                            if has_attributes:
                                if prev_char == "/":
                                    tag_attributes += "/"
                                tag_attributes += char
                            elif tag_name:
                                has_attributes = True
                        else:
                            if has_attributes:
                                tag_attributes += char
                            else:
                                tag_name += char.lower()
                        if yield_tag:
                            if not slash:
                                tag_type = Tag.OPEN
                            elif prev_char != "/":
                                tag_type = Tag.CLOSE
                            else:
                                tag_type = Tag.UNPAIRED
                            if tag_name != "!doctype":
                                parsed_result.append(HtmlTag(tag_type, tag_name, tag_attributes, tag_start, tag_end + 1))
                            if tag_name == "script":
                                script = True
                            if open_tag:
                                tag_start = i
                            reset_tag = True
                    else:
                        open_tag = False
                        if char == "<" and not quoted:
                            open_tag = True
                            tag_start = i
                            if tag_start > tag_end + 1:
                                parsed_result.append(HTMLOffset(tag_end + 1, tag_start, True))
                            tag_end = tag_start
                prev_char = char
                i += 1

        if tag_end + 1 < len(self.body):
            parsed_result.append(HTMLOffset(tag_end + 1, len(self.body), True))
        return parsed_result


class HtmlPage:
    def __init__(self, body, headers=None):
        self.body = body
        self.parsed_body = list(HTMLDataFrame(body).parse())
        self.headers = headers or {}

    def subregion(self, start=0, end=None):
        """HtmlPageRegion constructed from the start and end index (inclusive)
        into the parsed page
        """
        return HtmlPageParsedRegion(self, start, end)

    def fragment_data(self, dataframe):
        """portion of the body corresponding to the HtmlDataFragment"""
        return self.body[dataframe.start:dataframe.end]


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


class HtmlPageRegion:
    """A Region of an HtmlPage that has been extracted
    """
    def __init__(self, htmlpage, _):
        """Construct a new HtmlPageRegion object.

        htmlpage is the original page and data is the raw html
        """
        self.htmlpage = htmlpage

    @property
    def text_content(self):
        return self
