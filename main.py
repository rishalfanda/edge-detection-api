import base64  # Import library base64
import binascii  # Untuk menangkap error decode base64

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field  # Import BaseModel dan Field dari Pydantic


# --- Model Pydantic untuk Request Body ---
class ImageBase64Payload(BaseModel):
    image_base64: str = Field(
        ..., description="String Base64 dari gambar yang akan diproses."
    )
    # Contoh: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQE..." atau hanya string base64 nya saja


# --- Model Pydantic untuk Response Body ---
class ImageBase64Response(BaseModel):
    processed_image_base64: str = Field(
        ..., description="String Base64 dari gambar hasil pemrosesan."
    )
    message: str = Field(..., description="Pesan status.")


# --- Inisialisasi Aplikasi FastAPI ---
app = FastAPI(
    title="Image Processing API (Base64)",
    description="API untuk memproses gambar (input/output Base64): Grayscale, Otsu Thresholding, Sobel Edge Detection",
    version="1.1.0",
)


# --- Fungsi Logika Pemrosesan Gambar (Input byte, Output array NumPy) ---
# Fungsi ini tidak perlu diubah karena inputnya sudah bytes
def process_image_data(image_bytes: bytes):
    """
    Memproses byte gambar mentah menjadi grayscale, segmented, dan sobel.
    Mengembalikan tuple (gray, segmented, sobel) atau (None, None, None) jika error.
    """
    try:
        # Decode image dari bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Baca sebagai BGR

        if image is None:
            print("Error: Gagal decode gambar dari bytes.")
            return None, None, None  # Handle error jika decode gagal

        # --- Kode pemrosesan Anda ---
        resize_image = cv2.resize(image, (255, 255))
        gray_image = cv2.cvtColor(resize_image, cv2.COLOR_BGR2GRAY)
        _, segmented_image = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        sobel_combined = cv2.sqrt(
            cv2.addWeighted(cv2.pow(sobelx, 2.0), 1.0, cv2.pow(sobely, 2.0), 1.0, 0.0)
        )
        sobel_display = cv2.convertScaleAbs(sobel_combined)
        # --- Akhir kode pemrosesan ---

        print("Pemrosesan gambar berhasil.")
        return gray_image, segmented_image, sobel_display

    except Exception as e:
        print(f"Error selama pemrosesan gambar: {e}")
        return None, None, None


# --- Helper Function untuk Encode NumPy Array ke Base64 PNG String ---
def encode_image_to_base64(image_array: np.ndarray) -> str | None:
    """Meng-encode array gambar NumPy ke string Base64 format PNG."""
    try:
        is_success, buffer = cv2.imencode(".png", image_array)
        if not is_success:
            print("Error: Gagal meng-encode gambar ke PNG.")
            return None
        # Encode bytes ke base64, lalu decode hasil bytes base64 ke string utf-8
        base64_string = base64.b64encode(buffer).decode("utf-8")
        return base64_string
    except Exception as e:
        print(f"Error selama encoding ke Base64: {e}")
        return None


# --- Definisikan Endpoint API ---


# Gunakan response_model untuk mendokumentasikan & memvalidasi output
@app.post(
    "/process/segmented/base64",
    tags=["Image Processing (Base64)"],
    response_model=ImageBase64Response,
)
async def process_and_get_segmented_base64(payload: ImageBase64Payload):
    """
    Menerima JSON berisi gambar Base64, melakukan thresholding Otsu,
    dan mengembalikan JSON berisi gambar hasil segmentasi dalam Base64.
    """
    try:
        # 1. Dapatkan string base64 dari payload
        base64_input = payload.image_base64

        # (Opsional) Hapus prefix data URI jika ada (misal, "data:image/jpeg;base64,")
        if "," in base64_input:
            base64_input = base64_input.split(",", 1)[1]

        # 2. Decode Base64 menjadi bytes
        image_bytes = base64.b64decode(base64_input)

    except (binascii.Error, TypeError) as e:
        print(f"Error decoding Base64: {e}")
        raise HTTPException(status_code=400, detail="Input Base64 tidak valid.")
    except Exception as e:
        print(f"Unexpected error during base64 decode: {e}")
        raise HTTPException(status_code=400, detail="Gagal memproses input Base64.")

    # 3. Proses gambar (menggunakan fungsi yang sama)
    gray, segmented, sobel = process_image_data(image_bytes)

    # 4. Handle jika pemrosesan gagal
    if segmented is None:
        raise HTTPException(
            status_code=500, detail="Gagal memproses gambar setelah decode."
        )

    # 5. Encode gambar hasil (segmented) ke Base64
    base64_output = encode_image_to_base64(segmented)

    if base64_output is None:
        raise HTTPException(
            status_code=500, detail="Gagal meng-encode gambar hasil ke Base64."
        )

    # 6. Kembalikan hasil dalam format JSON yang ditentukan oleh ImageBase64Response
    return ImageBase64Response(
        processed_image_base64=base64_output,
        message="Gambar berhasil disegmentasi (Otsu).",
    )


@app.post(
    "/process/sobel/base64",
    tags=["Image Processing (Base64)"],
    response_model=ImageBase64Response,
)
async def process_and_get_sobel_base64(payload: ImageBase64Payload):
    """
    Menerima JSON berisi gambar Base64, melakukan deteksi tepi Sobel,
    dan mengembalikan JSON berisi gambar hasil deteksi tepi dalam Base64.
    """
    try:
        base64_input = payload.image_base64
        if "," in base64_input:
            base64_input = base64_input.split(",", 1)[1]
        image_bytes = base64.b64decode(base64_input)
    except (binascii.Error, TypeError):
        raise HTTPException(status_code=400, detail="Input Base64 tidak valid.")
    except Exception:
        raise HTTPException(status_code=400, detail="Gagal memproses input Base64.")

    gray, segmented, sobel = process_image_data(image_bytes)

    if sobel is None:
        raise HTTPException(
            status_code=500, detail="Gagal memproses gambar setelah decode."
        )

    base64_output = encode_image_to_base64(sobel)

    if base64_output is None:
        raise HTTPException(
            status_code=500, detail="Gagal meng-encode gambar hasil ke Base64."
        )

    return ImageBase64Response(
        processed_image_base64=base64_output,
        message="Deteksi tepi Sobel berhasil diterapkan.",
    )


@app.get("/", tags=["General"])
async def read_root():
    """Endpoint root untuk mengecek apakah API berjalan."""
    return {"message": "Selamat datang di Image Processing API (Base64)!"}


# --- Menjalankan server (jika script dieksekusi langsung) ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
