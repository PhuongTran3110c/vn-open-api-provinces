# Parse Address API

## Tổng quan

API phân tích địa chỉ Việt Nam từ chuỗi text thành các thành phần có cấu trúc.

## API v1 - Parse Address (3 cấp)

**Endpoint:** `GET /api/v1/parse-address`

**Cấu trúc:** Tỉnh → Huyện → Xã + Đường

### Parameters:

-   `address` (required): Chuỗi địa chỉ cần phân tích

### Response:

```json
{
    "province": "Tỉnh Cao Bằng",
    "province_code": 4,
    "district": "Huyện Thạch An",
    "district_code": 53,
    "ward": "Xã Quang Trọng",
    "ward_code": 1813,
    "street": "456 haha"
}
```

### Ví dụ:

#### 1. Địa chỉ đầy đủ:

```bash
curl "http://127.0.0.1:8000/api/v1/parse-address?address=456%20haha,%20Xã%20Quang%20Trọng,%20Huyện%20Thạch%20An,%20Tỉnh%20Cao%20Bằng"
```

#### 2. Chỉ có tỉnh:

```bash
curl "http://127.0.0.1:8000/api/v1/parse-address?address=Tỉnh%20Cao%20Bằng"
```

Response:

```json
{
    "province": "Tỉnh Cao Bằng",
    "province_code": 4,
    "district": null,
    "district_code": null,
    "ward": null,
    "ward_code": null,
    "street": null
}
```

#### 3. Tỉnh + Huyện:

```bash
curl "http://127.0.0.1:8000/api/v1/parse-address?address=Huyện%20Thạch%20An,%20Cao%20Bằng"
```

---

## API v2 - Parse Address (2 cấp)

**Endpoint:** `GET /api/v2/parse-address`

**Cấu trúc:** Tỉnh → Xã + Đường (không có cấp Huyện)

### Parameters:

-   `address` (required): Chuỗi địa chỉ cần phân tích

### Response:

```json
{
    "province": "Tỉnh Cao Bằng",
    "province_code": 4,
    "ward": "Xã Quang Trọng",
    "ward_code": 1813,
    "street": "456 haha"
}
```

### Ví dụ:

#### 1. Địa chỉ đầy đủ:

```bash
curl "http://127.0.0.1:8000/api/v2/parse-address?address=456%20haha,%20Xã%20Quang%20Trọng,%20Tỉnh%20Cao%20Bằng"
```

#### 2. Chỉ có tỉnh:

```bash
curl "http://127.0.0.1:8000/api/v2/parse-address?address=Cao%20Bằng"
```

Response:

```json
{
    "province": "Tỉnh Cao Bằng",
    "province_code": 4,
    "ward": null,
    "ward_code": null,
    "street": null
}
```

---

## Tính năng

### ✅ Hỗ trợ nhiều định dạng:

-   Có dấu hoặc không dấu: "Hà Nội" = "Ha Noi"
-   Có hoặc không có tiền tố: "Tỉnh Cao Bằng" = "Cao Bằng"
-   Thứ tự linh hoạt: "Cao Bằng, Xã Quang Trọng" hoặc "Xã Quang Trọng, Cao Bằng"

### ✅ Phân tích thông minh:

-   Tự động nhận diện tỉnh/thành phố
-   Tự động nhận diện huyện/quận (v1)
-   Tự động nhận diện xã/phường
-   Tách riêng số nhà/tên đường

### ✅ Xử lý lỗi:

-   Trả về `null` cho các trường không tìm thấy
-   Không throw error nếu thiếu thông tin

---

## Test Script

Chạy test script để thử nghiệm:

```bash
# Cài đặt requests nếu chưa có
pip install requests

# Chạy test
python test_parse_address.py
```

---

## Use Cases

### 1. Form nhập địa chỉ

-   User nhập địa chỉ tự do
-   API parse ra các thành phần
-   Hiển thị suggestions/corrections

### 2. Validation địa chỉ

-   Kiểm tra địa chỉ có hợp lệ không
-   Lấy mã code để lưu database

### 3. Chuẩn hóa địa chỉ

-   Chuyển địa chỉ tự do thành cấu trúc chuẩn
-   Đồng nhất format địa chỉ

### 4. Import dữ liệu

-   Chuyển đổi địa chỉ từ Excel/CSV
-   Tự động map với database
