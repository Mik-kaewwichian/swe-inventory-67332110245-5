# Code Review — `InventoryService` AI-generated PR

**Review status:** AI-assisted after the reviewer completed an initial independent pass.
**Reviewed file:** `assets-lab04-ai-coding-ux/inventory_service.py`
**Scope:** Correctness, concurrency, security, and style. The PR source was not modified.

## Summary

พบข้อบกพร่องด้าน correctness และ concurrency ที่ควรแก้หรือกำหนด contract ให้ชัดก่อน merge ไม่พบประเด็น security ที่ยืนยันได้จากไฟล์นี้เพียงไฟล์เดียว

| # | เมธอด / บรรทัด | หมวด | ระดับ | สรุปปัญหา | กรณีที่ทำให้พัง |
|---|---|---|---|---|---|
| 1 | `sell_batch` / 18–22 | correctness | high | ขายทีละรายการโดยไม่มี atomicity หรือ rollback | A มี 5 ชิ้น, B มี 1 ชิ้น; สั่ง A=1, B=2 แล้ว A ถูกหักก่อน B ทำให้ error |
| 2 | `reserve` / 27–31 | correctness | high | การจองไม่กัน `sell_batch` จากการขาย stock ที่ถูกจองแล้ว | A มี 5 ชิ้น, จอง 5 แล้วขาย A=5 ได้ ทำให้ยอดจริงเป็น 0 แต่ยังมี reservation 5 |
| 3 | `reserve` / 29–30 | correctness | medium | ไม่ปฏิเสธจำนวนจองติดลบ | จอง A ด้วย `amount=-2` ทำให้ยอดจองติดลบและค่าคงเหลือที่คืนสูงกว่าจำนวนจริง |
| 4 | `reserve` / 27–30 | concurrency | medium | การอ่านและเขียนยอดจองไม่ใช้ lock จึงแข่งกันได้ | สอง thread จอง A=4 พร้อมกันเมื่อมี 5 ชิ้น ทั้งคู่เห็นยอดจองเดิม 0 และผลสุดท้ายบันทึกจองเพียง 4 แทน 8 |
| 5 | `items_in_price_range` / 38 | correctness | medium | เงื่อนไขเป็นช่วงเปิด ทั้งที่ docstring ระบุช่วงปิด `[low, high]` | ราคาเท่ากับ `low` หรือ `high` ถูกตัดออกจากผลลัพธ์ |
| 6 | `low_stock_report` / 47 | correctness | medium | ใช้ `<` แทน `<=` ตาม docstring | เมื่อ threshold=5 สินค้าที่เหลือ 5 ชิ้นไม่ถูกรายงาน |
| 7 | `concurrent_restock` / 54–56 | concurrency | high | อ่าน quantity ก่อนเข้า lock ทำให้เขียนทับผลของ thread อื่น | stock=10; สอง thread เติม 2 และ 3 อ่าน 10 ก่อน แล้วเขียน 12 และ 13 แทนยอดที่ควรเป็น 15 |
| 8 | `concurrent_restock` / 54–56 | concurrency | high | ล็อกนี้ไม่ประสานกับการเปลี่ยน stock ใน `Inventory` หรือ service instance อื่น | thread เติม stock อ่าน 5; อีก thread ขาย 1 ผ่าน `Inventory.sell()` เหลือ 4; thread เติมเขียน 7 ทับ ทำให้ stock สุดท้ายผิดจาก 6 |
| 9 | `concurrent_restock` / 56 | correctness | medium | เขียน stock โดยตรงและไม่ตรวจ `amount > 0` ตาม contract ของ `Inventory.restock` | เติม `amount=-3` ให้ A ที่มี 10 ชิ้น ทำให้ stock ลดเหลือ 7 โดยไม่ error |
| 10 | `average_unit_value` / 62–64 | correctness | medium | หารด้วยจำนวนชนิดสินค้า ไม่ใช่จำนวนชิ้นทั้งหมด | สินค้า A มี 10 ชิ้น ราคา 2; ค่าที่คืนคือ 20 แทนค่าเฉลี่ยต่อชิ้น 2 |
| 11 | `average_unit_value` / 63–64 | correctness | low | คลังว่างทำให้หารด้วยศูนย์ | เรียกเมธอดกับ `Inventory` ที่ไม่มีสินค้าแล้วเกิด `ZeroDivisionError`; ควรกำหนดและทดสอบพฤติกรรมของกรณีนี้ |

ระดับ **high** หมายถึงทำให้ข้อมูลคลังหรือการขายผิด/ไม่สอดคล้องได้โดยตรง; **medium** หมายถึงผลลัพธ์ไม่ตรง contract หรือกรณีใช้งานบางแบบให้ผลผิด; **low** หมายถึง edge case ที่ควรกำหนดพฤติกรรมก่อนใช้งาน ในกรณีคลังว่างของ `average_unit_value` โค้ดหารศูนย์แน่นอน แต่ควรตกลง contract ก่อนสรุปว่าค่าที่คาดหวังคืออะไร

