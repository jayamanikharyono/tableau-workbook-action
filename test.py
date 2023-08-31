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



def get_full_schema_dev(project_dir):
    from mergedeep import merge, Strategy
    schema = dict()
    print(project_dir)
    for currentpath, folders, files in os.walk(project_dir):
        for file in files:
            if file.endswith(('.twb', '.twbx')):
                name = re.findall(r'^(.+?)(?:\.twb|\.twbx)', file)[0]
                project_path = re.findall(fr"{re.escape(project_dir)}/(.+)", currentpath)[0]
                file_path = file
                full_path = os.path.join(project_path, file_path)
                schema[full_path] = dict({'name': name,
                                          'project_path': project_path,
                                          'file_path': file_path,
                                          'full_path': full_path
                                          })
    return schema

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

def main():
    print(get_full_schema_dev(os.environ['WORKBOOK_DIR']))
    filepath = "tests/tableau_reports/folder2/folder3/added_file.twbx"
    filename = "added_file.twbx"
    #print(get_changed_files_dev())
    print("Success!!")

if __name__ == "__main__":
    main()
