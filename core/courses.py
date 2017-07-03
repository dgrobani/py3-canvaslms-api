import operator
import re

import canvas.core.api as api
from canvas.core.accounts import all_programs, program_account
from canvas.core.io import wait
from canvas.core.terms import all_terms, term_id_from_name


def course_front_page_set(course_id):
    """ return true if a front page has been set for a course """
    for page in get_course_pages(course_id):
        if page['front_page']:
            return True
    return False


def course_is_published(course):
    """ return true if a course is published """
    return course['workflow_state'] in ['available', 'completed']


def get_course(course_id):
    """ return a course """
    return api.get('courses/{}'.format(course_id)).json()


def get_course_announcements(course_id):
    """ return a list of announcements """
    return api.get_list('courses/{}/discussion_topics?only_announcements=true'.format(course_id))


def get_course_by_sis_id(sis_id):
    """ return one course for an sis id """
    return api.get('courses/sis_course_id:{}'.format(sis_id)).json()


def get_course_conferences(course_id):
    """ return a list of a course's conferences """
    return api.get('courses/{}/conferences'.format(course_id)).json()['conferences']


def get_course_files(course_id):
    """ return a list of a course's files """
    return api.get_list('courses/{}/files'.format(course_id))


def get_course_front_page(course_id):
    """ return a course's front page """
    return api.get('courses/{}/front_page'.format(course_id)).json()


def get_course_modules(course_id):
    """ return a list of a course's modules with its items [api won't return items if too many] """
    return sorted(api.get_list('courses/{}/modules?include[]=items'.format(course_id)), key=lambda m: m['position'])


def get_course_module_items(course_id, course_module):
    """ return a list of a module's items [if api didn't return items, make explicit call to get them] """
    if 'items' in course_module:
        return course_module['items']
    else:
        return sorted(api.get_list('courses/{}/modules/{}/items'
                                   .format(course_id, course_module['id'])), key=lambda m: m['position'])


def get_course_page(course_id, page_url):
    """ get a course page """
    return api.get('courses/{}/pages/{}'.format(course_id, page_url)).json()


def get_course_pages(course_id):
    """ return a list of a course's pages
    NOTE: api doesn't include page['body'] when requesting list """
    return api.get_list('courses/{}/pages'.format(course_id))


def get_course_people(course_id, role):
    """ return a list of a course's people with a given role
        https://canvas.instructure.com/doc/api/all_resources.html#method.courses.users """
    if role in ['teacher', 'student', 'student_view', 'ta', 'observer', 'designer']:
        people = api.get_list('courses/{}/users?include[]=email&enrollment_type[]={}'.format(course_id, role))
        return [] if 'errors' in people else people
    else:
        # e.g. Faculty of record
        people = []
        for person in api.get_list('courses/{}/users?include[]=email&include[]=enrollments'.format(course_id)):
            for enrollment in person['enrollments']:
                if enrollment['role'] == role:
                    del person['enrollments']
                    people.append(person)
                    break
        return people


def get_course_sections(course_id):
    """ return a list of a course's sections """
    return sorted(api.get_list('courses/{}/sections'.format(course_id)), key=lambda s: s['name'])


def get_course_syllabus_body(course_id):
    """ return a course's syllabus body html """
    return api.get('courses/{}?include[]=syllabus_body'.format(course_id)).json()['syllabus_body']


def get_course_tabs(course_id):
    """ return a list of a course's navigation tabs """
    return api.get_list('courses/{}/tabs'.format(course_id))


def get_courses(terms, programs, synergis, whitelist=None):
    """ yield a course augmented with sis info from a sorted list of courses for a list of terms & programs
        gratitude to http://nedbatchelder.com/text/iter.html#h_customizing_iteration
        NOTE: api returns courses in a subaccount AND ITS SUBACCOUNTS """

    if whitelist:
        for course_sis_id in sorted(whitelist):
            course = get_course_by_sis_id(course_sis_id)
            course_sis_info = validate_course(course)
            if course_sis_info:
                course['course_sis_info'] = course_sis_info
                yield course
            else:
                print('>>> no course for {}'.format(course_sis_id))
    else:
        for term in terms or all_terms():
            print(term, '-' * 70)
            for program in programs or all_programs(synergis):
                print(program, '-' * 70)
                courses = api.get_list('accounts/{}/courses?enrollment_term_id={}'
                                       .format(program_account(program), term_id_from_name(term)))
                for course in sorted([course for course in courses if course['sis_course_id']],
                                     key=operator.itemgetter('sis_course_id')):
                    course_sis_info = validate_course(course)
                    if course_sis_info:
                        course['course_sis_info'] = course_sis_info
                        yield course


