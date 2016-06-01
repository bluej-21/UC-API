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

logging.basicConfig(filename='ucla_courses.log')
HOMEURL = 'http://registrar.ucla.edu'

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
    
complete_urls = map(lambda x: (x[0], HOMEURL + x[1]), get_dept_description_urls())
descriptions = map(lambda x: (x[0], get_course_description(x[1])), complete_urls)
print descriptions
