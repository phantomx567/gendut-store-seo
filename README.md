# Gendut Store: sumber GitHub, penerbitan otomatis

## Aktivasi hosting sekali

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https%3A%2F%2Fgithub.com%2Fphantomx567%2Fgendut-store-seo)

Masuk ke Render dengan akunmu, pilih workspace **Hobby** gratis, lalu tinjau satu **Static Site** yang sudah didefinisikan di repository ini. Tidak perlu mengunggah file website. Jangan memilih layanan server atau upgrade berbayar. Setelah koneksi awal selesai, pembaruan pada branch `main` memicu build dan penerbitan otomatis.

[Hasil pemeriksaan website](https://github.com/phantomx567/gendut-store-seo/actions/workflows/checks.yml)

Folder publik `dist/` berisi website statis dan aset logo asli. `scripts/build-static.py` menyiapkan metadata, canonical, Open Graph, robots, dan sitemap dari URL hosting yang sebenarnya. Website tidak membutuhkan API model, database, atau backend kantor.

`render.yaml` membuat satu **Static Site**, bukan layanan server berbayar. Render membangun website setiap perubahan masuk ke branch publikasi yang dipilih. URL `onrender.com` berasal dari hasil layanan, bukan diklaim sudah tersedia. Repository sumber adalah https://github.com/phantomx567/gendut-store-seo. Hosting belum terhubung dan website belum dinyatakan tayang. Paket ini tidak membeli atau meningkatkan layanan dan tidak menyimpan kredensial.

Penerbitan berikutnya: staf menyiapkan perubahan → QA → keputusan konten Reza sesuai penugasan → perubahan yang disetujui masuk branch publikasi → hosting menerbitkan hasil build. Draft tidak dikirim ke branch publikasi. Raka tetap menangani publikasi media sosial seperti sebelumnya.

Repository GitHub khusus Gendut Store sudah tersedia. Pengaturan awal yang tersisa adalah menghubungkan akun hosting ke repository ini. Setelah terhubung, pembaruan branch publikasi diproses otomatis; tidak memerlukan upload file melalui dashboard hosting. Pemeriksaan GitHub memakai runner standar pada repository publik, tanpa model AI atau layanan berbayar.

Gunakan paket hosting gratis saja. Penggunaan mengikuti batas bandwidth dan build dari penyedia; jangan menambah kartu, upgrade, runner, API, atau layanan berbayar untuk melewati batas. Status paket dan pembatasan biaya harus dikonfirmasi saat akun hosting terhubung.

Setelah terbit, periksa URL sebenarnya, HTML, aset, canonical, robots, dan sitemap. Indexing dan peringkat Google masih harus diperiksa; build sukses tidak membuktikan keduanya. Website panduan ini terpisah dari gendutstore.com yang dikelola pusat.

Sumber teknis:

- https://render.com/docs/static-sites
- https://render.com/docs/environment-variables
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
