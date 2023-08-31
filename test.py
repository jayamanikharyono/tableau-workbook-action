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

def get_addmodified_files_dev():
    g = Github(os.environ['REPO_TOKEN'])
    repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
    pr_number = int(os.environ['PR_NUMBER'])
    pull_request = repo.get_pull(pr_number)
    base_commit = pull_request.base.sha
    head_commit = pull_request.head.sha

    diff = repo.compare(base_commit, head_commit)
    added_files = []
    renamed_files = []
    modified_files = []
    deleted_files = []
    copied_files = []

    for file in diff.files:
        if file.status == "added":
            added_files.append(file)
        elif file.status == "renamed":
            renamed_files.append(file)
        elif file.status == "modified":
            modified_files.append(file)
        elif file.status == "deleted":
            deleted_files.append(file)
        elif file.status == "copied":
            copied_files.append(file)
        else:
            print(f"WARNING: {file.filename} does not have the relevant status. Checking the file is suggested.")

    print("Added files:")
    for filename in added_files:
        print(f"A {filename}")
    print("Renamed files:")
    for filename in renamed_files:
        print(f"R {filename}")
    print("Modified files:")
    for filename in modified_files:
        print(f"M {filename}")
    print("Deleted files:")
    for filename in deleted_files:
        print(f"D {filename}")
    print("Copied files:")
    for filename in copied_files:
        print(f"C {filename}")

def main():
    #print(get_full_schema_dev(os.environ['WORKBOOK_DIR']))
    print(get_addmodified_files_dev())
    print("Success!!")

if __name__ == "__main__":
    main()
