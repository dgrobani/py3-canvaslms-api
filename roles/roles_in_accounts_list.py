from canvas.core import config

from canvas.core.accounts import get_subaccounts, get_roles
from canvas.core.io import tada


def roles_in_accounts_list(account_id, account_name):
    for role in get_roles(account_id):
        if role['label'] not in ('Account Admin', 'Student', 'Teacher', 'TA', 'Designer', 'Observer'):
            print('{},{}{},{}'.format(account_id, account_name, ',' * (5 - account_name.count(',')), role['label']))
    for subaccount in get_subaccounts(account_id):
        roles_in_accounts_list(subaccount['id'], account_name + ',' + subaccount['name'])


if __name__ == '__main__':
    roles_in_accounts_list(config.root_account, 'root')
    tada()
