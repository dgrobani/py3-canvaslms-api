import requests
import os
import bs4.BeautifulSoup


def get_syllabus(course):
    # returns course syllabus_body
    url = base_url + 'courses/' + str(course) + '?include[]=syllabus_body'
    return requests.get(url, headers=auth_headers).json()['syllabus_body']


def get_root_folder(course):
    # returns folder id
    url = base_url + 'courses/' + str(course) + '/folders/root'
    return requests.get(url, headers=auth_headers).json()['id']


def get_subfolders(folder):
    # returns list of subfolders
    # https://canvas.instructure.com/doc/api/file.pagination.html
    url = base_url + 'folders/' + str(folder) + '/folders?per_page=100'
    return requests.get(url, headers=auth_headers).json()


def get_files(folder):
    # returns list of files
    url = base_url + 'folders/' + str(folder) + '/files?per_page=100'
    return requests.get(url, headers=auth_headers).json()


def get_file_url(file):
    # returns url from file object
    url = base_url + 'files/' + str(file)
    r = requests.get(url, headers=auth_headers).json()
    return r['url'] if 'url' in r else ''


def download_file(source, url, program, course, file):
    print(url)
    r = requests.get(url)
    print(source, r, program, course, file, '\n')
    if not os.path.exists(program):
        os.makedirs(program)
    with open(program + '/' + course + ' ' + file, 'wb') as f:
        for chunk in r.iter_content():
            f.write(chunk)

base_url = 'https://samuelmerritt.test.instructure.com/api/v1/'
auth_headers = {'Authorization': 'Bearer <TOKEN>'}
canvas_courses_file = 'syllabi courses.csv'

for line in open(canvas_courses_file):
    fields = line.split(',')
    course_id = fields[0]
    cn = fields[1].split('-') # 2013FS-OAK-GENERAL-NURSG-108-LEC1-1
    course_name = cn[3] + '-' + cn[4] + '-' + cn[5] + '-' + cn[6] + '-' + cn[1] + '-' + cn[0]
    program = fields[5] # ACADEMIC_NURS_U_BSN

    # files
    course_root_folder = get_root_folder(course_id)
    folders = get_subfolders(course_root_folder)
    for i in folders:
        files = get_files(i['id'])
        for j in files:
            if 'syl' in j['display_name'].lower():
                download_file('F', j['url'], program, course_name, j['display_name'])

    # syllabus
    syllabus = get_syllabus(course_id)
    if syllabus is not None:
        soup = BeautifulSoup(str(syllabus))
        for link in soup.find_all('a'):
            url = link.get('href')
            file_name = link.get('title')
            if 'download?verifier' in url and file_name not in ('Preview the document', 'View in a new window'):
                print(url)
                if 'courses' in url:
                    url = get_file_url(url.split('/')[6])
                    if url == '':
                        continue
                download_file('S', url, program, course_name, file_name)
