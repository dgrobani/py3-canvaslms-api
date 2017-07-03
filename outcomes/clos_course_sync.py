import collections

from canvas.core.accounts import program_account
from canvas.core.courses import get_courses
from canvas.core.io import tada
from canvas.core.outcome_groups import delete_group, get_program_groups, get_root_group, get_subgroups
from canvas.core.outcomes import get_outcomes, link_outcome, unlink_outcome

from canvas.core.etc import DictDiffer, scrub


def clos_course_sync():

    def print_pretty(arg1, arg2='', arg3=''):
        print('{:<40}{: <20} {} {}'.format(course_sis_id, arg1, arg2, arg3))

    def load_clos(context, context_id, root_group, clo_descs, clo_ids):
        for clo in get_outcomes(context, context_id, root_group):
            if 'Genomics' not in clo['title']:
                load_key = clo['title'] + '|' + scrub(clo['description'])
                clo_descs[load_key] = scrub(clo['description'])
                clo_ids[load_key] = clo['id']

    def add(label):
        print_pretty(label, *key.split('|'))
        link_outcome('courses', course_id, course_root_group, program_clo_ids[key])

    def delete(verb):
        print_pretty(verb, *key.split('|'))
        results = unlink_outcome('courses', course_id, course_root_group, course_clo_ids[key])
        if not results:
            print_pretty('>>> FAILED--ALIGNED')

# ---- HERE WE GO! ---- #

    course_whitelist = []
    terms = ['2017-2SU']
    programs = []
    synergis = False

    previous_program = ''
    for course in get_courses(terms, programs, synergis, course_whitelist):

        course_id = course['id']
        course_sis_id = course['sis_course_id']
        course_sis_info = course['course_sis_info']
        course_number = course_sis_info['number']
        program = course_sis_info['program']

        # load program's outcome groups ("folders")
        if program != previous_program:
            course_folders = get_program_groups(program_account(program))
            previous_program = program

        # delete legacy folders
        course_root_group = get_root_group('courses', course_id)
        subgroups = get_subgroups('courses', course_id, course_root_group)
        if subgroups:
            for course_group in subgroups:
                delete_group('courses', course_id, course_group['id'])
                print_pretty('deleted folder', course_group['title'])
            for course_group in get_subgroups('courses', course_id, course_root_group):
                print_pretty(course_sis_id, '>>> STUCK FOLDER', course_group['title'])

        # skip if no program outcomes for course
        if course_number not in course_folders:
            print_pretty('>>> NO PROGRAM CLOS')
            continue

        # load course CLO titles & descriptions
        course_clo_descs = collections.OrderedDict()
        course_clo_ids = collections.OrderedDict()
        load_clos('courses', course_id, course_root_group, course_clo_descs, course_clo_ids)

        # load program CLO titles & descriptions
        program_clo_descs = collections.OrderedDict()
        program_clo_ids = collections.OrderedDict()
        load_clos('accounts', program_account(program), course_folders[course_number], program_clo_descs,
                  program_clo_ids)

        # synchronize course & program CLOs
        diffs = DictDiffer(program_clo_descs, course_clo_descs)
        for key in sorted(diffs.added()):
            add('added')
        for key in sorted(diffs.deleted()):
            delete('deleted')
        for key in sorted(diffs.changed()):
            delete('changed')
            add('to')

        # actions = {'added': diffs.added(), 'deleted': diffs.deleted(), 'changed': diffs.changed()}
        # for action in actions:
        #     for key in sorted(actions[action]):
        #         print_pretty(action, *key.split('|'))


if __name__ == '__main__':
    clos_course_sync()
    tada()
