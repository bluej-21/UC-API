from bs4 import BeautifulSoup

def get_td_text(td):
    for c in td.contents:
        try:
            if c.get_text().strip('\n'):
                return c.get_text()
        except AttributeError as e:
            try:
                if c.span.a.get_text().strip('\n'):
                    return c.span.get_text()
            except:
                pass

    return ''

def get_course_data():
    data = open('course.html','r').read()
    soup = BeautifulSoup(data, 'html.parser')
    tables = soup.find_all('table') 
    datas = []
    for table in tables:
        data = []
        # get table header
        rows = table.find_all('tr')
        for r in rows:
            print r
        headers = [td.text.strip() for td in rows[0].find_all('td')]
        for row in rows[1:]:
            row_html = [get_td_text(td) for td in row.find_all('td')]
            row_data = zip(headers, row_html)
            data.append(row_data)
        datas.append(data)
    return datas

print get_course_data()

