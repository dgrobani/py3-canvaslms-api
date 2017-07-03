import canvas.core.api as api


def get_outcome_group(context, context_id, group_id):
    """ return an outcome group """
    return api.get('{}/{}/outcome_groups/{}'.format(context, context_id, group_id)).json()


def get_program_groups(account):
    """ return a dict of course numbers and the id of their program-level outcome folders """
    course_folders = {}
    program_root_group = get_root_group('accounts', account)
    for course_folder in get_subgroups('accounts', account, program_root_group):
        # # if "N129/129L" format, add both N129 & N129L
        # splits = course_folder['title'].split('/')
        # course_folders[splits[0]] = course_folder['id']
        # if len(splits) == 2:
        #     course_number_stem = re.match(r'^[a-zA-Z]+', splits[0]).group(0)
        #     course_folders[course_number_stem + splits[1]] = course_folder['id']
        course_folders[course_folder['title']] = course_folder['id']
    return course_folders


def get_root_group(context, context_id):
    """ return the id of a root group """
    return str(api.get('{}/{}/root_outcome_group'.format(context, context_id)).json()['id'])


def get_subgroups(context, context_id, group_id):
    """ return a list of a group's subgroups """
    return api.get_list('{}/{}/outcome_groups/{}/subgroups/'.format(context, context_id, group_id))


def create_group(context, context_id, parent_group_id, req_data):
    """ create a group and return the group id """
    return str(api.post('{}/{}/outcome_groups/{}/subgroups/'.format(context, context_id, parent_group_id),
                        req_data).json()['id'])


def link_group(context, context_id, parent_group_id, child_group_id):
    """ link a group into a group and return the linked group id """
    req_data = {'source_outcome_group_id': child_group_id}
    return str(api.post('{}/{}/outcome_groups/{}/import/'.format(context, context_id, parent_group_id),
                        req_data).json()['id'])


def relink_group(context, context_id, group_id, new_parent_group_id):
    """ relink a group into another group and return the group id """
    req_data = {'parent_outcome_group_id': str(new_parent_group_id)}
    return str(api.put('{}/{}/outcome_groups/{}/'.format(context, context_id, group_id), req_data).json()['id'])


def delete_group(context, context_id, group_id):
    """ delete a group and return the group """
    return api.delete('{}/{}/outcome_groups/{}/'.format(context, context_id, group_id)).json()
