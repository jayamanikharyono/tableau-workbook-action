#!/bin/sh

echo "workbook_dir: $1"
echo "env: $2"
echo "repo_token: $3"

python main.py --workbook_dir=$1 --env=$2 --repo_token=$3

exit 0
