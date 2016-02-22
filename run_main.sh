#!/bin/bash

rm -rf log/*
mkdir -p log/state

python main.py \
    --sys-log-path log \
    --state-path log/state \
    --wiki-file $1 \
    --entity-wiki-file /data/home/zxteloiv/kbc/mid2wiki.txt \
    --entity-sentence-output-file $2 \
    --task-id $3 \

