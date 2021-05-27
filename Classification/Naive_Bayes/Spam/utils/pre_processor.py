import re

import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords


class EmailText:
    # email header
    email_subject_pattern = re.compile(r"[\s\S]*<p>Subject:.<span.name='subject'>([\s\S]+?)</span></p>")
    email_from_pattern = re.compile(r"[\s\S]*<p>Email From: <span name='email_from'>([\s\S]+?)</span></p>")
    email_label_pattern = re.compile(r"[\s\S]*<p>Labels:<span name='label_ids'>([\s\S]+?)</span></p>")

    # email body(server)
    email_body_div_pattern = re.compile(r"^([\s\S]+?)<div.name='html_body'>")
    email_body_style_pattern = re.compile(r"<style[^>]*?>[\s\S]*?</style>")

    # email_body: 「#」number
    email_body_well_number_2_4_pattern = re.compile(r"#\d{2,4}\b")
    email_body_well_number_5_8_pattern = re.compile(r"#\d{5,8}\b")
    email_body_well_number_9_16_pattern = re.compile(r"#\d{9,16}\b")
    email_body_well_number_16_pattern = re.compile(r"#\d{16,}\b")

    # email_body: 「#」number alpha
    email_body_well_number_alpha_pattern = re.compile(r"#(?![0-9]+\b)(?![a-zA-Z]+\b)[0-9A-Za-z]{4,32}\b")

    # email_body: number
    email_body_number_2_4_pattern = re.compile(r"\b\d{2,4}\b")
    email_body_number_5_8_pattern = re.compile(r"\b\d{5,8}\b")
    email_body_number_9_16_pattern = re.compile(r"\b\d{9,16}\b")
    email_body_number_16_pattern = re.compile(r"\b\d{16,}\b")

    # email_body: md5
    email_body_md5_pattern = re.compile(r"\b[0-9A-Fa-f]{32}\b")

    # email_body: long string
    email_body_long_pattern = re.compile(r"\b(?![0-9]+\b)(?![a-zA-Z]+\b)[0-9A-Za-z]{32,}\b")

    email_body_sub = (
        (email_body_well_number_2_4_pattern, "eb_well_small_num"),
        (email_body_well_number_5_8_pattern, "eb_well_middle_num"),
        (email_body_well_number_9_16_pattern, "eb_well_large_num"),
        (email_body_well_number_16_pattern, "eb_well_xlarge_num"),

        (email_body_well_number_alpha_pattern, "eb_well_num_alpha"),

        (email_body_number_2_4_pattern, "eb_small_num"),
        (email_body_number_5_8_pattern, "eb_middle_num"),
        (email_body_number_9_16_pattern, "eb_large_num"),
        (email_body_number_16_pattern, "eb_xlarge_num"),

        (email_body_md5_pattern, "eb_md5"),
        (email_body_long_pattern, "eb_long_str"),
    )

    # nltk_stem: only for english
    email_words_stem = nltk.stem.SnowballStemmer("english")

    def __get_header(self, email_body):
        email_header = ""

        email_subject = self.email_subject_pattern.match(email_body)
        if email_subject:
            email_header += email_subject.group(1)

        email_from = self.email_from_pattern.match(email_body)
        if email_from:
            email_from = email_from.group(1).replace(".", "_").replace("@", "_")
            # prefix email_from_: Make a distinction with「@email」 from email body
            email_header += f" ef_{email_from}"

        email_label = self.email_label_pattern.match(email_body)
        if email_label:
            email_header += email_label.group(1)

        return email_header

    def __get_body(self, email_body):
        email_body = re.sub(self.email_body_div_pattern, "", email_body)
        email_body = email_body.replace("<p>----------------------------------------------------------------</p>", "")
        email_body = email_body.replace("<p>text/plain email body</p>", "")
        email_body = re.sub(self.email_body_style_pattern, "", email_body)

        bs4_soup = BeautifulSoup(email_body, features="html.parser")
        return bs4_soup.get_text()

    def get_words_stem(self, email_body: str):
        """remove stop words & get words stem"""
        word_list = [word for word in email_body.split() if word.lower() not in stopwords.words('english')]
        return " ".join(list(map(lambda x: self.email_words_stem.stem(x), word_list)))

    def get_email_body(self, email_body):
        email_header = self.__get_header(email_body)
        email_body = self.__get_body(email_body)
        email_stem = self.get_words_stem(email_body)

        email_body = email_header + email_stem
        for pattern, replace_text in self.email_body_sub:
            email_body = re.sub(pattern, replace_text, email_body)

        return email_body
