from bs4 import BeautifulSoup
from bs4 import NavigableString
from tidylib import tidy_document
from lxml.html import fromstring
import re
import requests
import logging
import sys
import time

logging.basicConfig(filename='ucla_courses.log')

URL='http://www.registrar.ucla.edu/schedule/schedulehome.aspx'
DEPT_URL='http://www.registrar.ucla.edu/schedule/crsredir.aspx?termsel=' \
            '{term}&' \
            'subareasel={dept}'

COURSE_DATA = ['IDNumber', 'Type', 'Sec', 
              'Days', 'Start', 'Stop',  
              'Building', 'Room', "Res't", 
              '#En', 'EnCp', '#WL', 'WLCp', 'Status']

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

def get_soup(url):
    """Get a BeautifulSoup object that represents the html in the url

    params:
        url -- a string that is a url
    """

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        logging.log(40, e)
        sys.exit(1)

    html = response.content
    tidy, errors = tidy_document(html)
    print errors
    soup = BeautifulSoup(tidy, 'html.parser')
    return soup

def get_term_to_subject():
    """Get a tuple of (terms, (dept, dept_url))"""

    soup = get_soup(URL)

    # if not valid_page(soup):
    #     logging.log(ERROR, "page structure is not valid")
    #     sys.exit(1)
    
    # get content
    options = [str(o) for o in soup.find_all('option')]
    term_pattern = re.compile(r'<option value="(\d+\w)">(\w+(\s\w+)* \d{4})<\/option>')

    # group 1/2 matches shorthand for dept name, group 3 matches the
    # actual name
    dept_pattern = re.compile(r'<option value="([A-Z]+([&amp; -]' \
                               '+[A-Z]+)*)">(\w+([ /|,()-]+\w+' \
                               '[ \-().]*)*)<\/option>')

    dept_index = 0
    terms = []
    depts = []
    for option in options:
        m = term_pattern.match(option)
        d = dept_pattern.match(option)

        # can't match both
        if m and d:
            break
        if m:
            dept_index += 1
            terms.append(m.group(1))
        if d:
            search_url = DEPT_URL.format(term='{term}', dept=d.group(1).replace(" ", "-"))
            dept_name = d.group(3).replace("/", "%20F")
            depts.append((dept_name, search_url))

    if not (terms and depts):
        logging.log('CRITICAL', "page is not formatted the same")
        sys.exit(1)

    return (terms, depts)

def get_list_of_courses(dept, dept_url):
    """Return a list of all the courses offered in each term for this dept

    args:
        terms -- a list of terms ex: [summer, winter, fall, spring]
        dept_url -- iterable consisting of a dept name and url
                          ex: ('computer science', 'http://computerscience.com')
    """

    # data structure will look like: { deptname: course: [semesters offered] }
    dept_data = {} 
    soup = get_soup(dept_url)
    session_pattern = re.compile(r'ctl00_BodyContentPlaceHolder_crsredir1_pnl(NormalInfo|SessionInfo[a-zA-Z])') 

    session_divs = soup.find_all('div', id=session_pattern)
    courses_data = []
    for session in session_divs:
        select = session.find('select')
        courses = select.find_all('option')
        for course in courses:
            # each course looks something like:
            # <option value="0031    A">COM SCI 31 - Introduction to Computer Science I</option>
            k = course['value'].replace(' ', '+')
            name = course.text
            courses_data.append([name, k])
    return courses_data 

def validate_table(table):
    pass

def get_course_data(term, dept, course_code, summer=False):
    url = "http://www.registrar.ucla.edu/schedule/detselect.aspx?termsel={term}&subareasel={dept}&idxcrs={course_code}" 
    if summer:
        url = 'http://www.registrar.ucla.edu/schedule/detselect_summer.aspx?termsel={term}&subareasel={dept}&idxcrs={course_code}'
    url = url.format(term=term, dept=dept, course_code=course_code)
    soup = get_soup(url)
    tables = soup.find_all('table') 
    j_data = {term : {}} 

    for table in tables:

        if validate_table(table):
            rows = table.find_all('tr')
            header = [get_td_text(td) for td in rows[0].find_all('td')]
            for row in rows[1:]:
                row_data = [get_td_text(td) for td in row.find_all('td')]
                z = zip(COURSE_DATA,row_data)
                print z
                j_data[term][row_data[2]] = {d:v for d,v in z}
    return j_data 



          


if __name__ == '__main__':
    x = get_course_data('16W', 'EL+ENGR', '0102++++', summer=False)
    for a in x:
        print a
        print '=============================================='

