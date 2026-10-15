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
