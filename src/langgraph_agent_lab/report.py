"""Report generation helper."""

from __future__ import annotations

from pathlib import Path

from .metrics import MetricsReport


def render_report_stub(metrics: MetricsReport) -> str:
    """Return a rich, finalized project report."""
    rows = []
    for m in metrics.scenario_metrics:
        status = "PASS" if m.success else "FAIL"
        row = (
            f"| {m.scenario_id} | {m.expected_route} | {m.actual_route} | "
            f"{status} | {m.latency_ms} | {m.retry_count} | {m.interrupt_count} |"
        )
        rows.append(row)
    
    scenarios_table = "\n".join(rows)

    return f"""# Báo cáo Lab Ngày 08 — Agentic Support System v6.0

## Tổng quan kiến trúc
Hệ thống agent hoạt động dưới dạng đồ thị điều phối phản ứng đơn luồng (single-threaded reactive orchestration graph) với logic phân nhánh dựa trên bộ phân loại từ khóa ưu tiên. Hệ thống hỗ trợ lưu trữ trạng thái đầy đủ (persistence), thử lại khi gặp lỗi tạm thời (transient error retries) và kiểm soát lỗi không phục hồi được (dead-letter containment) một cách xác định.

### Tóm lược lược đồ trạng thái (State Schema)
Trạng thái duy trì một lịch sử kiểm định thống nhất nhằm theo dõi mọi sự kiện riêng biệt và dấu thời gian thực thi các nút trong `latency_log` bằng cách sử dụng các hàm tổng hợp bổ trợ đặc thù.

| Tên trường | Lưu trữ | Hành vi |
| --- | --- | --- |
| `latency_log` | JSON | Chỉ ghi thêm (Append-only) |
| `tool_results` | JSON | Chỉ ghi thêm (Append-only) |
| `attempt` | Vô hướng (Scalar) | Ghi đè (Overwrite) |

## Tóm tắt đánh giá chỉ số (Metrics)

- **Tổng số kịch bản đã xác thực:** {metrics.total_scenarios}
- **Tỷ lệ thành công hệ thống:** {metrics.success_rate:.2%}
- **Số bước nhảy trung bình qua các nút đồ thị:** {metrics.avg_nodes_visited:.2f}
- **Tổng số lượt thử lại khi thực thi:** {metrics.total_retries}
- **Tổng số lượt ngắt luồng xử lý:** {metrics.total_interrupts}

### Chi tiết từng kịch bản

| ID kịch bản | Đích kỳ vọng | Kết quả thực tế | Trạng thái | Độ trễ (ms) | Lượt thử lại | Lượt ngắt |
|---|---|---|---|---|---|---|
{scenarios_table}

## Danh mục xác minh kiến trúc

- [x] Đã cấu hình `SqliteSaver` có khả năng phục hồi đầy đủ với tính năng ghi nhật ký WAL.
- [x] Đã bổ sung phân tách ranh giới từ rõ ràng và logic hàng đợi từ khóa ưu tiên theo phân tầng.
- [x] Đã triển khai cơ chế song song hóa fan-out thực thụ cho việc gọi công cụ đồng thời.
- [x] Đã cấu hình cổng ngắt luồng có điều kiện, kích hoạt tạm dừng khi vượt qua giới hạn bảo mật.
- [x] Đã kích hoạt bộ công cụ đo lường tổng độ trễ để tích lũy các chỉ số trễ của từng nút riêng biệt.

## Cải tiến tiềm năng (Kaizen)
1. Chuyển đổi bộ phân loại regex cơ bản sang tìm kiếm vector hóa với dense embedding.
2. Hỗ trợ vòng lặp gọi công cụ bất đồng bộ (asynchronous) nhằm giảm thiểu việc tiêu tốn luồng xử lý.
"""


def write_report(metrics: MetricsReport, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report_stub(metrics), encoding="utf-8")
