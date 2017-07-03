from canvas.core.courses import get_courses, get_course_people

terms = ['2017-1SP']
programs = ['NFNPO']
synergis = True
print('course number, course sis id, student, teachers')
for course in get_courses(terms, programs, synergis):
    if course['course_sis_info']['number'] in ['N678L', 'N679L', 'N680L']:
        teachers = ', '.join([teacher['name'] for teacher in get_course_people(course['id'], 'teacher')])
        for student in sorted(get_course_people(course['id'], 'student'), key=lambda s: s['name']):
            print('{}, {}, {}, {}'.format(course['course_sis_info']['number'], course['sis_course_id'],
                                          student['name'], teachers))
