# แบบฝึกหัดส่งท้าย — Lab 04

**หมายเหตุ:** คำตอบนี้จัดทำแบบ AI-assisted โดยอ้างอิงโค้ดและบันทึกรีวิวใน repository ควรอ่านทวนและปรับสำนวนเป็นคำตอบของผู้เรียนก่อนส่ง

## 1. วิเคราะห์ bug ที่พบในส่วนที่ 2

### `sell_batch` ไม่ atomic — correctness/high

เมื่อขายสำเร็จบางรายการแล้วรายการถัดไปขายไม่ได้ เมธอดจะ raise exception แต่ไม่คืน stock รายการก่อนหน้า เช่น A มี 5 ชิ้น, B มี 1 ชิ้น แล้วเรียก `sell_batch({"A": 1, "B": 2})`; A จะเหลือ 4 แม้ batch ล้มเหลว Test ปกติที่ทดสอบเฉพาะกรณี stock พอทุกสินค้าจะผ่าน จึงไม่เปิดเผย partial update ต้องมี test ที่ทำให้รายการหลังล้มเหลวและตรวจว่า stock ทุกรายการคงเดิม

### `concurrent_restock` อ่าน stock ก่อนเข้า lock — concurrency/high

สอง thread อาจอ่าน stock เริ่มต้นเดียวกันแล้วเขียนค่าทับกัน เช่น stock 10 และมีคำขอเติม 2 กับ 3 ทั้งคู่เห็น 10 แล้วผลสุดท้ายอาจเป็น 12 หรือ 13 แทน 15 การทดสอบแบบ thread เดียวหรือทดสอบ concurrency โดยไม่บังคับจังหวะการสลับอาจไม่พบ race นี้ เพราะแต่ละรอบอาจบังเอิญทำงานต่อกันจนได้ผลถูกต้อง

## 2. ออกแบบ test สำหรับ bug concurrency

เลือกทดสอบ lost update ใน `concurrent_restock` โดยบังคับให้สอง thread อ่านค่าเดิมให้เสร็จก่อนที่จะปล่อยให้เข้า lock ด้วย `threading.Barrier` ใน test double ของ property `quantity`:

```python
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "assets-lab04-ai-coding-ux"))
from inventory import Inventory
from inventory_service import InventoryService


def test_concurrent_restock_does_not_lose_updates():
    barrier = Barrier(2)

    class CoordinatedItem:
        def __init__(self, quantity):
            self._quantity = quantity
            self._reads = 0
            self._read_lock = Lock()

        @property
        def quantity(self):
            with self._read_lock:
                self._reads += 1
                should_wait = self._reads <= 2
                value = self._quantity
            if should_wait:
                barrier.wait(timeout=3)
            return value

        @quantity.setter
        def quantity(self, value):
            self._quantity = value

    inventory = Inventory()
    inventory.add_item("A", 10, 1.0)
    inventory._items["A"] = CoordinatedItem(10)
    service = InventoryService(inventory)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(service.concurrent_restock, "A", 2)
        second = pool.submit(service.concurrent_restock, "A", 3)
        first.result(timeout=5)
        second.result(timeout=5)

    assert inventory._items["A"].quantity == 15
```

`Barrier` ทำให้การอ่านสองครั้งแรกได้ค่า 10 ก่อนที่ thread ใดจะเขียน เมื่อลองรัน test double นี้กับ implementation ปัจจุบัน ได้ stock สุดท้าย **12** แทน **15** จึงยืนยัน lost update ได้แบบทำซ้ำได้ ตัวอย่างนี้ใช้ private `_items` เพื่อควบคุมจังหวะอ่าน; ในโปรเจกต์จริงควรมี test seam หรือ API ที่เหมาะสมกว่า

## 3. ประเมิน AI reviewer

AI-assisted review ช่วยไล่ดูเมธอดครบชุดและเสนอกรณีทดสอบที่เจาะจง เช่น ราคาอยู่ตรงขอบช่วง, stock เท่ากับ threshold, reservation ที่ชนกับการขาย และ lost update จากการอ่านก่อน lock อีกทั้งช่วยแยกปัญหา correctness กับ concurrency และเสนอ review comment แบบมี input และแนวทางแก้

ข้อจำกัดคือรายการที่ AI พบยังต้องตรวจเทียบกับ contract จริง เช่น คลังว่างควรคืนค่าอะไรจาก `average_unit_value` และการรับ `amount == 0` ใน `reserve` ตั้งใจให้เป็น no-op หรือไม่ AI อาจจัดระดับความรุนแรงไม่ตรงกับบริบท หรือสรุปพฤติกรรมที่ยังไม่มี requirement ได้ จึงไม่ควรนำผลไปใช้โดยไม่ตรวจ execution และหลักฐาน

การแบ่งงานที่ปลอดภัยคือให้ AI ช่วยสร้าง checklist, วิเคราะห์เส้นทางข้อมูล และเสนอ edge cases; ให้คนตรวจ requirement, ยืนยันผลด้วย test หรือ synchronization ที่ควบคุมได้, พิจารณาความเสี่ยงเชิงธุรกิจ และเป็นผู้ตัดสินใจอนุมัติ PR

## 4. สะท้อนคิด (100–150 คำ)

การตรวจงานที่ AI สร้างสำคัญพอ ๆ กับการเขียนโค้ด เพราะโค้ดที่อ่านง่ายและรันได้ในกรณีทั่วไปยังซ่อนข้อผิดพลาดด้านข้อมูลและ concurrency ได้ ใน Lab นี้ `sell_batch` ดูตรงไปตรงมา แต่ถ้ารายการหลังขายไม่ได้ รายการแรกก็ถูกหัก stock ไปแล้ว ส่วน `concurrent_restock` มี lock แต่ยังอ่านค่า stock ก่อนเข้า lock จึงอาจเขียนทับการเติมของอีก thread ได้ การให้ AI review ช่วยเสนอกรณีขอบและชี้ตำแหน่งที่ควรตรวจ แต่ข้อเสนอของ AI ก็ต้องเทียบกับ requirement และพิสูจน์ด้วย test ที่ควบคุม input หรือจังหวะการทำงานจริง คนจึงต้องรับผิดชอบการยืนยัน root cause เลือกแนวแก้ที่รักษาพฤติกรรมระบบ และตรวจผลกระทบก่อน merge การพิมพ์โค้ดเร็วขึ้นไม่ช่วยหากเราอธิบายไม่ได้ว่าทำไมมันถูกต้อง

## ตรวจความพร้อมตาม Rubric

- **Persona และ UX synthesis:** มี Persona และ journey map แต่ระดับทักษะเทคโนโลยีไม่ได้ระบุจากข้อมูลจริง และข้อมูลสัมภาษณ์กับ Persona ควรตรวจให้สอดคล้องก่อนส่ง ห้ามเติมระดับทักษะโดยเดา
- **UI Mockup และ Accessibility:** มี mockup สองหน้าและ checklist; ลำดับ Tab ตรวจยืนยันได้จาก UI จริงเมื่อพัฒนาแล้วเท่านั้น
- **Prompt และ Context Engineering:** มี prompt สองรอบ แนบ interface เดิมและเกณฑ์ทดสอบ พร้อมสรุปความต่าง
- **Code Review:** มี review comments และตารางจัดหมวด แต่ผลเป็น AI-assisted; ผู้เรียนควรตรวจซ้ำกับ source และปรับเป็นเสียงของตน
- **Debugging:** มี failure ก่อนแก้, สมมติฐาน, การยืนยัน root cause และ test ผ่านหลังแก้; มี commit แยกตาม root cause
