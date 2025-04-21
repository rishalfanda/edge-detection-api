import base64

file_path = 'dino.jpg' # Ganti dengan path gambar Anda
with open(file_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
print(encoded_string)