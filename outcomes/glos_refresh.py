from canvas.core import *


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


def remove(key, verb):
    clo_id = canvas_other[key]
    prog, course_number, clo_title = key.split('|')  # ELMSN|N520|N520_04
    course_group_id = program_course_groups[course_number]
    # find archive ('OLD') group
    # look for archive group in lookup
    if course_number in course_archive_group_ids:
        archive_group_id = course_archive_group_ids[course_number]
    else:
        # look for archive group by traversing course subgroups
        course_subgroups = get_subgroups('accounts', account, course_group_id)
        for course_subgroup in course_subgroups:
            if course_subgroup['title'] == 'OLD':
                archive_group_id = course_subgroup['id']
                course_archive_group_ids[course_number] = archive_group_id
                break
        else:
            # archive group not found, so create it
            request_data = {'title': 'OLD', 'description': 'Old CLOs for ' + course_number}
            archive_group_id = create_group('accounts', account, course_group_id, request_data)
            course_archive_group_ids[course_number] = archive_group_id
    # link CLO into OLD subgroup
    link_outcome('accounts', account, archive_group_id, clo_id)
    # unlink CLO from original subgroup
    unlink_outcome('accounts', account, course_group_id, clo_id)
    # append replacement/retirement date to description
    update_outcome_description(clo_id, canvas_clos[key] + ' [' + verb + ' ' + time.strftime("%Y-%m-%d") + ']')


def quote(text):
    return '"' + text + '"'

#for program in ['ABSN', 'BSN', 'DNP', 'DPM', 'DPT', 'ELMSN', 'MOT', 'MPA', 'MSN_CM', 'MSN_CRNA', 'MSN_FNP']:
for program in ['BSN']:
    print(program)

    # query SMU CLOs
    db = pymysql.connect("OAKDB03", "dgrobani", "Welcome#13", "SMU")
    cur = db.cursor(pymysql.cursors.DictCursor)
    #query = ('SELECT CourseID AS course_id, CLO_ID AS clo_title, CLO AS clo_description ' +
    #'FROM Courses WHERE programID = "' + program + '" AND Active = 1 ORDER BY CourseID, CLO_ID')
    query = ('SELECT c.CourseID AS course_id, c.CLO_ID AS clo_title, c.CLO AS clo_description '
             'FROM Courses c '
             'WHERE c.programID = "' + program + '" AND c.Active = 1 '
             'UNION '
             'SELECT c.CourseID AS course_id, g.genomicsID AS clo_title, '
             'CONCAT(\'<p><a href="\', g.genomicsFile, \'" target="_blank">\', g.genomicsDescription, \'</a></p>\') '
             'AS clo_description '
             'FROM CLOGenomics g '
             'LEFT JOIN Courses c ON g.programID = c.programID AND g.cloID = c.CLO_ID '
             'WHERE c.programID = "' + program + '" AND c.Active = 1')
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    db.close()

    # load SMU CLOs
    cmi_clos = collections.OrderedDict()
    for row in rows:
        clo_key = program + '|' + row['course_id'].replace('-', '') + '|' + row['clo_title'].replace('-', '')
        cmi_clos[clo_key] = scrub(row['clo_description'])

    print('\nSMU:')
    print(json.dumps(cmi_clos, sort_keys=True, indent=4, separators=(',', ': ')))

    # load canvas CLOs
    # create lookups while traversing course subgroups:
    # lookup: program + course + clo title -> clo description
    canvas_clos = collections.OrderedDict()
    # lookup: program + course + clo title -> clo id [separate from canvas_clos to enable diffing on description]
    canvas_other = collections.OrderedDict()
    # lookup : course title -> subgroup id
    program_course_groups = collections.OrderedDict()
    print('\nCANVAS:')
    account = account_for_program(program)
    program_root_group_id = get_root_group('accounts', account)
    course_groups = get_subgroups('accounts', account, program_root_group_id)
    for course_group in course_groups:
        program_course_groups[course_group['title']] = course_group['id']
        course_clo_links = get_outcome_links('accounts', account, course_group['id'])
        for course_clo_link in course_clo_links:
            clo_id = course_clo_link['outcome']['id']
            clo = get_outcome(clo_id)
            clo_key = program + '|' + course_group['title'] + '|' + clo['title'].replace('CLO ', '')
            canvas_clos[clo_key] = scrub(clo['description'])
            canvas_other[clo_key] = clo['id']
            print(clo_key, ':', quote(canvas_clos[clo_key]))

    # compare SMU & canvas CLOs
    diffs = DictDiffer(cmi_clos, canvas_clos)

    print('\nADDED:')
    added = sorted(diffs.added())
    for clo_key in added:
        add(clo_key)
        print('   added:', clo_key, quote(cmi_clos[clo_key]))

    print('\nREMOVED:')
    course_archive_group_ids = collections.OrderedDict()
    removed = sorted(diffs.removed())
    for clo_key in removed:
        remove(clo_key, ' retired')
        print(' removed:', clo_key, quote(canvas_clos[clo_key]))

    print('\nCHANGED:')
    changed = sorted(diffs.changed())
    for clo_key in changed:
        remove(clo_key, 'replaced')
        print(' removed:', clo_key, quote(canvas_clos[clo_key]))
        add(clo_key)
        print('   added:', clo_key, quote(cmi_clos[clo_key]))
