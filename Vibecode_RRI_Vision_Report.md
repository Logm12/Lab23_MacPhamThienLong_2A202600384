# Vibecode Project Report: Day 08 LangGraph Agent Lab
## Discovery & Vision Phase

---

### 📋 RRI REPORT: Day 08 LangGraph Agent Lab
**ID:** RRI-20260511 | **Trạng thái:** Hoàn tất (Đã khóa)

#### 1. Requirements Matrix (REQ-IDs)
| ID | Yêu cầu | Độ ưu tiên | Ghi chú |
|:---|:---|:---:|:---|
| **REQ-01** | State Schema: TypedDict với `messages`, `route_status`, `attempt_count` | P0 | Bắt buộc để quản lý retry và routing |
| **REQ-02** | Bounded Retry: Tự động dừng và chuyển `dead_letter` khi vượt `max_attempts` | P0 | Tránh vòng lặp vô hạn |
| **REQ-03** | Persistence: Sử dụng `SqliteSaver` (WAL mode) làm mặc định | P1 | Lưu trữ tại `outputs/lab.db` |
| **REQ-04** | HITL Reject: Khi người dùng từ chối thao tác rủi ro -> chuyển về `dead_letter` | P1 | Luồng xử lý lỗi an toàn |
| **REQ-05** | High-fidelity Metrics: Tính `latency_ms` bằng tổng thời gian thực thi của các node | P1 | Chi tiết và chuyên nghiệp |
| **REQ-06** | Bonus: Streamlit UI Dashboard | P2 | Giao diện tương tác trực quan |
| **REQ-07** | Bonus: Parallel Fan-out | P2 | Gọi nhiều công cụ song song |
| **REQ-08** | Bonus: Mermaid Diagram Export | P2 | Tự động xuất sơ đồ graph |

#### 2. Decisions Log
* **Dec-01**: Luồng từ chối (Reject) tại node `approval` sẽ dẫn thẳng tới `dead_letter` thay vì quay lại đầu.
* **Dec-02**: Loại bỏ `MemorySaver`, chỉ dùng `SqliteSaver` để chứng minh khả năng crash-recovery.
* **Dec-03**: Triển khai trọn bộ Bonus Extensions bao gồm Streamlit UI, Parallel Fan-out và Mermaid Diagram.
* **Dec-04**: Metrics sẽ được tính chi tiết theo từng node (Lựa chọn B).

---

### 🚀 VISION PROPOSAL: Agentic Support System v6.0
**PROJECT:** Day 08 - Professional Support Agent
**NATURE:** Web Interface (Streamlit) + Agentic Lifecycle + High Resilience

#### 🏗️ ARCHITECTURE (Kiến trúc)
Hệ thống sẽ là một **Single-Agent Orchestrator** với khả năng **Parallel Tool Execution**:
1. **Intake/Classify**: Phân loại yêu cầu từ người dùng.
2. **Conditional Router**: Điều hướng linh hoạt giữa Simple Answer, Tool Call, Risky Action, hoặc Clarification.
3. **Persistence Layer**: Mọi bước đi đều được ghi vào SQLite (SqliteSaver), cho phép "Time Travel" hoặc phục hồi sau sự cố.
4. **Parallel Fan-out**: Khi cần tra cứu nhiều thông tin, agent sẽ kích hoạt nhiều worker song song để tối ưu tốc độ.

#### 🔄 USER FLOWS (Luồng người dùng)
* **Happy Path**: User nhập -> Agent gọi Tool -> Trả kết quả -> Kết thúc.
* **Safety Path (HITL)**: User yêu cầu hành động nhạy cảm -> Graph Interrupt (Dừng lại) -> User duyệt/từ chối trên Streamlit -> Nếu từ chối, chuyển về `dead_letter`.
* **Error Path**: Công cụ lỗi -> Tự động retry (tối đa N lần) -> Nếu vẫn lỗi thì đưa vào "Hòm thư chết" (Dead Letter) để nhân viên xử lý tay.

#### 🎨 DESIGN DIRECTION (Giao diện)
* **Streamlit UI**: Sử dụng Sidebar để quản lý `thread_id`.
* **Main Dashboard**: Hiển thị Chat Interface kết hợp với sơ đồ Graph Mermaid thời gian thực.
* **Metrics Panel**: Hiển thị biểu đồ Latency (tổng hợp từ latency từng node) và Success Rate.

#### 🛠️ TECH STACK (Công nghệ)
* **Core**: Python 3.11, LangGraph, LangChain.
* **Database**: SQLite (WAL Mode) cho Checkpointing.
* **UI**: Streamlit.
* **Testing**: Pytest & custom scenario runner.
