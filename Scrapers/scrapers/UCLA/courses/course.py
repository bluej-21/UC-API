from bs4 import BeautifulSoup
from bs4 import NavigableString

def _depth_first_html_search(html, level, levelDic):
    for node in html.children:
        if isinstance(node, NavigableString):
            if node.string:
                if level in levelDic.keys():
                    levelDic[level].append(node.string)
                else:
                    levelDic[level] = [node.string]
            return None
        _depth_first_html_search(node, level + 1, levelDic)
    return None

def get_text(tree):
    text_dict = {}
    level = 0

    _depth_first_html_search(tree, level, text_dict)
    return text_dict

def get_td_text(td):
    text = get_text(td)
    max_depth = max(text.keys())
    return text[max_depth][0]

def clean(txt):
    return txt if txt != u'\xa0' else ''

def get_course_data():
    data = open('course.html','r').read()
    soup = BeautifulSoup(data, 'html.parser')
    table = soup.find('table') 
    data = []

    # get table header
    rows = table.find_all('tr')
    header = [clean(get_td_text(td)) for td in rows[0].find_all('td')]

    # still only two rows getting caputred

get_course_data()

