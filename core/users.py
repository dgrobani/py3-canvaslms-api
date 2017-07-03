from canvas.core import api as api


def get_page_views(user, start_date, end_date):
    return api.get_list('users/{}/page_views?start_time="{}"&end_time="{}"'.format(user, start_date, end_date))


def get_user(user_id):
    return api.get('users/{}'.format(user_id)).json()


def get_user_by_sis_id(sis_user_id):
    return api.get('users/sis_user_id:{}'.format(sis_user_id)).json()
