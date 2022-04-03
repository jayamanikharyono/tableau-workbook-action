# -*- coding: utf-8 -*-
"""
@author: jayaharyonomanik
"""


from treelib import Tree
from operator import itemgetter


def find_all_child_by_parent_id(parent_id, list_project):
    temp_projects = list()
    for project in list_project:
        if '@parentProjectId' in project.keys():
            if project['@parentProjectId'] == parent_id:
                temp_projects.append(project)
    return temp_projects


def find_project_by_name(project_name, list_project):
    temp_projects = list()
    for project in list_project:
        if project['@name'] == project_name:
            temp_projects.append(project)
    return temp_projects


def find_project_by_id(project_id, list_projects):
    for project in list_projects:
        if project['@id'] == project_id:
            return project
    return None


def parse_projects_to_tree(all_projects):
    tree = Tree()
    tree.create_node("tableau", "tableau", data = 'tableau')

    list_root = []
    for project in all_projects:
        if '@parentProjectId' not in project.keys():
            tree.create_node(project['@id'], project['@id'], parent='tableau', data=project['@name'])
            list_root.append(all_projects.index(project))

    index_list = list(set(range(len(all_projects))).difference(list_root))
    all_projects = list(itemgetter(*index_list)(all_projects))

    while len(index_list) > 0:
        remove_index = list()
        for index, curr_project in enumerate(all_projects):
            parent_project_id = curr_project['@parentProjectId']
            child_project_id =  curr_project['@id']
            child_name =  curr_project['@name']
            if tree.get_node(parent_project_id) is not None:
                tree.create_node(child_project_id, child_project_id, parent=parent_project_id, data=child_name)
                remove_index.append(index)

        index_list = list(set(range(len(all_projects))).difference(remove_index))
        if len(index_list) > 0:
            all_projects = list(itemgetter(*index_list)(all_projects))
    return tree
