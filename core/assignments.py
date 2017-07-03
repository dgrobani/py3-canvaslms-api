from canvas.core import api as api


def assignment_is_graded(assignment):
    return 'not_graded' not in assignment['submission_types'] and assignment['points_possible'] \
            and not ('omit_from_final_grade' in assignment and assignment['omit_from_final_grade'])


def get_assignment(course_id, assignment_id):
    """ return one course assignment """
    return api.get('courses/{}/assignments/{}'.format(course_id, assignment_id)).json()


def get_assignments(course_id):
    """ return a list of a course's assignments """
    return sorted(api.get_list('courses/{}/assignments'.format(course_id)), key=lambda a: a['position'])


def get_assignment_grade_summaries(course_id):
    """ return a list of a course's assignments with a grade summary for each
        https://canvas.instructure.com/doc/api/analytics.html#method.analytics_api.course_assignments """
    assignments = api.get_list('courses/{}/analytics/assignments'.format(course_id))
    return [] if 'errors' in assignments else assignments


def get_assignment_groups(course_id):
    """ return a list of a course's assignment groups with their assignments """
    return sorted(api.get_list('courses/{}/assignment_groups?include[]=assignments'.format(course_id)),
                  key=lambda g: g['position'])


def get_assignment_student_grades(course_id, student_id):
    """ return a list of a student's assignments with grades
        https://canvas.instructure.com/doc/api/analytics.html#method.analytics_api.student_in_course_assignments """
    return api.get_list('courses/{}/analytics/users/{}/assignments'.format(course_id, student_id))


def get_assignment_submissions(course_id, assignment_id):
    """ return a list of submissions for an assignment """
    return api.get_list('courses/{}/assignments/{}/submissions'.format(course_id, assignment_id))


def get_discussions(course_id):
    """ return a list of a course's discussion topics """
    return api.get_list('courses/{}/discussion_topics'.format(course_id))


def get_quizzes(course_id):
    """ return a list of a course's quizzes """
    return api.get_list('courses/{}/quizzes'.format(course_id))
