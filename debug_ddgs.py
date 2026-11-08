from duckduckgo_search import DDGS

query = 'site:jobstreet.co.id "driver dump truck" Batam'
print(f"QUERY YANG DIKIRIM: {query}")
print("-" * 60)

with DDGS() as ddgs:
    hasil = list(ddgs.text(query, region="id-id", max_results=5))
    print(f"Jumlah hasil: {len(hasil)}")
    for i, r in enumerate(hasil, 1):
        print(f"\n{i}. {r.get('title')}")
        print(f"   {r.get('href')}")
