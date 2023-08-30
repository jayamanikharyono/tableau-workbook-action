import os
import sys
import yaml
import json
import logging
import argparse
from pathlib import Path
#from github import Github
from tableau_api import TableauApi

# new library
import re




def get_full_schema_original(project_dir):
    print(project_dir)
    from mergedeep import merge, Strategy
    full_schema = None
    for schema_file in Path(project_dir).glob("**/*.yml"):
        schema = yaml.full_load(schema_file.open())
        full_schema = merge(full_schema, schema, strategy=Strategy.ADDITIVE) if full_schema is not None else schema

    new_schema = dict({'workbooks':dict()})
    for value in full_schema['workbooks']:
        new_schema['workbooks'][value['file_path']] = value

    return new_schema

def get_full_schema_dev(project_dir):
    from mergedeep import merge, Strategy
    schema = dict()
    for currentpath, folders, files in os.walk(project_dir):
        print(files)
        for file in files:
            if file.endswith(('.twb', '.twbx')):
                name = re.findall(r'^(.+?)(?:\.twb|\.twbx)', file)[0]
                project_path = re.findall(fr"{re.escape(project_dir)}\\(.+)", currentpath)[0]
                file_path = file
                full_path = os.path.join(project_path, file_path)
                schema[full_path] = dict({'name': name,
                                          'project_path': project_path,
                                          'file_path': file_path,
                                          'full_path': full_path
                                          })
    return schema

def get_addmodified_files(repo_token):
    g = Github(repo_token)
    repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
    event_payload = open(os.environ['GITHUB_EVENT_PATH']).read()
    json_payload =  json.loads(event_payload)
    pr = repo.get_pull(json_payload['number'])
    list_files = [file.filename for file in pr.get_files() if os.path.exists(file.filename)]
    return list_files

print(get_full_schema_dev(os.environ['workbook_dir']))
print("Success!!")

