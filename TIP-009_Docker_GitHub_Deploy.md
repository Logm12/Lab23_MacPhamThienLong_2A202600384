# TASK INSTRUCTION PACK (TIP): TIP-009
**Dự án:** Day 08 - Professional Support Agent (LangGraph)
**Nhiệm vụ:** Final Test, Docker Build & GitHub Push
**Người thực hiện:** Thợ thi công (Builder)

---

## 1. HEADER
- **ID:** TIP-009
- **Trạng thái:** READY
- **Độ ưu tiên:** P1 (Giai đoạn Ship/Deploy)
- **Dependencies:** Đã hoàn thành toàn bộ TIP-001 đến TIP-008
- **Thời gian ước tính:** 15-20 phút

---

## 2. CONTEXT & REFERENCE
- **Thư mục làm việc:** Root directory (`/`)
- **File trọng tâm:** `Dockerfile`, `docker-compose.yml`, `Makefile`, `.gitignore`
- **Hiện trạng:** Codebase đã vượt qua 100% test scenarios. Hệ thống đã sẵn sàng cho Production.

---

## 3. TASK DESCRIPTION
Thực hiện chạy toàn bộ hệ thống kiểm tra tự động lần cuối (Lint, Typecheck, Test). Sau đó, tiến hành build Docker image từ `Dockerfile` và `docker-compose.yml` có sẵn để đảm bảo ứng dụng chạy tốt trong môi trường container. Cuối cùng, commit toàn bộ mã nguồn và đẩy lên GitHub.

---

## 4. SPECIFICATIONS (YÊU CẦU KỸ THUẬT)

### 4.1. Clean & Verify (Kiểm thử cuối)
- Chạy lệnh `make clean` để xóa bỏ các cache (`__pycache__`, v.v.).
- Chạy chuỗi lệnh kiểm tra chất lượng: `make lint`, `make typecheck`, và `make test`. Đảm bảo không có bất kỳ warning hay error nào.

### 4.2. Dockerization
- Sử dụng `docker-compose.yml` đã có trong dự án.
- Chạy lệnh `docker-compose build` để đóng gói container.
- Chạy thử `docker-compose up -d` và kiểm tra logs container xem Agent/Streamlit UI có khởi động thành công trên cổng được chỉ định không.
- Tắt và dọn dẹp container: `docker-compose down`.

### 4.3. Version Control (GitHub)
- Kiểm tra file `.gitignore`, đảm bảo các file sau **KHÔNG** bị track:
  - Thư mục `.venv/`
  - Các file biến môi trường: `.env`
  - Database và outputs nội bộ: `outputs/lab.db`, `outputs/metrics.json` (chỉ giữ lại `outputs/.gitkeep`).
- Thực hiện chuỗi lệnh Git:
  - `git add .`
  - `git commit -m "feat: complete day08 lab with 100% coverage and full bonus extensions"`
  - `git branch -M main`
  - `git push -u origin main` (Yêu cầu Homeowner cung cấp remote URL nếu chưa setup).

---

## 5. ACCEPTANCE CRITERIA (TIÊU CHÍ NGHIỆM THU)

- **Scenario 1: Code Health**
    - `Given` mã nguồn hiện tại.
    - `When` chạy `make lint` và `make typecheck`.
    - `Then` terminal trả về exit code 0 (không có lỗi).

- **Scenario 2: Container Readiness**
    - `Given` file Dockerfile và docker-compose.yml.
    - `When` thực hiện lệnh build.
    - `Then` image được tạo thành công không gặp lỗi dependency.

- **Scenario 3: An toàn bảo mật Git**
    - `Given` trạng thái staging chuẩn bị commit.
    - `When` kiểm tra danh sách file staged.
    - `Then` tuyệt đối không có file `.env` hoặc file `.db` thực tế nào nằm trong danh sách.

---

## 6. CONSTRAINTS (RÀNG BUỘC)
- Tuyệt đối không commit các khóa API hoặc dữ liệu cá nhân lên GitHub.
- Không thay đổi logic cốt lõi của Graph đã được nghiệm thu trong các TIP trước.

---

## 7. REPORT FORMAT (MẪU BÁO CÁO HOÀN THÀNH)
Builder sau khi xong phải báo cáo theo mẫu sau:
```markdown
# COMPLETION REPORT: TIP-009
**STATUS:** DONE
**FILES CHANGED:** `.gitignore` (nếu có cập nhật)
**TEST RESULTS:**
- Make Test/Lint: [PASS/FAIL]
- Docker Build: [PASS/FAIL]
- Git Push: [Thành công lên branch nào]
**ISSUES:** [Nếu có]
```
