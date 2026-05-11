# BLUEPRINT & TASK GRAPH: Agentic Support System v6.0
**Dự án:** Day 08 - Professional Support Agent (LangGraph)
**Vai trò:** Tài liệu chỉ dẫn thi công dành cho Thợ (Builder / Claude Code)

---

## PHẦN I: BLUEPRINT (BẢN THIẾT KẾ KỸ THUẬT)

### 1. Ánh xạ Yêu cầu (Requirements Traceability)
Đảm bảo mọi yêu cầu từ RRI đều có thiết kế tương ứng:
- **REQ-01 (State Schema):** Giải quyết tại `state.py` (TypedDict).
- **REQ-02 (Bounded Retry):** Giải quyết tại `routing.py` (biến `attempt_count`).
- **REQ-03 (Sqlite Persistence):** Giải quyết tại `persistence.py` & `graph.py`.
- **REQ-04 (HITL Reject):** Giải quyết tại `nodes.py` (node approval) & `routing.py`.
- **REQ-05 (Metrics):** Giải quyết tại `metrics.py` (đo latency từng node).
- **REQ-06, 07, 08 (Bonus):** Giải quyết tại `streamlit_app.py`, `nodes.py` (Fan-out), và `report.py` (Mermaid).

### 2. Kiến trúc & Tech Stack
- **Core Engine:** `langgraph`, `langchain`, `python >= 3.11`
- **Database:** `sqlite3` (chế độ WAL bắt buộc để tránh lock và đảm bảo an toàn thread).
- **State Management:** Append-only cho `messages`, Overwrite cho `route_status`, Increment cho `attempt_count`.
- **UI & Output:** `streamlit` cho giao diện HITL, `typer` cho CLI commands.

### 3. Cấu trúc File & Ranh giới Module
```text
src/langgraph_agent_lab/
├── state.py       # Chỉ chứa định nghĩa schema, không chứa logic routing.
├── nodes.py       # Các hàm Python thuần (pure functions) nhận State trả về State dict. Không có side-effects ngoài Tool call.
├── routing.py     # Chỉ chứa các hàm conditional edge trả về string (tên node tiếp theo).
├── graph.py       # Nơi duy nhất import StateGraph, add_node, add_edge, compile().
├── persistence.py # Khởi tạo SqliteSaver với sqlite3.connect().
├── metrics.py     # Logic gom nhóm log và tính toán accuracy, latency.
└── report.py      # Đọc outputs/metrics.json và tự động gen reports/lab_report.md.
```

---

## PHẦN II: TASK GRAPH (SƠ ĐỒ CÔNG VIỆC)

```text
TIP-001: State & Scaffolding ──────────┐
    │                                  │
    ▼                                  │
TIP-002: Persistence (SQLite) ─────────┤
    │                                  │
    ▼                                  ▼
TIP-003: Core Nodes & Routing     TIP-007: Streamlit UI Setup
    │                                  │
    ├──► TIP-004: Parallel Fan-out     │
    │                                  │
    ├──► TIP-005: HITL Workflow ───────┤
    │                                  │
    ▼                                  ▼
TIP-006: Metrics Engine ───────────────┘
    │
    ▼
TIP-008: Verify & Report Gen
```

---

## PHẦN III: TASK INSTRUCTION PACKS (TIPS)
*Thợ thi công (Builder) PHẢI đọc và thực hiện chính xác theo từng TIP. Không được tự ý thay đổi kiến trúc. Tự test trước khi báo cáo hoàn thành.*

### TIP-001: State Schema & Scaffolding
* **ID:** TIP-001 | **Priority:** P0 | **Dependencies:** None | **Effort:** 30m
* **Context:** Làm việc tại `src/langgraph_agent_lab/state.py`.
* **Task:** Định nghĩa `State` TypedDict chuẩn bị cho toàn bộ workflow.
* **Specifications:**
  - `messages`: `Annotated[list, add_messages]`
  - `route_status`: `str` (lưu kết quả của classify node)
  - `attempt_count`: `int`
  - `latency_log`: `list` (để tracking REQ-05)
* **Acceptance Criteria:**
  - `Given` một State trống, `When` khởi tạo qua Graph, `Then` code không văng lỗi Type.
  - `Given` dict `{ "attempt_count": 1 }`, `When` update state, `Then` giá trị được overwrite chính xác.
* **Constraints:** State phải 100% JSON serializable để ghi vào SQLite.
* **Report Format:** Completion Report (Status, Files, Tests).

### TIP-002: Persistence Layer
* **ID:** TIP-002 | **Priority:** P1 | **Dependencies:** TIP-001 | **Effort:** 30m
* **Context:** Làm việc tại `persistence.py` và `graph.py`. Tài liệu yêu cầu `SqliteSaver`.
* **Task:** Cấu hình SQLite dạng WAL làm checkpointer mặc định.
* **Specifications:**
  - Viết hàm `get_checkpointer(db_path: str = "outputs/lab.db")`
  - Khởi tạo kết nối: `conn = sqlite3.connect(db_path, check_same_thread=False)`
  - Bật WAL: `conn.execute("PRAGMA journal_mode=WAL;")`
  - Trả về `SqliteSaver(conn)`
* **Acceptance Criteria:**
  - `Given` graph được compile với checkpointer, `When` chạy thử 1 node, `Then` file `outputs/lab.db` được tạo thành công.
* **Constraints:** Không dùng `MemorySaver` trong code production/chấm điểm.
* **Report Format:** Completion Report.

