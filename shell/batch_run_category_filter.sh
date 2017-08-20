#!/bin/bash

domain=$1

nohup python -m cirrus.filter_category -r /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/redir_meta.merged.tsv -c /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/cate_hierarchy.merged.tsv -o out/domain.00.json -d $domain -f shell/cirrus-content.filelist.split.00 &> out/log.00 &
nohup python -m cirrus.filter_category -r /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/redir_meta.merged.tsv -c /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/cate_hierarchy.merged.tsv -o out/domain.01.json -d $domain -f shell/cirrus-content.filelist.split.01 &> out/log.01 &
nohup python -m cirrus.filter_category -r /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/redir_meta.merged.tsv -c /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/cate_hierarchy.merged.tsv -o out/domain.02.json -d $domain -f shell/cirrus-content.filelist.split.02 &> out/log.02 &
nohup python -m cirrus.filter_category -r /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/redir_meta.merged.tsv -c /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/cate_hierarchy.merged.tsv -o out/domain.03.json -d $domain -f shell/cirrus-content.filelist.split.03 &> out/log.03 &
nohup python -m cirrus.filter_category -r /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/redir_meta.merged.tsv -c /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/cate_hierarchy.merged.tsv -o out/domain.04.json -d $domain -f shell/cirrus-content.filelist.split.04 &> out/log.04 &
nohup python -m cirrus.filter_category -r /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/redir_meta.merged.tsv -c /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/cate_hierarchy.merged.tsv -o out/domain.05.json -d $domain -f shell/cirrus-content.filelist.split.05 &> out/log.05 &
nohup python -m cirrus.filter_category -r /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/redir_meta.merged.tsv -c /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/cate_hierarchy.merged.tsv -o out/domain.06.json -d $domain -f shell/cirrus-content.filelist.split.06 &> out/log.06 &
nohup python -m cirrus.filter_category -r /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/redir_meta.merged.tsv -c /home/zxteloiv/datasets/wikipedia-zhwiki/extracted/cate_hierarchy.merged.tsv -o out/domain.07.json -d $domain -f shell/cirrus-content.filelist.split.07 &> out/log.07 &
