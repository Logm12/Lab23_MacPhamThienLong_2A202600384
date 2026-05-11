# Day 23 - Mạc Phạm Thiên Long - 2A202600384
## Tổng quan kiến trúc
Hệ thống agent hoạt động dưới dạng đồ thị điều phối phản ứng đơn luồng (single-threaded reactive orchestration graph) với logic phân nhánh dựa trên bộ phân loại từ khóa ưu tiên. Hệ thống hỗ trợ lưu trữ trạng thái đầy đủ (persistence), thử lại khi gặp lỗi tạm thời (transient error retries) và kiểm soát lỗi không phục hồi được (dead-letter containment) một cách xác định.

### Tóm lược lược đồ trạng thái (State Schema)
Trạng thái duy trì một lịch sử kiểm định thống nhất nhằm theo dõi mọi sự kiện riêng biệt và dấu thời gian thực thi các nút trong `latency_log` bằng cách sử dụng các hàm tổng hợp bổ trợ đặc thù.

| Fields | Lưu trữ | Hành vi |
| --- | --- | --- |
| `latency_log` | JSON | Chỉ ghi thêm (Append-only) |
| `tool_results` | JSON | Chỉ ghi thêm (Append-only) |
| `attempt` | Vô hướng (Scalar) | Ghi đè (Overwrite) |

## Tóm tắt đánh giá chỉ số (Metrics)

- **Tổng số kịch bản đã xác thực:** 8
- **Tỷ lệ thành công hệ thống:** 100.00%
- **Số bước nhảy trung bình qua các nút đồ thị:** 13.25
- **Tổng số lượt thử lại khi thực thi:** 6
- **Tổng số lượt ngắt luồng xử lý:** 6

### Chi tiết từng kịch bản

| ID kịch bản | Đích kỳ vọng | Kết quả thực tế | Trạng thái | Độ trễ (ms) | Lượt thử lại | Lượt ngắt |
|---|---|---|---|---|---|---|
| S01_simple | simple | simple | PASS | 0 | 0 | 0 |
| S02_tool | tool | tool | PASS | 105 | 0 | 0 |
| S03_missing | missing_info | missing_info | PASS | 0 | 0 | 0 |
| S04_risky | risky | risky | PASS | 103 | 0 | 2 |
| S05_error | error | error | PASS | 207 | 4 | 0 |
| S06_delete | risky | risky | PASS | 102 | 0 | 2 |
| S07_dead_letter | error | error | PASS | 0 | 2 | 0 |
| S08_hitl_reject | risky | risky | PASS | 103 | 0 | 2 |

## Danh mục xác minh kiến trúc

- [x] Đã cấu hình `SqliteSaver` có khả năng phục hồi đầy đủ với tính năng ghi nhật ký WAL.
- [x] Đã bổ sung phân tách ranh giới từ rõ ràng và logic hàng đợi từ khóa ưu tiên theo phân tầng.
- [x] Đã triển khai cơ chế song song hóa fan-out thực thụ cho việc gọi công cụ đồng thời.
- [x] Đã cấu hình cổng ngắt luồng có điều kiện, kích hoạt tạm dừng khi vượt qua giới hạn bảo mật.
- [x] Đã kích hoạt bộ công cụ đo lường tổng độ trễ để tích lũy các chỉ số trễ của từng nút riêng biệt.

## Cải tiến tiềm năng
1. Chuyển đổi bộ phân loại regex cơ bản sang tìm kiếm vector hóa với dense embedding.
2. Hỗ trợ vòng lặp gọi công cụ bất đồng bộ (asynchronous) nhằm giảm thiểu việc tiêu tốn luồng xử lý.
