#!/bin/bash

if [ $# -ne 2 ]; then
    echo "usage:";
    echo "$1 category_sheet_file output_prefix(for all splits)";
    exit 1;
fi

category_sheet_file=$1
output_prefix=$2

mkdir -p $output_prefix

nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.00 -l shell/wikidata.filelists/wikidata.split.00.filelist &> $output_prefix/log.00 &
nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.01 -l shell/wikidata.filelists/wikidata.split.01.filelist &> $output_prefix/log.01 &
nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.02 -l shell/wikidata.filelists/wikidata.split.02.filelist &> $output_prefix/log.02 &
nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.03 -l shell/wikidata.filelists/wikidata.split.03.filelist &> $output_prefix/log.03 &
nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.04 -l shell/wikidata.filelists/wikidata.split.04.filelist &> $output_prefix/log.04 &
nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.05 -l shell/wikidata.filelists/wikidata.split.05.filelist &> $output_prefix/log.05 &
nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.06 -l shell/wikidata.filelists/wikidata.split.06.filelist &> $output_prefix/log.06 &
nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.07 -l shell/wikidata.filelists/wikidata.split.07.filelist &> $output_prefix/log.07 &
nohup python -m wikidata.filter_by_subclass --only entity -s $category_sheet_file -o $output_prefix/entity.08 -l shell/wikidata.filelists/wikidata.split.08.filelist &> $output_prefix/log.08 &
