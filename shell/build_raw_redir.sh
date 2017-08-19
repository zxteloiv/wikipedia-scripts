#!/bin/bash

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 filelist savepath"
    exit 1;
fi

savepath=$2
echo filelist=$1, savepath=$2

while read line;
do
    filesuffix=$(echo $line | awk -F "/" '{print $(NF-1)"_"$NF}')
    echo $line, $filesuffix
    python -m cirrus.extract_redirection_and_category -r $savepath/redir.$filesuffix -c disable $line;
done < $1

