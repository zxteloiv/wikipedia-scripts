#!/bin/bash

rm -rf log/state
rm -f $2
mkdir -p log/state

python $4 main.py \
    --sys-log-path log \
    --state-path log/state \
    --wiki-file $1 \
    --entity-wiki-file /data/home/zxteloiv/kbc/mid2wiki.txt \
    --entity-sentence-output-file $2 \
    --task-id $3 \
    --log-level DEBUG \

