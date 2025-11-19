import requests
import os
from requests.auth import HTTPBasicAuth

from datetime import date


def filter_work_items(project, area_path, org):
    x = f"""
        SELECT [System.Id], [System.Title], [System.State]
        FROM WorkItems
        WHERE
            [System.TeamProject] = '{project}'
            AND [System.AreaPath] = '{area_path}'
            AND [System.State] = 'Ready to Release'
        ORDER BY [System.ChangedDate] DESC
        """
    print(x)
    query = {
        "query": f"""
        SELECT [System.Id], [System.Title], [System.State]
        FROM WorkItems
        WHERE
            [System.TeamProject] = '{project}'
            AND [System.AreaPath] = '{area_path}'
            AND [System.State] = 'Ready to Release'
        ORDER BY [System.ChangedDate] DESC
        """
    }
    url = f"https://dev.azure.com/{org}/_apis/wit/wiql?api-version=6.0"

    print(url)
    response = requests.post(
        url,
        json=query,
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth("", pat)
    )

    if response.status_code == 200:
        work_items = response.json()["workItems"]
        ids = []
        for item in work_items:
            ids.append("#" + str(item['id']))
        return ids
    else:
        print(f" Failed to query: {response.status_code}")
        print(response.text)
    return


def create_release_ticket(project, release_date, area_path):
    # work_item_type = "User Story"  # Make sure this exists in your process (Agile template)
    url = ("https://dev.azure.com/OGCIO-Digital-Services/Digital Services "
           "Programme/_apis/wit/workitems/$User%20Story?api-version=7.1-preview.3")
    title = f"{project} Release: {release_date}"
    description = "Release ticket"

    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.Description", "value": description},
        {"op": "add", "path": "/fields/System.AreaPath", "value": area_path},
        {"op": "add", "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria", "value": "."}
    ]

    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json-patch+json"},
        auth=HTTPBasicAuth("", pat)
    )

    if response.status_code == 200 or response.status_code == 201:
        work_item = response.json()
        work_item_id = work_item['id']
        print(f"User Story created: {work_item_id} - {work_item['fields']['System.Title']}")
        print(f"{work_item['url']}")
        return work_item_id
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)
        return None


today = date.today()

day = today.day

organization = "OGCIO-Digital-Services"
project = "Digital Services Programme"
wiki_identifier = "Digital-Services-Programme.wiki"
code_base = os.environ.get("CODE_BASE")
pat = os.environ.get("PAT")
# code_base = "Ireland.ie"
# code_base = "MABS"
# code_base = "Citizens Info"

if code_base == 'Ireland.ie':
    day += 1
formatted = f"{today.year}-{str(today.month).zfill(2)}-{str(day).zfill(2)}"

page_path = f"/Release Notes/CMS/Hydrogen/{code_base}/{formatted}"

url = (f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_identifier}/pages?path={page_path}&api"
       f"-version=7.1-preview.1")

area_path = f"Digital Services Programme\\CMS Building Block\\WagTail Tech\\{code_base}"
work_items = filter_work_items(project, area_path, organization)

ticket_id = create_release_ticket(code_base, formatted, area_path)

release_item_url = f"https://dev.azure.com/{organization}/{project}/_workitems/edit/{ticket_id}"

headers = {
    "Content-Type": "application/json"
}
print(work_items)
data = {
    "content": "## Release ticket: " +
               "#" + str(ticket_id)
               + "\n  ## Tickets to Release\n" + "\n".join(work_items)
               + "\n ## Test Results"
               + "\n ## Accessibility"
               + "\n ## Performance"
               + "\n ## Mobile Rendering - Portrait"
               + "\n ## Mobile Rendering - Landscape"
               + "\n ## Cross Browser; Edge / Safari"
               + "\n ## JS Errors"
}

response = requests.put(url, json=data, headers=headers, auth=HTTPBasicAuth('', pat))
