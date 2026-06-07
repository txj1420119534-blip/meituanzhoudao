# Acceptance Report

- Total cases: 147
- Passed: 147
- Failed: 0
- Pass rate: 147/147 (100.0%)
- `python acceptance_check.py` stable exit: YES
- `python acceptance_check.py --quick` passed: YES
- Final zip POSIX paths: YES
- Runner IO mode: result-file-first subprocess protocol; stdout/stderr temp files are diagnostics only
- Runner completion rule: valid `.result.json` ends the case; lingering child receives a short grace period then kill
- System checks isolated: YES; legacy system cases 93/94/95 are not duplicated in quick/full case lists
- Old request defaults leak into UI/session public summary: NO
- Phase 2A can enter Phase 2B: YES
- Phase 2B rescue cases passed: 5/5
- Phase 2B vote cases passed: 6/6
- Phase 2B booking cases passed: 7/7
- Phase 2B checkout cases passed: 7/7
- Phase 2B support cases passed: 9/9
- Phase 2B add-on cases passed: 9/9
- Phase 2B final integration cases passed: 8/8
- Phase 2C workflow rebuild cases passed: 11/11
- Phase 2C polish/catalog cases passed: 16/16
- Phase 2C browser/deploy cases passed: 9/9
- Phase 2C user-flow patch cases passed: 22/22
- Phase 2C natural intent coordination cases passed: 18/18
- Garbled user-visible data remains: NO
- Deliverable document encoding check passed: YES
- Supported success cases: 143
- Graceful unavailable cases: 0
- Needs clarification cases: 4
- API smoke passed: YES
- session_id isolation passed: YES
- Security scan passed: YES

## System Checks
- PASSED: py_compile, module runs, no-key fallback, damaged data fallback, data integrity, document encoding, API smoke, security scan

## Case Results

### 6. coffee sit awhile - PASS

