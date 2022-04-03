#!/bin/sh

echo "Workbook Directory : $1"
echo "Environment : $2"
echo "Repo Token : $3"

cp -r /action/* /github/workspace/

python main.py --workbook_dir=$1 --env=$2 --repo_token=$3

exit 0
