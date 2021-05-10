from Clustering.K_Means.HTML_CLUSTERING.utils.html import HtmlPage


def build_dom(template):
    if isinstance(template, HtmlPage):
        return template

    return HtmlPage(body=template)
