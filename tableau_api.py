# -*- coding: utf-8 -*-
"""
@author: jayaharyonomanik
"""


import logging
import requests
import xmltodict
import tableauserverclient as TSC
import xml.dom.minidom as minidom
from collections import defaultdict

import util

API_VERSION = '3.9'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s')


class TableauApi:
    def __init__(self, username, password, tableau_api_url, tableau_url, site_id):
        self.username = username
        self.password = password
        self.tableau_api_url = tableau_api_url
        self.tableau_url = tableau_url
        self.site_id = site_id


    def sign_in(self):
        payload = \
        f"""<tsRequest>
          <credentials name="{ self.username }" password="{ self.password }" >
            <site contentUrl="" />
          </credentials>
        </tsRequest>"""
        response = requests.post(f'{self.tableau_api_url}{API_VERSION}/auth/signin', data=payload)
        doc = minidom.parseString(response.text)
        return doc.getElementsByTagName('credentials')[0].getAttribute("token")


    def get_all_projects(self):
        token = self.sign_in()
        headers = {
            'X-Tableau-Auth': token
        }
        response = requests.get(f'{self.tableau_api_url}{API_VERSION}/sites/{self.site_id}/projects?pageSize=1000', headers=headers)
        all_projects_response = xmltodict.parse(response.text)
        try:
            all_projects_response = all_projects_response['tsResponse']
            all_projects = all_projects_response['projects']['project']
            return all_projects
        except Exception as e:
            logging.error("Error parsing project response")
            logging.error(e.message)
            return None


    def list_all_data_sources(self):
        tableau_auth = TSC.TableauAuth(self.username, self.password)
        server = TSC.Server(self.tableau_url)

        with server.auth.sign_in(tableau_auth):
            all_datasources, pagination_item = server.datasources.get()
            logging.info(f"There are { pagination_item.total_available } datasources on site: ")

            while len(all_datasources) < pagination_item.total_available:
                request_options = TSC.RequestOptions(pagenumber=pagination_item.page_number+1)
                datasources, pagination_item = server.datasources.get(request_options)
                all_datasources.extend(datasources)
            return all_datasources


    def list_all_workbooks(self):
        tableau_auth = TSC.TableauAuth(self.username, self.password)
        server = TSC.Server(self.tableau_url)

        with server.auth.sign_in(tableau_auth):
            all_workbooks, pagination_item = server.workbooks.get()
            logging.info(f"There are { pagination_item.total_available } workbooks on site: ")

            while len(all_workbooks) < pagination_item.total_available:
                request_options = TSC.RequestOptions(pagenumber=pagination_item.page_number+1)
                workbooks, pagination_item = server.workbooks.get(request_options)
                all_workbooks.extend(workbooks)
            return all_workbooks


    def get_workbook_detail(self, workbook_id):
        tableau_auth = TSC.TableauAuth(self.username, self.password)
        server = TSC.Server(self.tableau_url)

        with server.auth.sign_in(tableau_auth):
            workbook = server.workbooks.get_by_id(workbook_id)
            return workbook


    def delete_workbook(self, workbook_id):
        tableau_auth = TSC.TableauAuth(self.username, self.password)
        server = TSC.Server(self.tableau_url)

        with server.auth.sign_in(tableau_auth):
            response = server.workbooks.delete(workbook_id)
            return response


    def get_project_id_by_path_with_tree(self, project_path):
        project_name = project_path.split("/")[-1]

        all_projects = self.get_all_projects()
        project_tree =  util.parse_projects_to_tree(all_projects)
        project_candidate = util.find_project_by_name(project_name, all_projects)

        project_path_dict = defaultdict(lambda: None)
        for project in project_candidate:
            nodes = list(project_tree.rsearch(project['@id']))
            nodes.reverse()
            node_path = "/".join([project_tree.get_node(node).data for node in nodes[1:]])
            project_path_dict[node_path] = project['@id']

        return project_path_dict[project_path]


    def create_project_by_path(self, project_path):
        project_path_split = project_path.split("/")

        last_project_id = None
        max_index = 0
        while self.get_project_id_by_path_with_tree("/".join(project_path_split[:max_index+1])) is not None:
            last_project_id = self.get_project_id_by_path_with_tree("/".join(project_path_split[:max_index+1]))
            max_index = max_index + 1

        for i in range(max_index, len(project_path_split)):
            logging.info("Creating Project within path : { '/'.join(project_path_split[:i+1]) }")
            new_project = TSC.ProjectItem(project_path_split[i],
                                          description=None,
                                          content_permissions=TSC.ProjectItem.ContentPermissions.ManagedByOwner,
                                          parent_id=last_project_id)

            tableau_auth = TSC.TableauAuth(self.username, self.password)
            server = TSC.Server(self.tableau_url)
            with server.auth.sign_in(tableau_auth):
                new_project = server.projects.create(new_project)
                last_project_id = new_project.id
        return last_project_id


    # Still figuring out how to put description in workbook via this api
    def publish_workbook(self, name, project_id, file_path, hidden_views = None, show_tabs = False, tags = None, description = None):
        tableau_auth = TSC.TableauAuth(self.username, self.password)
        server = TSC.Server(self.tableau_url)
        server.auth.sign_in(tableau_auth)
        new_workbook = TSC.WorkbookItem(name = name, project_id = project_id, show_tabs=show_tabs)
        new_workbook = server.workbooks.publish(new_workbook, file_path, TSC.Server.PublishMode.Overwrite, hidden_views=hidden_views)

        if tags is not None:
            new_workbook.tags = set(tags)
            new_workbook = server.workbooks.update(new_workbook)

        return new_workbook
