#!/bin/bash

mkdir -p out/properties;

for (( i=0; i<=8; i++ )); do 
    echo "nohup python -m wikidata.get_properties -l shell/wikidata.filelists/wikidata.split.0${i}.filelist -o out/properties/properties.0${i} &> out/log.properties.0${i} &"
    nohup python -m wikidata.get_properties -l shell/wikidata.filelists/wikidata.split.0${i}.filelist -o out/properties/properties.0${i} &> out/log.properties.0${i} &
done;
