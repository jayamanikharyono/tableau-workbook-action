import os
import sys
import yaml
import json
import logging
import argparse
from pathlib import Path
from github import Github
from tableau_api import TableauApi

# new library
import git
import re




def get_changed_files_dev():
    g = Github(os.environ['REPO_TOKEN'])
    repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
    pr_number = int(os.environ['PR_NUMBER'])
    pull_request = repo.get_pull(pr_number)
    base_commit = pull_request.base.sha
    head_commit = pull_request.head.sha
    diff = repo.compare(base_commit, head_commit)
    status_files = {
        "added": [],
        "renamed": [],
        "modified": [],
        "removed": []
    }
    for file in diff.files:
        if file.status == "added":
            status_files["added"].append(file)
        elif file.status == "renamed":
            status_files["renamed"].append(file)
        elif file.status == "modified":
            status_files["modified"].append(file)
        elif file.status == "removed":
            status_files["removed"].append(file)
        else:
            print(f"WARNING: {file.filename} does not have a relevant status. Checking the file is suggested.")
    # debug
    # print("Files by Status:")
    # for status, files in status_files.items():
    #     print(f"{status.capitalize()} files:")
    #     for file in files:
    #         print(f"{status[0].capitalize()} {file}")
    return status_files


def submit_workbook_dev(file_name, file_path, env):
    if env != 'production':
        project_path = 'fugo_test/' + os.environ['WORKBOOK_DIR']

    tableau_api = TableauApi(os.environ['USERNAME'],
                            os.environ['PASSWORD'],
                            os.environ['TABLEAU_URL'] + '/api/',
                            os.environ['TABLEAU_URL'],
                            os.environ['SITE_ID'])
    # project_id = tableau_api.get_project_id_by_path_with_tree(project_path)

    # if project_id is None:
    #     logging.info("Existing project on a given path doesn't exist, creating new project")
    #     project_id = tableau_api.create_project_by_path(project_path)



    # new_workbook = tableau_api.publish_workbook(name =  file_name,
    #                                             project_id = project_id,
    #                                             file_path = file_path)

    # return project_path, new_workbook

def main():
    
    filepath = "tests/tableau_reports/folder2/folder3/added_file.twbx"
    filename = "added_file"
    env = 'test'
    #print(get_changed_files_dev())
    submit_workbook_dev(filename, filepath, env)
    print("Success!!")

if __name__ == "__main__":
    main()
