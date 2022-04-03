# Tableau-Workbook-Action

You can use this action to easily validate and publish your tableau workbook to your tableau server. This action currently tested to publish workbook with .twb format.

Action Environment Variables:
- **USERNAME**: *Your tableau username*
- **PASSWORD**: *Your tableau password*
- **SITE_ID**: *Tableau site id*
- **TABLEAU_URL**: *Tableau url*

Action Arguments :
- **workbook_dir**: *Workbook dir in repo*
- **env**: *Target environment*
- **repo_token**: *Repo access token*


File Metadata (yaml file that hold workbook metadata):
- **name**: *Target workbook name on Tableau Server*
- **file_path**: *Path to workbook file in repo*
- **project_path**: *Target path on Tableau Server*

## Example
#### Usage Scenario

- Want to publish film workbook to tableau server
- workbook and metadata files placed in /tests/workbooks dir
- using one metadata files (can be multiple files)



#### Configuration


Metadata `tests/workbooks/workbooks.yml`
```
workbooks:
    - name: film_workbook
      file_path: film_workbook.twb
      project_path: Dashboard/Film
    - name: full_multi_view_workbook
      file_path: film_workbook.twb
      project_path: Dashboard/Film
    - name: multi_view_workbook
      file_path: film_workbook.twb
      project_path: Dashboard/Film
      option:
        tags:
          - sample
          - temp
        hidden_views:
          - Event by day
        show_tabs: true
        description: Sample description
```
Workflows `.github/workflows/staging-workflows.yml`
```yml
name: Tableau Workbook Workflows Staging
on:
  pull_request:
      branches:
        - master
jobs:
  tableau-validation-action:
    name: Tableau Workbook Staging Publisher
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: 'Tableau Workbook Action' 
        uses: jayamanikharyono/tableau-workbook-action@v1.4
        env:
          USERNAME: ${{ secrets.USERNAME }}
          PASSWORD: ${{ secrets.PASSWORD }}
          SITE_ID: ${{ secrets.SITE_ID }}
          TABLEAU_URL: ${{ secrets.TABLEAU_URL }}
        with:
          workbook_dir: tests/workbooks
          env: staging
          repo_token: ${{ secrets.GITHUB_TOKEN }}

```

#### Output

This scenario will output a new dashboard **film_workbook**, **full_multi_view_workbook**, and **multi_view_workbook** on project **staging/Dashboard/Film** in your Tableau server.


## TO DO
- Add Publishing option ✅
- Add Workbooks Description

## Contributing

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.
