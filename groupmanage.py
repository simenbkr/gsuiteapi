import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/admin.directory.group'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Python Group API Manager'

"""
Useful docs:
https://developers.google.com/admin-sdk/directory/v1/guides/manage-groups
https://developers.google.com/resources/api-libraries/documentation/admin/directory_v1/python/latest/
"""

flags = None


def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'admin-directory_v1-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def add_to_group(email, role, group):
    creds = get_credentials()

    http = creds.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http)

    body = {
        'email': email,
        'role': role
        }

    added = service.members().insert(groupKey=group, body=body).execute()

    return added


def remove_from_group(email, group):
    creds = get_credentials()

    http = creds.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http)

    removed = service.members().delete(groupKey=group, memberKey=email).execute()

    return removed


def in_group(email, group):
    """
    Did not get the Google API service.members().hasMember() endpoint to work properly, so I made
    this ghetto solution.
    """

    creds = get_credentials()

    http = creds.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http)

    in_ = service.members().list(groupKey=group).execute()

    for person in in_['members']:
        if person['email'] == email:
            return True

    return False


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--add', help='Add user to a group', required=False)
    parser.add_argument('-d', '--delete', help='Delete user from group', required=False)
    parser.add_argument('-i', '--in', help='Check if user is in a group', required=False)
    parser.add_argument('-g', '--group', help='Group', required=True)
    parser.add_argument('-r', '--role', help='Users role if it is to be added to a group.', required=False)
    args = vars(parser.parse_args())

    if args['add']:
        if args['role']:
            print add_to_group(args['add'], args['role'], args['group'])
        else:
            print add_to_group(args['add'], 'MEMBER', args['group'])
        print "Added {} to group {}".format(args['add'], args['group'])
    elif args['delete']:
        print remove_from_group(args['delete'], args['group'])
        print "{} has been deleted from the group {}".format(args['delete'], args['group'])
    elif args['in']:
        print in_group(args['in'], args['group'])
