from duckduckgo_search import DDGS
import warnings
warnings.filterwarnings("ignore")

tes = [
    "driver dump truck Batam",
    '"driver dump truck" Batam',
    "site:jobstreet.co.id driver dump truck Batam",
    'site:jobstreet.co.id "driver dump truck"',
    "loker driver dump truck Batam",
]

with DDGS() as ddgs:
    for q in tes:
        print(f"\n=== QUERY: {q} ===")
        try:
            hasil = list(ddgs.text(q, max_results=3))
            for r in hasil:
                print(f"  - {r.get('title')}")
                print(f"    {r.get('href')}")
        except Exception as e:
            print(f"  ERROR: {e}")
