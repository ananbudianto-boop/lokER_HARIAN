"""
Skrip pencari loker harian.
Jalan via GitHub Actions (cron), hasil dikirim ke Telegram.
"""

import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone

import requests

TAVILY_SEARCH_URL = "https://api.tavily.com/search"

BASE_DIR = Path(__file__).parent
FILTER_PATH = BASE_DIR / "filter.json"
RIWAYAT_PATH = BASE_DIR / "riwayat.json"
RIWAYAT_HARI = 30  # simpan link yang sudah pernah dikirim selama 30 hari


def load_filter():
    with open(FILTER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_riwayat():
    if RIWAYAT_PATH.exists():
        with open(RIWAYAT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_riwayat(riwayat):
    with open(RIWAYAT_PATH, "w", encoding="utf-8") as f:
        json.dump(riwayat, f, ensure_ascii=False, indent=2)


def bersihkan_riwayat_lama(riwayat):
    batas = (datetime.now(timezone.utc) - timedelta(days=RIWAYAT_HARI)).isoformat()
    return {link: tgl for link, tgl in riwayat.items() if tgl >= batas}


def cari_loker(filt, api_key):
    """Loop tiap kombinasi kata_kunci x lokasi lewat Tavily Search API.

    include_domains dipakai supaya pembatasan situs dilakukan resmi oleh
    API-nya sendiri, bukan lewat teks site: yang terbukti rawan rusak.
    """
    domain_list = [s.replace("site:", "") for s in filt.get("situs_sasaran", [])]
    hasil = []
    for kw in filt["kata_kunci"]:
        for lok in filt["lokasi"]:
            query = f"loker {kw} {lok}"
            try:
                resp = requests.post(
                    TAVILY_SEARCH_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": query,
                        "search_depth": "basic",
                        "max_results": 10,
                        "include_domains": domain_list,
                    },
                    timeout=30,
                )
                data = resp.json()
                if resp.status_code != 200:
                    pesan_err = data.get("detail", data) if isinstance(data, dict) else data
                    print(f"[WARN] Tavily API error untuk '{query}': {pesan_err}", file=sys.stderr)
                    continue
                for item in data.get("results", []):
                    hasil.append({
                        "title": item.get("title", ""),
                        "href": item.get("url", ""),
                        "body": item.get("content", ""),
                    })
            except Exception as e:
                print(f"[WARN] Query gagal: {query} -> {e}", file=sys.stderr)
            time.sleep(1)  # jeda sopan antar-query
    return hasil


def adalah_halaman_utama(link):
    """True kalau link cuma homepage situs (bukan halaman lowongan spesifik)."""
    try:
        path = urlparse(link).path.strip("/")
        return len(path) < 3
    except Exception:
        return False


def saring_hasil(hasil, filt, riwayat):
    # Pembatasan domain sudah dilakukan API (include_domains), di sini
    # tinggal buang duplikat, riwayat, homepage, dan kata exclude.
    exclude = [e.lower() for e in filt.get("exclude", [])]
    terpilih = []
    link_terlihat = set()

    for item in hasil:
        judul = item.get("title", "")
        link = item.get("href", "")
        ringkasan = item.get("body", "")

        if not link or link in link_terlihat:
            continue
        link_terlihat.add(link)

        if link in riwayat:
            continue  # sudah pernah dikirim sebelumnya

        if adalah_halaman_utama(link):
            continue  # buang homepage situs, bukan halaman lowongan spesifik

        teks_cek = f"{judul} {ringkasan}".lower()
        if any(kata in teks_cek for kata in exclude):
            continue

        terpilih.append({"judul": judul, "link": link, "ringkasan": ringkasan})

    return terpilih[: filt.get("maks_hasil_per_hari", 15)]


def format_pesan(loker_baru):
    tanggal = datetime.now(timezone.utc) + timedelta(hours=7)  # konversi ke WIB
    header = f"🚛 *Laporan Loker Harian* - {tanggal.strftime('%d %B %Y')}\n\n"

    if not loker_baru:
        return header + "Tidak ada lowongan baru hari ini yang cocok filter."

    baris = []
    for i, lok in enumerate(loker_baru, start=1):
        baris.append(f"{i}. *{lok['judul']}*\n{lok['link']}")

    return header + "\n\n".join(baris)


def kirim_telegram(pesan):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Telegram batasi ~4096 karakter per pesan -> potong jika perlu
    potongan = [pesan[i:i + 4000] for i in range(0, len(pesan), 4000)] or [pesan]

    for bagian in potongan:
        resp = requests.post(url, data={
            "chat_id": chat_id,
            "text": bagian,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }, timeout=30)
        if resp.status_code != 200:
            print(f"[ERROR] Gagal kirim ke Telegram: {resp.text}", file=sys.stderr)
            sys.exit(1)


def main():
    api_key = os.environ["TAVILY_API_KEY"]

    filt = load_filter()
    riwayat = bersihkan_riwayat_lama(load_riwayat())

    hasil_mentah = cari_loker(filt, api_key)
    loker_baru = saring_hasil(hasil_mentah, filt, riwayat)

    pesan = format_pesan(loker_baru)
    kirim_telegram(pesan)

    sekarang = datetime.now(timezone.utc).isoformat()
    for lok in loker_baru:
        riwayat[lok["link"]] = sekarang
    save_riwayat(riwayat)

    print(f"Selesai. {len(loker_baru)} lowongan baru dikirim ke Telegram.")


if __name__ == "__main__":
    main()
