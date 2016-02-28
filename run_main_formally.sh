#!/bin/bash

rm -rf log/state log/single-output log/pair-output
mkdir -p log/state

if [ $# -lt 1 ]; then
    echo "assume to use 'python' to execute the script"
    exec='python'
else
    echo "use '$1' to execute the script"
    exec=$1
fi

$exec main.py \
    --sys-log-path log \
    --state-path log/state \
    --wiki-file /home/zxteloiv/data/kbc/enwiki-20160113/article_linked.txt.revised \
    --entity-wiki-file /home/zxteloiv/data/kbc/mid2wiki.txt \
    --single-entity-output-file log/fbcc-t-single-output \
    --entity-pair-output-file log/fbcc-t-pair-output \
    --task-id  fbcct_final \
    --log-level INFO \
    --wiki-redirect-file /home/zxteloiv/data/kbc/enwiki-20160113/redirect_title \

