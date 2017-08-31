#!/bin/bash

rm -rf log/state/$2 log/entity-output
mkdir -p log/state

python $3 main_sentence_entity.py \
    --sys-log-path log \
    --state-path log/state \
    --entity-wiki-file /home/zxteloiv/data/wiki_resources/mid2wiki.txt \
    --wiki-redirect-file /home/zxteloiv/data/wiki_resources/redirect_title \
    --redis-server "172.18.28.118" \
    --wiki-file $1 \
    --task-id $2 \
    --log-level INFO \
    --entity-output-file log/entity-output \

