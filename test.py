import os
import sys
import yaml
import json
import logging
import argparse
from pathlib import Path
from github import Github

from tableau_api import TableauApi


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

full_schema_config = get_full_schema("tests/workbooks")
for i in full_schema_config['workbook'].keys():
    print(i)