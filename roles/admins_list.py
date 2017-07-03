from canvas.core import config

from canvas.core.accounts import get_subaccounts, get_admins
from canvas.core.io import tada


def admins_list(account_id, account_name):
    for admin in get_admins(account_id):
        print('{},{}{},{},{},{}'.format(account_id, account_name, ',' * (5 - account_name.count(',')),
              admin['role'], admin['user']['name'].replace(',', ''), admin['user']['login_id']))
    for subaccount in get_subaccounts(account_id):
        admins_list(subaccount['id'], account_name + ',' + subaccount['name'])


if __name__ == '__main__':
    admins_list(config.root_account, 'root')
    tada()
