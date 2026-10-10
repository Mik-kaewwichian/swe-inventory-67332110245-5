# Test Gap — AI-generated `sell` tests

**AI prompt:** “ช่วยเขียน pytest unit test สำหรับเมธอด sell ของ class Inventory ให้หน่อย”

## Test gap table

| กรณีที่ AI ให้มา | กรณีที่ขาด | test ที่เราเขียนเสริม |
|---|---|---|
| ขายจำนวนปกติแล้ว stock ลดลงตามจำนวนที่ขาย | ขายเท่ากับ stock ทั้งหมด และต้องเหลือศูนย์พอดี | `test_sell_all_remaining_stock_leaves_zero` |
| ขายจำนวนปกติแล้ว stock ลดลงตามจำนวนที่ขาย | จำนวนขายเป็นศูนย์ และ stock ต้องไม่เปลี่ยน | `test_sell_zero_amount_is_rejected_without_changing_stock` |
| ขายจำนวนปกติแล้ว stock ลดลงตามจำนวนที่ขาย | จำนวนขายติดลบ และ stock ต้องไม่เปลี่ยน | `test_sell_negative_amount_is_rejected_without_changing_stock` |
| ขายจำนวนปกติแล้ว stock ลดลงตามจำนวนที่ขาย | ขายเกินยอดคงเหลือ ต้องถูกปฏิเสธและ stock ต้องคงเดิม | `test_sell_more_than_available_is_rejected_without_changing_stock` |
| ขายจำนวนปกติแล้ว stock ลดลงตามจำนวนที่ขาย | สินค้าไม่มีในคลัง ต้องได้ `KeyError` ที่บอกชื่อสินค้า | `test_sell_unknown_item_raises_key_error_with_item_name` |
| ขายจำนวนปกติแล้ว stock ลดลงตามจำนวนที่ขาย | จำนวนเป็นทศนิยม ต้องไม่ถูกยอมรับเป็นจำนวนสินค้าแบบเศษชิ้น | `test_sell_fractional_amount_is_rejected_without_changing_stock` |
| ขายจำนวนปกติแล้ว stock ลดลงตามจำนวนที่ขาย | จำนวนเป็นข้อความ ต้องได้ error ที่ชัดเจนและ stock ไม่เปลี่ยน | `test_sell_text_amount_is_rejected_without_changing_stock` |

## ขอบเขตและผล

ตัวอย่าง “AI ให้มา” ในตารางเป็น test ปกติหนึ่งกรณีที่ร่างจาก prompt ข้างต้น ไม่ใช่ผล test ที่มีอยู่เดิมใน repository ก่อนเพิ่ม test-gap. Test เสริมครอบคลุมค่าขอบ, invalid amount, error path และชนิดข้อมูลตามโจทย์. Test ชนิดข้อมูลกำหนดให้ amount ที่ไม่ใช่จำนวนเต็ม raise `TypeError`; test นี้ใช้ตรวจ contract ที่เพิ่มให้ `sell` โดยตรง
