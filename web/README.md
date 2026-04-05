# Hệ Thống MultiConvert Pro Đầy Đủ (Frontend & Backend)

Dự án đã được tách ra làm 2 thành phần chuẩn mô hình Hệ thống Doanh nghiệp chuyên nghiệp.

## 📂 1. Cấu trúc thư mục
- `/FE` (Frontend): Giao diện thao tác của người dùng. Code hoàn toàn bằng HTML/CSS/JS thuần tĩnh. Bạn có thể kéo thả thư mục này lên Vercel/Netlify để public giao diện.
- `/BE` (Backend): Máy chủ xử lý lỗi và Logic ngầm, viết bằng Python (`FastAPI`). Sẽ hoạt động liên kết với mã Convert ban đầu của bạn.

---

## 💻 2. Khởi chạy Backend (BE)
Cần có Backend để các tính năng phức tạp (và các tool) có môi trường tính toán thực thụ.

1. Di chuyển vào thư mục BE:
```bash
cd c:\ProJect\Convert\web\BE
```
2. Cài đặt thư viện cần thiết (nếu bạn chưa có):
```bash
pip install fastapi uvicorn pypdf2 python-multipart
```
3. Khởi chạy Server:
```bash
python main.py
```
*(Server sẽ chạy tại `http://localhost:8000` và chờ nhận file từ Frontend)*.

---

## 🌐 3. Mở Frontend (FE)
1. Chỉ việc click đúp vào file `c:\ProJect\Convert\web\FE\index.html` để mở bằng thẻ Trình duyệt nào đó, hoặc chạy bằng Live Server nếu bạn sử dụng VSCode.
2. Thử nghiệm **Nút Công Cụ** trên thanh điều hướng để quay lại trang chủ, bấm thử tính năng **Nối file** hoặc **Bảo vệ File** (Nhập pass) rồi xem file output tải về có bị khóa thật không nhé!

📝 *Ghi chú cho lập trình viên (Bạn):*
Tại `/BE/main.py` tôi đã code sẵn thư viện `PyPDF2` để xử lý logic Thật cho tính năng Gộp và Bảo vệ. Bạn có thể import class Manager ở Source code Convert cũ của bạn nối tiếp vào đây để các tính năng OCR, Word2Pdf sử dụng chung ngầm nhé!
