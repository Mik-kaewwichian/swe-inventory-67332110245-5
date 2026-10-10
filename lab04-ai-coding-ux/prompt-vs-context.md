
# Prompt Engineering vs. Context Engineering

โจทย์เดียวกันทั้งสองรอบ: เพิ่มการขายหลายรายการพร้อมกันให้กับ `Inventory` จาก Lab 03.

## รอบที่ 1 — Prompt สั้น

### Prompt

```text
เขียน function ลด stock หลายรายการพร้อมกันให้หน่อย
```

### ผลลัพธ์จาก AI

```python
def sell_many(inventory, orders):
    result = {}
    for name, amount in orders.items():
        result[name] = inventory.sell(name, amount)
    return result
```

### Review ผลลัพธ์

โค้ดสั้นและเรียก `sell()` ที่มีอยู่แล้ว แต่ยังไม่ตรงกับพฤติกรรมที่อาจต้องการสำหรับ batch:

- ถ้าขายรายการแรกสำเร็จแล้วรายการถัดไปมี stock ไม่พอ รายการแรกถูกหักไปแล้ว ไม่มี rollback
- ไม่ระบุ signature, exception, return contract หรือข้อจำกัดเรื่อง dependency และ thread safety
- ไม่ได้ยึดโครงสร้างหรือ interface เดิมอย่างชัดเจน

## รอบที่ 2 — Prompt พร้อม context

### Prompt

```text
ปรับปรุงคลาส Inventory ด้านล่าง โดยเพิ่มเมธอด
sell_many(orders: dict[str, int]) -> dict[str, int]
เพื่อขายสินค้าหลายรายการพร้อมกัน

โค้ดเดิมจาก inventory.py:

class InventoryItem:
    def __init__(self, name: str, quantity: int, price: float):
        if not name or not name.strip():
            raise ValueError("ชื่อสินค้าต้องไม่ว่างเปล่า")
        if quantity < 0:
            raise ValueError("จำนวนสินค้าต้องไม่ติดลบ")
        if price <= 0:
            raise ValueError("ราคาต้องมากกว่าศูนย์")
        self.name = name.strip()
        self.quantity = quantity
        self.price = price


class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}

    def add_item(self, name: str, quantity: int, price: float) -> InventoryItem:
        if name in self._items:
            raise ValueError(f"สินค้า '{name}' มีอยู่ในระบบแล้ว")
        item = InventoryItem(name, quantity, price)
        self._items[name] = item
        return item

    def restock(self, name: str, amount: int) -> int:
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่เติมต้องมากกว่าศูนย์")
        self._items[name].quantity += amount
        return self._items[name].quantity

    def sell(self, name: str, amount: int) -> int:
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
        if self._items[name].quantity < amount:
            raise ValueError(
                f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น "
                f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
            )
        self._items[name].quantity -= amount
        return self._items[name].quantity

    def get_total_value(self) -> float:
        return sum(
            item.quantity * item.price for item in self._items.values()
        )

ข้อกำหนด:
- คืน dict ที่ map ชื่อสินค้ากับจำนวนคงเหลือหลังขาย
- หากสินค้ารายการใดไม่มีในคลัง ให้ raise KeyError แบบเดียวกับ sell()
- หากจำนวนที่ขายไม่มากกว่าศูนย์ หรือ stock ไม่พอ ให้ raise ValueError
- ต้อง atomic: ถ้ารายการใดรายการหนึ่งไม่ผ่าน ต้องไม่หัก stock ของรายการใดเลย
- ห้ามใช้ library ภายนอก
- การเรียกเมธอดเปลี่ยน stock พร้อมกันจากหลาย thread ต้องไม่ทำให้ stock ติดลบหรือเกิดการขายซ้ำเกินจำนวน
- รักษา interface และพฤติกรรมเดิมของ add_item(), restock(), sell() และ get_total_value()

เกณฑ์ทดสอบที่ต้องผ่าน:
1. ขายหลายรายการที่มี stock พอ คืนยอดคงเหลือถูกต้องและลด stock ทุกชิ้น
2. ถ้ารายการที่สอง stock ไม่พอ ต้อง raise ValueError และ stock ของรายการแรกกับรายการที่สองคงเดิม
3. ถ้ามีชื่อสินค้าไม่อยู่ในคลัง ต้อง raise KeyError และไม่มี stock ใดเปลี่ยน
4. จำนวนขายเป็นศูนย์หรือติดลบต้อง raise ValueError และไม่มี stock ใดเปลี่ยน
5. การเรียกขายพร้อมกันต้องใช้กลไก synchronization ร่วมกับเมธอดที่เปลี่ยน stock

ส่งผลลัพธ์เป็นคลาส Inventory ฉบับเต็มที่ปรับแล้ว พร้อมอธิบายวิธีทำให้ batch atomic
และ thread-safe
```

