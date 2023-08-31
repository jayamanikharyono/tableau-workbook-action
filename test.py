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

    repo = git.Repo(".")
    commits = repo.head.commit.parents
    previous_commit = commits[0] if commits else None

    if previous_commit:
        diff = previous_commit.diff(repo.head.commit)
        added_files = [file.a_path for file in diff.iter_change_type('A')]
        modified_files = [file.a_path for file in diff.iter_change_type('M')]
        deleted_files = [file.a_path for file in diff.iter_change_type('D')]

        print("Added files:", added_files)
        print("Modified files:", modified_files)
        print("Deleted files:", deleted_files)
    else:
        print("No previous commit available.")


def main():
    #print(get_full_schema_dev(os.environ['WORKBOOK_DIR']))
    print(get_addmodified_files_dev())
    print("Success!!")

if __name__ == "__main__":
    main()