- 输入：`只想找个咖啡店坐一会儿`
- 解析字段：`{"scene": "addon_only", "primary_intent": "coffee", "main_role": "ADDON", "requested_categories": ["咖啡"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "15:00", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "咖啡", "confirmed_fields": {"party_size": null, "start_time": "15:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "budget_per_person", "transport"], "sequence": [{"role": "ADDON", "category": "咖啡", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 咖啡 | ¥28 | 0.5h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：1.97s
- 是否通过：PASS
- 失败原因：无

### 63. regression period milk tea - PASS

- 输入：`我生理期，想喝点热的不要太甜的奶茶`
- 解析字段：`{"scene": "addon_only", "primary_intent": "milk_tea", "main_role": "ADDON", "requested_categories": ["奶茶"], "negative_intents": ["not_too_sweet", "no_ice"], "safety_flags": ["not_too_sweet", "cannot_ice", "body_uncomfortable"], "drink_preferences": {"sugar_level": "low", "ice_level": "hot", "hot_required": true}, "party_size": null, "start_time": "19:00", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "奶茶", "confirmed_fields": {"party_size": null, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "budget_per_person", "transport"], "sequence": [{"role": "ADDON", "category": "奶茶", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 奶茶 | ¥23 | 0.3h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：1.82s
- 是否通过：PASS
- 失败原因：无

### 64. regression movie no meal - PASS

- 输入：`今天晚上想看电影，不想吃饭`
- 解析字段：`{"scene": "play_only", "primary_intent": "movie", "main_role": "PLAY", "requested_categories": ["电影院"], "negative_intents": ["no_meal"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "19:30", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "电影院", "confirmed_fields": {"party_size": null, "start_time": "19:30", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "budget_per_person", "transport"], "sequence": [{"role": "PLAY", "category": "电影院", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 电影院 | ¥85 | 2.2h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.08s
- 是否通过：PASS
- 失败原因：无

### 65. phase2a broad food no itinerary - PASS

- 输入：`我想吃点什么`
- 解析字段：`{"scene": "food_only", "primary_intent": "food_discovery", "main_role": "EAT", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": null, "budget_per_person": null, "cuisine_preference": "any", "transport": "unknown", "confidence": 0.62, "missing_fields": ["home_area", "start_time", "budget_per_person"], "intent_frame_public": {"goal_summary": "想找点吃的", "confirmed_fields": {"party_size": null, "start_time": null, "end_time": null, "duration_minutes": null, "home_area": null, "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "unknown", "home_area": "unknown", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": ["party_size", "start_time", "duration_minutes", "home_area", "budget_per_person", "transport"], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`needs_clarification`
- 是否触发追问：`True`
- 是否已补全进入规划：`False`
- 主方案摘要：无方案
- 可选加购摘要：无
- 预约状态：mode=needs_clarification executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：1.01s
- 是否通过：PASS
- 失败原因：无

### 66. phase2a rest support no itinerary - PASS

- 输入：`我想睡会`
- 解析字段：`{"scene": "friends_out", "primary_intent": "rest", "main_role": "REST", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": null, "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.35, "missing_fields": ["at_home_or_outside"], "intent_frame_public": {"goal_summary": "想先休息一下", "confirmed_fields": {"party_size": null, "start_time": null, "end_time": null, "duration_minutes": null, "home_area": null, "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "unknown", "home_area": "unknown", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "start_time", "duration_minutes", "home_area", "budget_per_person", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：无方案
- 可选加购摘要：无
- 预约状态：mode=rest_support executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.86s
- 是否通过：PASS
- 失败原因：无

### 67. phase2a broad outing choice cards - PASS

- 输入：`我想和同学出去玩`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": null, "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.4, "missing_fields": ["activity_choice"], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": null, "start_time": null, "end_time": null, "duration_minutes": null, "home_area": null, "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "unknown", "home_area": "unknown", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "start_time", "duration_minutes", "home_area", "budget_per_person", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：无方案
- 可选加购摘要：无
- 预约状态：mode=category_choices executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.81s
- 是否通过：PASS
- 失败原因：无

### 68. phase2a script then meal itinerary - PASS

- 输入：`想打个本，再去吃个饭`
- 解析字段：`{"scene": "friends_out", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 180, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "unknown", "confidence": 0.92, "missing_fields": [], "script_style_choices": ["欢乐本"], "intent_frame_public": {"goal_summary": "剧本杀，再吃饭", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null, "script_style": "欢乐本"}, "field_sources": {"party_size": "user_answer", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default", "duration_minutes": "user_answer", "script_style": "user_answer"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 剧本杀 / 火锅 | ¥343 | 8.9h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.75s
- 是否通过：PASS
- 失败原因：无

### 69. phase2a script single closed itinerary - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.44s
- 是否通过：PASS
- 失败原因：无

### 70. phase2a 2h movie no forced meal - PASS

- 输入：`1个人19:00想出去玩2小时，看个电影，新街口，人均100`
- 解析字段：`{"scene": "play_only", "primary_intent": "movie", "main_role": "PLAY", "requested_categories": ["电影院"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 1, "start_time": "19:00", "budget_per_person": 100, "cuisine_preference": null, "transport": "unknown", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "电影院", "confirmed_fields": {"party_size": 1, "start_time": "19:00", "end_time": null, "duration_minutes": 120, "home_area": "新街口", "friend_areas": [], "budget_per_person": 100, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "电影院", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 电影院 | ¥85 | 2.2h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.19s
- 是否通过：PASS
- 失败原因：无

### 83. cleanup refined home_area updates origin - PASS

- 输入：`想打个本，再去吃个饭`
- 解析字段：`{"scene": "friends_out", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 180, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "unknown", "confidence": 0.92, "missing_fields": [], "script_style_choices": ["欢乐本"], "intent_frame_public": {"goal_summary": "剧本杀，再吃饭", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null, "script_style": "欢乐本"}, "field_sources": {"party_size": "user_answer", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default", "duration_minutes": "user_answer", "script_style": "user_answer"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 火锅 | ¥343 | 8.9h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.65s
- 是否通过：PASS
- 失败原因：无

### 84. cleanup no internal default after broad input - PASS

- 输入：`我想吃点什么`
- 解析字段：`{"scene": "food_only", "primary_intent": "food_discovery", "main_role": "EAT", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": null, "budget_per_person": null, "cuisine_preference": "any", "transport": "unknown", "confidence": 0.62, "missing_fields": ["home_area", "start_time", "budget_per_person"], "intent_frame_public": {"goal_summary": "想找点吃的", "confirmed_fields": {"party_size": null, "start_time": null, "end_time": null, "duration_minutes": null, "home_area": null, "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "unknown", "home_area": "unknown", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": ["party_size", "start_time", "duration_minutes", "home_area", "budget_per_person", "transport"], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`needs_clarification`
- 是否触发追问：`True`
- 是否已补全进入规划：`False`
- 主方案摘要：无方案
- 可选加购摘要：无
- 预约状态：mode=needs_clarification executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.81s
- 是否通过：PASS
- 失败原因：无

### 85. cleanup script then meal explicit sources - PASS

- 输入：`想打个本，再去吃个饭`
- 解析字段：`{"scene": "friends_out", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 180, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "unknown", "confidence": 0.92, "missing_fields": [], "script_style_choices": ["欢乐本"], "intent_frame_public": {"goal_summary": "剧本杀，再吃饭", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null, "script_style": "欢乐本"}, "field_sources": {"party_size": "user_answer", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default", "duration_minutes": "user_answer", "script_style": "user_answer"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 火锅 | ¥343 | 8.9h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：5.12s
- 是否通过：PASS
- 失败原因：无

### 86. cleanup movie 5h meal not explicit - PASS

- 输入：`1个人19:00想出去玩5小时，看个电影，新街口，人均150`
- 解析字段：`{"scene": "play_only", "primary_intent": "movie", "main_role": "PLAY", "requested_categories": ["电影院"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 1, "start_time": "19:00", "budget_per_person": 150, "cuisine_preference": null, "transport": "unknown", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "电影院", "confirmed_fields": {"party_size": 1, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "电影院", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 电影院 | ¥85 | 2.2h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.03s
- 是否通过：PASS
- 失败原因：无

### 87. cleanup price totals nonzero - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.49s
- 是否通过：PASS
- 失败原因：无

### 88. cleanup stay_in no online movie merchant - PASS

- 输入：`我今天不想出门，就想宅家看点东西，点点吃的`
- 解析字段：`{"scene": "stay_in", "primary_intent": "stay_in", "main_role": "STAYIN", "requested_categories": ["外卖"], "negative_intents": ["no_outdoor"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "20:00", "budget_per_person": 120, "cuisine_preference": null, "transport": "unknown", "confidence": 0.74, "missing_fields": [], "intent_frame_public": {"goal_summary": "宅家休息和外卖补给", "confirmed_fields": {"party_size": null, "start_time": "20:00", "end_time": null, "duration_minutes": null, "home_area": "线上", "friend_areas": [], "budget_per_person": 120, "transport": "unknown", "dine_mode": "delivery", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "planning_default", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "explicit_text", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes"], "sequence": [{"role": "STAYIN", "category": "外卖", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 外卖 | ¥44 | 0.7h
- 可选加购摘要：optional=老门东外卖店24(外卖); 奥体闪购零食店12(闪购零食)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.13s
- 是否通过：PASS
- 失败原因：无

### 89. cleanup support API TestClient - PASS

- 输入：`support api`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.69s
- 是否通过：PASS
- 失败原因：无

### 90. cleanup unknown origin no fake transit - PASS

- 输入：`今天晚上想看电影，不想吃饭`
- 解析字段：`{"scene": "play_only", "primary_intent": "movie", "main_role": "PLAY", "requested_categories": ["电影院"], "negative_intents": ["no_meal"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "19:30", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "电影院", "confirmed_fields": {"party_size": null, "start_time": "19:30", "end_time": null, "duration_minutes": null, "home_area": null, "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "unknown", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "home_area", "budget_per_person", "transport"], "sequence": [{"role": "PLAY", "category": "电影院", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 电影院 | ¥85 | 2.2h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.19s
- 是否通过：PASS
- 失败原因：无

### 91. cleanup known origin transit and return - PASS

- 输入：`想打个本，再去吃个饭`
- 解析字段：`{"scene": "friends_out", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 180, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "unknown", "confidence": 0.92, "missing_fields": [], "script_style_choices": ["欢乐本"], "intent_frame_public": {"goal_summary": "剧本杀，再吃饭", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null, "script_style": "欢乐本"}, "field_sources": {"party_size": "user_answer", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default", "duration_minutes": "user_answer", "script_style": "user_answer"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 火锅 | ¥343 | 8.9h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：5.06s
- 是否通过：PASS
- 失败原因：无

### 92. cleanup segment coupon summary nonzero - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.64s
- 是否通过：PASS
- 失败原因：无

### 96. microfix positive movie then meal retained - PASS

- 输入：`4个人21:00先看电影再吃饭，公共交通，新街口，人均150，2小时`
- 解析字段：`{"scene": "friends_out", "primary_intent": "movie", "main_role": "PLAY", "requested_categories": ["电影院"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "21:00", "budget_per_person": 150, "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "电影院，再吃饭", "confirmed_fields": {"party_size": 4, "start_time": "21:00", "end_time": null, "duration_minutes": 120, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "电影院", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 电影院 / 简餐 | ¥124 | 3.1h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.5s
- 是否通过：PASS
- 失败原因：无

### 97. phase2b rescue restaurant segment only - PASS

- 输入：`4个朋友今天18:00想先看展再吃饭，人均180，新街口，公共交通，4小时`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "PLAY", "requested_categories": ["展览"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 180, "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "展览", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 展览 / 江浙菜 | ¥153 | 3.1h
- 可选加购摘要：optional=顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=selected executed=False bookings=0 share=yes
- 异常重排结果：restaurant | 原「新街口江浙菜店14」已满座。已就近换到 新街口 的「新街口江浙菜店06」（评分 4.8），其它节点不动，人均变为 ¥155，仍在预算内。 | needs_user_confirm=False
- 单用例耗时：4.95s
- 是否通过：PASS
- 失败原因：无

### 98. phase2b rescue activity soldout segment only - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=yes
- 异常重排结果：activity | 原「新街口剧本杀店08」门票已售罄。已就近换到 新街口 的「新街口剧本杀店25」（评分 4.8），其它节点不动，人均变为 ¥112，仍在预算内。 | needs_user_confirm=False
- 单用例耗时：4.04s
- 是否通过：PASS
- 失败原因：无

### 99. phase2b rescue friend late shifts itinerary - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=yes
- 异常重排结果：time | 收到反馈「时间太赶」。已把整条行程顺延 60 分钟——出发从 19:00 改到 20:00，活动和餐厅原样保留，总时长不变。 | needs_user_confirm=False
- 单用例耗时：4.14s
- 是否通过：PASS
- 失败原因：无

### 100. phase2b rescue frontend entry - PASS

- 输入：`frontend static rescue check`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：frontend check
- 异常重排结果：frontend check
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 101. phase2b rescue no global reset - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=yes
- 异常重排结果：activity | 原「新街口剧本杀店08」门票已售罄。已就近换到 新街口 的「新街口剧本杀店25」（评分 4.8），其它节点不动，人均变为 ¥112，仍在预算内。 | needs_user_confirm=False
- 单用例耗时：4.05s
- 是否通过：PASS
- 失败原因：无

### 102. phase2b vote room create - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.19s
- 是否通过：PASS
- 失败原因：无

### 103. phase2b normal vote tally and confirm - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.44s
- 是否通过：PASS
- 失败原因：无

### 104. phase2b vote no spicy replans restaurant only - PASS

- 输入：`4个朋友今天18:00想先看展再吃饭，人均180，新街口，公共交通，4小时`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "PLAY", "requested_categories": ["展览"], "negative_intents": [], "safety_flags": ["no_spicy"], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 180, "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "展览", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 展览 / 江浙菜 | ¥153 | 3.1h
- 可选加购摘要：optional=顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=selected executed=False bookings=0 share=yes
- 异常重排结果：restaurant | 原「新街口江浙菜店14」已满座。已就近换到 新街口 的「新街口江浙菜店06」（评分 4.8），其它节点不动，人均变为 ¥155，仍在预算内。 | needs_user_confirm=False
- 单用例耗时：4.9s
- 是否通过：PASS
- 失败原因：无

### 105. phase2b vote played-before replans activity only - PASS

- 输入：`4个朋友今天18:00想先看展再吃饭，人均180，新街口，公共交通，4小时`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "PLAY", "requested_categories": ["展览"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 180, "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "展览", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 展览 / 江浙菜 | ¥153 | 3.1h
- 可选加购摘要：optional=顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=selected executed=False bookings=0 share=yes
- 异常重排结果：activity | 原「新街口展览店10」门票已售罄。已就近换到 新街口 的「新街口展览店18」（评分 4.3），其它节点不动，人均变为 ¥151，仍在预算内。 | needs_user_confirm=False
- 单用例耗时：5.51s
- 是否通过：PASS
- 失败原因：无

### 106. phase2b vote late 30 shifts timeline - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=yes
- 异常重排结果：time | 收到反馈「时间太赶」。已把整条行程顺延 30 分钟——出发从 19:00 改到 19:30，活动和餐厅原样保留，总时长不变。 | needs_user_confirm=False
- 单用例耗时：4.2s
- 是否通过：PASS
- 失败原因：无

### 107. phase2b vote session isolation - PASS

- 输入：`vote session isolation`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：vote session isolation
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：5.57s
- 是否通过：PASS
- 失败原因：无

### 108. phase2b booking review after selected plan - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：booking review after selected plan
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.54s
- 是否通过：PASS
- 失败原因：无

### 109. phase2b vote confirm does not auto book - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.23s
- 是否通过：PASS
- 失败原因：无

### 110. phase2b restaurant booking card - PASS

- 输入：`4个朋友今天18:00想先看展再吃饭，人均180，新街口，公共交通，4小时`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "PLAY", "requested_categories": ["展览"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 180, "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "展览", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：restaurant booking card
- 可选加购摘要：optional=顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.24s
- 是否通过：PASS
- 失败原因：无

### 111. phase2b booking time edit shifts later segments - PASS

- 输入：`4个朋友今天18:00想先看展再吃饭，人均180，新街口，公共交通，4小时`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "PLAY", "requested_categories": ["展览"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 180, "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "展览", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：booking time edit shifts later segments
- 可选加购摘要：optional=顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=booking_review executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.6s
- 是否通过：PASS
- 失败原因：无

### 112. phase2b optional addon excluded from booking by default - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：optional addon excluded from booking by default
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.04s
- 是否通过：PASS
- 失败原因：无

### 113. phase2b confirm booking creates mock bookings - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：confirm booking creates mock bookings
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：4.9s
- 是否通过：PASS
- 失败原因：无

### 114. phase2b booking session isolation - PASS

- 输入：`booking session isolation`
- 解析字段：`{"scene": "addon_only", "primary_intent": "milk_tea", "main_role": "ADDON", "requested_categories": ["奶茶"], "negative_intents": ["no_ice", "not_too_sweet"], "safety_flags": ["cannot_ice", "not_too_sweet"], "drink_preferences": {"sugar_level": "low", "ice_level": "no_ice", "hot_required": true}, "party_size": null, "start_time": "19:00", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "奶茶", "confirmed_fields": {"party_size": null, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "budget_per_person", "transport"], "sequence": [{"role": "ADDON", "category": "奶茶", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：booking session isolation
- 可选加购摘要：无
- 预约状态：mode=booking_review executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：6.27s
- 是否通过：PASS
- 失败原因：无

### 115. phase2b checkout blocked before booking - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：pay blocked before booking
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：2.98s
- 是否通过：PASS
- 失败原因：无

### 116. phase2b checkout preview after booking - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：checkout flow
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：4.91s
- 是否通过：PASS
- 失败原因：无

### 117. phase2b transit is non billable - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：checkout flow
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：4.8s
- 是否通过：PASS
- 失败原因：无

### 118. phase2b optional add-on excluded by default - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：checkout flow
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.21s
- 是否通过：PASS
- 失败原因：无

### 119. phase2b accepted add-on enters checkout - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：checkout flow
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.0s
- 是否通过：PASS
- 失败原因：无

### 121. phase2b one-click mock payment - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：checkout flow
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：4.65s
- 是否通过：PASS
- 失败原因：无

### 122. phase2b AA split bill - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：checkout flow
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.31s
- 是否通过：PASS
- 失败原因：无

### 126. phase2b support create for selected itinerary - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support merchant_full from selected_itinerary
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.74s
- 是否通过：PASS
- 失败原因：无

### 127. phase2b support create for booking review segment - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support change_time from booking_review
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=booking_review executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.48s
- 是否通过：PASS
- 失败原因：无

### 128. phase2b support create for checkout result - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support coupon_help from checkout_result
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.0s
- 是否通过：PASS
- 失败原因：无

### 129. phase2b refund request is mock only - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support refund_request from booking_review
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=booking_review executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.54s
- 是否通过：PASS
- 失败原因：无

### 130. phase2b merchant full suggests rescue - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support merchant_full from selected_itinerary
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.64s
- 是否通过：PASS
- 失败原因：无

### 131. phase2b coupon help returns mock coupon rules - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support coupon_help from checkout_result
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.35s
- 是否通过：PASS
- 失败原因：无

### 132. phase2b complaint creates mock ticket - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support complaint from booking_review
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=booking_review executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.59s
- 是否通过：PASS
- 失败原因：无

### 133. phase2b support case session-bound - PASS

- 输入：`support session isolation`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support session isolation
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.59s
- 是否通过：PASS
- 失败原因：无

### 134. phase2b support API smoke - PASS

- 输入：`support API smoke`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：support API smoke
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.64s
- 是否通过：PASS
- 失败原因：无

### 135. phase2b birthday ritual add-ons - PASS

- 输入：`朋友生日，4个人，预算300一人，想有点仪式感`
- 解析字段：`{"scene": "friends_out", "primary_intent": "birthday", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 300, "cuisine_preference": null, "transport": "unknown", "confidence": 0.72, "missing_fields": [], "intent_frame_public": {"goal_summary": "朋友生日仪式感安排", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 300, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": "生日"}, "field_sources": {"party_size": "explicit_text", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["duration_minutes", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 火锅 | ¥285 | 8.7h
- 可选加购摘要：optional=新街口蛋糕鲜花店12(生日补给); 新街口外卖店10(外卖)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：5.17s
- 是否通过：PASS
- 失败原因：无

### 136. phase2b date ritual add-ons - PASS

- 输入：`想和女朋友约会，浪漫一点，18点，新街口，人均300`
- 解析字段：`{"scene": "couple", "primary_intent": "date", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "18:00", "budget_per_person": 300, "cuisine_preference": null, "transport": "unknown", "confidence": 0.62, "missing_fields": [], "intent_frame_public": {"goal_summary": "想安排一次约会", "confirmed_fields": {"party_size": null, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 300, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": "约会"}, "field_sources": {"party_size": "unknown", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 电影院 / 江浙菜 | ¥191 | 3.8h
- 可选加购摘要：optional=新街口奶茶店11(奶茶); 顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.57s
- 是否通过：PASS
- 失败原因：无

### 137. phase2b long script supply add-ons - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，6小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 360, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.43s
- 是否通过：PASS
- 失败原因：无

### 138. phase2b stay-in delivery and xiaoxiang add-ons - PASS

- 输入：`我今天不想出门，就想宅家看点东西，点点吃的`
- 解析字段：`{"scene": "stay_in", "primary_intent": "stay_in", "main_role": "STAYIN", "requested_categories": ["外卖"], "negative_intents": ["no_outdoor"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "20:00", "budget_per_person": 120, "cuisine_preference": null, "transport": "unknown", "confidence": 0.74, "missing_fields": [], "intent_frame_public": {"goal_summary": "宅家休息和外卖补给", "confirmed_fields": {"party_size": null, "start_time": "20:00", "end_time": null, "duration_minutes": null, "home_area": "线上", "friend_areas": [], "budget_per_person": 120, "transport": "unknown", "dine_mode": "delivery", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "planning_default", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "explicit_text", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes"], "sequence": [{"role": "STAYIN", "category": "外卖", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 外卖 | ¥44 | 0.7h
- 可选加购摘要：optional=老门东外卖店24(外卖); 奥体闪购零食店12(闪购零食)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：2.68s
- 是否通过：PASS
- 失败原因：无

### 139. phase2b movie no meal blocks dinner add-ons - PASS

- 输入：`今天晚上想看电影，不想吃饭`
- 解析字段：`{"scene": "play_only", "primary_intent": "movie", "main_role": "PLAY", "requested_categories": ["电影院"], "negative_intents": ["no_meal"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "19:30", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "电影院", "confirmed_fields": {"party_size": null, "start_time": "19:30", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "budget_per_person", "transport"], "sequence": [{"role": "PLAY", "category": "电影院", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 电影院 | ¥85 | 2.2h
- 可选加购摘要：无
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：2.89s
- 是否通过：PASS
- 失败原因：无

### 140. phase2b add-ons excluded from checkout by default - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，6小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 360, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.05s
- 是否通过：PASS
- 失败原因：无

### 141. phase2b accepted add-on enters mock checkout - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，6小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 360, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.41s
- 是否通过：PASS
- 失败原因：无

### 142. phase2b rejected add-on not repeated in session - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，6小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 360, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口奶茶店11(奶茶)；confirmed_addon=新街口奶茶店11(奶茶)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.4s
- 是否通过：PASS
- 失败原因：无

### 143. phase2b photo guide content card only - PASS

- 输入：`想和女朋友约会，浪漫一点，18点，新街口，人均300`
- 解析字段：`{"scene": "couple", "primary_intent": "date", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "18:00", "budget_per_person": 300, "cuisine_preference": null, "transport": "unknown", "confidence": 0.62, "missing_fields": [], "intent_frame_public": {"goal_summary": "想安排一次约会", "confirmed_fields": {"party_size": null, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 300, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": "约会"}, "field_sources": {"party_size": "unknown", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 电影院 / 江浙菜 | ¥191 | 3.8h
- 可选加购摘要：optional=新街口奶茶店11(奶茶); 顺手出片攻略（Mock）(内容攻略)；confirmed_addon=新街口奶茶店11(奶茶)
- 预约状态：mode=executed executed=True bookings=2 share=yes
- 异常重排结果：未触发
- 单用例耗时：7.22s
- 是否通过：PASS
- 失败原因：无

### 144. phase2b final birthday closed loop - PASS

- 输入：`朋友生日，4个人，预算300一人，想有点仪式感`
- 解析字段：`{"scene": "friends_out", "primary_intent": "birthday", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 300, "cuisine_preference": null, "transport": "unknown", "confidence": 0.72, "missing_fields": [], "intent_frame_public": {"goal_summary": "朋友生日仪式感安排", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 300, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": "生日"}, "field_sources": {"party_size": "explicit_text", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["duration_minutes", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：final integration birthday closed loop
- 可选加购摘要：optional=新街口蛋糕鲜花店12(生日补给); 新街口外卖店10(外卖)；confirmed_addon=新街口蛋糕鲜花店12(生日补给)
- 预约状态：mode=executed executed=True bookings=2 share=yes
- 异常重排结果：未触发
- 单用例耗时：7.08s
- 是否通过：PASS
- 失败原因：无

### 145. phase2b final date add-on separation - PASS

- 输入：`想和女朋友约会，浪漫一点，18点，新街口，人均300`
- 解析字段：`{"scene": "couple", "primary_intent": "date", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "18:00", "budget_per_person": 300, "cuisine_preference": null, "transport": "unknown", "confidence": 0.62, "missing_fields": [], "intent_frame_public": {"goal_summary": "想安排一次约会", "confirmed_fields": {"party_size": null, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 300, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": "约会"}, "field_sources": {"party_size": "unknown", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 电影院 / 江浙菜 | ¥191 | 3.8h
- 可选加购摘要：optional=新街口奶茶店11(奶茶); 顺手出片攻略（Mock）(内容攻略)；confirmed_addon=新街口奶茶店11(奶茶)
- 预约状态：mode=executed executed=True bookings=2 share=yes
- 异常重排结果：未触发
- 单用例耗时：6.67s
- 是否通过：PASS
- 失败原因：无

### 146. phase2b final long script supply loop - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，6小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 360, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.35s
- 是否通过：PASS
- 失败原因：无

### 147. phase2b final movie no-meal loop - PASS

- 输入：`今天晚上想看电影，不想吃饭`
- 解析字段：`{"scene": "play_only", "primary_intent": "movie", "main_role": "PLAY", "requested_categories": ["电影院"], "negative_intents": ["no_meal"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "19:30", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "电影院", "confirmed_fields": {"party_size": null, "start_time": "19:30", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "budget_per_person", "transport"], "sequence": [{"role": "PLAY", "category": "电影院", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 电影院 | ¥85 | 2.2h
- 可选加购摘要：无
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：4.41s
- 是否通过：PASS
- 失败原因：无

### 148. phase2b final vote booking checkout loop - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：final integration vote booking checkout
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.06s
- 是否通过：PASS
- 失败原因：无

### 149. phase2b final rescue to support loop - PASS

- 输入：`4个朋友今天18:00想先看展再吃饭，人均180，新街口，公共交通，4小时`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "PLAY", "requested_categories": ["展览"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 180, "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 180, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "展览", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：final rescue to support
- 可选加购摘要：optional=顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=selected executed=False bookings=0 share=yes
- 异常重排结果：restaurant | 原「新街口江浙菜店14」已满座。已就近换到 新街口 的「新街口江浙菜店06」（评分 4.8），其它节点不动，人均变为 ¥155，仍在预算内。 | needs_user_confirm=False
- 单用例耗时：4.8s
- 是否通过：PASS
- 失败原因：无

### 150. phase2b final addon reject session consistency - PASS

- 输入：`4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，6小时`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 360, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：final addon reject consistency
- 可选加购摘要：optional=新街口奶茶店11(奶茶)；confirmed_addon=新街口奶茶店11(奶茶)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：8.89s
- 是否通过：PASS
- 失败原因：无

### 151. phase2b final all-mock boundary scan - PASS

- 输入：`full mock boundary scan`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 360, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=1 share=yes
- 异常重排结果：未触发
- 单用例耗时：5.1s
- 是否通过：PASS
- 失败原因：无

### 152. phase2c food intent contract and required slots - PASS

- 输入：`我想和3个朋友一起去吃个饭`
- 解析字段：`{"scene": "food_only", "primary_intent": "food_discovery", "main_role": "EAT", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 150, "cuisine_preference": "any", "transport": "unknown", "confidence": 0.4, "missing_fields": [], "intent_frame_public": {"goal_summary": "想找点吃的", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": ["duration_minutes", "transport"], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 江浙菜 | ¥106 | 1.4h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：2.78s
- 是否通过：PASS
- 失败原因：无

### 153. phase2c script required slots contract - PASS

- 输入：`我想玩个剧本杀`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": null, "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.92, "missing_fields": ["party_size", "start_time", "budget_per_person", "script_style", "window_hours", "home_area"], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": null, "start_time": null, "end_time": null, "duration_minutes": null, "home_area": null, "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "unknown", "home_area": "unknown", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "start_time", "duration_minutes", "home_area", "budget_per_person", "transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`needs_clarification`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：script required slots
- 可选加购摘要：无
- 预约状态：mode=needs_clarification executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.82s
- 是否通过：PASS
- 失败原因：无

### 154. phase2c named script before secondary meal - PASS

- 输入：`我想玩《快乐人生》，顺便吃点`
- 解析字段：`{"scene": "friends_out", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "unknown", "confidence": 0.92, "missing_fields": [], "script_style_choices": ["欢乐本"], "intent_frame_public": {"goal_summary": "剧本杀，再吃饭", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null, "script_style": "欢乐本"}, "field_sources": {"party_size": "user_answer", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default", "duration_minutes": "user_answer", "script_style": "user_answer"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text", "script_title": "快乐人生"}, {"role": "EAT", "category": null, "source": "explicit_text", "meal_bridge_preference": true}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 本地小吃 | ¥148 | 5.0h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.15s
- 是否通过：PASS
- 失败原因：无

### 156. phase2c complete date creates two clean candidates - PASS

- 输入：`明天18:00想和女朋友在河西约会，人均300，浪漫一点，不想太累`
- 解析字段：`{"scene": "couple", "primary_intent": "date", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "18:00", "budget_per_person": 300, "cuisine_preference": null, "transport": "unknown", "confidence": 0.62, "missing_fields": [], "intent_frame_public": {"goal_summary": "想安排一次约会", "confirmed_fields": {"party_size": null, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "河西", "friend_areas": [], "budget_per_person": 300, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": "约会"}, "field_sources": {"party_size": "unknown", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 电影院 / 江浙菜 | ¥197 | 4.5h
- 可选加购摘要：optional=河西奶茶店23(奶茶); 顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.31s
- 是否通过：PASS
- 失败原因：无

### 157. phase2c stepper and intent UI static - PASS

- 输入：`frontend static stepper`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 158. phase2c old engineering UI hidden - PASS

- 输入：`frontend static cleanup`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 159. phase2c plan comparison and friend co-select UI - PASS

- 输入：`frontend static candidates`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 160. phase2c bottom drawer booking UI - PASS

- 输入：`frontend static booking drawer`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 161. phase2c execution page merged actions UI - PASS

- 输入：`frontend static execution`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 163. phase2c LongCat-only LLM boundary with fallback - PASS

- 输入：`想喝奶茶，不要太甜，不能喝冰的`
- 解析字段：`{"scene": "addon_only", "primary_intent": "milk_tea", "main_role": "ADDON", "requested_categories": ["奶茶"], "negative_intents": ["no_ice", "not_too_sweet"], "safety_flags": ["not_too_sweet", "cannot_ice"], "drink_preferences": {"sugar_level": "low", "ice_level": "no_ice", "hot_required": true}, "party_size": null, "start_time": "19:00", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "奶茶", "confirmed_fields": {"party_size": null, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "duration_minutes", "budget_per_person", "transport"], "sequence": [{"role": "ADDON", "category": "奶茶", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 奶茶 | ¥23 | 0.3h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：1.92s
- 是否通过：PASS
- 失败原因：无

### 168. phase2c public docs and frontend residue cleanup - PASS

- 输入：`public residue scan`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：static scan
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 169. phase2c date preferences multi-select - PASS

- 输入：`想和女朋友约会，浪漫一点`
- 解析字段：`{"scene": "couple", "primary_intent": "date", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "18:00", "budget_per_person": 300, "cuisine_preference": null, "transport": "unknown", "confidence": 0.86, "missing_fields": [], "date_preferences": ["看电影", "拍照", "不太累"], "intent_frame_public": {"goal_summary": "想安排一次约会", "confirmed_fields": {"party_size": null, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 300, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": "约会", "date_preferences": ["看电影", "拍照", "不太累"]}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown", "date_preferences": "user_answer"}, "unknown_fields": ["party_size", "duration_minutes", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`True`
- 是否已补全进入规划：`True`
- 主方案摘要：Plan A | 电影院 | ¥85 | 2.2h
- 可选加购摘要：optional=新街口奶茶店11(奶茶); 顺手出片攻略（Mock）(内容攻略)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.14s
- 是否通过：PASS
- 失败原因：无

### 170. phase2c homepage template completeness - PASS

- 输入：`frontend homepage templates`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 171. phase2c candidate card cleanup - PASS

- 输入：`frontend candidate card`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.15s
- 是否通过：PASS
- 失败原因：无

### 172. phase2c stepper navigation gate - PASS

- 输入：`frontend stepper gate`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 173. phase2c friend co-select no-option - PASS

- 输入：`frontend friend co-select`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.15s
- 是否通过：PASS
- 失败原因：无

### 174. phase2c execution payment buttons - PASS

- 输入：`frontend payment buttons`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.15s
- 是否通过：PASS
- 失败原因：无

### 175. phase2c split bill manual adjustment - PASS

- 输入：`frontend split bill`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 176. phase2c support other issue - PASS

- 输入：`frontend support other`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 177. phase2c addon placement - PASS

- 输入：`frontend addon placement`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 178. phase2c long-lead addon early prompt - PASS

- 输入：`朋友生日，4个人，预算300一人，想有点仪式感`
- 解析字段：`{"scene": "friends_out", "primary_intent": "birthday", "main_role": "PLAY", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "18:00", "budget_per_person": 300, "cuisine_preference": null, "transport": "unknown", "confidence": 0.72, "missing_fields": [], "intent_frame_public": {"goal_summary": "朋友生日仪式感安排", "confirmed_fields": {"party_size": 4, "start_time": "18:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 300, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": "生日"}, "field_sources": {"party_size": "explicit_text", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["duration_minutes", "transport"], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 火锅 | ¥285 | 8.7h
- 可选加购摘要：optional=新街口蛋糕鲜花店12(生日补给); 新街口外卖店10(外卖)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.5s
- 是否通过：PASS
- 失败原因：无

### 179. phase2c catalog size - PASS

- 输入：`catalog stats`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：catalog check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.31s
- 是否通过：PASS
- 失败原因：无

### 180. phase2c catalog coverage - PASS

- 输入：`catalog coverage`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：catalog check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.26s
- 是否通过：PASS
- 失败原因：无

### 181. phase2c data-driven food recommendation - PASS

- 输入：`food data-driven`
- 解析字段：`{"scene": "food_only", "primary_intent": "food_discovery", "main_role": "EAT", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "cuisine_preference": "any", "transport": "unknown", "confidence": 0.62, "missing_fields": [], "intent_frame_public": {"goal_summary": "想找点吃的", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "explicit_text"}, "unknown_fields": ["duration_minutes", "transport"], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 江浙菜 | ¥106 | 1.4h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.75s
- 是否通过：PASS
- 失败原因：无

### 182. phase2c data-driven script recommendation - PASS

- 输入：`script data-driven`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "public", "confidence": 0.35, "missing_fields": [], "intent_frame_public": {"goal_summary": "还需要确认目标", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.34s
- 是否通过：PASS
- 失败原因：无

### 183. phase2c no online movie core recommendation - PASS

- 输入：`stay-in no online movie`
- 解析字段：`{"scene": "stay_in", "primary_intent": "stay_in", "main_role": "STAYIN", "requested_categories": ["外卖", "闪购零食"], "negative_intents": ["no_outdoor"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 2, "start_time": "19:00", "budget_per_person": 100, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "宅家休息和外卖补给", "confirmed_fields": {"party_size": 2, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "线上", "friend_areas": [], "budget_per_person": 100, "transport": "unknown", "dine_mode": "delivery", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "planning_default", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "explicit_text", "cuisine_preference": "unknown"}, "unknown_fields": ["duration_minutes"], "sequence": [{"role": "STAYIN", "category": "外卖", "source": "explicit_text"}, {"role": "STAYIN", "category": "闪购零食", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 外卖 / 闪购零食 | ¥88 | 1.2h
- 可选加购摘要：optional=老门东外卖店24(外卖); 奥体闪购零食店12(闪购零食)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.3s
- 是否通过：PASS
- 失败原因：无

### 184. phase2c mock boundary scan - PASS

- 输入：`mock boundary scan`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：static scan
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 185. phase2c browser candidate card visual cleanup - PASS

- 输入：`frontend candidate visual cleanup`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 186. phase2c browser stepper back navigation reset - PASS

- 输入：`frontend stepper reset`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 187. phase2c browser split manual amount sync - PASS

- 输入：`frontend split sync`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 188. phase2c browser support other issue inline input - PASS

- 输入：`frontend support inline`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 189. phase2c browser user-facing merchant names clean - PASS

- 输入：`merchant names clean`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：catalog check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.31s
- 是否通过：PASS
- 失败原因：无

### 190. phase2c browser no online movie user-facing recommendation - PASS

- 输入：`stay-in online cleanup`
- 解析字段：`{"scene": "stay_in", "primary_intent": "stay_in", "main_role": "STAYIN", "requested_categories": ["外卖", "闪购零食"], "negative_intents": ["no_outdoor"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 1, "start_time": "19:00", "budget_per_person": 100, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "宅家休息和外卖补给", "confirmed_fields": {"party_size": 1, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "线上", "friend_areas": [], "budget_per_person": 100, "transport": "unknown", "dine_mode": "delivery", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "planning_default", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "explicit_text", "cuisine_preference": "unknown"}, "unknown_fields": ["duration_minutes"], "sequence": [{"role": "STAYIN", "category": "外卖", "source": "explicit_text"}, {"role": "STAYIN", "category": "闪购零食", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 外卖 / 闪购零食 | ¥88 | 1.2h
- 可选加购摘要：optional=老门东外卖店24(外卖); 奥体闪购零食店12(闪购零食)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.24s
- 是否通过：PASS
- 失败原因：无

### 191. phase2c browser render config - PASS

- 输入：`render config`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：deploy check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 192. phase2c browser friend test checklist - PASS

- 输入：`friend checklist`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：doc check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 193. phase2c browser no external API boundary regression - PASS

- 输入：`external boundary scan`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：static scan
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 194. phase2c itinerary home chat entry - PASS

- 输入：`frontend home chat`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 195. phase2c itinerary complete examples fill only - PASS

- 输入：`frontend examples`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 196. phase2c itinerary clarification and loading copy - PASS

- 输入：`frontend clarify`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 197. phase2c itinerary preserves explicit segment order - PASS

- 输入：`sequence order`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "EAT", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 400, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "script_style_choices": ["欢乐本"], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 400, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null, "script_style": "欢乐本"}, "field_sources": {"party_size": "user_answer", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "user_answer", "dine_mode": "planning_default", "cuisine_preference": "planning_default", "duration_minutes": "user_answer", "script_style": "user_answer"}, "unknown_fields": [], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}, {"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：sequence order
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：7.79s
- 是否通过：PASS
- 失败原因：无

### 198. phase2c itinerary total budget includes all main segments - PASS

- 输入：`budget total`
- 解析字段：`{"scene": "friends_out", "primary_intent": "outing", "main_role": "EAT", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "script_style_choices": ["欢乐本"], "intent_frame_public": {"goal_summary": "想出门玩，但还没确定活动类型", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null, "script_style": "欢乐本"}, "field_sources": {"party_size": "user_answer", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "user_answer", "dine_mode": "planning_default", "cuisine_preference": "planning_default", "duration_minutes": "user_answer", "script_style": "user_answer"}, "unknown_fields": [], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}, {"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 简餐 / 剧本杀 | ¥183 | 5.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.49s
- 是否通过：PASS
- 失败原因：无

### 199. phase2c itinerary store card structure - PASS

- 输入：`frontend store cards`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.16s
- 是否通过：PASS
- 失败原因：无

### 200. phase2c itinerary merchant detail and coupons - PASS

- 输入：`merchant detail`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.15s
- 是否通过：PASS
- 失败原因：无

### 201. phase2c itinerary per-segment selection backend - PASS

- 输入：`select segments`
- 解析字段：`{"scene": "friends_out", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 400, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "script_style_choices": ["欢乐本"], "intent_frame_public": {"goal_summary": "剧本杀，再吃饭", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 400, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null, "script_style": "欢乐本"}, "field_sources": {"party_size": "user_answer", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "user_answer", "transport": "user_answer", "dine_mode": "planning_default", "cuisine_preference": "planning_default", "duration_minutes": "user_answer", "script_style": "user_answer"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 简餐 | ¥245 | 7.8h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=selected executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.6s
- 是否通过：PASS
- 失败原因：无

### 202. phase2c itinerary booking bubbles - PASS

- 输入：`frontend booking`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 203. phase2c itinerary API select booking reservation smoke - PASS

- 输入：`api segment smoke`
- 解析字段：`{"scene": "friends_out", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 400, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "public", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀，再吃饭", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 400, "transport": "public", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "explicit_text", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": [], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：segment API smoke
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)；confirmed_addon=新街口外卖店10(外卖)
- 预约状态：mode=executed executed=True bookings=2 share=yes
- 异常重排结果：未触发
- 单用例耗时：7.37s
- 是否通过：PASS
- 失败原因：无

### 204. phase2c itinerary friend co-select in segment - PASS

- 输入：`friend co-select`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 205. phase2c itinerary execution action order - PASS

- 输入：`execution actions`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 206. phase2c itinerary execution transport and itinerary blocks - PASS

- 输入：`execution blocks`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 207. phase2c itinerary rescue and bill drawers - PASS

- 输入：`drawers`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 208. phase2c itinerary 5000 merchant catalog contract - PASS

- 输入：`catalog contract`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：catalog check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.36s
- 是否通过：PASS
- 失败原因：无

### 209. phase2c itinerary admin key fields and reservation status - PASS

- 输入：`admin fields`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：admin check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 210. phase2c itinerary Plan A/B distinct merchants - PASS

- 输入：`distinct plans`
- 解析字段：`{"scene": "food_only", "primary_intent": "food_discovery", "main_role": "EAT", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "cuisine_preference": "any", "transport": "unknown", "confidence": 0.62, "missing_fields": [], "intent_frame_public": {"goal_summary": "想找点吃的", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "explicit_text", "cuisine_preference": "explicit_text"}, "unknown_fields": ["duration_minutes", "transport"], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 江浙菜 | ¥106 | 1.4h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.13s
- 是否通过：PASS
- 失败原因：无

### 211. phase2c itinerary stay-in delivery semantics - PASS

- 输入：`stay-in delivery`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：stay-in check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.91s
- 是否通过：PASS
- 失败原因：无

### 212. phase2c itinerary replace current card only - PASS

- 输入：`replace current card`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.26s
- 是否通过：PASS
- 失败原因：无

### 213. phase2c itinerary stage gates - PASS

- 输入：`stage gates`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.15s
- 是否通过：PASS
- 失败原因：无

### 214. phase2c itinerary local Mock boundary - PASS

- 输入：`mock boundary`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：boundary check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 215. phase2c itinerary integration tokens - PASS

- 输入：`integration tokens`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：integration check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 216. phase2c natural eat template should not block - PASS

- 输入：`natural intent eat template`
- 解析字段：`{"scene": "food_only", "primary_intent": "food_discovery", "main_role": "EAT", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "cuisine_preference": "any", "transport": "unknown", "confidence": 0.62, "missing_fields": [], "intent_frame_public": {"goal_summary": "想找点吃的", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "explicit_text", "cuisine_preference": "explicit_text"}, "unknown_fields": ["duration_minutes", "transport"], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 江浙菜 | ¥106 | 1.4h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：2.93s
- 是否通过：PASS
- 失败原因：无

### 217. phase2c natural eat-in planning default - PASS

- 输入：`dine mode default`
- 解析字段：`{"scene": "food_only", "primary_intent": "food_discovery", "main_role": "EAT", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "19:00", "budget_per_person": 150, "cuisine_preference": "any", "transport": "unknown", "confidence": 0.62, "missing_fields": [], "intent_frame_public": {"goal_summary": "想找点吃的", "confirmed_fields": {"party_size": null, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": ["party_size", "duration_minutes", "transport"], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 江浙菜 | ¥106 | 1.4h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：2.48s
- 是否通过：PASS
- 失败原因：无

### 218. phase2c natural cuisine any recognized - PASS

- 输入：`cuisine any`
- 解析字段：`{"scene": "food_only", "primary_intent": "food_discovery", "main_role": "EAT", "requested_categories": [], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "19:00", "budget_per_person": 150, "cuisine_preference": "any", "transport": "unknown", "confidence": 0.62, "missing_fields": ["start_time"], "intent_frame_public": {"goal_summary": "想找点吃的", "confirmed_fields": {"party_size": 4, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "explicit_text"}, "unknown_fields": ["duration_minutes", "transport"], "sequence": [{"role": "EAT", "category": null, "source": "explicit_text"}]}}`
- result_type：`needs_clarification`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：无方案
- 可选加购摘要：无
- 预约状态：mode=needs_clarification executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.91s
- 是否通过：PASS
- 失败原因：无

### 219. phase2c natural home eating is delivery - PASS

- 输入：`home eating`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：home eating check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.91s
- 是否通过：PASS
- 失败原因：无

### 220. phase2c natural stay-in takeaway snacks sequence - PASS

- 输入：`stay-in sequence`
- 解析字段：`{"scene": "stay_in", "primary_intent": "stay_in", "main_role": "STAYIN", "requested_categories": ["外卖", "闪购零食"], "negative_intents": ["no_outdoor"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 2, "start_time": "19:00", "budget_per_person": 100, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "宅家休息和外卖补给", "confirmed_fields": {"party_size": 2, "start_time": "19:00", "end_time": null, "duration_minutes": null, "home_area": "线上", "friend_areas": [], "budget_per_person": 100, "transport": "unknown", "dine_mode": "delivery", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "planning_default", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "explicit_text", "cuisine_preference": "unknown"}, "unknown_fields": ["duration_minutes"], "sequence": [{"role": "STAYIN", "category": "外卖", "source": "explicit_text"}, {"role": "STAYIN", "category": "闪购零食", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 外卖 / 闪购零食 | ¥88 | 1.2h
- 可选加购摘要：optional=老门东外卖店24(外卖); 奥体闪购零食店12(闪购零食)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.94s
- 是否通过：PASS
- 失败原因：无

### 221. phase2c natural clarification key field compatibility - PASS

- 输入：`clarify schema`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：clarify schema check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.96s
- 是否通过：PASS
- 失败原因：无

### 222. phase2c natural stale missing fields cleared - PASS

- 输入：`missing cleanup`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：missing cleanup check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.84s
- 是否通过：PASS
- 失败原因：无

### 223. phase2c natural activity order plus meal bridge - PASS

- 输入：`meal bridge no explicit meal`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀", "台球"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "17:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "unknown", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀，再台球", "confirmed_fields": {"party_size": 4, "start_time": "17:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "PLAY", "category": "台球", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 台球 | ¥207 | 6.1h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.8s
- 是否通过：PASS
- 失败原因：无

### 224. phase2c natural explicit middle meal preserved - PASS

- 输入：`explicit meal bridge`
- 解析字段：`{"scene": "friends_out", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀", "台球"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "17:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": "any", "transport": "unknown", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀，再吃饭，再台球", "confirmed_fields": {"party_size": 4, "start_time": "17:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "eat_in", "cuisine_preference": "any", "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "planning_default", "cuisine_preference": "planning_default"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "EAT", "category": null, "source": "explicit_text", "meal_bridge_preference": true}, {"role": "PLAY", "category": "台球", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 简餐 / 台球 | ¥278 | 7.2h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：5.45s
- 是否通过：PASS
- 失败原因：无

### 225. phase2c natural long activity dinner bridge - PASS

- 输入：`long activity meal bridge`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "17:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "unknown", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀", "confirmed_fields": {"party_size": 4, "start_time": "17:00", "end_time": null, "duration_minutes": 240, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 | ¥112 | 4.3h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.58s
- 是否通过：PASS
- 失败原因：无

### 226. phase2c natural no meal blocks bridge - PASS

- 输入：`no meal bridge`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀", "台球"], "negative_intents": ["no_meal"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "17:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀，再台球", "confirmed_fields": {"party_size": 4, "start_time": "17:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "PLAY", "category": "台球", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 台球 | ¥207 | 6.1h
- 可选加购摘要：optional=新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：3.84s
- 是否通过：PASS
- 失败原因：无

### 227. phase2c natural stay-in no area slot - PASS

- 输入：`stay-in no area`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：stay-in area check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：4.95s
- 是否通过：PASS
- 失败原因：无

### 228. phase2c natural factual plan focus - PASS

- 输入：`focus factual`
- 解析字段：`{"scene": "play_only", "primary_intent": "script_game", "main_role": "PLAY", "requested_categories": ["剧本杀", "台球"], "negative_intents": [], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": 4, "start_time": "17:00", "budget_per_person": 150, "script_style": "欢乐本", "cuisine_preference": null, "transport": "unknown", "confidence": 0.92, "missing_fields": [], "intent_frame_public": {"goal_summary": "剧本杀，再台球", "confirmed_fields": {"party_size": 4, "start_time": "17:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": 150, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "explicit_text", "start_time": "explicit_text", "home_area": "explicit_text", "budget_per_person": "explicit_text", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["transport"], "sequence": [{"role": "PLAY", "category": "剧本杀", "source": "explicit_text"}, {"role": "PLAY", "category": "台球", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 剧本杀 / 台球 | ¥207 | 6.1h
- 可选加购摘要：optional=新街口外卖店10(外卖); 新街口奶茶店11(奶茶)
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：5.51s
- 是否通过：PASS
- 失败原因：无

### 229. phase2c natural homepage template alignment - PASS

- 输入：`homepage templates`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：frontend template check
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.21s
- 是否通过：PASS
- 失败原因：无

### 230. phase2c natural coordination regression pack - PASS

- 输入：`natural regression`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：natural regression pack
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：11.51s
- 是否通过：PASS
- 失败原因：无

### 231. phase2c no_meal public default cleanup - PASS

- 输入：`no_meal public defaults`
- 解析字段：`{"scene": "play_only", "primary_intent": "movie", "main_role": "PLAY", "requested_categories": ["电影院"], "negative_intents": ["no_meal"], "safety_flags": [], "drink_preferences": {"sugar_level": null, "ice_level": null, "hot_required": false}, "party_size": null, "start_time": "19:00", "budget_per_person": null, "cuisine_preference": null, "transport": "unknown", "confidence": 0.9400000000000001, "missing_fields": [], "intent_frame_public": {"goal_summary": "电影院", "confirmed_fields": {"party_size": null, "start_time": "19:00", "end_time": null, "duration_minutes": 300, "home_area": "新街口", "friend_areas": [], "budget_per_person": null, "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": null, "diet_limits": [], "occasion": null}, "field_sources": {"party_size": "unknown", "start_time": "user_answer", "home_area": "user_answer", "budget_per_person": "unknown", "transport": "unknown", "dine_mode": "unknown", "cuisine_preference": "unknown"}, "unknown_fields": ["party_size", "budget_per_person", "transport"], "sequence": [{"role": "PLAY", "category": "电影院", "source": "explicit_text"}]}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：Plan A | 电影院 | ¥85 | 2.2h
- 可选加购摘要：无
- 预约状态：mode=planned executed=False bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：2.93s
- 是否通过：PASS
- 失败原因：无

### 232. phase2c home eating clarification boundary - PASS

- 输入：`home eating clarification`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：home eating clarification
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：0.96s
- 是否通过：PASS
- 失败原因：无

### 233. phase2c script billiards required slots preserved - PASS

- 输入：`script billiards missing slots`
- 解析字段：`{"intent_frame_public": {"goal_summary": null, "confirmed_fields": {}, "field_sources": {}, "unknown_fields": [], "sequence": []}}`
- result_type：`supported_success`
- 是否触发追问：`False`
- 是否已补全进入规划：`False`
- 主方案摘要：script billiards clarification
- 可选加购摘要：无
- 预约状态：mode=None executed=None bookings=0 share=no
- 异常重排结果：未触发
- 单用例耗时：1.02s
- 是否通过：PASS
- 失败原因：无

## 失败用例和修复状态
- 无失败用例。

## 仍未解决问题

- 多人投票仍为 Mock，不是真实多端实时同步。
- 真实商户库存、真实支付、真实优惠券仍为 Mock。
- 复杂路线优化仍是轻规则，不是真实地图引擎。

## 代码风险点

- session_id 已做最小隔离，但未做持久化和过期清理。
- LLM 开启后仍可能带来等待时间，规则兜底必须保留。
- 数据文件人工编辑时字段类型不一致会降低推荐质量。
