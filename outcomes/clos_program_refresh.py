import collections
import time

from canvas.core.accounts import program_account, all_programs
from canvas.core.io import get_cmi_clos_by_program, tada
from canvas.core.outcome_groups import create_group, get_root_group, get_subgroups
from canvas.core.outcomes import get_outcomes, link_new_outcome, link_outcome, unlink_outcome, update_outcome_desc, \
    update_outcome_title

from canvas.core.etc import DictDiffer, scrub, quote


def clos_program_refresh():
    def add(key):
        prog, course_number, clo_title = key.split('|')  # ELMSN|N520|N520_04
        # create course subgroup if it doesn't exist
        if course_number in program_course_groups:
            course_group_id = program_course_groups[course_number]
        else:
            request_data = {'title': course_number, 'description': 'CLOs for ' + course_number}
            course_group_id = create_group('accounts', account, program_root_group_id, request_data)
            program_course_groups[course_number] = course_group_id
            print('added course:', course_number)
        # create new CLO
        link_new_outcome('accounts', account, course_group_id, clo_title, cmi_clos[key])

    def delete(key, verb):
        outcome_id = canvas_clo_id[key]
        prog, course_number, clo_title = key.split('|')  # ELMSN|N520|N520_04
        course_group_id = program_course_groups[course_number]

        # # try deleting CLO; success means it was unaligned and doesn't need archiving
        # if unlink_outcome('accounts', account, course_group_id, outcome_id):
        #     return

        # find archive ('OLD') group
        # search for archive group in ones already encountereds
        if course_number in course_archive_group_ids:
            archive_group_id = course_archive_group_ids[course_number]
        else:
            # if archive group not already encountered, search by traversing course subgroups
            for course_subgroup in get_subgroups('accounts', account, course_group_id):
                if course_subgroup['title'] == 'OLD':
                    archive_group_id = course_subgroup['id']
                    course_archive_group_ids[course_number] = archive_group_id
                    break
            else:
                # if archive group still not found, create it
                request_data = {'title': 'OLD', 'description': 'Old CLOs for ' + course_number}
                archive_group_id = create_group('accounts', account, course_group_id, request_data)
                course_archive_group_ids[course_number] = archive_group_id

        # link CLO into OLD subgroup
        link_outcome('accounts', account, archive_group_id, outcome_id)

        # unlink CLO from original subgroup
        if not unlink_outcome('accounts', account, course_group_id, outcome_id):
            print('>>>> failed to unlink {} from {}'.format(clo_title, course_number))

        # append 'OLD' to title
        if not update_outcome_title(outcome_id, 'CLO {} OLD'.format(clo_title)):
            print('>>>> failed to append OLD to {} title'.format(clo_title))

        # append replacement / retirement date to description
        if not update_outcome_desc(outcome_id,
                                   '{} [{} {}]'.format(canvas_clo_desc[key], verb, time.strftime("%Y-%m-%d"))):
            print('>>>> failed to append date to {} description'.format(clo_title))

    programs = []
    for program in programs or all_programs(synergis=True):
        print('\n' + program)

        # load CMI CLOs
        cmi_clos = collections.OrderedDict()
        for clo in get_cmi_clos_by_program(program):
            clo_key = '{}|{}|{}'.format(program, clo['course_id'].replace('-', ''), clo['clo_title'].replace('-', ''))
            cmi_clos[clo_key] = scrub(clo['clo_description'])
        # print('\nCMI:', json.dumps(cmi_clos, sort_keys=True, indent=4, separators=(',', ': ')))

        # load canvas CLOs
        # create lookups while traversing course subgroups:
        program_course_groups = collections.OrderedDict()  # key = course title; value = subgroup id
        # next two are separate to enable diffing on description
        canvas_clo_desc = collections.OrderedDict()  # key = program + course + clo title; value = clo description
        canvas_clo_id = collections.OrderedDict()  # key = program + course + clo title; value = clo id
        # print('\nCANVAS:')
        account = program_account(program)
        program_root_group_id = get_root_group('accounts', account)
        for course_group in get_subgroups('accounts', account, program_root_group_id):
            print(course_group['title'])
            program_course_groups[course_group['title']] = course_group['id']
            for clo in get_outcomes('accounts', account, course_group['id']):
                clo_key = '{}|{}|{}'.format(program, course_group['title'], clo['title'].replace('CLO ', ''))
                canvas_clo_desc[clo_key] = scrub(clo['description'])
                canvas_clo_id[clo_key] = clo['id']
                # print(clo_key, ':', quote(canvas_clo_desc[clo_key]))

        # compare CMI & canvas CLOs
        diffs = DictDiffer(cmi_clos, canvas_clo_desc)
        course_archive_group_ids = collections.OrderedDict()

        added = diffs.added()
        if added:
            print('\nADDED:')
            for clo_key in sorted(added):
#                add(clo_key)
                print('   added:', clo_key, quote(cmi_clos[clo_key]))

        deleted = diffs.deleted()
        if deleted:
            print('\nDELETED:')
            # TODO: investigate how course_archive_group_ids[] works when removing is part of changing
            for clo_key in sorted(deleted):
#                delete(clo_key, 'retired')
                print(' deleted:', clo_key, quote(canvas_clo_desc[clo_key]))

        changed = diffs.changed()
        if changed:
            print('\nCHANGED:')
            for clo_key in sorted(changed):
#                delete(clo_key, 'replaced')
                print(' changed:', clo_key, quote(canvas_clo_desc[clo_key]))
#                add(clo_key)
                print('      to:', clo_key, quote(cmi_clos[clo_key]))


if __name__ == '__main__':
    clos_program_refresh()
    tada()
