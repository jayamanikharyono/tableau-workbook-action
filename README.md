# Tableau-Workbook-Action

You can use this action to easily validate and publish your tableau workbook to your tableau server. This action currently tested to publish workbook with .twb format.

Action Env Var:
- **USERNAME**: ${{ secrets.USERNAME }} *Your tableau username*
- **PASSWORD**: ${{ secrets.PASSWORD }} *Your tableau password*
- **SITE_ID**: ${{ secrets.SITE_ID }} *Tableau site id*
- **TABLEAU_URL**: ${{ secrets.TABLEAU_URL }} *Tableau url*

Action Args :
- **workbook_dir**: tests/workbooks *Workbook dir in repo*
- **env**: staging *Target environment*
- **repo_token**: ${{ secrets.GITHUB_TOKEN }} *Repo access token*

File Metadata (yaml file that hold workbook metadata):
- **name**: *Target workbook name on Tableau Server*
- **file_path**: *Path to workbook file in repo*
- **project_path**: *Target path on Tableau Server*

## Example
##### Usage Scenario

> - Want to publish film workbook to tableau server
> - workbook and metadata files placed in /tests/workbooks dir
> - using one metadata files (can be multiple files)



##### Config


Metadata `tests/workbooks/workbooks.yml`
```
workbooks:
    - name: film_workbook
      file_path: film_workbook.twb
      project_path: Dashboard/Film
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
      - name: 'Tableau Workbook Action' #This workflows expected to be error since no secrets vars provided
        uses: ./
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

##### Output

> This scenario will output a new dashboard on staging/Dashboard/Film/film_workbook in your Tableau server.


## Contributing

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.