def parse_course_sis(course_sis_id):
    """ return a dict of the info in a course sis id  """

    if not course_sis_id:
        return None

    # new format implemented 2016.02.08
    new_format_match = re.match(r'(.*)-(.*)-(.*)-(.*)-(.*)-(.*)-(.*)-(.*)', course_sis_id)
    if new_format_match:
        program = new_format_match.group(4)
        return {"term": '{}-{}'.format(new_format_match.group(1), new_format_match.group(2)),
                "session": new_format_match.group(3),
                "program": program,
                "number": ('N' if program.startswith('N') else program) + new_format_match.group(5),
                "type": new_format_match.group(6),
                "campus": new_format_match.group(7),
                "section": new_format_match.group(8)}

    old_format_match = re.match(r'(.*)-(.*)-(.*)-(.*)-(.*)-(.*)-(.*)', course_sis_id)
    if old_format_match:
        program = old_format_match.group(4)
        number_prefix = {
            'BSCI': 'BSCI',
            'GENED': 'NGE',
            'IPE': 'IPE',
            'NURSG': 'N',
            'OCCTH': 'OT',
            'PA': 'PA',
            'PM': 'PM',
            'PHYTH': 'PT'
        }[program]
        return {"term": old_format_match.group(1),
                "campus": old_format_match.group(2),
                "session": old_format_match.group(3),
                "program": program,
                "number": number_prefix + old_format_match.group(5),
                "type": old_format_match.group(6),
                "section": old_format_match.group(7)}

    return None


def update_course_page_contents(course_id, page_url, body):
    """ update a course page's content """
    req_data = {'wiki_page[body]': body}
    return api.put('courses/{}/pages/{}'.format(course_id, page_url), req_data)


def update_tab(course_id, tab_id, position, hidden):
    """ update a course navigation tab and return the updated tab """
    req_data = {'position': position, 'hidden': hidden}
    return api.put('courses/{}/tabs/{}'.format(course_id, tab_id), req_data).json()


def validate_course(course):
    """ if valid, return dict of course info from SIS ID, else return None """

    if 'sis_course_id' not in course:
        return None

    # get the course id & sis id
    course_sis_id = course['sis_course_id']
    if not course_sis_id:
        print('>>> no sis id for https://samuelmerritt.instructure.com/courses/{}'.format(course['id']))
        return None

    # derive course info from the sis id
    course_sis_info = parse_course_sis(course_sis_id)
    if not course_sis_info:
        print('>>> bad sis id: {}'.format(course_sis_id))
        return None

    # alert & skip if course is cross-listed across programs
    for section in get_course_sections(course['id']):
        if section['nonxlist_course_id']:
            nonxlist_course_sis_id = get_course(section['nonxlist_course_id'])['sis_course_id']
            section_course_info = parse_course_sis(nonxlist_course_sis_id)
            if section_course_info['program'] != course_sis_info['program']:
                print('{} >>> cross-listed across programs with {}'.format(course_sis_id, nonxlist_course_sis_id))
                return None

    return course_sis_info


def create_course(account_id, code, name):
    """ create a new course and return the new course """
    req_data = {
        'course[course_code]': code,
        'course[name]': name
    }
    return api.post('accounts/{}/courses'.format(account_id), req_data).json()


def create_enrollment(course_id, canvas_or_sis_user_id, user_id, role, notify=False):
    """ enroll a user in a course
    https://canvas.instructure.com/doc/api/enrollments.html#method.enrollments_api.create
    """
    req_data = {
        'enrollment[user_id]': user_id if canvas_or_sis_user_id == 'canvas' else 'sis_user_id:' + user_id,
        'enrollment[enrollment_state]': 'active',
        'enrollment[notify]': notify
    }
    role_translate = {'student': 'StudentEnrollment', 'teacher': 'TeacherEnrollment', 'ta': 'TaEnrollment',
                      'observer': 'ObserverEnrollment', 'designer': 'DesignerEnrollment'}
    if role in role_translate:
        req_data['enrollment[type]'] = role_translate[role]
    else:
        req_data['enrollment[role_id]'] = role

    print(api.post('courses/{}/enrollments'.format(course_id), req_data).json())


def copy_course(source_course_id, dest_course_id):
    """ copy course content from source to dest
    https://canvas.instructure.com/doc/api/content_migrations.html#method.content_migrations.create
    https://community.canvaslms.com/thread/2454#comment-9347
    """
    req_data = {
        'migration_type': 'course_copy_importer',
        'settings[source_course_id]': source_course_id
    }
    progress_url = api.post('courses/{}/content_migrations'.format(dest_course_id), req_data).json()['progress_url']
    progress = 0
    while progress < 100:
        progress = api.get(progress_url).json()['completion']
        wait('\tcopy progress: {}%'.format(int(progress)), 5)
    print('\r\tcopy completed')


def delete_course(course_id):
    """ delete a course """
    req_data = {'event': 'delete'}
    api.delete('courses/{}'.format(course_id), req_data)


def reset_course(course_id):
    """ reset a course's content (deletes the course and creates a new course); return the new course """
    req_data = {}
    return api.post('courses/{}/reset_content'.format(course_id), req_data).json()


def rename_course(course_id, name, code):
    """ update a course's name and/or code """
    req_data = {}
    if name:
        req_data['course[name]'] = name
    if code:
        req_data['course[code]'] = code
    if req_data:
        api.put('courses/{}'.format(course_id), req_data)


def get_courses_by_account_id(account_id, term):
    """ return a list of courses for a program by its account id """
    return sorted(api.get_list('accounts/{}/courses?enrollment_term_id={}'.format(account_id, term_id_from_name(term))),
                  key=lambda c: c['name'])


def get_onl_masters(program):
    account_id = {'NFNPO': '168920', 'NCMO': '168922'}[program]
    return sorted([course for course in get_courses_by_account_id(account_id, 'DEFAULT')
            if course['name'].startswith('N') and course['name'].endswith(' - MASTER')], key=lambda c: c['name'])
