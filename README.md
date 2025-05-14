# TTNT_MazeGame

Môn học: Trí tuệ nhân tạo

Đề tài: Trò chơi mê cung - Escape From The Forest

1. Mục tiêu

Đề tài "Escape From The Forest" nhằm xây dựng một trò chơi mê cung 2D đơn giản để:
- Áp dụng các thuật toán tìm kiếm (DFS, A*, AND-OR Search, Steepest-Ascent Hill-Climbing, Backtracking, Q-Learning) vào bài toán tìm đường từ điểm xuất phát đến đích.
- Trực quan hóa sự khác biệt về hiệu suất giữa các thuật toán thông qua thời gian đến đích (TimeToGoal) và số bước đi (Steps).
- Tạo môi trường thực hành cho sinh viên Công nghệ Thông tin và người yêu thích trí tuệ nhân tạo (AI), giúp hiểu cách AI hoạt động trong trò chơi.
- Đảm bảo giao diện thân thiện, hỗ trợ chọn bản đồ, thuật toán, hiển thị đường đi, và tích hợp âm thanh sinh động.

2. Nội dung
   
2.1 Uninformed Search

Các thuật toán Uninformed Search (tìm kiếm không có thông tin) không sử dụng heuristic, dựa vào duyệt toàn bộ không gian trạng thái theo chiến lược cố định. Trong đề tài sử dụng DFS (Depth-first search).

- Thành phần chính của bài toán tìm kiếm:
  
Không gian trạng thái: Mê cung là ma trận 2D (25x25 ô), với ô: 0 (tường), 1 (đường đi), 2 (xuất phát), 3 (đích).

Trạng thái ban đầu: Vị trí xuất phát (2).

Trạng thái mục tiêu: Vị trí đích (3).

Hành động: Di chuyển qua 4 hướng (lên, xuống, trái, phải) đến ô hợp lệ (1, 2, 3).

Chi phí: Mỗi bước di chuyển có chi phí 1, tổng chi phí là số bước.

Solution: Chuỗi các ô từ xuất phát đến đích, hiển thị bằng đường đỏ.

- Ảnh GIF:
  
- Ảnh so sánh hiệu suất trên 3 bản đồ:

