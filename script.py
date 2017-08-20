"""script.py

This script takes a Google Sheet ID and it grabs all of its data and column headers. It then
syncs this data to a Firebase Database using the PIP package 'pyrebase'.

An example of how this works:

Say you have a spreadsheet URL that looks something like this

    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
                                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                           This part of the URL is the spreadsheet ID
                                           You will supply this to the script by changing
                                           the `SHEET_ID` variable.

The only other setting you have to set up manually is the spreadsheet range. Suppose the
spreadsheet looks something like this:

+=====+============+============+============+============+============+============+=====+
|     |     A      |     B      |     C      |     D      |     E      |     F      | ... |
+=====+============+============+============+============+============+============+=====+
|   1 | Field Name | Field Name | Field Name | Field Name | Field Name | Field Name |     |
+-----+------------+------------+------------+------------+------------+------------+-----+
|   2 | field_slug | field_slug | field_slug | field_slug | field_slug | field_slug |     |
+-----+------------+------------+------------+------------+------------+------------+-----+
|   3 | data       | data       | data       | data       | data       | data       |     |
+-----+------------+------------+------------+------------+------------+------------+-----+
|   4 | data       | data       | data       | data       | data       | data       |     |
+-----+------------+------------+------------+------------+------------+------------+-----+
|   5 | data       | data       | data       | data       | data       | data       |     |
+-----+------------+------------+------------+------------+------------+------------+-----+
| ... |            |            |            |            |            |            |     |
+-----+------------+------------+------------+------------+------------+------------+-----+
===========================================================================================
|                                                                                         |
| MyFirstSheet | MySecond Sheet | ...                                                     |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
NOTE that the SECOND row is all slugged (i.e. computer readable names), and the FIRST row
is the human readable version. It is IMPERATIVE that your range starts with the slug row,
so you would start the range at A2 in this case, and go to column F (or wherever the dataset
ends). Set the `DATA_RANGE` variable to a Google Sheets compatible range. For example,
considering the sheet above, my range would be "A2:F". You can find out more at this link:
https://productforums.google.com/forum/#!topic/docs/8w9TzS7JEQI

We also need the sheet names. These are located at the bottom of the spreadsheet. Put the
names in the `SHEET_NAMES` dict in the following syntax:

    {sheet_name: slug_name}

For example: if there is a sheet called "Patrick's To-dos", my dict entry might look like:

    {
        ...,
        "Patrick's To-dos": 'patricks_todos',
        ...
    }

Populate this with as many entries as there are sheets, or else some sheets won't be pushed.

"""

import httplib2
import os
import pyrebase
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage


# SHEETS CONFIG VARIABLES
# These MUST be set correctly for the API to work as intended
# (All of these are documented above)
SHEET_ID = ''
DATA_RANGE = ''
SPORT_SHEET_NAMES = {
    "": ''
}


# FIREBASE CONFIG

config = {
    'apiKey': '',
    'authDomain': '<YOUR_PROJECT_ID_HERE>.firebaseapp.com',
    'databaseURL': 'https://<YOUR_PROJECT_ID_HERE>.firebaseio.com/',
    'storageBucket': '<YOUR_PROJECT_ID_HERE>.appspot.com',
    'serviceAccount': os.path.dirname(os.path.realpath(__file__)) + '/service_auth.json'
}

firebase = pyrebase.initialize_app(config)

# GOOGLE SHEETS API CODE

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Your App Name Here'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Pushes the sheet data to Firebase

    This function loops through the list of sheets, and for each one, pulls it down
    and associates it with a slug, like "Patrick's To-dos" => 'patricks_todos'.

    Then, it pushes to Firebase; to a child object with the same name as the slug.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    for sheet,slug in SPORT_SHEET_NAMES.items():
        range_name = sheet + '!'  + DATA_RANGE
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=range_name).execute()
        values = result.get('values', [])

        # This list hold the column names (from the table header row)
        columns = values[0]
        print(columns)

        if not values:
            print('No data found.')
        else:
            db = firebase.database()
            for row in values[1:]:
                # Push each row to the Firebase DB
                staging_dict = {k: v for k, v in zip(columns, row)}
                db.child(slug).push(staging_dict)


if __name__ == '__main__':
    main()