## Review comments

### 1. `[sell_batch] correctness/high` — บรรทัด 18–22

**ปัญหา:** หัก stock ทีละรายการทันทีที่วนลูป จึงไม่ atomic
**กรณีที่ทำให้พัง:** A มี 5 ชิ้นและ B มี 1 ชิ้น; เรียก `sell_batch({"A": 1, "B": 2})` จะขาย A สำเร็จแล้ว `sell("B", 2)` raise `ValueError` ทำให้ A ถูกหักไปทั้งที่ batch ล้มเหลว
**ข้อเสนอ:** ตรวจสอบชื่อ จำนวน และ stock ของทุกรายการก่อนแก้ state แล้วทำการหักทั้งหมดภายใต้ synchronization เดียวกัน หรือใช้กลไก transaction/rollback เพื่อให้ทั้ง batch สำเร็จหรือล้มเหลวพร้อมกัน

### 2. `[reserve] correctness/high` — บรรทัด 27–31

**ปัญหา:** ยอดใน `_reserved` ไม่ถูกนำไปพิจารณาเมื่อขายผ่าน `sell_batch`
**กรณีที่ทำให้พัง:** A มี 5 ชิ้น; `reserve("A", 5)` จองครบแล้ว แต่ `sell_batch({"A": 5})` ยังขายได้ผ่าน `Inventory.sell()` ทำให้ stock จริงเป็น 0 ขณะที่ยังมี reservation 5
**ข้อเสนอ:** กำหนดกติกาการใช้/ยกเลิก reservation ให้ชัด และตรวจ available stock (`quantity - reserved`) ในทุกเส้นทางที่ขายหรือจองสินค้า

### 3. `[reserve] correctness/medium` — บรรทัด 29–30

**ปัญหา:** ไม่ปฏิเสธจำนวนจองติดลบ
**กรณีที่ทำให้พัง:** เมื่อ A มี 5 ชิ้นและเรียก `reserve("A", -2)`, เงื่อนไขผ่านและยอดจองกลายเป็น -2; เมธอดคืน 7 ซึ่งมากกว่า stock จริง
**ข้อเสนอ:** ปฏิเสธ `amount < 0` ด้วย `ValueError` ก่อนเปลี่ยน `_reserved` และกำหนดให้ชัดว่า `amount == 0` เป็น no-op ที่ยอมรับได้หรือเป็น input ที่ไม่ถูกต้อง

### 4. `[reserve] concurrency/medium` — บรรทัด 27–30

**ปัญหา:** อ่าน `already` และเขียน `_reserved[name]` โดยไม่มี lock ทำให้ reservation พร้อมกันสูญหาย
**กรณีที่ทำให้พัง:** A มี 5 ชิ้น; สอง thread เรียกจอง 4 ชิ้นพร้อมกัน ทั้งคู่สามารถอ่าน `already == 0`, ผ่านการตรวจ และเขียนยอด 4 ทับกัน แม้ผลรวมคำขอเป็น 8
**ข้อเสนอ:** ทำการอ่าน-ตรวจ-เขียน reservation เป็น critical section ภายใต้ lock ที่ใช้ร่วมกัน และประสานกับการขาย stock

### 5. `[items_in_price_range] correctness/medium` — บรรทัด 38

**ปัญหา:** docstring บอกว่ารวมขอบเขต `[low, high]` แต่ใช้ `low < price < high` ซึ่งไม่รวมราคาเท่าขอบเขต
**กรณีที่ทำให้พัง:** เรียกช่วง 10 ถึง 20; สินค้าราคา 10 หรือ 20 ไม่อยู่ในผลลัพธ์
**ข้อเสนอ:** ใช้เงื่อนไขที่รวมขอบเขตตาม contract หรือแก้ contract หากตั้งใจให้เป็นช่วงเปิด และเพิ่ม test สำหรับราคาที่เท่ากับขอบทั้งสอง

### 6. `[low_stock_report] correctness/medium` — บรรทัด 47

**ปัญหา:** docstring ระบุ stock ต่ำกว่าหรือเท่ากับ threshold แต่ implementation เช็กเฉพาะต่ำกว่า
**กรณีที่ทำให้พัง:** threshold เท่ากับ 5; สินค้าที่เหลือ 5 ชิ้นไม่ปรากฏในรายงาน ทั้งที่ควรถูกรายงาน
**ข้อเสนอ:** เปรียบเทียบแบบรวม threshold (`<=`) และเพิ่ม test ที่ stock เท่ากับ 5

### 7. `[concurrent_restock] concurrency/high` — บรรทัด 54–56

**ปัญหา:** อ่านค่า `current` ก่อนเข้าล็อก จึงยังมี lost update แม้การเขียนจะอยู่ใน lock
**กรณีที่ทำให้พัง:** stock เริ่มที่ 10; thread หนึ่งเติม 2 และอีก thread เติม 3; ทั้งคู่สามารถอ่าน 10 ก่อน แล้วเขียน 12 และ 13 ทำให้ผลสุดท้ายเป็น 12 หรือ 13 แทน 15
**ข้อเสนอ:** อ่าน quantity และปรับเพิ่มภายใน lock เดียวกันตลอดทั้ง read-modify-write หรือเรียก operation ที่ทำ atomic increment ภายใต้ synchronization ที่ทุก mutation ใช้ร่วมกัน

