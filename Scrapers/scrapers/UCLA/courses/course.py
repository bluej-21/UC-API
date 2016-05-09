from bs4 import BeautifulSoup
from bs4 import NavigableString
from io import StringIO
from tidylib import tidy_document
from lxml.html import fromstring

def _depth_first_html_search(html, level, levelDic):
    for node in html.children:
        if isinstance(node, NavigableString):
            if node.string:
                if level in levelDic.keys():
                    levelDic[level].append(node.string)
                else:
                    levelDic[level] = [node.string]
            return
        _depth_first_html_search(node, level + 1, levelDic)
    return None

def get_text(tree):
    text_dict = {}
    level = 0
    
    _depth_first_html_search(tree, level, text_dict)
    return text_dict

def get_doc_text(doc):
    for t in doc.itertext():
        clean_text = "".join(t.split())
        if clean_text and clean_text != u'\xa0':
            return clean_text
    return ''


def get_td_text(td):
    text = get_text(td)

    # we do this because our get_text method does not work 
    # well with ill-formed html
    td_string = str(td)
    doc = fromstring(td_string)
    doc_text = get_doc_text(doc)

    if text and not doc_text:
        max_depth = max(text.keys())
        txt = text[max_depth][0]
        depth = max_depth
        while txt != '\n' and depth > 0:
            depth -= 1
            for i in len(text[depth]):
                if text[depth][i] and text[depth][i] != '\n':
                    txt = text[depth][i]
                    break
            if txt and txt != '\n':
                break
        return txt.replace('\n','').replace('  ','') if txt != u'\xa0' else ''
    return doc_text 

def get_course_data():
    data = open('course.html','r').read()
    tidy, errors = tidy_document(data)
    soup = BeautifulSoup(tidy, 'html.parser')
    table = soup.find('table') 
    data = []

    # get table header
    rows = table.find_all('tr')
    header = [get_td_text(td) for td in rows[0].find_all('td')]
    for row in rows[1:]:
        row_data = [get_td_text(td) for td in row.find_all('td')]
        z = zip(header, row_data)
        data.append(z)

    return data

print get_course_data()

