import os
from dotenv import load_dotenv
import pytz
from datetime import datetime
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from colorama import Fore
from azure.devops.v7_0.work_item_tracking.models import Wiql
from tabulate import SEPARATING_LINE, tabulate

# Fill in with your personal access token and org URL
load_dotenv()
personal_access_token = os.environ['PERSONAL_ACCESS_TOKEN']
organization_url = os.environ['ORGANIZATION_URL']

class DevOpsService:
    def __init__(self):
        credentials = BasicAuthentication('', personal_access_token)
        connection = Connection(base_url=organization_url, creds=credentials)
        self.core_client = connection.clients.get_work_item_tracking_client()

    def get_recent_activity_data(self):
        # Get the first page of projects
        recent_activity = self.core_client.get_recent_activity_data();
        query = """SELECT
            [System.Id],
            [System.WorkItemType],
            [System.Title],
            [System.AssignedTo],
            [System.State],
            [System.Tags],
            [System.ChangedDate]
        FROM workitems
        WHERE
            [System.WorkItemType] = 'Task'
            AND [System.State] <> ''
            AND [System.ChangedBy] = @me
            AND [System.ChangedDate] >= @today - 7
        """
        wiql = Wiql(query)
        recent_work_items = self.core_client.query_by_wiql(wiql);
        # Create a list of our work item ids
        ids = []
        for work_item in recent_work_items.work_items:
            ids.append(work_item.id)

        recent_activity = self.core_client.get_work_items(ids, fields=["System.Id", "System.Title", "System.State", "System.Tags", "System.WorkItemType", "System.AssignedTo", "System.ChangedDate", "System.ChangedBy"], expand='Links')

        table = []
        index = 0
        recent_activity = sorted(recent_activity, key=lambda k: k.fields['System.ChangedDate'], reverse=True)
        for work_item in recent_activity:
            # format date to string
            date = work_item.fields['System.ChangedDate']
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
            # convert to local timezone
            date = pytz.utc.localize(date).astimezone()
            date = date.strftime('%d/%m/%Y %H:%M:%S')
            state = work_item.fields['System.State']
            if state == 'Closed':
                circle_color = Fore.GREEN + '●'
            elif state == 'Active':
                circle_color = Fore.BLUE + '●'
            elif state == 'Needs review':
                circle_color = Fore.MAGENTA + '●'
            else:
                circle_color = Fore.YELLOW + '●'

            try:
                assigned_to = work_item.fields['System.AssignedTo']
            except:
                assigned_to = {'displayName': "Unassigned " + str(work_item.fields['System.Id']) }


            url = work_item._links.additional_properties['html']['href']
            title = work_item.fields['System.Title']

            table.append([circle_color + " " + state, date, title + "\n" + url, assigned_to['displayName']])
            table.append(SEPARATING_LINE)

        print(tabulate(table, headers=['State', 'Date', 'Title & Url', 'Assignee'], tablefmt='orgtbl'))