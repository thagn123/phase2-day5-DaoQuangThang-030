# Design Template

## Problem

Xây dựng một hệ thống AI (Research Assistant) có khả năng tự động xử lý các câu hỏi nghiên cứu phức tạp. Hệ thống cần thực hiện việc tìm kiếm thông tin từ các nguồn ngoài, tổng hợp, phân tích các điểm mạnh/yếu, và cuối cùng là viết ra một báo cáo toàn diện, có trích dẫn nguồn rõ ràng.

## Why multi-agent?

Một single-agent khó có thể làm tốt tất cả các vai trò cùng lúc (tìm kiếm, phân tích logic, và viết lách) do giới hạn về context window và khả năng tập trung (attention). Multi-agent cho phép:
1. **Specialization**: Mỗi agent đảm nhận một vai trò cụ thể với prompt được tối ưu hóa.
2. **Cross-checking (Debate/Critic)**: Có agent đóng vai trò kiểm duyệt để giảm thiểu hallucination.
3. **Pipeline Control**: Tách biệt luồng xử lý giúp dễ debug, quản lý lỗi (fallback) và đánh giá từng chặng (benchmark).

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối luồng chạy, quyết định agent nào tiếp theo và khi nào dừng | State hiện tại, Route history | Tên agent tiếp theo | Vòng lặp vô hạn (Infinite loop) |
| Researcher | Tìm kiếm và tóm tắt thông tin thô từ web/tài liệu | Query, max_sources | `research_notes`, `sources` | Lỗi API Search, không tìm thấy thông tin |
| Analyst | Phân tích sâu thông tin, tìm ra luận điểm chính và các lỗ hổng | Query, `research_notes` | `analysis_notes` | Phân tích nông, lặp lại thông tin |
| Writer | Tổng hợp thông tin từ notes để viết báo cáo cuối cùng | Query, Audience, `research_notes`, `analysis_notes` | `final_answer` | Quên trích dẫn nguồn, hallucination |
| Critic | Đánh giá và kiểm tra fact-check báo cáo của Writer | Query, `final_answer` | Phản hồi (Feedback) / Agent result | Đánh giá sai, vòng lặp giữa Writer-Critic |

## Shared state

- `request` (ResearchQuery): Đầu vào của người dùng. Giữ mục tiêu chung.
- `sources` (list): Lưu các tài liệu đã tìm được. Dùng để trích dẫn.
- `research_notes` (str): Tóm tắt thô từ Researcher. Làm đầu vào cho Analyst.
- `analysis_notes` (str): Phân tích logic từ Analyst. Làm đầu vào cho Writer.
- `final_answer` (str): Bài viết cuối. Đầu ra chính của hệ thống.
- `iteration` (int): Số bước đã chạy. Cần cho guardrail.
- `route_history` (list): Lịch sử gọi agent. Giúp Supervisor định tuyến.
- `agent_results` (list): Lưu trữ chi tiết log (chi phí, độ dài) của từng agent phục vụ benchmark.

## Routing policy

Luồng chạy graph được Supervisor điều hướng tuần tự nhưng có điều kiện:
`Start` -> `Supervisor`
- Nếu chưa có `research_notes` -> gọi `Researcher` -> `Supervisor`
- Nếu chưa có `analysis_notes` -> gọi `Analyst` -> `Supervisor`
- Nếu chưa có `final_answer` -> gọi `Writer` -> `Supervisor`
- Nếu chưa chạy `Critic` -> gọi `Critic` -> `Supervisor`
- Nếu đã đầy đủ -> trả về `END`

## Guardrails

- Max iterations: Giới hạn 5 lần lặp tại `SupervisorAgent` để ngăn chặn vòng lặp vô hạn.
- Timeout: Tích hợp timeout trong httpx call của `LLMClient`.
- Retry / Fallback: `SearchClient` tự động fallback sang mock data nếu gọi API Tavily thất bại.
- Validation: `CriticAgent` kiểm tra hallucination và logic sau khi có `final_answer`.

## Benchmark plan

- **Query**: "Research GraphRAG state-of-the-art"
- **Metrics**: 
  - Latency (Thời gian hoàn thành luồng).
  - Cost (Tổng chi phí USD cho tất cả các LLM calls).
  - Quality (Chất lượng đầu ra đánh giá qua rubric 1-10).
- **Expected outcome**: Multi-agent mất nhiều thời gian và chi phí hơn so với single-agent baseline, nhưng kết quả đầu ra có cấu trúc sâu sắc hơn, dẫn nguồn tin cậy hơn và vượt qua được bài kiểm tra hallucination của Critic.
