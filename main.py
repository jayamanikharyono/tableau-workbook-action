# -*- coding: utf-8 -*-
"""
@author: jayaharyonomanik
"""


import os
import yaml
import json
import logging
import argparse
from pathlib import Path
from github import Github

from tableau_api import TableauApi


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s')

class TableauWorkbookError(Exception):
    """Exception raised for errors in tableau workbook.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


def get_full_schema(project_dir):
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


def comment_pr(repo_token, message):
    g = Github(repo_token)
    repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
    event_payload = open(os.environ['GITHUB_EVENT_PATH']).read()
    json_payload =  json.loads(event_payload)
    pr = repo.get_pull(json_payload['number'])
    pr.create_issue_comment(message)
    return True


def get_addmodified_files(repo_token):
    g = Github(repo_token)
    repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
    event_payload = open(os.environ['GITHUB_EVENT_PATH']).read()
    json_payload =  json.loads(event_payload)
    pr = repo.get_pull(json_payload['number'])
    list_files = [file.filename for file in pr.get_files() if os.path.exists(file.filename)]
    return list_files


def submit_workbook(workbook_schema, file_path, env):
    if env != 'production':
        project_path = 'staging/' + workbook_schema['project_path']

    tableau_api = TableauApi(os.environ['USERNAME'],
                            os.environ['PASSWORD'],
                            os.environ['TABLEAU_URL'] + '/api/',
                            os.environ['TABLEAU_URL'],
                            os.environ['SITE_ID'])
    project_id = tableau_api.get_project_id_by_path_with_tree(project_path)

    if project_id is None:
        logging.info("Existing project on a given path doesn't exist, creating new project")
        project_id = tableau_api.create_project_by_path(project_path)

    hidden_views = None
    show_tabs = False
    tags = None
    description = None

    if 'option' in workbook_schema:
        hidden_views = workbook_schema['option']['hidden_views'] if 'hidden_views' in workbook_schema['option'] else None
        show_tabs = workbook_schema['option']['show_tabs'] if 'show_tabs' in workbook_schema['option'] else False
        tags = workbook_schema['option']['tags'] if 'tags' in workbook_schema['option'] else None
        description = workbook_schema['option']['description'] if 'description' in workbook_schema['option'] else None

    new_workbook = tableau_api.publish_workbook(name =  workbook_schema['name'],
                                                project_id = project_id,
                                                file_path = file_path,
                                                hidden_views = hidden_views,
                                                show_tabs = show_tabs,
                                                tags = tags,
                                                description = description)

    return project_path, new_workbook


def main(args):
    logging.info(f"Workbook Dir : { args.workbook_dir }")
    logging.info(f"Environments : { args.env }")

    full_schema_config = get_full_schema(args.workbook_dir)

    addmodified_files = get_addmodified_files(args.repo_token)
    addmodified_files = [file.lstrip(args.workbook_dir) for file in addmodified_files if args.workbook_dir in file and ".twb" in file]

    if len(addmodified_files) > 0:
        logging.info("Add & Modified Files:")
        logging.info(addmodified_files)

        status = True
        list_message = list()
        for file in addmodified_files:
            if file in full_schema_config['workbooks'].keys():
                workbook_schema = full_schema_config['workbooks'][file]
                try:
                    logging.info("Publishing workbook : { workbook_schema['project_path'] + '/' + workbook_schema['name'] } to Tableau")
                    project_path, new_workbook = submit_workbook(workbook_schema,
                                                                 args.workbook_dir + "/" + file,
                                                                 args.env)
                    logging.info(f"Workbook : { project_path } Published to Tableau")
                    list_message.append(f"Workbook : { project_path } published to Tableau  :heavy_check_mark:")
                except Exception as e:
                    logging.info(f"Error publishing workbook { workbook_schema['name'] }")
                    logging.error(e)
                    list_message.append(f"Workbook : { workbook_schema['name'] } not published to Tableau   :x:")
                    status = False
            else:
                logging.info(f"Skip publishing workbook { workbook_schema['name'] } not listed in config files")

        comment_pr(args.repo_token, "\n".join(list_message))
        if status is False:
            raise TableauWorkbookError("\n".join(list_message))
    else:
        logging.info("No file changes detected")
    return True


if __name__=='__main__':
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--workbook_dir', action='store', type=str, required=False)
    parser.add_argument('--env', action = 'store', type = str, required = True)
    parser.add_argument('--repo_token', action = 'store', type=str, required = True)

    args = parser.parse_args()
    main(args)
