from bs4 import BeautifulSoup
from bs4 import NavigableString
from tidylib import tidy_document
from lxml import html
from lxml.html import fromstring
import re
import requests
import logging
import sys
import time
import json
import scrapers
import itertools

logging.basicConfig(filename='ucla_courses.log')
HOMEURL = 'http://registrar.ucla.edu'


def get_popover_items(popover):
    info = {}

    enrlmnt_restriction = popover.find('div', {'class':'enrollment_restrictions_content'})
    grade_type = popover.find('div', {'class': 'grade_type'})
    final_exam = popover.find('div', {'class': 'final_exam'})
    course_notes = popover.find('div', {'class': 'course_notes'})

    if enrlmt_restriction:
        info['enrollmentRestriction'] = enrlmnt_restriction.find('p').text
    if grade_type:
        grade = grade_type.find_all('p')
        more_info = {}
        for i in grade:
            text = i.text.split(':')
            key = text[0].strip()
            value = ' '.join([x.strip() for x in text[1:]])
            more_info[key] = value
        info['gradeType'] = more_info
    if final_exam:
        content = final_exam.find('div', {'class': 'final_exam_content'})
        data = content.find('div', {'class': 'data-row'})
        date = data.find('div', {'class': 'span1'}).text
        day = data.find('div', {'class': 'span2'}).text
        time = data.find('div', {'class': 'span3'}).text
        locations = data.find('div', {'class': 'span4'}).text
        final_exam_data = {'date': date, 'day': day, 'time': time, 'location(s)': locations}
        info['finalExam'] = final_exam_data
    if course_notes:
        content = course_notes.find('div', {'class': 'class_notes_content'})
        text = map(lambda x: x.find('p').text, content.find('ul').find_all('li'))
        info['classNotes'] = text

    return info
    

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
    # tidy, errors = tidy_document(html)
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_dept_description_urls(url=HOMEURL + '/Academics/Course-Descriptions'):
    dept_name_to_desc_url = []
    soup = get_soup(url)
    contents = soup.find("div", {"class": "list-alpha"})
    for letter in contents.find_all("div", {"class": "list-letter"}):
        depts = letter.find_all('a', href=True)
        for d in depts:
            dept_name_to_desc_url.append((d.text, d['href']))
        
    return dept_name_to_desc_url 


def get_course_description(url):
    soup = get_soup(url)
    course_descriptions = []
    course_views = soup.find_all("ul", {"class": "category-list"})
    for courses in course_views:
        descriptions = courses.find_all("li", {"class": "category-list-item"})
        for course_description in descriptions:
            text = course_description.find('h3').text.split('.')
            course_code = text[0]
            name = ' '.join(text[1:])
            d = course_description.find_all('p')
            units = d[0].text.split(':')[1].strip()
            d = d[1].text
            course_descriptions.append({
                course_code: 
                    [('name', name), 
                     ('description', d),
                     ('units', units)
                     ]
            })

    return course_descriptions


def get_dept_course_timings(url):
    soup = get_soup(url)
    courses = soup.find_all('div', {'class': 'class-title'})
    dept_data = []
    for course in courses:
        print course
        name = course.find('h3').find('a').text.split(' - ')
        course_code = name[0]
        course_title = ' '.join(name[1:])

        section_column = course.find_all('div', {'class': 'sectionColumn'})
        status_column = course.find_all('div', {'class':'statusColumn'})
        waitlist_column = course.find_all('div', {'class':'waitlistColumn'})
        info_column = course.find_all('div', {'class':'infoColumn'})
        day_column = course.find_all('div', {'class': 'dayColumn'})
        time_column = course.find_all('div', {'class': 'timeColumn'})
        unit_column = course.find_all('div', {'class': 'unitColumn'})
        instructor_column = course.find_all('div', {'class': 'instructorColumn'})
        print section_column        
        i = len(section_column)
        section = [x for x in range(i)] 
        status = [x.find('p').text for x in status_column]
        waitlist = [x.find('p').text for x in waitlist_column]
        info = [get_popover_items(x.find('div', {'class':'popver-content'})) for x in info_column] 
        days = [x for x in range(i)] 
        times = [x for x in range(i)] 
        units = [x for x in range(i)]
        instructors = [x for x in range(i)] 

        for sc, st, wt, days, tms, unts, inst in itertools.izip(
                section, status, waitlist, info, days, times, units, instructors):
            data = {'section': sc, 'status': st, 'waitlist': wt, 'days': days, 'time': tms, 'units': unts, 'instructor(s)': inst}
            dept_data.append(data)
    return dept_data
    
    
# complete_urls = map(lambda x: (x[0], HOMEURL + x[1]), get_dept_description_urls())
# descriptions = map(lambda x: (x[0], get_course_description(x[1])), complete_urls)
print get_dept_course_timings('https://sa.ucla.edu/ro/Public/SOC/Results?t=16F&sBy=subject&sName=Computer+Science+%28COM+SCI%29&subj=COM+SCI&crsCatlg=Enter+a+Catalog+Number+or+Class+Title+%28Optional%29&catlg=&cls_no=&btnIsInIndex=btn_inIndex')
