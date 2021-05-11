import numpy as np

from Clustering.K_Means.HTML_CLUSTERING.utils.html import HtmlTag, TagType


class TagFrequency:
    def __init__(self):
        self.dictionary = {}
        self.dimension = 0

    def __call__(self, page):
        to_index = []
        for dataframe in filter(self._is_non_closing_tag, page.parsed_body):
            token = self._tag_to_token(dataframe)
            index = self.dictionary.get(token)
            if index is not None:
                to_index.append(index)
            else:
                to_index.append(self.dimension)
                self.dictionary[token] = self.dimension
                self.dimension += 1

        vector = np.zeros((len(self.dictionary),))
        for index in to_index:
            vector[index] += 1
        return vector/np.sum(vector)

    def _is_non_closing_tag(self, dataframe):
        return self._is_tag(dataframe) and not self._is_closing(dataframe)

    def _is_tag(self, dataframe):
        """Check if a dataframe is also an HTML tag"""
        return isinstance(dataframe, HtmlTag)

    def _is_closing(self, dataframe):
        return dataframe.tag_type == TagType.CLOSE

    def _tag_to_token(self, dataframe):
        return dataframe.tag, self._get_class(dataframe)

    def _get_class(self, dataframe):
        """Return a set with class attributes for a given fragment"""
        if self._is_tag(dataframe):
            return frozenset((dataframe.attributes.get('class') or '').split())
        else:
            return frozenset()


tag_freq = TagFrequency()
