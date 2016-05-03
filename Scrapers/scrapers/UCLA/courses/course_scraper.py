from bs4 import BeautifulSoup 
import re
import requests
import logging
import sys

logging.basicConfig(filename='ucla_courses.log')

URL='http://www.registrar.ucla.edu/schedule/schedulehome.aspx'
DEPT_URL='http://www.registrar.ucla.edu/schedule/crsredir.aspx?termsel=' \
            '{term}&' \
            'subareasel={dept}'

def parse_course(course_link):
    pass

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
    soup = BeautifulSoup(html, 'html.parser')
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

def get_textbook(url):
    pass

def get_course_data(term, dept, course_code, summer=False):
    url = "http://www.registrar.ucla.edu/schedule/detselect.aspx?termsel={term}&subareasel={dept}&idxcrs={course_code}" 
    if summer:
        url = 'http://www.registrar.ucla.edu/schedule/detselect_summer.aspx?termsel={term}&subareasel={dept}&idxcrs={course_code}'

    soup = get_soup(url)
    tables = soup.find_all('table') 
    # check which tables contain course info
    for table in tables:
        headings = [th.get_text() for th in table.find('tr').find_all('td')]
        if headings[0] == 'ID Number':
            correct_tables.append(table)
            headings = [h for h in headings if h.get_text() != '\xa0']
            datasets = []
            for row in table.find_all("tr")[1:]:
                dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
                datasets.append(dataset)
            


 
    headings = table.find('tr', attr={'class':'dgdClassDataHeader'}).find_all('th')
    headings = [h.get_text() for h in headings if h.get_text() != '&nbsp;']
    print headings
    datasets = []
    for row in table.find_all("tr")[1:]:
	    dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
	    datasets.append(dataset)

    print datasets



          



