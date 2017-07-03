import time
import winsound

from requests import delete as api_delete, exceptions as api_exceptions, get as api_get, post as api_post, \
    put as api_put

from canvas.core import config


def get(url):
    while True:
        try:
            return api_get(normalize_url(url), headers=config.auth_header, timeout=10, stream=False)
        except api_exceptions.RequestException as e:
            time_out(url, 'GET', e)


def get_list(url):
    """ compile a paginated list up to 100 at a time (instead of default 10) and return the entire list """
    paginated = []
    r = get('{}{}per_page=100'.format(url, '&' if '?' in url else '?'))
    while 'next' in r.links:
        paginated.extend(r.json())
        r = get(r.links['next']['url'])
    paginated.extend(r.json())
    return paginated


def get_file(url):
    while True:
        try:
            return api_get(url, headers=config.auth_header, timeout=10, stream=True)
        except api_exceptions.RequestException as e:
            time_out(url, 'GET', e)


def post(url, r_data):
    while True:
        try:
            return api_post(normalize_url(url), headers=config.auth_header, timeout=5, stream=False, data=r_data)
        except api_exceptions.RequestException as e:
            time_out(url, 'POST', e)


def put(url, r_data):
    while True:
        try:
            return api_put(normalize_url(url), headers=config.auth_header, timeout=5, stream=False, data=r_data)
        except api_exceptions.RequestException as e:
            time_out(url, 'PUT', e)


def delete(url, r_data=''):
    while True:
        try:
            return api_delete(normalize_url(url), headers=config.auth_header, timeout=5, stream=False, data=r_data)
        except api_exceptions.RequestException as e:
            time_out(url, 'DELETE', e)


def normalize_url(url):
    # paginated 'next' urls already start with base_url
    return url if url.startswith(config.base_url) else config.base_url + url


def time_out(url, action, e):
    winsound.Beep(1200, 300)
    print('*' * 40, ' ERROR - RETRYING IN 10 SECONDS ', '*' * 40)
    print('\n***EXCEPTION:', e, '\n***ACTION:', action, '\n***URL:', url, '\n')
    time.sleep(10)