![image](https://github.com/user-attachments/assets/ca9b547d-99ad-46be-b4f0-4f21eb61a916)

- Nhận xét hiệu suất:
  
Kém hiệu quả trên Map 1 (48.20 giây, 174 bước) và Map 2 (31.57 giây, 114 bước) do khám phá sâu, tạo đường đi dài.

Tốt hơn trên Map 3 (14.80 giây, 54 bước).

-> Phù hợp cho mê cung đơn giản, không hiệu quả với bản đồ phức tạp.

2.2 Informed Search

Các thuật toán Informed Search (tìm kiếm có thông tin) sử dụng heuristic để ưu tiên trạng thái gần đích. Trong đề tài sử dụng A*.

- Thành phần chính của bài toán tìm kiếm
  
Không gian trạng thái: Mê cung là ma trận 2D (25x25 ô), với ô: 0 (tường), 1 (đường đi), 2 (xuất phát), 3 (đích).

Trạng thái ban đầu: Vị trí xuất phát (2).

Trạng thái mục tiêu: Vị trí đích (3).

Hành động: Di chuyển qua 4 hướng (lên, xuống, trái, phải) đến ô hợp lệ (1, 2, 3).

Heuristic: Khoảng cách Manhattan ước lượng chi phí từ ô hiện tại đến đích.

Chi phí: Mỗi bước di chuyển có chi phí 1, tổng chi phí là số bước.

Solution: Đường đi ngắn nhất hoặc gần tối ưu, hiển thị bằng đường đỏ.

- Ảnh GIF

- Ảnh so sánh hiệu suất trên 3 bản đồ

![image](https://github.com/user-attachments/assets/24649885-f806-466b-88d8-ae4f75cb2a9e)

- Nhận xét hiệu suất

Hiệu suất vượt trội: Map 1 (14.80 giây, 54 bước), Map 2 (12.70 giây, 46 bước), Map 3 (12.60 giây, 46 bước).

Hàm heuristic Manhattan đảm bảo đường đi ngắn nhất, cân bằng chi phí thực tế và ước lượng.

-> Phù hợp cho mọi mê cung, đặc biệt là Map 1 (nhiều nhánh, ngõ cụt).

2.3 Local Search

Các thuật toán Local Search tập trung vào tối ưu hóa cục bộ, chọn trạng thái tốt nhất từ các trạng thái lân cận. Trong đề tài sử dụng Steepest-Ascent Hill-Climbing.

-Thành phần chính của bài toán tìm kiếm

Không gian trạng thái: Mê cung là ma trận 2D (25x25 ô), với ô: 0 (tường), 1 (đường đi), 2 (xuất phát), 3 (đích).

Trạng thái ban đầu: Vị trí xuất phát (2).

Trạng thái mục tiêu: Vị trí đích (3).

Hành động: Di chuyển qua 4 hướng (lên, xuống, trái, phải) đến ô hợp lệ (1, 2, 3).

Chi phí: Mỗi bước di chuyển có chi phí 1, tổng chi phí là số bước.

Heuristic: Khoảng cách Manhattan để chọn ô lân cận gần đích nhất.

Solution: Đường đi gần tối ưu, có thể không ngắn nhất do cực trị cục bộ.

- Ảnh GIF

- Ảnh so sánh hiệu suất trên 3 bản đồ

![image](https://github.com/user-attachments/assets/129afd05-b448-48eb-ae48-7d1757ef4933)

- Nhận xét hiệu suất

Hiệu quả trên Map 2 và Map 3 (12.60 giây, 46 bước) nhờ heuristic Manhattan.

Chậm trên Map 1 (31.77 giây, 114 bước) do kẹt ở cực trị cục bộ.

-> Phù hợp cho mê cung đơn giản, hạn chế trên bản đồ phức tạp như Map 1.

2.4 Reinforcement Learning

Các thuật toán Reinforcement Learning học hành động tối ưu qua thử nghiệm và phần thưởng. Trong đề tài sử dụng Q-Learning.

- Thành phần chính của bài toán tìm kiếm

Không gian trạng thái: Mê cung là ma trận 2D (25x25 ô), với ô: 0 (tường), 1 (đường đi), 2 (xuất phát), 3 (đích).

Trạng thái ban đầu: Vị trí xuất phát (2).

Trạng thái mục tiêu: Vị trí đích (3).

Hành động: Di chuyển qua 4 hướng (lên, xuống, trái, phải) đến ô hợp lệ (1, 2, 3).

Q-Table: Lưu giá trị hành động-trạng thái, cập nhật qua học tăng cường.

Solution: Đường đi tối ưu hoặc gần tối ưu sau huấn luyện, hiển thị bằng đường đỏ.

- Ảnh GIF

- Ảnh so sánh hiệu suất trên 3 bản đồ

![image](https://github.com/user-attachments/assets/7cbc46c2-e6f6-4c0d-981f-9379db054beb)

- Nhận xét hiệu suất

Hiệu suất cao: Map 1 (14.97 giây, 54 bước), Map 2 và Map 3 (12.60 giây, 46 bước).

Hiệu quả có thể do huấn luyện trước, cần kiểm tra trạng thái chưa huấn luyện.

-> Thích hợp để minh họa AI tự học, nhưng phụ thuộc vào quá trình huấn luyện.

2.5 Constraint Satisfaction Problems (CSPS)

CSPS giải bài toán bằng cách gán giá trị cho biến thỏa mãn ràng buộc. Trong đề tài sử dụng Backtracking kiểm tra tuần tự các đường đi khả thi, loại bỏ nhánh không thỏa mãn (ô tường hoặc đã thăm)

- Thành phần chính của bài toán tìm kiếm

Biến: Các ô trong mê cung.

Miền giá trị: 4 hướng di chuyển (lên, xuống, trái, phải).

Ràng buộc: Ô phải hợp lệ (1, 2, 3), không phải tường (0), và chưa được thăm.

Solution: Đường đi từ xuất phát đến đích thỏa mãn tất cả ràng buộc.

- Ảnh GIF

- Ảnh so sánh hiệu suất trên 3 bản đồ

![image](https://github.com/user-attachments/assets/579f8722-0de0-41de-9d42-c322829ed656)

- Nhận xét hiệu suất

Ổn định trên Map 1 (18.90 giây, 68 bước), nhưng chậm trên Map 2 (32.00 giây, 116 bước) và Map 3 (35.20 giây, 128 bước) do kiểm tra toàn bộ không gian trạng thái.

Kiểm tra toàn bộ không gian trạng thái đảm bảo tìm đường, nhưng không tối ưu thời gian.

-> Phù hợp để minh họa cách giải CSPS, nhưng kém hiệu quả so với Informed Search.

2.6 Complex Environments

Complex Environments liên quan đến môi trường có nhiều nhánh, ngõ cụt, hoặc yêu cầu xử lý trạng thái phức tạp. Trong đề tài, AND-OR Search phù hợp để mô phỏng tìm kiếm trong môi trường này, do khả năng xử lý nhánh quyết định đồng thời (cây AND-OR).

- Thành phần chính của bài toán tìm kiếm

Không gian trạng thái: Mê cung là ma trận 2D (25x25 ô), với ô: 0 (tường), 1 (đường đi), 2 (xuất phát), 3 (đích). Mê cung có nhiều nhánh và ngõ cụt (đặc biệt Map 1)

Trạng thái ban đầu: Vị trí xuất phát (2).

Trạng thái mục tiêu: Vị trí đích (3).

Hành động: Di chuyển qua 4 hướng (lên, xuống, trái, phải) đến ô hợp lệ (1, 2, 3). Di chuyển ngẫu nhiên hóa thứ tự để tránh ưu tiên cố định

Chi phí: Mỗi bước di chuyển có chi phí 1, tổng chi phí là số bước.

Solution: Đường đi khả thi, không nhất thiết tối ưu, hiển thị bằng đường đỏ.

- Ảnh GIF

- Ảnh so sánh hiệu suất trên 3 bản đồ

![image](https://github.com/user-attachments/assets/affc50e7-ab2a-41a8-975c-a87bd9093797)

- Nhận xét hiệu suất

Biến động lớn trên Map 1 (25.30–44.60 giây, 92–160 bước) do thiếu heuristic và xử lý kém trạng thái lặp.

Hiệu suất trung bình trên Map 2 (18.30 giây, 66.67 bước) và Map 3 (17.00 giây, 62 bước).

-> Phù hợp để minh họa tìm kiếm trong môi trường phức tạp, nhưng không hiệu quả thực tế.

2.7 Dữ liệu thử nghiệm:

Lưu vào game_records.xlsx với cột: DateTime, Algorithm, Maze, TimeToGoal, Steps.

Mỗi thuật toán chạy 3 lần trên mỗi bản đồ, tính trung bình để so sánh.

3. Kết luận

- Kết quả đạt được: 

Xây dựng trò chơi hoàn chỉnh, trò chơi mê cung 2D hoạt động ổn định, hỗ trợ chọn 3 bản đồ (Map 1, Map 2, Map 3) và 6 thuật toán (DFS, A*, AND-OR Search, Steepest-Ascent Hill-Climbing, Backtracking, Q-Learning).

Giao diện thân thiện, hiển thị trực quan mê cung, đường đi, và thời gian thực tế.

Âm thanh (nhạc nền, bước chân, thắng) tăng trải nghiệm người chơi.

Tích hợp thành công các thuật toán, phân loại theo Uninformed Search (DFS, Backtracking), Informed Search (A*), Local Search (Steepest-Ascent Hill-Climbing), Reinforcement Learning (Q-Learning), CSPS (Backtracking), và Complex Environments (AND-OR Search).

A* và Q-Learning vượt trội (12.60–14.97 giây, 46–54 bước), phù hợp mọi bản đồ.

DFS và Backtracking kém hiệu quả trên Map 1 (48.20 giây, 174 bước; 35.20 giây, 128 bước), minh họa duyệt sâu.

Xuất dữ liệu trò chơi ra file game_records.xlsx hỗ trợ đánh giá hiệu suất.

- Ứng dụng:

Cung cấp môi trường thực hành cho sinh viên và người học AI, giúp hiểu cách áp dụng thuật toán tìm kiếm trong trò chơi. Minh họa rõ vai trò của heuristic (A*, Steepest-Ascent Hill-Climbing) và học tăng cường (Q-Learning).

- Hạn chế:

AND-OR Search không ổn định trên Map 1, cần cơ chế tránh lặp trạng thái.

Q-Learning có thể phụ thuộc vào huấn luyện trước, cần thử nghiệm với trạng thái chưa huấn luyện.

Độ trễ di chuyển (300ms) làm tăng TimeToGoal, đặc biệt với thuật toán nhiều bước (DFS, Backtracking).

- Hướng phát triển:

Giảm độ trễ di chuyển để rút ngắn TimeToGoal.

Tối ưu AND-OR Search bằng cách giới hạn độ sâu hoặc tránh lặp.

Thêm bản đồ mê cung lớn hơn (ví dụ: 50x50) và phân tích độ lệch chuẩn để đánh giá tính ổn định.

