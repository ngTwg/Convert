# HƯỚNG DẪN NHANH / QUICK START GUIDE

## Dành Cho Nhà Phát Triển / For Developers

### Tạo Windows Installer (KHUYẾN NGHỊ ⭐)

**Yêu cầu:**
1. Cài đặt [Inno Setup](https://jrsoftware.org/isdl.php)
2. Python 3.11+ với pip

**Lệnh:**
```powershell
powershell -ExecutionPolicy Bypass -File build_installer.ps1 -UseVenv
```

**Kết quả:**
- File installer chuyên nghiệp: `installer_output/MultiConvert_Setup_v1.0.0.exe`
- Người dùng cuối chỉ cần tải và chạy file này!

---

## Dành Cho Người Dùng / For End Users

### Cài đặt MultiConvert

1. **Tải file installer**
   - `MultiConvert_Setup_v1.0.0.exe` (~900 MB)

2. **Chạy installer**
   - Nhấp đúp file `.exe`
   - Chọn ngôn ngữ (Tiếng Việt hoặc English)
   - Nhấn "Next" → "Install"

3. **Kiểm tra phụ thuộc (tùy chọn)**
   - ✅ Pandoc: Đã tích hợp sẵn
   - ⚠️ LibreOffice: Tải tại https://www.libreoffice.org/
   - ⚠️ Tesseract OCR: Tải tại https://github.com/UB-Mannheim/tesseract/wiki

4. **Sử dụng**
   - Mở từ Start Menu hoặc Desktop shortcut
   - Kéo thả file vào ứng dụng
   - Chọn định dạng đầu ra
   - Nhấn "Chuyển Đổi"

---

## Tính Năng Chính / Key Features

### 1. Chuyển Đổi File
- **Hỗ trợ 16+ định dạng đầu vào**: MD, HTML, DOCX, PDF, JPG, PNG, ...
- **9 định dạng đầu ra**: PDF, DOCX, HTML, MD, TXT, ...
- **Tự động tìm đường**: Ứng dụng tự chọn cách tốt nhất để chuyển đổi

### 2. Chỉnh Sửa Trong App
- Mở file → Chỉnh sửa → Xuất ra định dạng khác
- Định dạng: **In đậm**, *In nghiêng*, Tiêu đề, Danh sách
- Chèn link, undo/redo

### 3. Xử Lý Hàng Loạt
- Kéo thả nhiều file cùng lúc
- Chuyển đổi tất cả sang cùng 1 định dạng
- Hiển thị tiến trình realtime

### 4. Nhận Diện Chữ (OCR)
- Chuyển ảnh (JPG, PNG) thành văn bản
- Chuyển PDF scan thành file có thể chỉnh sửa
- Hỗ trợ Tiếng Việt + English

---

## Xử Lý Sự Cố / Troubleshooting

### Không chuyển được Office → PDF?
➜ Cài đặt LibreOffice: https://www.libreoffice.org/

### Không nhận diện được chữ từ ảnh?
➜ Cài đặt Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki

### App không mở được?
➜ Kiểm tra Windows Defender/Antivirus có chặn không

---

## Liên Hệ / Contact

- **Issues**: https://github.com/ngTwg/Convert/issues
- **Documentation**: Xem file `README.md` và `TESTING_REPORT.md`

---

**Phiên bản / Version**: 1.0.0
**Cập nhật / Updated**: March 2026
