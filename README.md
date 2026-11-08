# Laporan Loker Harian

Skrip otomatis: cari lowongan driver (dump truck/trailer/mixer) tiap hari jam
07:00 WIB via GitHub Actions, hasil dikirim ke Telegram. Tidak butuh PC nyala,
gratis, tidak scraping langsung situs loker (jadi tidak melanggar ToS).

## Cara Setup (sekali saja)

### 1. Buat Bot Telegram
1. Buka Telegram, cari **@BotFather**.
2. Kirim `/newbot`, ikuti instruksi (kasih nama bot, mis. `LokerHarianBot`).
3. BotFather akan kasih **token** seperti `123456789:ABCdefGhIJKlmNoPQRstuVWXyz`.
   Simpan ini — ini `TELEGRAM_BOT_TOKEN`.

### 2. Dapatkan Chat ID Anda
1. Cari bot **@userinfobot** di Telegram, chat dengannya, dia akan balas ID Anda (angka, mis. `987654321`).
   Simpan ini — ini `TELEGRAM_CHAT_ID`.
2. **Penting:** buka chat dengan bot yang baru Anda buat tadi (`LokerHarianBot`),
   kirim pesan apa saja (mis. "halo"). Ini wajib — tanpa ini bot tidak bisa
   mengirim pesan ke Anda karena Telegram memblokir bot mengirim duluan ke
   user yang belum pernah chat.

### 3. Upload Folder Ini ke Repo GitHub Anda
Dari folder `loker-harian/` ini, push semua isi ke repo GitHub Anda (termasuk
folder `.github/workflows/`).

```bash
cd loker-harian
git init
git add .
git commit -m "Setup laporan loker harian"
git branch -M main
git remote add origin https://github.com/USERNAME/NAMA_REPO.git
git push -u origin main
```

### 4. Simpan Token & Chat ID sebagai GitHub Secrets
1. Buka repo Anda di GitHub → **Settings** → **Secrets and variables** → **Actions**.
2. Klik **New repository secret**, buat dua secret:
   - Nama: `TELEGRAM_BOT_TOKEN`, Value: token dari langkah 1.
   - Nama: `TELEGRAM_CHAT_ID`, Value: chat ID dari langkah 2.

### 5. Aktifkan & Tes
1. Buka tab **Actions** di repo Anda.
2. Pilih workflow **"Laporan Loker Harian"**.
3. Klik **Run workflow** (tombol manual) untuk tes pertama kali.
4. Cek Telegram Anda — kalau sukses, laporan loker akan masuk dalam 1-2 menit.
5. Kalau gagal, buka log run tersebut di tab Actions untuk lihat error-nya.

Setelah tes pertama berhasil, workflow akan **otomatis jalan sendiri tiap jam
07:00 WIB** tanpa perlu Anda apa-apakan lagi.

## Mengubah Filter
Edit `filter.json` langsung di GitHub (klik file → pensil edit → commit),
tidak perlu buka kode Python. Setelah commit, perubahan otomatis dipakai
di run berikutnya:

- `kata_kunci`: daftar posisi yang dicari
- `lokasi`: daftar lokasi
- `exclude`: kata yang bikin lowongan dibuang dari hasil (lowercase, tanpa keharusan match persis)
- `situs_sasaran`: situs loker yang jadi target (`site:namadomain.com`)
- `maks_hasil_per_hari`: batas jumlah lowongan di satu laporan

## Cara Kerja Singkat
1. Baca `filter.json`.
2. Untuk tiap kombinasi kata kunci x lokasi x situs, cari via DuckDuckGo.
3. Buang hasil yang mengandung kata di `exclude`.
4. Buang hasil yang linknya sudah ada di `riwayat.json` (sudah pernah dikirim,
   disimpan 30 hari) — supaya tidak dapat loker yang sama berulang-ulang.
5. Kirim sisanya ke Telegram, lalu update `riwayat.json` (otomatis di-commit
   balik ke repo oleh Actions).

## Troubleshooting
| Masalah | Penyebab Umum |
|---|---|
| Tidak ada pesan masuk sama sekali | Anda belum chat duluan ke bot (lihat langkah 2) |
| Error "Unauthorized" di log Actions | Token salah / salah copy |
| Error "chat not found" | Chat ID salah, atau belum chat ke bot |
| Hasil selalu kosong | Query terlalu spesifik — coba kurangi `exclude` atau tambah `situs_sasaran` |
| Workflow tidak jalan otomatis | Repo GitHub gratis kadang menonaktifkan Actions schedule kalau repo tidak ada aktivitas >60 hari — buka tab Actions sesekali untuk "membangunkannya" |
