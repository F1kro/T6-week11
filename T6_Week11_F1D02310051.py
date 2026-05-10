# Nama  : Fiqro Najiah
# NIM   : F1D02310051
# Kelas : [isi kelas kamu]

import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QLineEdit, QTextEdit, QMessageBox, QFrame, QDialog,
    QFormLayout, QDialogButtonBox, QStatusBar, QComboBox, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal

BASE_URL = 'https://api.pahrul.my.id/api/posts'

STYLESHEET = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #1e1e2e;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 80px;
}
QPushButton:hover    { background-color: #45475a; border-color: #7f849c; }
QPushButton:pressed  { background-color: #585b70; }
QPushButton:disabled { background-color: #27273a; color: #585b70; border-color: #313244; }

QPushButton#btn_tambah {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    font-weight: bold;
}
QPushButton#btn_tambah:hover   { background-color: #b4d0fb; }
QPushButton#btn_tambah:pressed { background-color: #74a8f9; }
QPushButton#btn_tambah:disabled { background-color: #27273a; color: #585b70; border: 1px solid #313244; }

QPushButton#btn_hapus {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: none;
    font-weight: bold;
}
QPushButton#btn_hapus:hover    { background-color: #f5a8bc; }
QPushButton#btn_hapus:pressed  { background-color: #f07090; }
QPushButton#btn_hapus:disabled { background-color: #27273a; color: #585b70; border: 1px solid #313244; }

QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 8px;
    selection-background-color: #45475a;
    selection-color: #cdd6f4;
}
QTableWidget::item { padding: 6px; border: none; }
QTableWidget::item:selected { background-color: #45475a; }

QHeaderView::section {
    background-color: #181825;
    color: #a6adc8;
    padding: 8px 6px;
    border: none;
    border-bottom: 2px solid #45475a;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border-color: #89b4fa; }

QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    selection-background-color: #45475a;
}

QFrame#panel_detail {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
}

QSplitter::handle { background-color: #313244; width: 2px; }

QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
    font-size: 12px;
}

