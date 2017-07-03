import canvas.core.api as api


def get_outcome(outcome_id):
    """ return an outcome """
    return api.get('outcomes/{}'.format(outcome_id)).json()


def get_outcomes(context, context_id, group_id):
    """ return a list of outcomes
        calls get_outcome() for full outcome, as get_outcome_links() returns outcome links with abbreviated outcomes """
    links = get_outcome_links(context, context_id, group_id)
    return [get_outcome(link['outcome']['id']) for link in links] if links else []


def get_all_outcome_links(context, context_id):
    """ return a list of all outcome links for an entire context
        BETA: https://canvas.instructure.com/doc/api/outcome_groups.html#method.outcome_groups_api.link_index """
    return api.get_list('{}/{}/outcome_group_links'.format(context, context_id))


def get_outcome_links(context, context_id, group_id):
    """ return a list of outcome links for a group """
    return api.get_list('{}/{}/outcome_groups/{}/outcomes'.format(context, context_id, group_id))


def link_new_outcome(context, context_id, group_id, title, description):
    """ create a new outcome, link it, and return the outcome id """
    req_data = {
        'title': 'CLO ' + title,
        'description': description,
        'mastery_points': 1,
        'ratings[][description]': 'Aligned',
        'ratings[][points]': 1
    }
    return str(api.post('{}/{}/outcome_groups/{}/outcomes'.format(context, context_id, group_id), req_data)
               .json()['outcome']['id'])


def link_outcome(context, context_id, group_id, outcome_id):
    """ link an existing outcome into a group and return the outcome link """
    return api.put('{}/{}/outcome_groups/{}/outcomes/{}'.format(context, context_id, group_id, outcome_id), '').json()


def outcome_came_from_cmi(outcome_title, course_number):
    return course_number + '_' in outcome_title


def update_outcome_title(outcome_id, title):
    """ update an outcome's title and return the request result """
    req_data = {'title': title}
    result = api.put('outcomes/{}'.format(outcome_id), req_data).json()
    return 'errors' not in result and 'message' not in result


def update_outcome_desc(outcome_id, description):
    """ update an outcome's description and return the request result """
    req_data = {'description': description}
    result = api.put('outcomes/{}'.format(outcome_id), req_data).json()
    return 'errors' not in result and 'message' not in result


def unlink_outcome(context, context_id, group_id, outcome_id):
    """ unlink an outcome from a group and return true if successful, false if not """
    result = api.delete('{}/{}/outcome_groups/{}/outcomes/{}'.format(context, context_id, group_id, outcome_id)).json()
    return 'errors' not in result and 'message' not in result
