from canvas.core.accounts import program_account
from canvas.core.courses import get_courses_by_account_id, create_course, copy_course, get_course_people, \
    create_enrollment, delete_course, get_course, get_courses
from canvas.core.io import tada

term = '2017-2SU'
course_whitelist = ['N626', 'N671', 'N675L']

masters_account_id = '168920'  # DEV/FNPONL subaccount
copies_account_id = '170513'  # DEV/FNPONL/MASTER COPIES subaccount
master_copier_role_id = '3630'

# get FNP courses for the term [convert generator to list for multiple use in fnp_targets]
all_fnp_courses = list(get_courses([term], ['NFNP'], False))

# delete existing master copies
for copy in get_courses_by_account_id(copies_account_id, 'DEFAULT'):
    if not course_whitelist:
        # delete_course(copy['id'])
        print('deleted ' + copy['name'])
    else:
        for course_name in course_whitelist:
            if course_name == copy['name'].split(' ')[4]:
                # delete_course(copy['id'])
                print('deleted ' + copy['name'])
                break

for master in get_courses_by_account_id(masters_account_id, 'DEFAULT'):

    # get the master details
    master_name = master['name']
    if not master_name.startswith('N') or not master_name.endswith(' - MASTER'):
        continue

    course_number = master_name.split(' ')[0]
    if course_whitelist and course_number not in course_whitelist:
        continue

    print('master: ' + master_name)

    # create a master copy & import the master's content into it
#    copy_name = 'MASTER COPY FNP ONL ' + master['name']
#    copy_id = create_course(copies_account_id, copy_name, copy_name)['id']
#    copy_course(master['id'], copy_id)

    # get the courses in the FNP subaccount with the same course number
    fnp_targets = [f for f in all_fnp_courses if course_number + ' ' in f['course_code']]
    if not fnp_targets:
        print('\t>>> NO FNP COURSES')
        continue

    # enroll the teachers of each FNP course in the master copy with notification
    for fnp_target in fnp_targets:
        fnp_target_id = fnp_target['id']
        fnp_target_sis_id = fnp_target['sis_course_id']
        teachers = get_course_people(fnp_target_id, 'teacher')
        fors = get_course_people(fnp_target_id, 'Faculty of record')
        teachers.extend([f for f in fors if f['id'] not in [t['id'] for t in teachers]])
        if not teachers:
            print('>>> NO TEACHERS: ' + fnp_target_sis_id)
        for teacher in teachers:
            print('\tenrolling {} from {}'.format(teacher['name'], fnp_target_sis_id))
#            create_enrollment(copy_id, 'canvas', teacher['id'], master_copier_role_id, True)

tada()