### ผลลัพธ์จาก AI

```python
import threading


class InventoryItem:
    def __init__(self, name: str, quantity: int, price: float):
        if not name or not name.strip():
            raise ValueError("ชื่อสินค้าต้องไม่ว่างเปล่า")
        if quantity < 0:
            raise ValueError("จำนวนสินค้าต้องไม่ติดลบ")
        if price <= 0:
            raise ValueError("ราคาต้องมากกว่าศูนย์")
        self.name = name.strip()
        self.quantity = quantity
        self.price = price


class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}
        self._lock = threading.RLock()

    def add_item(self, name: str, quantity: int, price: float) -> InventoryItem:
        with self._lock:
            if name in self._items:
                raise ValueError(f"สินค้า '{name}' มีอยู่ในระบบแล้ว")
            item = InventoryItem(name, quantity, price)
            self._items[name] = item
            return item

    def restock(self, name: str, amount: int) -> int:
        with self._lock:
            if name not in self._items:
                raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
            if amount <= 0:
                raise ValueError("จำนวนที่เติมต้องมากกว่าศูนย์")
            self._items[name].quantity += amount
            return self._items[name].quantity

    def sell(self, name: str, amount: int) -> int:
        with self._lock:
            if name not in self._items:
                raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
            if amount <= 0:
                raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
            if self._items[name].quantity < amount:
                raise ValueError(
                    f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น "
                    f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
                )
            self._items[name].quantity -= amount
            return self._items[name].quantity

    def sell_many(self, orders: dict[str, int]) -> dict[str, int]:
        with self._lock:
            for name, amount in orders.items():
                if name not in self._items:
                    raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
                if amount <= 0:
                    raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
                if self._items[name].quantity < amount:
                    raise ValueError(
                        f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น "
                        f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
                    )

            return {
                name: self.sell(name, amount)
                for name, amount in orders.items()
            }

    def get_total_value(self) -> float:
        with self._lock:
            return sum(
                item.quantity * item.price for item in self._items.values()
            )
```

คำอธิบายผลลัพธ์: ตรวจสอบชื่อ จำนวน และ stock ของทุกรายการก่อนเริ่มหัก stock จึงไม่เกิด partial sale เมื่อ validation ล้มเหลว ใช้ `RLock` เดียวกันในเมธอดที่เปลี่ยน stock เพื่อป้องกัน concurrent mutation ระหว่างตรวจสอบกับการขาย และอนุญาตให้ `sell_many()` เรียก `sell()` ภายใต้ lock เดิมได้

## สรุปเปรียบเทียบ

รอบที่ 1 ให้โค้ดที่พอเห็นแนวทาง แต่เพียงวนเรียก `sell()` ทีละรายการ จึงอาจหัก stock ไปบางส่วนแล้วค่อย error และไม่ได้แสดงวิธีคง interface หรือป้องกัน race condition. รอบที่ 2 มีข้อมูลโค้ดจริง, signature และ exception ที่ต้องรักษา, เงื่อนไข atomic, ข้อจำกัด library, ความต้องการ thread safety และกรณีทดสอบที่ตรวจผลได้ จึงทำให้ AI สร้างโค้ดที่ตรวจสอบทุก order ก่อนแก้ state และประสาน lock กับการเปลี่ยน stock เดิม.

**ข้อสังเกตจากการ review:** ควรยืนยันพฤติกรรมที่ต้องการเมื่อ `orders` ว่าง และรัน test concurrency จริงก่อนนำไปใช้ การมี context ทำให้คำตอบตรงข้อกำหนดขึ้น แต่ไม่ได้แทนการรันทดสอบและ review โดยคน
