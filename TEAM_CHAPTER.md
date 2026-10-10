# TEAM_CHARTER.md

## สมาชิกและบทบาท

| ชื่อ | GitHub Username | บทบาท |
|เตชสิทธิ์ แก้ววิเชียร|Mik-kaewwichian||
|เตชสิทธิ์ แก้ววิเชียร | Mik-kaewwichian|  | Product Owner |
| Copilot| Mik-kaewwichian | Scrum Master / Developer |
| Copilot| Mik-kaewwichian | Developer |

(ถ้าทำคนเดียว ใส่สองแถว แถวแรกเป็นตัวเอง บทบาท Product Owner และ Developer
 แถวที่สองช่องชื่อใส่ชื่อ AI ที่ใช้ ช่อง GitHub Username ใส่ - บทบาท Scrum Master และ Developer ที่ประมาณ story point กับ review PR)

## Branching Strategy

ใช้ GitHub Flow:
- main branch ต้อง deploy ได้เสมอ ห้าม commit โดยตรง
- ทุก feature ใหม่ต้องสร้าง branch ชื่อ feat/<issue-number>-<short-name>
- ทุก PR ต้องผ่าน review ก่อน merge
  - ทำเป็นทีม: คนอื่นในทีมอย่างน้อย 1 คน review และ approve และคนกด merge ต้องไม่ใช่เจ้าของ PR
  - ทำคนเดียว: AI ในบท reviewer review ตามสี่มุมของขั้นที่ 8 วางผลลงใน PR และตอบทุกข้อก่อน merge

## WIP limit

- คอลัมน์ In Progress มีการ์ดพร้อมกันได้ไม่เกิน ___ ใบ (ทีมเริ่มที่จำนวนคนที่เขียนโค้ดในทีม ทำคนเดียวเริ่มที่ 1 ใบ)
- เมื่อการ์ดเต็ม WIP limit ห้ามลากการ์ดใหม่เข้ามา ให้ทำการ์ดเดิมให้เสร็จ หรือ review PR ที่ค้างใน In Review ก่อน
- ปรับ WIP limit ระหว่าง sprint ได้ แต่ต้องเขียนเหตุผลกำกับไว้ท้ายหัวข้อนี้ ไม่ใช่ปรับเพราะการ์ดล้น

## Sprint Goal (Sprint 1)

(กรอกหลังขั้นที่ 5)

## AI Usage Policy

- ใช้ AI ช่วยเขียน draft code และ draft commit message ได้
- ทุก commit message ที่ AI generate ต้องอ่านและแก้ให้ตรงกับ diff จริงก่อน commit
- ห้าม copy code จาก AI โดยไม่อ่านและทำความเข้าใจก่อน
- ใช้เฉพาะ AI ที่ไม่มีค่าใช้จ่าย ไม่บังคับซื้อ subscription
