#!/bin/bash

mkdir -p out/entity_idx;

for (( i=0; i<=8; i++ )); do 
    echo "nohup python -m wikidata.build_idx -l shell/wikidata.filelists/wikidata.split.0${i}.filelist -o out/entity_idx/wikidata.idx.0${i} &> out/log.idx.0${i} &"
    nohup python -m wikidata.build_idx -l shell/wikidata.filelists/wikidata.split.0${i}.filelist -o out/entity_idx/wikidata.idx.0${i} &> out/log.idx.0${i} &
done;
