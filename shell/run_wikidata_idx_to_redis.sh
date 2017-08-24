
for (( i=0; i<=8; i++ ));
do
    
    echo "python -m redis_utils.load_idx --db 2 -i /data/home/zxteloiv/data/wikidata/entity_idx/wikidata.idx.0${i} --prefix WIKIDATA_QID_ &> out/log.wikidata2redis.${i}"
    python -m redis_utils.load_idx --db 2 -i /data/home/zxteloiv/data/wikidata/entity_idx/wikidata.idx.0${i} --prefix WIKIDATA_QID_ &> out/log.wikidata2redis.${i}
done;
