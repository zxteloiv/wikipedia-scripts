
for (( i=0; i<=8; i++ ));
do
    
    echo "python -m utils.redis_importer --db 2 -i /data/home/zxteloiv/data/wikidata/entity_idx/wikidata.idx.0${i} --prefix WIKIDATA_QID_ &> out/log.wikidata2redis.${i}"
    python -m utils.redis_importer --db 2 -i /data/home/zxteloiv/data/wikidata/entity_idx/wikidata.idx.0${i} --prefix WIKIDATA_QID_ &> out/log.wikidata2redis.${i}
done;
