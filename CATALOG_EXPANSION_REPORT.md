# Catalog Expansion Report

## Summary

- Merchant count: 5000
- Area count: 11
- Category count: 24
- Top areas: 新街口 482, 老门东 482, 河西 482, 夫子庙 482, 鼓楼 482, 玄武湖 482, 江宁 482, 仙林 482, 百家湖 482, 奥体 482, 马鞍山 180
- Top categories: 火锅 308, 剧本杀 308, 电影院 308, 奶茶 280, 外卖 280, 江浙菜 198, 烧烤 198, 海鲜 198, 简餐 198, 本地小吃 198, KTV 186, 台球 180, 密室 180, 桌游 180, 展览 180, 按摩 180, 酒店 180, citywalk 180, 咖啡 180, 甜品 180, 冰淇淋 180, 蛋糕鲜花 180, 闪购零食 180, 酒吧 180

## Coverage Strategy

- The catalog was expanded with synthetic local-life Mock merchants, not scraped or API-fetched production data.
- Required areas include 新街口, 河西, 老门东, 夫子庙, 鼓楼, 玄武湖, 江宁, 仙林, 百家湖, 奥体, 马鞍山.
- Required categories include food, drinks, play, stay-in supply, birthday supply, massage, billiards, hotel, and citywalk.
- Ratings, price, queue time, duration, tags, group-deal, coupon, and feature fields vary across records to support filtering.

## Data-Driven Recommendation Evidence

- Planner output keeps `matching_meta` with candidate pool and selected merchant ids.
- Case 181 checks food candidates come from `data/merchants.json`, use a candidate pool larger than one, and change when constraints change.
- Case 182 checks script-game recommendations use script fields, player counts, duration, budget, and merchant ids.
- Case 183 checks stay-in recommendations avoid online movie as a core transaction item.

## Catalog Acceptance

- 179. phase2c catalog size: PASS
- 180. phase2c catalog coverage: PASS
- 181. phase2c data-driven food recommendation: PASS
- 182. phase2c data-driven script recommendation: PASS
- 183. phase2c no online movie core recommendation: PASS

## Mock Boundary

- All catalog entries are local Mock records.
- There is no live merchant inventory, ranking, price, queue, coupon, or booking integration.
- The purpose is to prove that the demo is selecting from a large inspectable data set rather than hardcoding one script.

## System Failures

- none
