# T6-Week11 — Threading & REST API

**Nama:** Fiqro Najiah  
**NIM:** F1D02310051  
**Kelas:** D

## Deskripsi

Aplikasi desktop berbasis PySide6 untuk mengelola data post menggunakan REST API nyata di `https://api.pahrul.my.id/api/posts`. Semua request HTTP dijalankan di thread terpisah menggunakan `QThread` sehingga antarmuka tidak pernah freeze saat menunggu respons server.

## Fitur

- GET — memuat semua posts ke dalam tabel (ID, Title, Author, Status)
- GET detail — klik baris tabel untuk menampilkan detail lengkap post beserta daftar komentar di panel kanan
- POST — form input untuk menambahkan post baru (title, body, author, slug, status)
- PUT — edit data post yang dipilih dari tabel
- DELETE — hapus post dengan dialog konfirmasi (cascade delete, semua komentar ikut terhapus)
- Threading — semua API call berjalan di `QThread` terpisah, UI tidak freeze
- State handling — indikator loading saat request berjalan, tombol Edit/Hapus hanya aktif saat ada baris terpilih
- Error handling — menangani timeout, connection error, dan validasi 422 (slug duplikat)


## Screenshot
`/ss.png`

<!-- Tambahkan screenshot di sini setelah menjalankan aplikasi -->
![Screenshot Aplikasi](screenshot.png)
