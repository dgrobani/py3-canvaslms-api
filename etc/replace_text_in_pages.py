import re

from canvas.core.courses import get_course_page, get_course_pages, update_course_page_contents, get_courses, \
    get_courses_whitelisted

from canvas.core.io import tada


def replace_text_in_pages():

    course_whitelist = get_courses_whitelisted([])
    terms = ['2016-2SU']
    programs = ['NFNPO']
    synergis = True

    text_find = '(.*)http://(www.)*synergiseducation.com/academics/schools/SMU/(.*)'
    text_replace = 'http://media.samuelmerritt.edu/'

    for course in course_whitelist or get_courses(terms, programs, synergis):

        course_id = course['course_id']
        print(course['course_sis_id'], course['course_code'])

        # pages; api doesn't include page['body'] when requesting page list, so must request each page
        for page in get_course_pages(course_id):
            page_url = page['url']
            body_old = get_course_page(course_id, page_url)['body']
            if not body_old:
                continue
            body_new = re.sub(text_find, r'\1' + text_replace + r'\3', body_old)
            if body_new != body_old:
                update_course_page_contents(course_id, page_url, body_new)
                # print(page_url, '\n', get_course_page(course_id, page_url)['body'])
                print(page_url)

        # assignments
        # discussions
        # to do; modify from old\mediacore_find_refs.py

if __name__ == '__main__':
    replace_text_in_pages()
    tada()
