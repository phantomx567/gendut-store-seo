# Gendut Store: sumber GitHub, penerbitan otomatis

## Website publik

[Buka Panduan Gendut Store](https://gendut-store-panduan.onrender.com/)

Website sudah terbit di Render sebagai **Static Site**. Koneksi awal ke repository ini sudah selesai; pembaruan pada branch `main` memicu build dan penerbitan otomatis tanpa upload file melalui dashboard hosting.

[Sitemap publik](https://gendut-store-panduan.onrender.com/sitemap.xml) · [Robots](https://gendut-store-panduan.onrender.com/robots.txt)

[Hasil pemeriksaan website](https://github.com/phantomx567/gendut-store-seo/actions/workflows/checks.yml)

Folder publik `dist/` berisi website statis dan aset logo asli. `scripts/build-static.py` menyiapkan metadata, canonical, Open Graph, robots, dan sitemap dari URL hosting yang sebenarnya. Website tidak membutuhkan API model, database, atau backend kantor.

`render.yaml` mendefinisikan satu **Static Site** dengan `autoDeployTrigger: commit`. Render membangun website setiap perubahan masuk ke branch publikasi `main`. Alamat publik di atas sudah diperiksa melalui HTTPS: HTML, seluruh aset, canonical, Open Graph, structured data, robots, dan sitemap sesuai hasil build dari repository ini. Repository tidak menyimpan kredensial.

Penerbitan berikutnya: staf menyiapkan perubahan → QA → keputusan konten Reza sesuai penugasan → perubahan yang disetujui masuk branch publikasi → hosting menerbitkan hasil build. Draft tidak dikirim ke branch publikasi. Raka tetap menangani publikasi media sosial seperti sebelumnya.

Pemeriksaan GitHub memakai runner standar pada repository publik, tanpa model AI atau layanan berbayar. Hasil deployment Render juga dapat ditelusuri melalui deployment repository GitHub agar commit yang diterbitkan dapat diperiksa.

Gunakan paket hosting gratis saja. Penggunaan mengikuti batas bandwidth dan build dari penyedia; jangan menambah kartu, upgrade, runner, API, atau layanan berbayar untuk melewati batas. Status paket dan pembatasan biaya harus dikonfirmasi saat akun hosting terhubung.

Setiap perubahan publik perlu menjaga URL, HTML, aset, canonical, robots, dan sitemap yang benar. Indexing dan peringkat Google masih harus diperiksa; build sukses tidak membuktikan keduanya. Website panduan ini terpisah dari gendutstore.com yang dikelola pusat.

Sumber teknis:

- https://render.com/docs/static-sites
- https://render.com/docs/environment-variables
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

## Adapter penarikan halaman

Instruksi penarikan berasal dari `withdrawal_export` privat milik owner, bukan penolakan tugas umum. Simpan ekspor privat di luar repository, lalu jalankan `python3 scripts/withdraw-approved-page.py --export /private/withdrawal.json`. Untuk LP legacy, sertakan `--manifest /private/current-site-manifest.json --render-output /private/current-build`; adapter memeriksa commit/path/SHA dan membangun ulang source saat ini untuk menolak bukti lama. Untuk revisi approved baru yang sudah antre sementara versi sebelumnya masih live, sertakan manifest target publik agar kedua pasangan versi dibedakan secara tepat.

Adapter menyimpan hanya seleksi publik minimal; alasan, UUID owner, history dan hash draf yang belum live tidak masuk seleksi. Snapshot approved tidak ditimpa atau dihapus. Build bersih meniadakan route, banner yatim, daftar/hub/sitemap dan href terkait sambil mempertahankan label/prosa. Penarikan beranda ditolak. Batas `revoked_through_revision` membatalkan seluruh revisi sampai keputusan penarikan; impor ulang approval lama tidak mengaktifkannya. Hanya ekspor approved yang lebih baru dapat membuka rilis lagi. Verifikasi404/410 independen tetap diperlukan setelah deployment; localbuild tidak berarti halaman sudah ditarik.

Tanpa file seleksi, hasil sebelas halaman existing tidak berubah. Tidak ada instruksi penarikan nyata yang disertakan dalam perubahan dukungan ini. Jalankan `python3 -m unittest discover -s tests -v` untuk regresi dan fixture sintetis; jangan memakai halaman live sebagai percobaan.

## Editorial scene covers — current owner direction, 25 October 2026

Use epic landscape art recognizable from actual game characters/world references, not generic castle/island wallpaper, catalog icons, giant logos or blank purple halves. Curated cover metadata is separate from immutable approved Article documents. The assigned scene appears at both hub-card top and Article opening; content-specific instructional diagrams stay inside below the lead, with approved bytes unchanged. Existing GS header supplies brand identity; no social footer/CTA.

Every Article path must have an explicit curated cover assignment matching an approved related game path and exact asset SHA. New Articles require a newly reviewed image/variant by default; reuse must be deliberate and independently checked, never automatic per-game fallback. Missing assignment/qualified cover blocks import/build/release. Multiple variants can belong to one game. Validate local content-addressed path, MIME, hash, dimensions and honest illustration ALT; format-only compression must disclose lossy delivery. Root views actual original/delivery and integrated390px preview before freeze; Sari independently checks all responsive/text200/focus/contrast, source/asset and withdrawal guards. Unreferenced scene files are omitted from output after withdrawal. No new workflow stage, runtime or automation.
