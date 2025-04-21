# API Pemrosesan Gambar (FastAPI & Base64)

API sederhana yang dibangun menggunakan FastAPI untuk melakukan operasi pemrosesan gambar dasar. API ini menerima gambar dalam format string Base64 melalui request body JSON dan mengembalikan gambar yang telah diproses juga dalam format string Base64 pada response body JSON.

## Fitur

*   Menerima input gambar sebagai string Base64 dalam payload JSON.
*   Endpoint untuk melakukan segmentasi gambar menggunakan **Otsu Thresholding**.
*   Endpoint untuk melakukan deteksi tepi menggunakan **Filter Sobel**.
*   Mengembalikan gambar hasil pemrosesan sebagai string Base64 (format PNG) dalam respons JSON.
*   Dibangun dengan **FastAPI** (kinerja tinggi, mudah digunakan).
*   Dokumentasi API otomatis via **Swagger UI** (`/docs`) dan **ReDoc** (`/redoc`).
*   Dapat dijalankan menggunakan server ASGI seperti **Uvicorn**.
*   (Opsional) Dapat dikemas dalam **kontainer Docker**.
*   (Opsional) Dapat diekspos ke internet untuk pengujian menggunakan **Ngrok**.

## Prasyarat

Sebelum memulai, pastikan Anda telah menginstal:

*   **Python** (versi 3.8 atau lebih baru direkomendasikan)
*   **pip** (package installer untuk Python)
*   (Opsional) **Docker Desktop** jika Anda ingin menjalankan via container.
*   (Opsional) **Ngrok** jika Anda ingin mengekspos API lokal ke internet.
*   (Opsional) **Git** untuk mengkloning repositori (jika berlaku).

## Instalasi & Setup

1.  **Clone Repositori (jika ada):**
    ```bash
    git clone <url-repositori-anda>
    cd <nama-direktori-proyek>
    ```
    *Jika Anda hanya memiliki file `main.py`, `requirements.txt`, dll., cukup buat direktori proyek dan let