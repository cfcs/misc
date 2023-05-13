#!/usr/bin/env python3

# Attempt to predict postgres' md5(hstore()::text) on the app side,
# to allow using hashes as FKs in many-to-one relations.
# The hstore table should have a functional index on the TEXT/BYTEA hash
# for JOINs.
# This approach makes for cheap COPY FROM STDIN inserts to the main
# table at least.

import psycopg # psycopg3, not psycopg2
import asyncio

async def main():
    pg3conn = await psycopg.AsyncConnection.connect()
    from psycopg.types import TypeInfo
    from psycopg.types.hstore import register_hstore

    typeinfo = await TypeInfo.fetch(pg3conn, "hstore")
    register_hstore(typeinfo, pg3conn)
    hstore_dumper = pg3conn.adapters.get_dumper_by_oid(typeinfo.oid, 0) # 0=text
    hstore_dumper = hstore_dumper(cls=hstore_dumper)

    hs = {"a":"2", "AAA": "5", "C": "1", "DC":"4", "b": "3",}

    # hstore(%s)::text
    hs_text = hstore_to_text(hs)
    print(hs_text) # b'"C":"1","a":"2","b":"3","DC":"4","AAA":"5"'

    # digest(hstore(%s)::text, 'md5')
    hdict_hash = hashlib.md5(hs).digest()

def hstore_to_text(hdict, encoding='ascii'):
    '''sort dict by key length, subsequently lexicographically,
    and finally insert spaces between the elements since psycopg
    produces a compact representation
    see https://github.com/postgres/postgres/blob/master/contrib/hstore/hstore_io.c#L325
    hstoreUniquePairs(pairs, len, buflen) ->
    qsort(a, l, sizeof(Pairs), comparePairs); ->
    comparePairs(a,b) ->
      compare by len, then memcmp.
    '''
    hdict = dict(sorted(hdict.items(), key=lambda kv:(
        len(kv[0].encode(encoding)), kv[0].encode(encoding))))
    return hstore_dumper.dump(hdict).replace(b'","', b'", "')

if __name__ == '__main__':
    asyncio.run(main())
