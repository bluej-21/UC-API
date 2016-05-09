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
DEPT_URL='http://www.registrar.ucla.edu/schedule/crsredir.aspx?' \
            'termsel={term}&' \
            'subareasel={dept}'
COURSE_DATA = [u'IDNumber', u'Type', u'Sec', 
              u'Days', u'Start', u'Stop',  
              u'Building', u'Room', u"Res't", 
              u'#En', u'EnCp', u'#WL', u'WLCp', u'Status']

def clean_text(t):
        dirty = [u'\xc2\xa0', '\n', '  ']
        regex = '[' + re.escape(''.join(dirty)) + ']'
        return re.sub(regex, '', t)

def get_doc_text(doc):
    for t in doc.itertext():
        clean = "".join(t.split())
        cleaned = clean_text(clean)
        if cleaned:
            return cleaned 
    return ''


def get_td_text(td):

    td_string = str(td)
    doc = fromstring(td_string)
    doc_text = get_doc_text(doc)

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
    session_pattern = re.compile(
        r'ctl00_BodyContent' \
        'PlaceHolder_crsredir1_pnl(NormalInfo|SessionInfo[a-zA-Z])'
    ) 

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
    rows = table.find_all('tr')
    for i in range(len(rows)):
        h = []
        for td in rows[i].find_all('td'):
            unclean_td = get_td_text(td)
            print "unclean: %s" % unclean_td
            if unclean_td:
                h.append(unclean_td)
        if h and h[0] == u'IDNumber':
            print i + 1
            return i + 1
    return 0 

def get_course_data(term, dept, course_code, summer=False):
    url = "http://www.registrar.ucla.edu/schedule/detselect.aspx?termsel={term}&subareasel={dept}&idxcrs={course_code}" 
    if summer:
        url = 'http://www.registrar.ucla.edu/schedule/detselect_summer.aspx?termsel={term}&subareasel={dept}&idxcrs={course_code}'
    url = url.format(term=term, dept=dept, course_code=course_code)
    print url
    soup = get_soup(url)
    tables = soup.find_all('table') 
    j_data = {term : {}} 

    for table in tables:
        i = validate_table(table)
        print i
        if i > 0:
            print i
            rows = table.find_all('tr')
            header = [get_td_text(td) for td in rows[i-1].find_all('td')]
            print rows
            print header
            for row in rows[i:]:
                row_data = [get_td_text(td) for td in row.find_all('td')]
                if len(row_data) > 2:
                    if len(row_data) == 2*len(COURSE_DATA):
                        row_data = [
                    row_data[i]  for i in range(len(row_data)) if i % 2 == 0
                        ]
                    z = zip(COURSE_DATA,row_data)
                    data = {d:v for d,v in z}
                    j_data[term][data[u'Sec']] = data
    return j_data 



          


if __name__ == '__main__':
    x = get_course_data('16W', 'EL+ENGR', '0102++++', summer=False)
    print x

