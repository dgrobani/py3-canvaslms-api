import json

env = 'test' if input('Enter=PROD, or TEST? ').lower() == 'test' else 'prod'
print(env)

with open('..\\core\\config.json') as config_file:
    config = json.load(config_file)

# canvas
base_url = config['canvas'][env]
token = config['canvas']['token']
auth_header = {'Authorization': 'Bearer {}'.format(token)}
root_account = config['canvas']['root_account']
academic_account = config['canvas']['academic_account']


# CMI
cmi_host = config['cmi']['host']
cmi_user = config['cmi']['user']
cmi_pw = config['cmi']['pw']
cmi_db = config['cmi']['db']

# PowerCampus
powercampus_connection_string = config['powercampus']['connection_string']

# directories
sql_dir = config['directories']['sql_dir']
output_dir = config['directories']['output_dir']

# AWS
aws_access_key_id = config['aws']['aws_access_key_id']
aws_secret_access_key = config['aws']['aws_secret_access_key']