### TIP-003: Core Nodes & Routing
* **ID:** TIP-003 | **Priority:** P0 | **Dependencies:** TIP-002 | **Effort:** 60m
* **Context:** `nodes.py` và `routing.py`. Cốt lõi của workflow.
* **Task:** Code các node xử lý (intake, classify, answer, dead_letter) và logic định hướng.
* **Specifications:**
  - Node `classify`: phân tích tin nhắn, trả về `route_status` (simple, tool, risky, missing).
  - Định nghĩa logic `attempt_count` tăng lên 1 mỗi khi đi qua node `evaluate`.
  - Nếu `attempt_count >= config['max_attempts']`, route về `dead_letter`.
* **Acceptance Criteria:**
  - `Given` một scenario quá số lần retry, `When` route logic kích hoạt, `Then` nó buộc phải rẽ nhánh vào `dead_letter`.
* **Constraints:** Không dùng LLM trực tiếp trong router, router chỉ lấy giá trị từ state (pure function).
* **Report Format:** Completion Report.

### TIP-004: Parallel Fan-out (Bonus)
* **ID:** TIP-004 | **Priority:** P2 | **Dependencies:** TIP-003 | **Effort:** 45m
* **Context:** Tính năng gọi tool song song để tăng tốc độ.
* **Task:** Thiết kế node chạy đa luồng cho các công cụ tra cứu.
* **Specifications:**
  - Sử dụng ThreadPoolExecutor hoặc `RunnableParallel` của LangChain.
  - Khi state yêu cầu gọi nhiều tool, gọi đồng thời, gom kết quả (append list) trả về 1 lượt.
* **Acceptance Criteria:**
  - `Given` yêu cầu cần 2 tools, `When` node chạy, `Then` thời gian thực thi xấp xỉ tool chạy chậm nhất (không phải tổng 2 tool).
* **Constraints:** Quản lý error cẩn thận, 1 thread xịt không làm sập Graph.
* **Report Format:** Completion Report.

### TIP-005: HITL Workflow (Risky Action)
* **ID:** TIP-005 | **Priority:** P1 | **Dependencies:** TIP-003 | **Effort:** 45m
* **Context:** Node `approval`. Yêu cầu có sự xác nhận của người dùng.
* **Task:** Cài đặt `interrupt_before=["approval"]`.
* **Specifications:**
  - Đảm bảo luồng: `risky_action` -> GRAPH INTERRUPT -> Đợi input -> `approval` node update state -> Route.
  - Nếu user reject (update state = reject) -> Route thẳng sang `dead_letter`.
* **Acceptance Criteria:**
  - `Given` Graph bị pause tại `approval`, `When` user resume với trạng thái "rejected", `Then` Graph đi tới `dead_letter` và kết thúc.
* **Constraints:** Resume state cần có thread_id chính xác trong config.
* **Report Format:** Completion Report.

### TIP-006: Metrics Engine
* **ID:** TIP-006 | **Priority:** P1 | **Dependencies:** TIP-003 | **Effort:** 45m
* **Context:** `metrics.py`. Cần tính toán số liệu đo lường chất lượng.
* **Task:** Xây dựng logic tracking và xuất `outputs/metrics.json`.
* **Specifications:**
  - Tính `latency_ms` chi tiết từng node (dựa trên logs được nhét vào `latency_log` trong State).
  - Tính tổng số lần retry, tỷ lệ success rate.
  - Đảm bảo output khớp hoàn toàn với schema của `MetricsReport`.
* **Acceptance Criteria:**
  - `Given` file `scenarios.jsonl`, `When` chạy `make run-scenarios`, `Then` file `metrics.json` sinh ra hợp lệ và chứa latency thực tế.
* **Constraints:** Bắt lỗi json serializable cẩn thận.
* **Report Format:** Completion Report.

### TIP-007: Streamlit UI
* **ID:** TIP-007 | **Priority:** P2 | **Dependencies:** TIP-002, TIP-005 | **Effort:** 60m
* **Context:** `streamlit_app.py`. Mở rộng giao diện đồ họa.
* **Task:** Xây dựng Chat UI tích hợp LangGraph, có resume session và HITL.
* **Specifications:**
  - Sidebar: Nhập thread_id để load lại lịch sử từ SQLite.
  - Hiển thị pop-up/button khi Graph bị interrupt (HITL) để cho phép user Approve/Reject.
  - [Bonus] Render sơ đồ kiến trúc Mermaid của Graph hiện tại.
* **Acceptance Criteria:**
  - `Given` app đang chạy, `When` nhập thread_id cũ, `Then` toàn bộ lịch sử chat và state hiện ra đầy đủ.
* **Constraints:** Không làm thay đổi logic Graph cốt lõi.
* **Report Format:** Completion Report.

### TIP-008: Verify & Lab Report Generation
* **ID:** TIP-008 | **Priority:** P0 | **Dependencies:** Toàn bộ TIP trên | **Effort:** 30m
* **Context:** `report.py` và `Makefile`.
* **Task:** Chạy toàn bộ test, format báo cáo.
* **Specifications:**
  - Chạy test suite nghiệm thu (`make test`).
  - Viết script tự động thay thế các placeholder trong `reports/lab_report_template.md` bằng dữ liệu từ `metrics.json`.
* **Acceptance Criteria:**
  - `Given` dự án hoàn tất, `When` chạy `make grade-local`, `Then` pass toàn bộ.
  - `Given` lệnh report, `When` chạy xong, `Then` `lab_report.md` có đầy đủ bảng metrics và phân tích.
* **Constraints:** Report phải có phần "Improvement Ideas" và bằng chứng của phần Bonus.
* **Report Format:** Verify Report (thay cho Completion Report).