### 8. `[concurrent_restock] concurrency/high` — บรรทัด 54–56

**ปัญหา:** `_lock` เป็น lock เฉพาะ `InventoryService` instance นี้ แต่ `Inventory.sell()`/`restock()` และ `InventoryService` instance อื่นไม่ได้ใช้ lock เดียวกัน การล็อกเฉพาะเมธอดนี้จึงไม่ทำให้ stock ปลอด race กับ mutation เส้นทางอื่น
**กรณีที่ทำให้พัง:** stock เริ่มที่ 5; thread เติม 2 อ่าน current=5 แล้วพัก; อีก thread เรียก `Inventory.sell("A", 1)` ทำให้ stock เป็น 4; thread แรกเขียน 7 ทับ ทั้งที่ค่าที่ถูกต้องควรเป็น 6
**ข้อเสนอ:** ย้าย synchronization ไปไว้ที่ `Inventory` และให้ทุก operation ที่เปลี่ยน stock ใช้กลไกเดียวกัน หรือให้ service เรียก atomic public methods ที่ `Inventory` จัดเตรียมไว้

### 9. `[concurrent_restock] correctness/medium` — บรรทัด 56

**ปัญหา:** แก้ private state โดยตรง จึงข้าม validation ของ `Inventory.restock()` ที่ปฏิเสธจำนวนไม่เป็นบวก
**กรณีที่ทำให้พัง:** A มี 10 ชิ้น; `concurrent_restock("A", -3)` ลด stock เหลือ 7 แทนที่จะ raise `ValueError`
**ข้อเสนอ:** ใช้ public operation ที่ตรวจ input หรือเพิ่ม API สำหรับ restock แบบ atomic ที่รักษา validation เดิม

### 10. `[average_unit_value] correctness/medium` — บรรทัด 62–64

**ปัญหา:** `total_items` นับจำนวนชนิดสินค้า (`len(_items)`) แต่ docstring ต้องการค่าเฉลี่ยต่อชิ้น
**กรณีที่ทำให้พัง:** A มี 10 ชิ้น ราคา 2; มูลค่ารวม 20 หารด้วยชนิดสินค้า 1 ได้ 20 แทน 2 ต่อชิ้น
**ข้อเสนอ:** หารมูลค่ารวมด้วยผลรวม quantity ของสินค้าทั้งหมด และกำหนดพฤติกรรมเมื่อผลรวม quantity เป็นศูนย์

### 11. `[average_unit_value] correctness/low` — บรรทัด 63–64

**ปัญหา:** เมื่อไม่มีสินค้า `len(_items)` เป็นศูนย์และเกิด `ZeroDivisionError`
**กรณีที่ทำให้พัง:** สร้าง `Inventory` ว่างแล้วเรียก `average_unit_value()`
**ข้อเสนอ:** ระบุ contract สำหรับคลังว่าง เช่น คืน `0.0` หรือ raise exception ที่ตั้งใจไว้ และเพิ่ม test ให้ตรงกับ contract นั้น

## Security และ style

- **Security:** ไม่พบช่องโหว่ด้าน security ที่ยืนยันได้จากโค้ดส่วนนี้โดยตรง
- **Style/maintainability:** `inventory` ไม่มี type annotation และมีการเข้าถึง private attribute `_items` หลายจุด ทำให้ service ผูกกับ implementation ภายในของ `Inventory`; ควรพิจารณา public API ที่รองรับการ query/atomic mutation โดยไม่เปิดเผย dict ภายใน

## เปรียบเทียบกับ AI-assisted review

ข้อสังเกตจากการอ่านเองของผู้เรียนระบุความไม่ตรงกันของ `low_stock_report` กับคำอธิบาย และส่ง `reserve` กับ `sell_batch` มาเป็นจุดที่สงสัย; ระหว่างการสนทนา ผู้เรียนชี้กรณี `sell_batch` ทำงานทีละรายการ ส่วนการยอมรับจำนวนจองติดลบเป็นกรณีที่การตรวจแบบ AI-assisted ช่วยระบุเพิ่ม. การตรวจแบบ AI-assisted ยังเพิ่มกรณี reservation กับการขาย/การแข่งขันระหว่าง thread, ช่วงราคาที่ไม่รวมขอบ, lost update และ lock ที่ไม่ประสานกับ Inventory ใน `concurrent_restock`, การข้าม validation ของ `restock` และการคำนวณค่าเฉลี่ยผิด. ไม่ได้จัดประเด็นที่ยังต้องมี product contract เพิ่มเติมเป็น bug ที่ยืนยันแล้ว และไม่ได้พบ security bug ที่มีหลักฐานเพียงพอ.
