import os

voyages_auth_token=os.environ['voyages_auth_token']
base_url=os.environ['base_url']

headers={'Authorization': 'Token %s' %voyages_auth_token}