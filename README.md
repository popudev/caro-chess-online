# Tên Dự Án

Cờ Caro (hay còn gọi là Gomoku hoặc Five in a Row) là một trò chơi chiến thuật hai người chơi, thường được chơi trên một bảng vuông chia ô giống như bàn cờ vua hoặc cờ vây.Cờ Caro từ lâu đã được học sinh chơi nhiều ở trường học trong những giờ giải trí. Trò chơi này rất phổ biến ở nhiều nước, đặc biệt là ở châu Á.
Với ý tưởng này, Nhóm 33 xây dựng một trò chơi Cờ Caro mã nguồn mở được phát triển dựa trên Python, với mục tiêu cho người dùng có thể ôn lại kỉ niệm và giải trí ngắn sau những giờ học tập làm việc mệt mỏi. Nhóm 33 sẽ sẵn sàng tiếp nhận góp ý từ thầy .

## Website giới thiệu

- Link: [Caro Game Website](https://carogamenhom33.surge.sh)

## Yêu Cầu Hệ Thống

- Python 3.x
- pip (Python package installer)

## Hướng Dẫn Cài Đặt

### Bước 1: Clone repository của bạn

```sh
git clone https://github.com/popudev/caro-chess-online.git
cd caro-chess-online
```

### Bước 2: Tạo môi trường ảo

- Trên Windows:

```sh
python -m venv .venv
.\.venv\Scripts\activate
```

- Trên macOS/Linux:

```sh
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt các thư viện cần thiết

```sh
pip install -r requirements.txt
```

### Bước 4: Chạy dự án

- Chạy server

```sh
cd server
python server.py
```

- Chạy client

```sh
cd client
python menu.py
```

## Báo cáo môn học

[Report OSSD Latex](https://www.overleaf.com/project/664397a2f4687cd554cced28)
