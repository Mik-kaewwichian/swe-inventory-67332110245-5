# Phase 3A — Debugging Evidence

**Reviewed module:** `assets-lab04-ai-coding-ux/discount.py`
**Tests:** `assets-lab04-ai-coding-ux/tests/test_discount.py`
**AI use:** AI-assisted diagnosis and editing; the changes were verified by rerunning the project tests.

## 1. Reproduce

รันจากโฟลเดอร์ `assets-lab04-ai-coding-ux`:

```powershell
python -m pytest -q
```

ผลก่อนแก้: **4 failed, 2 passed**

- `test_apply_discount_basic`: คาดหวัง `90.0` แต่ได้ `99.9`
- `test_bulk_total`: คาดหวัง `270.0` แต่ได้ `299.9`
- `test_average_price_empty`: เกิด `ZeroDivisionError`
- `test_cheapest_n`: คาดหวัง `[10.0, 20.0]` แต่ได้ `[20.0]`

การรันครั้งแรกจาก repository root เกิด `ModuleNotFoundError: No module named 'discount'` เพราะ test import โมดูลด้วยชื่อ `discount` แบบ local module; เปลี่ยนไปทำงานจากโฟลเดอร์โปรเจกต์ตามคำสั่งด้านบนแล้วจึง reproduce failure ของ test ได้

## 2. อ่าน traceback และ assertion

- ส่วนลดและยอดรวมล้มเหลวที่ assertion ใน `test_apply_discount_basic` และ `test_bulk_total`; actual values แสดงว่า function หัก `0.1` ออกจากยอด ไม่ได้คิด 10% ของราคา
- `test_average_price_empty` traceback ชี้ไปที่ `discount.py` บรรทัดคำนวณ `sum(prices) / len(prices)` โดย `len([]) == 0`
- `test_cheapest_n` assertion แสดงว่าผลลัพธ์ขาดรายการราคาต่ำสุด

## 3. สมมติฐาน

1. `apply_discount` คำนวณจำนวนส่วนลดผิดสูตร โดยใช้สัดส่วนส่วนลดแทนจำนวนเงินส่วนลด
2. `average_price` ไม่มีกรณีพิเศษสำหรับ list ว่างตามพฤติกรรมที่ test ระบุว่าต้องคืน `0.0`
3. `cheapest_n` เริ่ม slice ที่ index 1 ทำให้ข้ามรายการแรกหลังเรียงราคา

## 4. ยืนยัน root cause

ตรวจ implementation เทียบกับ input ใน test:

- ราคา `100` และส่วนลด `10%` ต้องคำนวณ `100 * (1 - 10 / 100) = 90`; โค้ดเดิมคำนวณ `100 - 10 / 100 = 99.9`
- เมื่อ `prices=[]`, `sum(prices) / len(prices)` กลายเป็น `0 / 0` จึงเกิด `ZeroDivisionError`
- `[50, 10, 30, 20]` เรียงแล้วเป็น `[10, 20, 30, 50]`; slice `[1:2]` คืน `[20]` จึงยืนยันว่าจุดเริ่ม index เป็นสาเหตุที่ละรายการถูกที่สุด

## 5. แก้และรันซ้ำ

แก้เฉพาะ root cause ใน `discount.py`:

- คำนวณราคาหลังส่วนลดด้วย `price * (1 - percent / 100)`; `bulk_total` ใช้ helper นี้อยู่แล้วจึงได้ผลถูกต้องโดยไม่ต้องเปลี่ยน interface
- คืน `0.0` เมื่อ `average_price` ได้ list ว่าง ตาม contract ที่ระบุใน test
- เปลี่ยน slice เป็น `ordered[:n]` เพื่อรวมรายการราคาถูกที่สุดตั้งแต่ตัวแรก

รันชุดทดสอบทั้งหมดอีกครั้งจากโฟลเดอร์โปรเจกต์:

```powershell
python -m pytest -q
```

ผลหลังแก้: **6 passed**.
