# Mock Catalog Seed Notes

## Purpose

The expanded merchant catalog is synthetic local Mock data for the hackathon demo. It is used to prove that Plan A / Plan B can be selected from an inspectable data set instead of a single hardcoded path.

## Coverage

- Areas include 新街口, 河西, 老门东, 夫子庙, 鼓楼, 玄武湖, 江宁, 仙林, 百家湖, 奥体, 马鞍山, and a small 线上 bucket for non-core legacy content.
- Categories include dining, drinks, play, birthday supply, stay-in supply, massage, billiards, hotel, and scenic spots. User text such as "citywalk" is routed into the 景区 category.
- Each major area and category has enough records for budget, area, category, queue, duration, kid-safe, no-spicy, date, birthday, and stay-in filtering.

## Boundaries

- No production merchant data is used.
- No live price, queue, inventory, coupon, ranking, map, delivery, or booking service is called.
- All records should be treated as local Mock records for demo and acceptance only.
