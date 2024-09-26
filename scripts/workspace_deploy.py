import os
import sys
from pathlib import Path
import urllib.parse

import requests
import yaml


def main():

    config_path = sys.argv[2]
    separator = sys.argv[3]
    tenant_id = sys.argv[4]

    with open(config_path, 'r') as yml_file:
        cfg = yaml.safe_load(yml_file)

    data = {
        'client_id': os.environ['CLIENT_ID'],
        'grant_type': 'client_credentials',
        'resource': 'https://analysis.windows.net/powerbi/api',
        'response_mode': 'query',
        'client_secret': os.environ['CLIENT_SECRET']
    }

    resp = requests.get('https://login.microsoftonline.com/{}/oauth2/token'.format(tenant_id), data=data)
    access_token = resp.json()['access_token']
    token = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    file_list = sys.argv[1].split(separator)

    for file in file_list:
        if file.endswith('.pbix') and os.path.exists(file):
            path = Path(file)
            workspace = os.path.basename(path.parent.absolute())
            file_name = os.path.basename(file)
            display_name = file_name.replace('_', ' ')
            workspace_id = cfg[workspace]['workspace_id']
            if workspace_id is None:
                print(f"Workspace {workspace} not found in config file")
                raise Exception(f"Workspace {workspace} not found in config file")

            print('Deploying {} to {}'.format(file_name, workspace))
            file_import = {'file': open(file, 'rb')}
            response = requests.request("POST",
                                        (
                                            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?"
                                            f"datasetDisplayName={urllib.parse.quote(display_name)}"
                                            f"&nameConflict=CreateOrOverwrite"
                                        ), files=file_import, headers=token)

            print(response.status_code)
            print("---")
            print(response.json())
            print("---")
            #Request headers
            print(response.request.headers)
            print("---")
            #Response headers
            print(response.headers)
            print("---")

            if response.status_code not in [200, 201, 202, 204]:
                raise Exception("ERROR: " + response.status_code + ":response.content\nURL: " + response.url)
        else:
            print(f"File {file} not found or not a pbix file")


if __name__ == '__main__':
    main()
