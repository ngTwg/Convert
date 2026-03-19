# MultiConvert 🔄 🇻🇳

> **Công cụ chuyển đổi & chỉnh sửa file đa định dạng cao cấp dành cho Windows**
> Chuyển đổi qua lại giữa 19 định dạng đầu vào và 9 định dạng đầu ra với chất lượng cao • Trình chỉnh sửa ngay trong App • Xử lý hàng loạt (Batch)

[Read in English](README.md)

---

## 📥 Tải Xuống (Dành cho Người Dùng)

**Cách tải và cài đặt nhanh nhất:**
1. Vào mục [**Releases**](../../releases/latest) ở cột bên phải màn hình GitHub.
2. Tải file cài đặt `.exe` mới nhất (Ví dụ: `MultiConvert_Setup_v0.1.0.exe`).
3. Nhấp đúp vào file để cài đặt (Cứ bấm Next là xong!).
4. Trong lúc cài, phần mềm có thể tự động tải thêm bộ công cụ bổ sung (tùy chọn) nếu máy bạn chưa có.

---

## ✨ Tính Năng Nổi Bật

### 🔄 Chuyển Đổi Đa Định Dạng
- **Đầu vào (19)**: MD, RST, TXT, HTML, DOCX, DOC, ODT, RTF, EPUB, PDF, PPTX, XLSX, CSV, JPG, PNG, TIF, BMP, GIF, WEBP
- **Đầu ra (9)**: MD, TXT, HTML, DOCX, ODT, RTF, EPUB, PDF, CSV
- **Chuyển đổi bắc cầu tự động**: Nếu không có đường chuyển đổi trực tiếp (VD: `md→pdf`), app sẽ tự động mượn định dạng trung gian (`md→html→pdf`).

### ✏️ Trình Chỉnh Sửa Trực Tiếp (WYSIWYG)
- Soạn thảo giống Word với các định dạng **In đậm**, *In nghiêng*, ~~Gạch ngang~~
- Làm việc với Tiêu đề (H1-H3), danh sách, blockquote, link
- Kéo thả file bất kỳ vào app → chỉnh sửa HTML trực tiếp → xuất ra định dạng khác.

### 📥 Kéo & Thả (Drag & Drop)
- Có thể kéo thả 1 file hoặc cả đống file cùng lúc vào màn hình chờ
- Tự động nhận dạng và xếp vào hàng đợi xử lý.

### ⚡ Xử Lý Hàng Loạt
- Chuyển đổi cả một thư mục chỉ với 1 cú click
- Xử lý song song cho tốc độ siêu nhanh.

### 🔍 Hỗ trợ Nhận Dạng Ký Tự (OCR)
- Bóc tách toàn bộ chữ từ ảnh chụp hoặc các tệp PDF được scan
- Hỗ trợ tốt nhất tiếng Việt & tiếng Anh.

---

## 🚀 Dành Cho Lập Trình Viên (Dựng từ Source)

### 1. Cài đặt Môi trường
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

### 2. Hướng Dẫn Đóng Gói

Chạy lệnh sau để tự tạo ra file `.exe` cài đặt:
```powershell
powershell -ExecutionPolicy Bypass -File build_installer.ps1 -UseVenv
```
File installer hoàn chỉnh sẽ nằm ở: `installer_output/MultiConvert_Setup_v<version>.exe`.