QScrollBar:vertical {
    background: #181825; width: 8px; border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #45475a; border-radius: 4px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #181825; height: 8px; border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #45475a; border-radius: 4px; min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #585b70; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QLabel#judul {
    color: #89b4fa;
    font-size: 18px;
    font-weight: bold;
    padding: 4px 0 8px 0;
}
QLabel#lbl_loading {
    color: #f9e2af;
    font-style: italic;
    font-size: 12px;
}
QLabel#lbl_detail {
    color: #a6adc8;
    font-size: 11px;
    font-weight: bold;
    padding-bottom: 6px;
}
"""


# ─────────────────────────────────────────────────────────
# Worker — semua HTTP request jalan di thread terpisah
# ─────────────────────────────────────────────────────────
class ApiWorker(QThread):
    selesai = Signal(object)
    error   = Signal(str)

    def __init__(self, method, url, payload=None):
        super().__init__()
        self.method  = method
        self.url     = url
        self.payload = payload

    def run(self):
        try:
            if self.method == 'GET':
                r = requests.get(self.url, timeout=10)
            elif self.method == 'POST':
                r = requests.post(self.url, json=self.payload, timeout=10)
            elif self.method == 'PUT':
                r = requests.put(self.url, json=self.payload, timeout=10)
            elif self.method == 'DELETE':
                r = requests.delete(self.url, timeout=10)
            else:
                self.error.emit(f'Method tidak dikenal: {self.method}')
                return

            # tangani validasi 422 (slug duplikat, dll)
            if r.status_code == 422:
                try:
                    detail = r.json()
                    pesan  = detail.get('message', 'Validasi gagal.')
                    errors = detail.get('errors', {})
                    if errors:
                        baris = '\n'.join(
                            f'  - {k}: {", ".join(v) if isinstance(v, list) else v}'
                            for k, v in errors.items()
                        )
                        pesan = f'{pesan}\n{baris}'
                except Exception:
                    pesan = 'Validasi gagal (422).'
                self.error.emit(pesan)
                return

            r.raise_for_status()

            try:
                data = r.json()
            except Exception:
                data = {}

            self.selesai.emit(data)

        except requests.exceptions.ConnectionError:
            self.error.emit('Tidak dapat terhubung ke server.\nPeriksa koneksi internet.')
        except requests.exceptions.Timeout:
            self.error.emit('Request timeout. Server tidak merespons.')
        except requests.exceptions.HTTPError as e:
            self.error.emit(f'HTTP Error: {e}')
        except Exception as e:
            self.error.emit(f'Error tidak terduga: {e}')


# ─────────────────────────────────────────────────────────
# Dialog form tambah / edit post
# ─────────────────────────────────────────────────────────
class DialogPost(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Tambah Post' if data is None else 'Edit Post')
        self.setMinimumWidth(440)
        self._bangun_ui(data)

    def _bangun_ui(self, data):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.input_title  = QLineEdit()
        self.input_author = QLineEdit()
        self.input_slug   = QLineEdit()
        self.input_slug.setPlaceholderText('contoh: judul-post-saya')
        self.combo_status = QComboBox()
        self.combo_status.addItems(['published', 'draft'])
        self.input_body   = QTextEdit()
        self.input_body.setMinimumHeight(110)

        form.addRow('Title :', self.input_title)
        form.addRow('Author :', self.input_author)
        form.addRow('Slug :', self.input_slug)
        form.addRow('Status :', self.combo_status)
        form.addRow('Body :', self.input_body)
        layout.addLayout(form)

        if data:
            self.input_title.setText(data.get('title', ''))
            self.input_author.setText(data.get('author', ''))
            self.input_slug.setText(data.get('slug', ''))
            self.input_body.setPlainText(data.get('body', ''))
            idx = self.combo_status.findText(data.get('status', 'draft'))
            if idx >= 0:
                self.combo_status.setCurrentIndex(idx)

        tombol = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        tombol.accepted.connect(self._validasi)
        tombol.rejected.connect(self.reject)
        layout.addWidget(tombol)

    def _validasi(self):
        if not self.input_title.text().strip():
            QMessageBox.warning(self, 'Peringatan', 'Title wajib diisi!')
            return
        if not self.input_author.text().strip():
            QMessageBox.warning(self, 'Peringatan', 'Author wajib diisi!')
            return
        if not self.input_slug.text().strip():
            QMessageBox.warning(self, 'Peringatan', 'Slug wajib diisi!')
            return
        if not self.input_body.toPlainText().strip():
            QMessageBox.warning(self, 'Peringatan', 'Body wajib diisi!')
            return
        self.accept()

    def ambil_data(self):
        return {
            'title':  self.input_title.text().strip(),
            'author': self.input_author.text().strip(),
            'slug':   self.input_slug.text().strip(),
            'status': self.combo_status.currentText(),
            'body':   self.input_body.toPlainText().strip(),
        }


# ─────────────────────────────────────────────────────────
# Jendela utama
# ─────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Post Manager — api.pahrul.my.id')
        self.setMinimumSize(1000, 600)
        self.workers    = []
        self.data_posts = []
        self._bangun_ui()
        self._muat_posts()

    def _bangun_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        root = QVBoxLayout(widget)
        root.setContentsMargins(16, 16, 16, 8)
        root.setSpacing(10)

        # judul
        judul = QLabel('Post Manager')
        judul.setObjectName('judul')
        root.addWidget(judul)

        # baris tombol
        baris = QHBoxLayout()
        baris.setSpacing(8)
        self.btn_refresh = QPushButton('Refresh')
        self.btn_tambah  = QPushButton('+ Tambah Post')
        self.btn_edit    = QPushButton('Edit')
        self.btn_hapus   = QPushButton('Hapus')

        self.btn_tambah.setObjectName('btn_tambah')
        self.btn_hapus.setObjectName('btn_hapus')
        self.btn_edit.setEnabled(False)
        self.btn_hapus.setEnabled(False)

        for b in [self.btn_refresh, self.btn_tambah, self.btn_edit, self.btn_hapus]:
            baris.addWidget(b)
        baris.addStretch()

        self.label_loading = QLabel('')
        self.label_loading.setObjectName('lbl_loading')
        baris.addWidget(self.label_loading)
        root.addLayout(baris)

        # splitter: tabel kiri | detail kanan
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)

        # tabel
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(4)
        self.tabel.setHorizontalHeaderLabels(['ID', 'Title', 'Author', 'Status'])
        self.tabel.setColumnHidden(0, True)
        self.tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabel.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabel.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel.setAlternatingRowColors(True)
        self.tabel.verticalHeader().setDefaultSectionSize(36)
        self.tabel.itemSelectionChanged.connect(self._on_pilih_baris)
        splitter.addWidget(self.tabel)

        # panel detail
        panel = QFrame()
        panel.setObjectName('panel_detail')
        layout_panel = QVBoxLayout(panel)
        layout_panel.setContentsMargins(12, 12, 12, 12)
        lbl_detail = QLabel('DETAIL POST')
        lbl_detail.setObjectName('lbl_detail')
        layout_panel.addWidget(lbl_detail)
        self.area_detail = QTextEdit()
        self.area_detail.setReadOnly(True)
        self.area_detail.setPlaceholderText('Klik baris di tabel untuk melihat detail post...')
        layout_panel.addWidget(self.area_detail)
        splitter.addWidget(panel)

        splitter.setSizes([580, 380])
        root.addWidget(splitter)

        # status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage('Siap.')

        # sambungkan tombol
        self.btn_refresh.clicked.connect(self._muat_posts)
        self.btn_tambah.clicked.connect(self._aksi_tambah)
        self.btn_edit.clicked.connect(self._aksi_edit)
        self.btn_hapus.clicked.connect(self._aksi_hapus)

    # ── helper jalankan worker ──
    def _jalankan_worker(self, method, url, payload=None, on_selesai=None, on_error=None):
        self._set_loading(True)
        worker = ApiWorker(method, url, payload)
        worker.selesai.connect(on_selesai or (lambda _: None))
        worker.error.connect(on_error or self._on_error)
        worker.selesai.connect(lambda _: self._set_loading(False))
        worker.error.connect(lambda _: self._set_loading(False))
        worker.finished.connect(lambda: self.workers.remove(worker) if worker in self.workers else None)
        self.workers.append(worker)
        worker.start()

    def _set_loading(self, aktif):
        self.btn_refresh.setEnabled(not aktif)
        self.btn_tambah.setEnabled(not aktif)
        if aktif:
            self.label_loading.setText('Memuat...')
            self.btn_edit.setEnabled(False)
            self.btn_hapus.setEnabled(False)
        else:
            self.label_loading.setText('')
            ada_pilihan = self.tabel.currentRow() >= 0
            self.btn_edit.setEnabled(ada_pilihan)
            self.btn_hapus.setEnabled(ada_pilihan)

    def _on_pilih_baris(self):
        baris = self.tabel.currentRow()
        ada   = baris >= 0
        self.btn_edit.setEnabled(ada)
        self.btn_hapus.setEnabled(ada)
        if ada:
            self._muat_detail(baris)

    # ── GET semua posts ──
    def _muat_posts(self):
        self.area_detail.clear()
        self.status.showMessage('Mengambil data posts...')
        self._jalankan_worker('GET', BASE_URL, on_selesai=self._on_posts_loaded)

    def _on_posts_loaded(self, resp):
        posts = resp.get('data', []) if isinstance(resp, dict) else resp
        self.data_posts = posts
        self.tabel.setRowCount(0)
        for post in posts:
            baris = self.tabel.rowCount()
            self.tabel.insertRow(baris)
            for k, val in enumerate([post['id'], post['title'], post['author'], post['status']]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                if k == 3:
                    warna = '#a6e3a1' if val == 'published' else '#fab387'
                    item.setForeground(__import__('PySide6.QtGui', fromlist=['QColor']).QColor(warna))
                self.tabel.setItem(baris, k, item)
        self.status.showMessage(f'{len(posts)} post berhasil dimuat.')

    # ── GET detail satu post ──
    def _muat_detail(self, baris):
        if baris < 0 or baris >= len(self.data_posts):
            return
        post_id = self.data_posts[baris]['id']
        self.area_detail.setPlainText('Memuat detail...')
        self._jalankan_worker('GET', f'{BASE_URL}/{post_id}', on_selesai=self._on_detail_loaded)

    def _on_detail_loaded(self, resp):
        post     = resp.get('data', {}) if isinstance(resp, dict) else resp
        comments = post.get('comments', [])

        baris_komentar = '\n\nKomentar:\n' + '-' * 32
        if comments:
            for c in comments:
                baris_komentar += (
                    f"\n  {c.get('name', '-')} <{c.get('email', '-')}>\n"
                    f"  {c.get('body', '')}\n"
                    f"  [{c.get('status', '-')}]"
                )
        else:
            baris_komentar += '\n  Belum ada komentar.'

        teks = (
            f"ID       : {post.get('id', '-')}\n"
            f"Title    : {post.get('title', '-')}\n"
            f"Author   : {post.get('author', '-')}\n"
            f"Slug     : {post.get('slug', '-')}\n"
            f"Status   : {post.get('status', '-')}\n"
            f"Dibuat   : {post.get('created_at', '-')}\n"
            f"Diupdate : {post.get('updated_at', '-')}\n"
            f"\nBody:\n{post.get('body', '-')}"
            f"{baris_komentar}"
        )
        self.area_detail.setPlainText(teks)
        self.status.showMessage(f'Detail post ID {post.get("id")} dimuat.')

    # ── POST tambah post ──
    def _aksi_tambah(self):
        dialog = DialogPost(self)
        if not dialog.exec():
            return
        payload = dialog.ambil_data()
        self.status.showMessage('Menambahkan post baru...')
        self._jalankan_worker('POST', BASE_URL, payload=payload, on_selesai=self._on_tambah_selesai)

    def _on_tambah_selesai(self, resp):
        post = resp.get('data', resp)
        self.status.showMessage(f'Post "{post.get("title")}" berhasil ditambahkan (ID: {post.get("id")}).')
        QMessageBox.information(self, 'Berhasil', f'Post berhasil ditambahkan!\nID: {post.get("id")}')
        self._muat_posts()

    # ── PUT edit post ──
    def _aksi_edit(self):
        baris = self.tabel.currentRow()
        if baris < 0:
            return
        post = self.data_posts[baris]
        dialog = DialogPost(self, data=post)
        if not dialog.exec():
            return
        payload = dialog.ambil_data()
        self.status.showMessage(f'Mengupdate post ID {post["id"]}...')
        self._jalankan_worker(
            'PUT', f'{BASE_URL}/{post["id"]}',
            payload=payload, on_selesai=self._on_edit_selesai
        )

    def _on_edit_selesai(self, resp):
        post = resp.get('data', resp)
        self.status.showMessage(f'Post ID {post.get("id")} berhasil diupdate.')
        QMessageBox.information(self, 'Berhasil', f'Post ID {post.get("id")} berhasil diupdate!')
        self._muat_posts()

    # ── DELETE hapus post ──
    def _aksi_hapus(self):
        baris = self.tabel.currentRow()
        if baris < 0:
            return
        post = self.data_posts[baris]
        konfirmasi = QMessageBox.question(
            self, 'Konfirmasi Hapus',
            f'Yakin hapus post "{post["title"]}"?\n\nSemua komentar pada post ini juga akan ikut terhapus.',
            QMessageBox.Yes | QMessageBox.No
        )
        if konfirmasi != QMessageBox.Yes:
            return
        self.status.showMessage(f'Menghapus post ID {post["id"]}...')
        self._jalankan_worker(
            'DELETE', f'{BASE_URL}/{post["id"]}',
            on_selesai=lambda _: self._on_hapus_selesai(post)
        )

    def _on_hapus_selesai(self, post):
        self.status.showMessage(f'Post "{post["title"]}" berhasil dihapus.')
        QMessageBox.information(self, 'Berhasil', f'Post "{post["title"]}" berhasil dihapus!')
        self.area_detail.clear()
        self._muat_posts()

    # ── error handler global ──
    def _on_error(self, pesan):
        self.status.showMessage(f'Error: {pesan.splitlines()[0]}')
        QMessageBox.critical(self, 'Error', pesan)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
