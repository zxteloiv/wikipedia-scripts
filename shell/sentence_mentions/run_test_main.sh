#!/bin/bash

rm -rf log/state/$2 log/single-output log/pair-output
mkdir -p log/state

python $3 main.py \
    --sys-log-path log \
    --state-path log/state \
    --redis-server "172.18.28.118" \
    --wiki-file $1 \
    --entity-wiki-file /home/zxteloiv/data/kbc/mid2wiki.txt \
    --single-entity-output-file log/single-output \
    --entity-pair-output-file log/pair-output \
    --task-id $2 \
    --log-level INFO \
    --wiki-redirect-file /home/zxteloiv/data/kbc/enwiki-20160113/redirect_title \

