# CLAUDE.md 路 weekend-agent 椤圭洰瑙勬牸涔?
> 杩欐槸杩欎釜椤圭洰鐨?瀹硶"銆備綘锛圕laude Code / Codex / 鍏跺畠 AI 缂栫▼鍔╂墜锛夋瘡娆¤繘鍏ヨ繖涓」鐩兘鍏堣瀹冿紝骞跺湪鏁翠釜浼氳瘽閲岄伒瀹堝畠銆?>
> 鐢ㄦ埛鍥㈤槦鏄枃绉戠敓 / 闈炶绠楁満涓撲笟鐨勫悓瀛︼紝鍏ㄧ▼闈犱綘鍐欎唬鐮併€備粬浠笉浼氳浠ｇ爜銆佷笉浼氬仛娣卞眰 debug锛屾墍浠ヤ綘鍐欑殑姣忎竴娈甸兘瑕侊細鈶?涓枃娉ㄩ噴鍏呭垎锛涒憽 鑷甫涓€娈靛彲鐩存帴杩愯鐨?`__main__` 娴嬭瘯锛涒憿 鍑洪敊姘歌繙璧板厹搴曡€屼笉鏄穿婧冦€?>
> 鐢ㄦ埛宸茬粡鏈変袱浠界粰浜虹湅鐨勬枃妗ｏ紙涓ゅ懆寮€鍙戞墜鍐?v2 + 鍐崇瓥璁板綍锛夈€?*鏈枃浠朵笉閲嶅閭ｄ簺缁嗚妭锛屾湰鏂囦欢鍙瀹?浠ｇ爜蹇呴』闀挎垚浠€涔堟牱銆佺粷瀵逛笉鑳介暱鎴愪粈涔堟牱"銆?* 濡傛灉鐢ㄦ埛鐨勮姹傚拰鏈枃浠跺啿绐侊紝鍏堟寚鍑哄啿绐佸啀璇锋眰纭锛涗笉瑕佽嚜琛屽喅瀹氥€?
---

## 0. 浣犵殑瑙掕壊

浣犳槸涓€浣嶈€愬績鐨勮祫娣?Python 宸ョ▼甯堬紝姝ｅ湪甯竴鏀潪绉戠彮鍥㈤槦鍙傚姞缇庡洟 2026 AI 榛戝鏉撅紙鍛介鍏細鏈湴鎺㈢储 路 鍛ㄦ湯闂叉椂娲诲姩瑙勫垝锛夈€?
**浣犱紭鍏堝仛鐨勪簨**锛氣憼 涓ユ牸鎸夋湰瑙勬牸涔﹀啓浠ｇ爜锛涒憽 涓€娆″彧鏀逛竴涓ā鍧楋紱鈶?姣忓啓瀹屼竴娈碉紝鏄庣‘鍛婅瘔鐢ㄦ埛"鎬庝箞杩愯瀹冩潵楠岃瘉"锛涒懀 鐪嬩笉鎳傛垨鏈夋涔夊氨鍏堥棶锛屼笉瑕佺瀻鐚溿€?
**浣犵粷涓嶅仛鐨勪簨**锛堣瑙佺 9 鑺?缁濆绂佹"锛夛細鍋峰伔閲嶆瀯鏃犲叧浠ｇ爜銆佸紩鍏ユ湭鍒楀嚭鐨勪緷璧栥€佹敼鍔ㄦ暟鎹?Schema銆佹妸 API key 鍐欒繘浠ｇ爜銆佽澶фā鍨嬪喅瀹氭祦绋嬨€佽浠讳綍妯″潡鍦ㄥ紓甯告椂宕╂帀銆?
---

## 1. 椤圭洰韬唤

- **鏄粈涔?*锛氫竴涓湰鍦扮敓娲绘墽琛?agent銆傜敤鎴峰彂涓€鍙ヨ瘽璇村懆鏈兂骞插槢锛岀郴缁熻皟鍔ㄧ編鍥㈢敓鎬佺殑鍚冨枬鐜╀箰璧勬簮锛岃鍒掑ソ鏁存潯閾捐矾骞舵ā鎷熶笅鍗曘€?- **涓嶆槸浠€涔?*锛氫笉鏄悳绱㈡銆佷笉鏄矾绾胯鍒掑櫒銆佷笉鏄亰澶╂満鍣ㄤ汉銆?- **鐩爣鍦烘櫙锛堟繁鍋氾級**锛氣憼 鏈嬪弸鍑洪棬灞€锛坄friends_out`锛夛紝鈶?瀹呭灞€锛坄stay_in`锛夈€傚叾浠栧満鏅兘璇嗗埆鍗冲彲锛屼笉鍋氭紨绀烘繁搴︺€?- **缁堟瀬浜や粯**锛欳LI Demo + Web Demo锛堢敤鎴峰簲鐢ㄩ〉 + 骞冲彴鍚庡彴椤碉級+ 鈮? 椤佃璁℃枃妗ｃ€?
---

## 2. 涓嶅彲濡ュ崗鐨勭‖绾︽潫

浠讳綍璁╀綘杩濆弽浠ヤ笅浠讳綍涓€鏉＄殑璇锋眰锛岄兘鍏堟嫆缁濆苟瑙ｉ噴銆?
| 绾︽潫 | 鏁板€?| 浣犲繀椤讳繚璇佺殑浜?|
|---|---|---|
| 鏂规鐢熸垚 | 鈮?30 绉?| 瑙勫垝鍏ㄧ▼鐢?Python 瑙勫垯锛涘ぇ妯″瀷鏈€澶氳皟 1 娆′笖璁?8 绉掕秴鏃?|
| 鍗曟宸ュ叿鍝嶅簲 | 鈮?3 绉?| 宸ュ叿鍐?`time.sleep(random 0.3~0.8)`锛?*涓婇檺鍐欐 0.8 绉?* |
| 绔埌绔祦绋?| 鈮?2 鍒嗛挓 | 涓绘祦绋?60鈥?0 绉掋€佸紓甯?30 绉?|
| 寮傚父瑕嗙洊 | 鈮?3 绫?| 蹇呴』鏀寔 `restaurant_full` / `ticket_soldout` / `time_conflict` |
| 鏍囧噯鍦烘櫙 Pass@1 | = 100% | 4 涓爣鍑嗘祴璇曞満鏅?鏈嬪弸灞€/瀹呭灞€/鍓ф湰鏉€缂轰俊鎭?鐢熸棩灞€)棣栨绔埌绔窇閫氭垚鍔?|
| 鍏?Mock | 100% | 姘歌繙涓嶈皟鐢ㄧ湡瀹?缇庡洟 / 楂樺痉 / 澶т紬鐐硅瘎绛夊閮ㄦ帴鍙ｏ紱鍙鏈湴 JSON |
| LLM 璋冪敤鐐?| 鍙?2 澶?| 浠?`agent/parser.py::parse_request` 鍜?`agent/tools.py::compose_share_card`銆傚叾浠栧湴鏂圭粷涓嶈皟鐢ㄥぇ妯″瀷 |
| 姘镐笉宕?| 100% | 浠讳綍澶栭儴璋冪敤澶辫触銆佽В鏋愬け璐ャ€佹枃浠剁己澶憋紝閮借鍏滃簳锛涚粷涓嶅悜涓婃姏鏈崟鑾峰紓甯?|
| API key | 0 澶勭‖缂栫爜 | 閫氳繃 `python-dotenv` 浠?`.env` 璇诲彇锛宍.env` 蹇呴』鍦?`.gitignore` 閲?|

---

## 3. 鏋舵瀯鎬昏锛氫唬鐮侀┍鍔ㄧ殑 agent

```
                    鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                    鈹?鐢ㄦ埛杈撳叆涓€鍙ヨ瘽                            鈹?                    鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                                     鈻?   鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?   鈹?agent/core.py  Agent 缂栨帓鑰?                                              鈹?   鈹?  娴佺▼鐢?Python 浠ｇ爜椤哄簭椹卞姩锛屼笉鐢卞ぇ妯″瀷鍐崇瓥                               鈹?   鈹斺攢鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?        鈻?             鈻?             鈻?             鈻?             鈻?   parser.py       clarify.py     catalog.py     planner.py     tools.py
   (LLM 澶?1)      (鏅鸿兘杩介棶)      (鎸夋Ы浣嶆绱?    (瑙勫垯鎺掓柟妗?    (Mock 鎺ュ彛)
        鈹?             鈹?             鈹?             鈹?             鈹?        鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                                             鈻?                                    data/*.json (Mock 鏁版嵁)
                                             鈹?                                             鈻?                                    logbook.py 鍏ㄧ▼璁板綍
```

**鏍稿績璁ょ煡锛堣鎶婅繖鏉″埢杩涜剳瀛愶級**锛氭祦绋嬫槸 Python 浠ｇ爜椤哄簭椹卞姩鐨勩€傚ぇ妯″瀷鍙湪涓や釜鍘熷瓙鐐瑰嚭鍦衡€斺€旀妸涓€鍙ヨ瘽鍙樼粨鏋勫寲銆佹妸鏂规鍙樼兢鑱婃枃妗堛€傚叾浣欑殑"鍐冲畾璇ヨ皟鍝釜宸ュ叿""鎬庝箞鎺掓椂闂磋酱""鎬庝箞鎵撳垎"閮芥槸 Python 瑙勫垯銆?*姘歌繙涓嶈缁欏ぇ妯″瀷涓€涓?鍐冲畾璋冪敤浠€涔堝伐鍏?鐨勬彁绀鸿瘝銆?*

---

## 4. 鏂囦欢缁撴瀯涓庤亴璐?
姣忎釜鏂囦欢鍙共涓€浠朵簨銆傛柊澧炲姛鑳芥椂浼樺厛鍦ㄥ凡鏈夋枃浠堕噷鍔犲嚱鏁帮紝鑰屼笉鏄柊寤烘枃浠躲€?
```
weekend-agent/
鈹溾攢鈹€ data/
鈹?  鈹溾攢鈹€ merchants.json     # 缁熶竴鍟嗘埛/椤圭洰搴擄紙涓€鍒囧悆鍠濈帺涔愮殕鍦ㄦ锛?鈹?  鈹溾攢鈹€ scenes.json        # 鍦烘櫙 鈫?妲戒綅妯℃澘
鈹?  鈹溾攢鈹€ travel.json        # 鍖哄煙闂翠氦閫氭椂闂?鈹?  鈹溾攢鈹€ samples.json       # 绀轰緥涓€鍙ヨ瘽
鈹?  鈹溾攢鈹€ user_profile.json  # 绀轰緥鐢ㄦ埛鐢诲儚
鈹?  鈹斺攢鈹€ clarify_questions.json  # 鏅鸿兘杩介棶鐨勯棶棰樻ā鏉垮簱
鈹溾攢鈹€ agent/
鈹?  鈹溾攢鈹€ __init__.py        # 绌烘枃浠跺嵆鍙紝鏍囪瘑鍖?鈹?  鈹溾攢鈹€ llm.py             # 灏佽 DeepSeek 璋冪敤锛屽惈瓒呮椂鍜屽厹搴?鈹?  鈹溾攢鈹€ logbook.py         # 鎵ц鏃ュ織锛堟渶鍏堝缓锛?鈹?  鈹溾攢鈹€ parser.py          # parse_request锛氫竴鍙ヨ瘽 鈫?闇€姹傦紙鍚?missing 瀛楁锛?鈹?  鈹溾攢鈹€ clarify.py         # decide_clarifications锛氭牴鎹己澶卞瓧娈?鎰忓浘鍐冲畾杩介棶鍝嚑涓?鈹?  鈹溾攢鈹€ catalog.py         # search_merchants锛氭寜妲戒綅/绾︽潫妫€绱?鈹?  鈹溾攢鈹€ tools.py           # check_availability / get_travel_time / book_item / compose_share_card
鈹?  鈹溾攢鈹€ planner.py         # build_itinerary / score_plan / replan
鈹?  鈹溾攢鈹€ addon.py           # suggest_addon锛氬鍊煎皬鎺ㄨ崘 + 瀹夊叏瑙勫垯
鈹?  鈹斺攢鈹€ core.py            # Agent 缂栨帓鑰咃紙鏈€鍚庡缓锛?鈹溾攢鈹€ cli.py                 # 鍛戒护琛?Demo
鈹溾攢鈹€ server.py              # FastAPI 钖勬湇鍔″眰锛堜笉鏀句笟鍔￠€昏緫锛?鈹溾攢鈹€ web/
鈹?  鈹溾攢鈹€ app.html           # 鐢ㄦ埛搴旂敤椤碉紙鍗曟枃浠讹紝鍘熺敓 JS锛?鈹?  鈹斺攢鈹€ admin.html         # 骞冲彴鍚庡彴椤碉紙鍗曟枃浠讹紝鍘熺敓 JS锛?鈹溾攢鈹€ config.py              # 浠?.env 璇?API key
鈹溾攢鈹€ requirements.txt       # 鍙斁 openai, fastapi, uvicorn, python-dotenv
鈹溾攢鈹€ .env.example           # 绀鸿寖鏂囦欢锛屽惈 DEEPSEEK_API_KEY= 杩欎竴琛?鈹溾攢鈹€ .gitignore             # 蹇呭惈 .env 鍜?__pycache__
鈹斺攢鈹€ README.md
```

**绂佹**锛氭柊澧炰笂杩颁互澶栫殑鏂囦欢澶癸紙濡?`tests/`銆乣utils/`銆乣models/`锛夛紱鏂板涓婅堪浠ュ鐨勪緷璧栵紱鎶婂涓ā鍧楀悎骞跺埌涓€涓枃浠堕噷銆?
---

## 5. 鏍稿績鏁版嵁缁撴瀯锛圫chema 鏄绾︼紝涓嶈鏀癸級

淇敼 Schema 蹇呴』鍏堝拰鐢ㄦ埛纭銆備唬鐮侀噷璇昏繖浜?JSON 鏃惰鎸変笅闈㈠瓧娈靛悕璁块棶銆?
### 5.1 merchant锛坄merchants.json` 閲屾瘡涓€鏉★級

```json
{
  "id": "m_012",
  "name": "鍩庡競褰卞儚灞?,
  "category": "灞曡",
  "slot_role": "PLAY",
  "area": "鏂拌鍙?,
  "price": 48,
  "duration_minutes": 90,
  "rating": 4.7,
  "review_count": 1280,
  "review_tags": ["鍑虹墖", "瀹夐潤", "甯冨睍鐢ㄥ績"],
  "review_snippet": "鍏夌嚎寰堥€傚悎鎷嶇収锛岄€涗笅鏉ュ緢鑸掓湇銆?,
  "open": "10:00",
  "close": "21:00",
  "can_reserve": true,
  "group_deal": {"name": "鍙屼汉瑙傚睍濂楃エ", "price": 78, "save": 18},
  "stock": 30,
  "slots": ["14:00", "14:30", "15:00", "15:30"],
  "queue_minutes": 0,
  "ad_bid": 0,
  "suitable_scenes": ["friends_out", "couple"],
  "flags": {"alcohol": false, "kid_friendly": true},
  "recommended_dishes": []
}
```

**鍏抽敭瀛楁璇存槑**锛?- `slot_role` 鈭?`{PLAY, EAT, STAYIN, ADDON}`銆傝繖鏄?鍗＄墖涓嶆贩绫荤洰"鐨勭粨鏋勪繚闅溾€斺€斿悓涓€涓Ы浣嶇殑鍗＄墖鍙兘鍒楀嚭璇?`slot_role` 鐨勫晢鎴枫€?- `category` 鏄粏鍒嗗搧绫伙紙PLAY 涓嬶細灞曡/鍓ф湰鏉€/鐢靛奖闄?鎵嬩綔/甯傞泦 绛夛紱STAYIN 涓嬶細鍦ㄧ嚎鐢靛奖/澶栧崠姝ｉ/闂喘闆堕 绛夛級銆?- `ad_bid`锛堥粯璁?0锛? 鍏紑鐨勫箍鍛婂嚭浠枫€傝瀹冨姞鏉冭繘鍗＄墖鐨勫晢鎴烽渶鍦ㄥ墠绔墦"鎺ㄥ箍"鏍囥€?- `flags.alcohol` / `flags.kid_friendly` 鐢ㄤ簬 `addon.py` 鐨勫畨鍏ㄨ繃婊ゃ€?- `group_deal` 鍙负 `null`銆俙stock` 鐢ㄤ簬娲诲姩浣欑エ鍒ゆ柇锛宍slots` 鐢ㄤ簬鏃舵鍙敤鍒ゆ柇锛宍queue_minutes` 鐢ㄤ簬椁愬巺鎺掗槦銆?
### 5.2 scene template锛坄scenes.json` 閲屾瘡涓€鏉★級

```json
{
  "friends_out": {
    "label": "鏈嬪弸鍑洪棬灞€",
    "slots": [
      {"role": "PLAY", "title": "鍏堝幓鐜?},
      {"role": "EAT",  "title": "鍐嶅幓鍚?}
    ],
    "addon": {"role": "ADDON", "title": "椤鸿矾鍔犱竴鏉?}
  },
  "stay_in": {
    "label": "瀹呭灞€",
    "slots": [
      {"role": "STAYIN", "want": "鍦ㄧ嚎鐢靛奖",                       "title": "鐪嬬偣浠€涔?},
      {"role": "STAYIN", "want": ["澶栧崠姝ｉ", "闂喘闆堕"],          "title": "鍚冪偣浠€涔?}
    ]
  }
}
```

`slots` 鏄『搴忔暟缁勶紝瀹氫箟浜嗚鍦烘櫙瑕佸～鍑犱釜妲戒綅銆佹瘡妲戒粈涔堣鑹诧紙鍙姞 `want` 闄愬埗 category锛夈€俙addon` 鍙€夈€?
### 5.3 request锛坄parse_request` 鐨勪骇鐗╋級

```json
{
  "scene": "friends_out",
  "intent_tags": ["photo"],
  "party_size": 4,
  "has_kid": false,
  "transport": "public",
  "start_time": "14:00",
  "window_hours": 5,
  "home_area": "鏂拌鍙?,
  "budget_per_person": 150,
  "preferences": ["photo", "good_food", "easy_pace"],
  "hard_limits": ["no_evening_queue", "stay_near"],
  "missing": [],
  "raw_text": "鍘熷彞"
}
```

- `transport` 鈭?`{public, self_drive, unknown}`锛堝奖鍝?`addon` 鐨勯厭绫昏繃婊わ級銆?- `preferences` 鏄蒋鍋忓ソ锛堢敤浜庤瘎鍒嗗姞鍒嗭級銆?- `hard_limits` 鏄‖绾︽潫锛堢敤浜?`catalog` 杩囨护娣樻卑锛夈€?- **`missing`** 鏄?LLM 鏍囧嚭鐨?鎴戞病鍚埌 / 涓嶇‘瀹?鐨勫瓧娈靛悕鍒楄〃锛屼緥濡?`["party_size","budget_per_person"]`銆傚畠椹卞姩鏅鸿兘杩介棶锛堣 搂8.7锛夈€侺LM **鍙爣缂哄け**锛屼笉鐢熸垚闂鏂囨湰鎴栭€夐」銆?
### 5.4 plan锛坄build_itinerary` 鐨勪骇鐗╋紝鍙兘鏈夊涓級

```json
{
  "title": "鎷嶇収杞绘澗灞€",
  "focus": "鍑虹墖 路 灏戣蛋璺?路 涓嶆帓闃?,
  "steps": [
    {"kind": "play",   "merchant_id": "m_012", "start": "14:30", "end": "16:00", "cost": 48},
    {"kind": "travel", "mode": "walk", "minutes": 12, "from": "鏂拌鍙?, "to": "鏂拌鍙?},
    {"kind": "eat",    "merchant_id": "m_007", "start": "17:30", "end": "19:00", "cost": 90}
  ],
  "slot_alternatives": {
    "play": ["m_022", "m_031"],
    "eat":  ["m_011", "m_023"]
  },
  "total_cost_per_person": 138,
  "total_minutes": 270,
  "score": {"total": 87, "people_fit": 23, "time": 18, "budget": 15, "distance": 14, "queue": 12, "highlight": 5},
  "reason": "浜哄潎 138 鍏冿紝鏈秴棰勭畻锛涒€?,
  "risks": ["鏅氶珮宄版墦杞﹀彲鑳界暐鍫?]
}
```

`steps` 鏁扮粍閲?`kind` 鈭?`{play, eat, stayin, travel, addon}`銆俙slot_alternatives` 鏄瘡涓Ы浣嶇殑澶囬€?id 鍒楄〃锛屼緵鍓嶇"鎹竴涓?鐢ㄣ€?
### 5.5 session锛坄agent/core.py` 鐨?Agent 绫诲唴閮ㄧ淮鎶わ級

```python
session = {
    "request": {...},          # parse 鍑虹殑闇€姹?    "profile": {...},          # 浠?user_profile.json 璇荤殑绀轰緥鐢诲儚
    "plans": [...],            # build_itinerary 鍑虹殑鏂规鍒楄〃
    "chosen": {...},           # 鐢ㄦ埛閫変腑鐨勬柟妗?    "executed": False,
    "rejected_ids": set(),     # 鐢ㄦ埛鎷掔粷杩囩殑鍟嗘埛 id 闆嗗悎锛堝叧閿細鐢ㄤ簬鎺掑簭鍓嶆姂鍒讹級
    "clarifications": [],      # 褰撳墠闇€瑕佽拷闂殑闂鍒楄〃锛堢粨鏋勮 5.8锛夛紱绌鸿〃绀烘棤闇€杩介棶
    "pending_clarify": False,  # True 鏃朵富娴佺▼鏆傚仠锛岀瓑鐢ㄦ埛绛斿畬杩介棶
    "logs": LogBook()
}
```

### 5.6 tool 杩斿洖鍊硷紙鎵€鏈?Tool 鍑芥暟蹇呴』鐢ㄨ繖涓澹筹級

```python
{"ok": True,  "data": {...}, "message": "鏌ヨ鎴愬姛"}
{"ok": False, "data": None,  "message": "鍘熼鍘呰鏃舵宸叉弧搴?}
```

**鎵€鏈?Tool 鍑芥暟鏃犱緥澶栭兘杩斿洖杩欎釜 dict 缁撴瀯銆?* 澶辫触涔熻繑鍥?dict锛屼笉瑕佹姏寮傚父銆?
### 5.7 log entry锛坄LogBook.add` 鍐欏叆鐨勬瘡鏉★級

```python
{
    "step": "鏌ヨ浣欎綅",       # 姝ラ鍚嶏紝鐭?    "status": "running",     # pending/running/success/warning/error
    "message": "姝ｅ湪鑱旂郴鍗楀贩灏忛鈥?,  # 鍍忓姪鎵嬪湪姹囨姤锛屼笉瑕佹妧鏈瘝
    "ts": "12:34:56"         # HH:MM:SS
}
```

### 5.8 clarification question锛坄clarify_questions.json` 閲屾瘡涓€鏉?+ `decide_clarifications` 鐨勪骇鐗╋級

**妯℃澘搴擄紙`data/clarify_questions.json`锛夋瘡鏉?*锛?
```json
{
  "field": "party_size",
  "text": "鍑犱釜浜轰竴璧峰幓?",
  "options": [
    {"label": "2浜?,     "value": 2},
    {"label": "3-4浜?,  "value": 4},
    {"label": "5-6浜?,  "value": 6},
    {"label": "6浜轰互涓?,"value": 8}
  ],
  "priority": {"default": 2, "鍓ф湰鏉€": 1, "妗屾父": 1, "瀹呭": 99}
}
```

- `field`锛氳琛ュ叏鐨?request 瀛楁鍚嶃€?- `text`锛氱粰鐢ㄦ埛鐪嬬殑闂鏂囧瓧銆?*姘歌繙鏄ā鏉块璁剧殑锛屼笉鐢?LLM 鐢熸垚銆?*
- `options`锛氬彲閫?chip 鏁扮粍锛屾瘡椤?`{label, value}`銆俙value` 绫诲瀷蹇呴』鍜?request 閲岃瀛楁鐨勭被鍨嬩竴鑷淬€?- `priority`锛氭瘡绉?`intent_tag`锛堟潵鑷?`request.intent_tags[0]`锛夌殑浼樺厛绾э紝鏁板瓧瓒婂皬瓒婇潬鍓嶃€俙99` = 璇ユ剰鍥句笅**涓嶉棶**杩欎釜闂銆俙default` 蹇呭～銆?
**`decide_clarifications(request)` 杩斿洖**锛氫竴涓暟缁勶紙0鈥? 涓棶棰橈級锛岀粨鏋勫悓涓婁絾鍘绘帀 `priority`锛屾寜浼樺厛绾ф帓搴忓悗鍙栧墠鍑犱釜銆傜┖鏁扮粍琛ㄧず鏃犻渶杩介棶銆?
---

## 6. 鍏卞悓浠ｇ爜绾﹀畾锛堟墍鏈夋ā鍧楀繀椤婚伒瀹堬級

1. **Tool 鍑芥暟杩斿洖鍥哄畾澶栧３** `{"ok","data","message"}`锛岃 5.6銆傚け璐ヤ篃杩斿洖锛屼笉鎶涘紓甯搞€?2. **姣忎釜 Tool / Catalog / Planner 鍑芥暟閮芥帴鍙椾竴涓?`logbook` 鍙傛暟**锛屽湪寮€濮嬫椂鍐欎竴鏉?`running` 鏃ュ織锛岀粨鏉熸椂鍐欎竴鏉?`success`/`warning`/`error` 鏃ュ織銆傛棩蹇楁枃瀛楀儚"鍔╂墜姹囨姤杩涘害"锛屼緥濡?鉁卄"姝ｅ湪妫€鏌ラ鍘呬綑浣?` 鉂宍"calling check_availability with id=res_07"`銆?3. **寤惰繜妯℃嫙涓婇檺 0.8 绉?*锛氭墍鏈?Tool 鍐呴儴 `time.sleep(random.uniform(0.3, 0.8))`锛?*涓婇檺涓ユ牸涓嶈秴杩?0.8 绉?*銆傜粷涓嶈秴杩?1 绉掋€?4. **鏃堕棿鏍煎紡缁熶竴**锛氭墍鏈夋椂闂村瓧绗︿覆鐢?`"HH:MM"`锛屾瘮杈冨拰鍔犲噺鏃舵崲鎴愬垎閽熸暣鏁拌绠椼€?5. **涓枃娉ㄩ噴鍏呭垎**锛氭瘡涓嚱鏁伴《閮ㄥ啓涓€鍙ヨ瘽璇存槑"瀹冨仛浠€涔堛€佷粈涔堟椂鍊欒璋佽皟鐢?锛涘鏉傞€昏緫鍒嗗潡鍔犳敞閲娿€?6. **绫诲瀷鎻愮ず鍙€変絾鍙橀噺鍚嶈娓呮櫚**锛氳兘鐢?`chosen_restaurant` 灏变笉瑕佺敤 `r`銆?7. **涓嶄娇鐢ㄧ被**闄ら潪纭湁蹇呰锛坄LogBook` 鍜?`Agent` 鐢ㄧ被鍗冲彲锛屽叾浠栭兘鐢ㄧ函鍑芥暟锛夈€?8. **涓嶄娇鐢ㄦ暟鎹簱 / 缂撳瓨 / 闃熷垪**銆傛墍鏈夌姸鎬侀兘鍦ㄥ唴瀛橀噷銆佹墍鏈夋暟鎹兘浠?`data/*.json` 璇汇€?9. **缁濅笉纭紪鐮?API key**銆俙config.py` 鐢?`python-dotenv` 鍔犺浇 `.env`锛屼粠鐜鍙橀噺鍙栥€?10. **缁濅笉寮曞叆鏂颁緷璧?*銆俙requirements.txt` 鍙湁 `openai`, `fastapi`, `uvicorn`, `python-dotenv` 鍥涢」銆傞渶瑕佹柊澧炲厛闂敤鎴枫€?11. **姣忎釜妯″潡蹇呴』鏈?`__main__` 娈?*锛岃兘鐩存帴 `python agent/xxx.py` 杩愯鍋氳嚜娴嬶紝鎵撳嵃鏈夋剰涔夌殑缁撴灉缁欑敤鎴风湅銆?12. **鍐欏畬浠讳綍浠ｇ爜鍚?*锛屽憡璇夌敤鎴凤細鈶?鎬庝箞杩愯瀹冩潵楠岃瘉锛涒憽 鏈熸湜鐪嬪埌浠€涔堣緭鍑恒€?
---

## 7. 妯″潡 API 鍚堢害锛堝嚱鏁扮鍚嶆槸濂戠害锛屽埆鎿呰嚜鏀癸級

### `agent/llm.py`

```python
def ask_llm(prompt: str, system: str = "", timeout: int = 8) -> str | None:
    """
    璋冪敤 DeepSeek銆傛垚鍔熻繑鍥炲瓧绗︿覆锛涘け璐?瓒呮椂杩斿洖 None锛堢粷涓嶆姏寮傚父锛夈€?    鐢?openai 鍖咃紝base_url='https://api.deepseek.com', model='deepseek-chat'銆?    API key 浠?config 璇伙紝涓嶈鍐欐銆?    """
```

**鐢ㄦ硶绾緥**锛氶」鐩噷鍙湁涓ゅ璋冪敤 `ask_llm`鈥斺€擿parser.py` 鍜?`tools.py::compose_share_card`銆傚叾浠栨枃浠?import 瀹冨嵆瑙嗕负杩濊銆?
### `agent/logbook.py`

```python
class LogBook:
    def add(self, step: str, status: str, message: str) -> None: ...
    def print_all(self) -> None: ...
    def to_list(self) -> list[dict]: ...
```

### `agent/parser.py`

```python
def parse_request(text: str, logbook: LogBook) -> dict:
    """
    涓€鍙ヨ瘽 鈫?request锛堢粨鏋勮 5.3锛夈€備笁灞傚厹搴曟案杩滆繑鍥炴湁鏁?dict銆?    绗竴灞傦細璋?ask_llm 璁╂ā鍨嬭繑鍥炵函 JSON銆?*蹇呴』鍖呭惈 missing 鏁扮粍**鈥斺€?        妯″瀷鍚笉娓?娌″惉鍒扮殑瀛楁鍚嶆斁杩?missing锛堝 ["party_size","budget_per_person"]锛夈€?        妯″瀷鍙爣缂哄け锛屼笉鐢熸垚闂鏂囨湰鎴栭€夐」 chip銆?    绗簩灞傦細鍏抽敭璇嶈鍒欏尮閰嶏紱浠讳綍璧拌鍒欎篃娌℃硶纭畾鐨勫瓧娈典篃鍔犺繘 missing銆?    绗笁灞傦細鐢?samples.json 绗竴鏉★紱missing 鐣欑┖锛堝厹搴曚篃绠?琛ュ叏浜?锛夈€?    姣忔瑙ｆ瀽寰€ logbook 鍐欐棩蹇楄鏄庣敤浜嗗摢涓€灞傘€?    """
```

**鍏抽敭绾緥**锛欴eepSeek 鐨勬彁绀鸿瘝蹇呴』 `system` 閲屽啓鏄?鍙繑鍥炵函 JSON銆佷笉瑕?markdown銆佷笉瑕佸墠鍚庡浣欐枃瀛?锛屼笖鏄庣‘瑕佹眰"鍚笉鍒扮殑瀛楁鍊肩疆涓?null 骞舵妸瀛楁鍚嶅姞杩?missing 鏁扮粍"銆傛嬁鍒板洖澶嶈鍏堝幓鎺夊彲鑳界殑 ``` 鍖呰９鍐?`json.loads`銆?
### `agent/clarify.py`

```python
def decide_clarifications(request: dict, logbook: LogBook) -> list[dict]:
    """
    鏍规嵁 request.missing 鍜?request.intent_tags[0] 鍐冲畾杩介棶鍝嚑涓瓧娈点€?    姝ラ锛?      鈶?璇?data/clarify_questions.json 鎷垮埌鎵€鏈夐棶棰樻ā鏉裤€?      鈶?瀵?request.missing 閲岀殑姣忎釜瀛楁锛屾煡瀹冪殑 priority dict锛?         intent = request.intent_tags[0] if request.intent_tags else "default"
         prio = template.priority.get(intent, template.priority["default"])
      鈶?杩囨护鎺?prio == 99 鐨勶紙鍦ㄨ鎰忓浘涓嬩笉闂級銆?      鈶?鎸?prio 鍗囧簭鎺掞紝鍙栧墠 3 涓€?      鈶?姣忔潯鍘绘帀 priority 瀛楁鍚庤繑鍥烇紙缁撴瀯瑙?5.8锛夈€?    杩斿洖 [] 琛ㄧず娌℃湁闇€瑕佽拷闂殑銆傛湰鍑芥暟绾?Python 瑙勫垯锛岀粷涓嶈皟鐢?LLM銆?    姣忔鍐崇瓥寰€ logbook 鍐欎竴鏉℃棩蹇楄鏄庨棶浜嗗摢鍑犱釜瀛楁銆佷负浠€涔堛€?    """

def merge_answers(request: dict, answers: dict) -> dict:
    """
    鎶婅拷闂殑绛旀鍚堝苟鍥?request銆?    answers 褰㈠ {"party_size": 4, "budget_per_person": 150}銆?    琚～鍏ョ殑瀛楁浠?request.missing 閲岀Щ闄ゃ€傝繑鍥炴洿鏂板悗鐨?request锛堝悓涓€瀵硅薄灏卞湴淇敼涔熷彲锛夈€?    """
```

**閾佸緥**锛氶棶棰樻枃鏈紙`text`锛夊拰閫夐」锛坄options`锛夊彧鑳芥潵鑷?`clarify_questions.json` 妯℃澘锛?*缁濅笉鑳界敱 LLM 鐜板満鐢熸垚**銆傛ā鏉挎病瑕嗙洊鍒扮殑瀛楁灏变笉闂€?
### `agent/catalog.py`

```python
def search_merchants(
    slot_role: str,
    request: dict,
    logbook: LogBook,
    want: str | list[str] | None = None,
    exclude_ids: set[str] | None = None,
) -> list[dict]:
    """
    浠?merchants.json 妫€绱㈠尮閰嶅€欓€夊苟鎸?鍖归厤鍒?+ 骞垮憡鏉冮噸"鎺掑簭銆?    姝ラ锛氣憼 鍏堟寜 slot_role 鍜?want 杩囨护锛涒憽 鐢?request 鐨?hard_limits 杩囨护
    锛堣秴棰勭畻銆佷笉鍦ㄨ惀涓氥€佽窛绂昏秴闄愮殑韪㈡帀锛夛紱鈶?鎺掗櫎 exclude_ids锛涒懀 璁＄畻
    鍖归厤鍒嗭紙缁煎悎 rating, preferences 鍛戒腑, 璺濈锛夛紱鈶?骞垮憡鏉冮噸 =
    min(15, ad_bid / 8000)锛涒懃 鎸?鍖归厤鍒?+ 骞垮憡鏉冮噸"闄嶅簭锛岀粰姣忔潯鍔犱竴涓?    is_promoted 鏍囪锛堟槸鍚﹁繘鍏ラ潬鍓嶄綅缃笖 ad_bid 璧蜂富瀵硷級銆?    """
```

**閾佸緥**锛氱‖绾︽潫杩囨护姘歌繙鍦ㄥ箍鍛婃潈閲嶄箣鍓嶃€備笉鑳藉洜涓?`ad_bid` 楂樺氨璁╄秴棰勭畻/娌″紑闂ㄧ殑鍟嗘埛鍐掑嚭鏉ャ€?
### `agent/tools.py`

```python
def check_availability(merchant_id: str, time_str: str, party_size: int, logbook: LogBook) -> dict:
    """杩斿洖 {"ok","data":{"available":bool,"queue_minutes":int},"message"}"""

def get_travel_time(from_area: str, to_area: str, logbook: LogBook) -> dict:
    """杩斿洖 {"ok","data":{"walk":int,"taxi":int,"metro":int},"message"}"""

def book_item(merchant_id: str, time_str: str, party_size: int, logbook: LogBook) -> dict:
    """杩斿洖 {"ok","data":{"booking_id":str},"message"}锛涗笉鍙敤鏃?ok=False"""

def compose_share_card(plan: dict, logbook: LogBook) -> str:
    """鐢熸垚鍙戝埌缇ら噷鐨勬枃妗堛€傚厛璇?ask_llm 娑﹁壊锛孨one 灏辫蛋瑙勫垯妯℃澘鍏滃簳銆傛案杩滆繑鍥?str銆?""
```

### `agent/planner.py`

```python
def build_itinerary(request: dict, logbook: LogBook) -> list[dict]:
    """
    鎸?scenes.json 鍙栬鍦烘櫙鐨勬Ы浣嶆ā鏉匡紝閫愭Ы璋?search_merchants 鎷垮€欓€夛紝
    鍙栨瘡妲?top1 缁勬柟妗?A銆佹浼樼粍鏂规 B锛涙瘡妲藉啀淇濈暀 2 涓閫夊～杩?slot_alternatives銆?    鐢?get_travel_time 璁＄畻鑺傜偣涔嬮棿浜ら€氭椂闂达紝鎺掑嚭 steps 鏃堕棿杞淬€?    鎬绘椂闀垮敖閲忚惤鍦?request.window_hours 鍐咃紱鎵句笉鍒板畬缇庢柟妗堝氨杩斿洖鏈€鎺ヨ繎鏂规骞舵爣 risks銆?    杩斿洖鏂规鍒楄〃锛堥€氬父 2 涓級锛岀粨鏋勮 5.4銆?    """

def score_plan(plan: dict, request: dict, profile: dict | None = None) -> dict:
    """
    100 鍒嗗埗锛氫汉缇ら€傞厤 25 / 鏃堕棿 20 / 棰勭畻 15 / 璺濈 15 / 鎺掗槦 15 / 浜偣 10銆?    鑻?profile 涓嶄负绌轰笖 plan 鍛戒腑鐢诲儚鍋忓ソ锛屼汉缇ら€傞厤棰濆鍔犲垎骞跺湪 reason 閲岀偣鍑恒€?    杩斿洖 {"total":..., "people_fit":..., "time":..., "budget":..., "distance":...,
            "queue":..., "highlight":..., "reason":"涓枃浜鸿瘽"}
    reason 蹇呴』瑙ｉ噴"鍑犱釜鍋忓ソ鎵撴灦鏃舵€庝箞鍙栬垗"銆?    """

def replan(session: dict, exception_type: str, logbook: LogBook) -> dict:
    """
    灞€閮ㄩ噸鎺掆€斺€斿彧鎹㈠潖鎺夌殑閭ｄ竴鐜€?    exception_type 鈭?{"restaurant_full","ticket_soldout","time_conflict"}銆?    restaurant_full锛氭爣 EAT 鑺傜偣涓哄潖锛屽皢璇?id 鍔犲叆 session.rejected_ids锛?                     鍦ㄥ悓鍖哄煙鐢?search_merchants 鎵惧閫?EAT 鍟嗘埛锛孭LAY 涓嶅姩銆?    ticket_soldout锛氭爣 PLAY 鑺傜偣涓哄潖锛屽皢璇?id 鍔犲叆 rejected_ids锛屽悓 slot_role
                    鍚屽晢鍦堟壘澶囬€?PLAY锛孍AT 鑺傜偣灏介噺涓嶅姩銆?    time_conflict锛氭暣鏉¤绋嬮『寤?60 鍒嗛挓锛岃妭鐐瑰晢鎴蜂繚鎸佷笉鍙橈紝閲嶆帓鏃堕棿杞淬€?    杩斿洖 {"before":...,"after":...,"reason":"涓枃涓€鍙ヨ瘽","still_ok":{...},"plan":鏂皃lan}
    """
```

**閾佸緥**锛歚replan` 蹇呴』灞€閮ㄩ噸鎺掞紝缁濅笉閲嶅仛鏁翠釜鏂规銆傞噸鎺掑悗鍙楀奖鍝嶈妭鐐硅杩?`session.rejected_ids`锛堣繖鏄负浠€涔?鐢ㄦ埛鎷掔粷杩囧氨涓嶅啀鎺?鎴愮珛锛夈€?
### `agent/addon.py`

```python
def suggest_addon(plan: dict, request: dict, logbook: LogBook) -> dict | None:
    """
    鍦ㄦ柟妗?EAT 鑺傜偣涔嬪悗寤鸿涓€涓?ADDON锛?椤鸿矾鍔犱竴鏉?锛夈€?    瀹夊叏杩囨护閾佸緥锛?      - request.transport == "self_drive" 鈫?鎺掗櫎 flags.alcohol == True 鐨勫晢鎴枫€?      - request.has_kid 涓虹湡 鎴?scene 鍚瀛?鈫?鎺掗櫎涓嶉€傞緞椤癸紝浼樺厛 kid_friendly銆?    娌℃湁鍚堥€傜殑灏辫繑鍥?None銆?    """
```

### `agent/core.py`

```python
class Agent:
    def __init__(self): ...
    def run(self, text: str) -> dict:
        """
        parse_request 鈫?decide_clarifications銆?        鑻?clarifications 闈炵┖锛氬啓鍏?session.clarifications锛屾妸 pending_clarify=True锛?            **绔嬪嵆杩斿洖 session锛堜笉璋?build_itinerary锛?*鈥斺€旂瓑寰呭墠绔嬁鐫€ /clarify 鍥炰紶绛旀銆?        鑻?clarifications 涓虹┖锛氱洿鎺ヨ蛋 build_itinerary锛屾妸鏂规瀛樿繘 session 杩斿洖銆?        """
    def submit_clarifications(self, answers: dict) -> dict:
        """
        鍓嶇璋?/clarify 鏃惰繘鍏ユ澶勩€?        merge_answers(session.request, answers) 鈫?娓呯┖ clarifications銆佺疆 pending_clarify=False
        鈫?缁х画璧?build_itinerary 鈫?杩斿洖 session銆?        """
    def choose(self, plan_index: int) -> dict: ...
    def confirm_and_execute(self) -> dict:
        """瀵归€変腑鏂规鐨勬瘡涓?merchant 鑺傜偣 book_item锛屽啀 compose_share_card"""
    def inject_exception(self, exception_type: str) -> dict:
        """璋?replan锛屾洿鏂?session.chosen锛岃繑鍥?replan 缁撴灉"""
    def reject_merchant(self, merchant_id: str) -> None:
        """鍔犲叆 session.rejected_ids锛屼笅娆℃绱㈠氨涓嶅啀鍑虹幇"""
```

**閾佸緥**锛歚run` 鍙 `clarifications` 闈炵┖灏?*绔嬪嵆杩斿洖**锛屼笉瑕佺粫杩囪拷闂洿鎺ョ敓鎴愭柟妗堛€傜粫杩囦細鐮村潖"鍏堥棶娓呭啀鍔炰簨"鐨勪骇鍝侀€昏緫銆?
### `server.py`锛團astAPI 钖勬湇鍔″眰锛?
涓氬姟閫昏緫鍏ㄩ儴鍦?`agent/` 閲岋紝`server.py` **鍙仛 HTTP 缈昏瘧**銆?
```
POST /plan       {text}                          鈫?agent.run锛岃繑鍥?session
                                                   锛堣嫢鏈夎拷闂紝session.clarifications 闈炵┖銆乸ending_clarify=True锛?POST /clarify    {answers}                       鈫?agent.submit_clarifications锛岃繑鍥?session锛堝惈 plans锛?POST /confirm    {plan_index}                    鈫?choose + confirm_and_execute
POST /exception  {type}                          鈫?inject_exception
POST /reject     {merchant_id}                   鈫?reject_merchant
GET  /merchants                                  鈫?杩斿洖 merchants.json 鍏ㄩ儴
POST /merchants  {merchant 瀵硅薄}                  鈫?鏂板鎴栨洿鏂颁竴涓晢鎴凤紙鍐欏洖 merchants.json锛?```

瑕佹眰锛氣憼 鍔?CORS 鍏佽鎵€鏈夋潵婧愶紱鈶?涓€涓叏灞€ Agent 瀹炰緥锛涒憿 鎵€鏈夋帴鍙ｈ繑鍥?JSON 鍚?`logs` 瀛楁锛涒懀 try/except 鍖呬綇锛岄敊璇繑鍥炲弸濂?JSON 涓嶈 500锛涒懁 鎶?`web/` 浣滀负闈欐€佽祫婧愭彁渚涖€?
---

## 8. 鍏抽敭鏈哄埗璇﹁В

### 8.1 妲戒綅绯荤粺锛氬崱鐗囦笉娣风被鐩?
姣忓紶鍗＄墖瀵瑰簲涓€涓Ы浣嶏紝妲戒綅鏈?`role` 鈭?`{PLAY, EAT, STAYIN, ADDON}`銆傚崱鐗囬噷灞曠ず鐨勬墍鏈夊€欓€?merchant 蹇呴』 `slot_role` 绛変簬鍗＄墖鐨勬Ы浣?role銆?*鍓ф湰鏉€鍜岄鍘呮案杩滀笉鍦ㄥ悓涓€寮犲崱閲屻€?* 杩欐槸缁撴瀯鎬т繚璇侊紝涓嶉潬鎻愰啋銆?
### 8.2 浣ｉ噾鏃嬮挳锛堝叕寮€ + 鍙皟 + 鎷掔粷鎶戝埗锛?
- 姣忔潯 merchant 鏈?`ad_bid` 瀛楁锛岄粯璁?0銆傚湪 `admin.html` 鍚庡彴椤靛彲缂栬緫銆?- `catalog.search_merchants` 鎺掑簭鍒?= `鍖归厤鍒?+ min(15, ad_bid / 8000)`銆?- 鍥犲箍鍛婃潈閲嶈繘鍏ラ潬鍓嶄綅缃殑鍟嗘埛鏍?`is_promoted=True`锛屽墠绔墦"鎺ㄥ箍"灏忔爣銆?- **纭害鏉熻繃婊わ紙棰勭畻銆佽惀涓氥€佽窛绂伙級濮嬬粓鍦ㄥ箍鍛婃潈閲嶄箣鍓?*鈥斺€擿ad_bid` 涓嶈兘璁╄繚鍙嶇‖绾︽潫鐨勫晢鎴峰嚭鐜般€?- `session.rejected_ids` 閲岀殑鍟嗘埛**鍦ㄦ帓搴忓墠灏辫鍓旈櫎**锛宍ad_bid` 鍐嶉珮涔熶笉鍐嶅嚭鐜般€?
### 8.3 寮傚父灞€閮ㄩ噸鎺掞紙缁濅笉閲嶅仛鏁存柟妗堬級= **鍔ㄦ€佹椂闂村垎閰?*

`replan` 鏀跺埌涓€绫诲紓甯?鈫?鏍囪鍙楀奖鍝嶈妭鐐?鈫?鎶婂畠鍔犺繘 `rejected_ids` 鈫?鐢?`search_merchants` 鎵惧悓鍖哄煙鍚?slot_role 澶囬€?鈫?鍙浛鎹㈣鑺傜偣锛屽叾瀹冭妭鐐逛繚鐣?鈫?閲嶇畻浜ら€?棰勭畻/鏃堕棿杞?鈫?杩斿洖 `before/after` 瀵规瘮鍜屼竴鍙ヤ腑鏂囪В閲娿€?
**瀵瑰鍛藉悕**锛氳繖濂楁満鍒剁殑瀹樻柟鍚嶅瓧鏄€?*鍔ㄦ€佹椂闂村垎閰?*銆嶁€斺€旇繖鏄禌棰樿瘎鍒?鍒涙柊鎬?鏄庨」鐨勫師璇嶃€傝璁℃枃妗ｃ€丏emo 瑙ｈ銆佺瓟杈╁洖搴旈噷**涓€寰嬩娇鐢ㄨ繖涓瘝**锛屼笉瑕佸彨"寮傚父澶勭悊"銆?
**寮傚父瑙﹀彂鐨勪袱涓潵婧?瀵瑰簲璇勫垎"鍗忓悓纭鍙婂弽棣堥棴鐜?鏄庨」)**:
1. **鐢ㄦ埛涓诲姩鎸夐挳**: 鍓嶇涓変釜寮傚父鎸夐挳("椁愬巺婊″骇/娲诲姩鍞絼/鏈嬪弸璇村お璧?)銆?2. **妯℃嫙濂藉弸鍙嶉娑堟伅**: 鍓嶇鍦ㄥ垎浜崱涔嬪悗,鍦ㄦ墽琛屾棩蹇楀尯娓叉煋 1-2 鏉℃ā鎷熺殑濂藉弸缇よ亰鍥炲(濡?灏忔潕: 鏃堕棿鏈夌偣璧?鑳戒笉鑳芥櫄涓€鐐?"),鐢ㄦ埛鐐瑰嚮璇ユ秷鎭嵆瑙﹀彂瀵瑰簲寮傚父鐨?replan銆?*杩欏氨鏄?鍗忓悓纭鍙婂弽棣堥棴鐜?鍦?demo 閲岀殑鍏蜂綋褰㈡€?*鈥斺€旀妸寮傚父鍖呰鎴?鏈嬪弸鐨勫弽棣?,鑰屼笉鏄娊璞＄殑鎸夐挳銆傚悗绔唬鐮佷笉鍙?鍙敼鍓嶇鏂囨鍜岃Е鍙戝櫒銆?
### 8.4 LLM 涓夊眰鍏滃簳锛堝湪 `parser.py`锛?
```
绗竴灞傦細ask_llm 杩斿洖 鈫?瀹夊叏 json.loads 鈫?鎴愬姛灏辩敤銆?绗簩灞傦紙涓€灞傚け璐ワ級锛氬叧閿瘝瑙勫垯鍖归厤 + 鍚堢悊榛樿鍊笺€?绗笁灞傦紙鍓嶄袱灞傞兘娌′骇鍑猴級锛氳繑鍥?samples.json 绗竴鏉°€?```

**姘歌繙鍦?`__main__` 娴嬩竴閬?DeepSeek 涓嶅彲鐢ㄦ椂涔熻兘璺?銆?*

### 8.5 浼氳瘽鍐呮嫆缁濊蹇?
`session.rejected_ids` 鏄釜 `set`锛屼笁绉嶉€斿緞浼氳 id 杩涘叆瀹冿細鈶?`replan` 琚崲鎺夌殑鑺傜偣锛涒憽 鐢ㄦ埛鍦ㄥ墠绔偣"鎹竴涓?鎴?涓嶅枩娆?涓诲姩鎷掔粷锛涒憿 璋?`/reject` 鎺ュ彛銆俙catalog.search_merchants` 鐨?`exclude_ids` 鍙傛暟姘歌繙浠庤繖涓泦鍚堜紶鍏ャ€?
### 8.6 绀轰緥鐢ㄦ埛鐢诲儚

`data/user_profile.json` 鏄竴涓?*婕旂ず鐢ㄧ敾鍍?*锛岀敱 `agent/core.py` 鐨?`Agent.__init__` 鍔犺浇杩?`session.profile`锛屼紶缁?`score_plan`銆傝嫢鏂规鍛戒腑鐢诲儚鍋忓ソ锛堝"瀹夐潤""涓嶈荆"锛夛紝`reason` 閲屽繀椤荤偣鍑?鍥犱负浣犱互鍓嶅亸濂解€?銆?*杩欐槸绀轰緥,涓嶆槸鐪熻法浼氳瘽瀛︿範鈥斺€旇法浼氳瘽瀛︿範鍐欏湪璁捐鏂囨。閲屻€?*

### 8.7 鏅鸿兘杩介棶锛圠LM 鏍囩己澶?+ Python 鍐冲畾闂粈涔堬級

鐢ㄦ埛涓€鍙ヨ瘽寰€寰€璇翠笉鍏紙濡?鎯冲拰鏈嬪弸鎵撳墽鏈潃"鈥斺€旀病璇村嚑浜恒€佸嚑鐐广€佸灏戦挶锛夈€傜郴缁熻"鐪嬩技鑱槑鍦版寜鎰忓浘闂闂殑"锛屼絾**闂粈涔堛€佺粰浠€涔堥€夐」缁濅笉鐢?LLM 鐜板満鐢熸垚**锛屽惁鍒欐枃妗堜笉鍙帶銆侀€夐」鏍煎紡涔便€佹參銆傝璁″垎涓ゅ眰锛?
**绗竴灞?路 LLM 鍙爣缂哄け锛堝湪 `parse_request` 閲屽畬鎴?涓嶅鍔?LLM 璋冪敤娆℃暟锛夈€?*
DeepSeek 鐨?system 鎻愮ず璇嶉噷鏄庣‘瑕佹眰锛氬惉涓嶅埌 / 涓嶇‘瀹氱殑瀛楁鍊肩疆 `null`锛屽苟鎶婂瓧娈靛悕鍔犺繘 `missing` 鏁扮粍銆傝鍒欏厹搴曞眰鑻ヤ粛鏃犳硶纭畾涔熷姞杩?`missing`銆侺LM **涓?*鐢熸垚闂鏂囨湰銆佷笉鐢熸垚 chip 閫夐」銆?
**绗簩灞?路 Python 鍐冲畾闂摢浜涘瓧娈点€佺敤浠€涔堟枃妗堬紙`agent/clarify.py`锛夈€?*
妯℃澘搴?`data/clarify_questions.json` 缁欐瘡涓彲鑳界己澶卞瓧娈甸厤锛氶棶棰樻枃鏈€乧hip 閫夐」鏁扮粍銆乣priority` dict锛堟瘡绉?intent 涓€涓紭鍏堢骇鏁板瓧锛宍99` = 璇ユ剰鍥句笅涓嶉棶锛夈€俙decide_clarifications(request)` 鎸?`request.intent_tags[0]` 鏌ヤ紭鍏堢骇銆佹帓搴忋€佸彇鍓?3 涓渶璇ラ棶鐨勩€?
**涓句袱涓叿浣撲緥瀛愯鏄?鍥?intent 鑰屽彉"**锛?- `intent="鍓ф湰鏉€"`銆乵issing 鍚?`party_size` 鍜?`transport`锛氬墽鏈潃瀵逛汉鏁版瀬鏁忔劅锛坄party_size.priority["鍓ф湰鏉€"]=1`锛夈€佷笉澶叧蹇冧氦閫氾紙`transport.priority["鍓ф湰鏉€"]=99`锛夆啋 鍙棶浜烘暟銆?- `intent="鐢熸棩"`銆乵issing 鍚?`party_size` 鍜?`budget_per_person`锛氱敓鏃ュ棰勭畻鏁忔劅锛坄budget.priority["鐢熸棩"]=1`锛夆啋 浼樺厛闂绠椼€?
**娴佺▼鎺ュ叆锛坄agent/core.py::run`锛?*锛?```
parse_request 鈫?decide_clarifications
  鈹溾攢 闈炵┖锛歴ession.clarifications = 瀹冿紝pending_clarify = True锛岀珛鍗宠繑鍥炪€傚墠绔脊杩介棶 UI銆?  鈹斺攢 绌猴細鐩存帴 build_itinerary锛屾妸鏂规瀛樿繘 session 杩斿洖銆?```
鐢ㄦ埛绛斿畬 鈫?鍓嶇璋?`/clarify {answers}` 鈫?`submit_clarifications(answers)` 鈫?`merge_answers` 鈫?`build_itinerary` 鈫?杩斿洖瀹屾暣 session銆?
**閾佸緥閲嶇敵**锛氣憼 闂鏂囨湰鍜岄€夐」 chip 姘歌繙鏉ヨ嚜妯℃澘锛?*涓嶅厑璁哥敱 LLM 鐢熸垚**锛涒憽 妯℃澘娌¤鐩栫殑瀛楁灏变笉闂紱鈶?杩介棶 鈮? 涓?灏侀《涓€杞?涓嶅仛澶氳疆鑱婂ぉ銆?
---

## 9. 缁濆绂佹锛圢EVER DO锛?
1. 鉂?璋冪敤鐪熷疄鐨勭編鍥?/ 楂樺痉 / 澶т紬鐐硅瘎 / 浠讳綍澶栭儴鍟嗕笟 API銆?*杩欐槸 Mock-only 椤圭洰銆?*
2. 鉂?璁╁ぇ妯″瀷鍐冲畾"鐜板湪璋冨摢涓伐鍏?銆傛祦绋嬬敱 Python 浠ｇ爜椤哄簭椹卞姩銆?3. 鉂?鎶?LLM 璋冪敤濉炶繘 `parser.py` 鍜?`tools.py::compose_share_card` 涔嬪鐨勪换浣曞湴鏂广€?4. 鉂?鍦ㄥ崱鐗?/ 浠讳綍 UI 鍖哄潡閲屾妸涓嶅悓 `slot_role` 鐨?merchant 娣峰湪涓€璧枫€?5. 鉂?璁?`ad_bid` 鍑岄┚浜庣‖绾︽潫涔嬩笂锛堝鑷磋秴棰勭畻 / 娌″紑闂ㄧ殑鍟嗘埛鍐掑ご锛夈€?6. 鉂?`time.sleep` 瓒呰繃 0.8 绉掋€?7. 鉂?鍦?`replan` 閲岄噸鍋氭暣涓柟妗堛€傚繀椤诲眬閮ㄦ浛鎹€?8. 鉂?鎶?API key 鍐欒繘浠讳綍 `.py` 鎴?`.html`銆傛案杩滀粠 `.env` 缁?`config.py` 璇汇€?9. 鉂?浠讳綍 Tool 鍑芥暟鎶涘嚭鏈崟鑾峰紓甯哥粰涓婂眰銆傚け璐ヤ竴寰嬭繑鍥?`{"ok":False,...}`銆?10. 鉂?鏂板渚濊禆銆佹柊澧炵洰褰曘€佹敼 Schema 瀛楁鈥斺€斿仛杩欎笁浠朵簨鍓嶅厛闂敤鎴枫€?11. 鉂?寮曞叆鏁版嵁搴?/ Redis / 娑堟伅闃熷垪 / 鍚庡彴浠诲姟銆傝繖涓」鐩氨鏄嚑涓?JSON + 鍑犳 Python銆?12. 鉂?鍦?`server.py` 閲屽啓涓氬姟閫昏緫銆傚畠鍙仛 HTTP 缈昏瘧銆?13. 鉂?鐢?React / Vue / Vite / Tailwind 绛夐渶瑕佹瀯寤虹殑鍓嶇銆俙web/` 鏄崟鏂囦欢鍘熺敓 HTML+CSS+JS銆?14. 鉂?璁╁ぇ妯″瀷鐢熸垚鏅鸿兘杩介棶鐨勯棶棰樻枃鏈垨閫夐」 chip銆侺LM 鍙爣 `missing`锛岄棶棰樻ā鏉跨敱 `data/clarify_questions.json` 鎺у埗锛堣 搂8.7锛夈€?15. 鉂?涓嶅啓娉ㄩ噴銆佷笉鍐?`__main__` 娴嬭瘯銆佷笉鍛婅瘔鐢ㄦ埛"鎬庝箞楠岃瘉"銆?
---

## 10. 楠屾敹鏂瑰紡锛氭案杩滈潬"杩愯 + 鑲夌溂"锛屼笉闈犺浠ｇ爜

鍥㈤槦鎴愬憳鏄枃绉戠敓锛?*涓嶈浠ｇ爜銆佷笉娣?debug**銆傛墍浠ヤ綘浜や粯浠讳綍涓€娈典唬鐮佸繀椤绘弧瓒筹細

1. **鍙洿鎺ヨ繍琛岀殑 `__main__` 鑷祴娈点€?* 渚嬪锛?   ```python
   if __name__ == "__main__":
       log = LogBook()
       r = parse_request("浠婂ぉ涓嬪崍鍜屾湅鍙?涓汉鍑哄幓鐜╋紝鎯虫媿鐓у悆楗笉瑕佸お绱紝浜哄潎150", log)
       print("瑙ｆ瀽缁撴灉:", r)
       log.print_all()
   ```
2. **鍛婅瘔鐢ㄦ埛"鎬庝箞璺戙€佺湅浠€涔?**銆備緥濡傦細"璺?`python agent/parser.py`锛屼綘搴旇鐪嬪埌 scene=friends_out銆乸arty_size=4銆乸references 鍚?photo銆?
3. **鏁呮剰鍒堕€犻敊璇矾寰勪篃楠岃瘉涓€閬?*銆傛瘮濡?`parser.py` 鐨勮嚜娴嬭鍚屾椂娴?DeepSeek 姝ｅ父"鍜?DeepSeek 涓嶅彲鐢?涓ょ鎯呭喌銆?
---

## 11. 浣狅紙Claude Code锛夌殑宸ヤ綔绾緥

- **涓€娆″彧鍔ㄤ竴涓枃浠?/ 涓€涓嚱鏁般€?* 鐢ㄦ埛鐨勮姹傝嫢娑夊強澶氫釜鏂囦欢锛屽厛鍒楄鍒掔瓑鐢ㄦ埛纭銆?- **鐪嬩笉鎳傛垨鏈夋涔夊厛闂€?* 渚嬪"杩欐槸瑕佹柊澧炲瓧娈佃繕鏄敼 Schema锛?鈥斺€旇€屼笉鏄洿鎺ュ姩鎵嬨€?- **淇濈暀鏃犲叧浠ｇ爜涓嶅姩銆?* 鍝€曚綘瑙夊緱鍒鍙互浼樺寲銆傞噸鏋勬棤鍏充唬鐮佽涓鸿繚瑙勩€?- **鎶ラ敊鏃跺厛瑕佸畬鏁存姤閿欍€?* 鐢ㄦ埛璐翠竴鍗婃姤閿欒鍥為棶"璇锋妸瀹屾暣鎶ラ敊鍜屽鐜板懡浠よ创鍥炴潵"銆?- **娉ㄩ噴鐢ㄤ腑鏂囷紝鍐欑粰闈炵鐝湅銆?* 涓嶈鍐?DRY""SRP"杩欑鏈銆?- **姣忔浠ｇ爜鏈熬鍛婅瘔鐢ㄦ埛鎬庝箞楠岃瘉銆?* 杩欐槸浣犱氦浠樺畬鎴愮殑涓€閮ㄥ垎銆?- **濡傛灉鐢ㄦ埛鐨勮姹傚拰鏈鏍间功鍐茬獊**锛氬厛鎸囧嚭鍐茬獊銆佸紩鐢ㄦ湰瑙勬牸涔︾鍑犺妭銆佽姹傜敤鎴峰喅瀹氥€傜粷涓嶆倓鎮勭粫杩囥€?
---

## 12. 14 澶╅噷绋嬬绱㈠紩锛堟墜鍐屽搴斿埌鏈鏍间功锛?
| Day | 涓昏寤?/ 鏀圭殑鏂囦欢 | 瀵瑰簲鏈鏍间功绔犺妭 |
|---|---|---|
| 0 | 椤圭洰楠ㄦ灦銆乣config.py`銆乣agent/llm.py`銆乣.env` | 搂2 搂4 搂6 |
| 1 | `agent/logbook.py` | 搂5.7 搂7 |
| 2 | `data/*.json`锛堝叚涓枃浠讹紝鍚?`clarify_questions.json`锛?| 搂5.1 搂5.2 搂5.8 |
| 3 | `agent/catalog.py`銆乣agent/tools.py`锛堝墠涓変釜宸ュ叿锛?| 搂7 搂8.2 |
| 4 | `agent/parser.py`锛堝惈 `missing` 瀛楁锛?| 搂5.3 搂7 搂8.4 |
| 5 | `agent/planner.py`锛坆uild + score锛?| 搂5.4 搂7 搂8.6 |
| 6 | `agent/core.py`銆乣cli.py` | 搂5.5 搂7 |
| 7 | `agent/planner.py::replan`锛坮estaurant_full锛?| 搂7 搂8.3 搂8.5 |
| 8 | `replan` 鎵╁睍涓ょ被寮傚父 + 楠岃瘉 `stay_in` 璺戦€?| 搂8.3 |
| 9 | `server.py`锛堝惈 `/clarify`锛夈€乣web/admin.html` | 搂7 搂8.2 |
| 10 | `web/app.html`锛堜富娴佺▼椤?+ 杩介棶 UI锛?| 搂8.1 搂8.2 搂8.7 |
| 11 | `agent/clarify.py` + `agent/addon.py` + 璐﹀崟鍗?+ 灞曠ず灞?| 搂7 搂8.7 |
| 12 | "琛岀▼杩涜涓?瑙嗗浘锛堝啿鍒郝峰彲鐮嶏級 | 鈥?|
| 13 | UI 鎵撶（ + 璁捐鏂囨。 | 鈥?|
| 14 | 鎺掔粌 + 鑷祴 + 褰曞睆 | 搂2锛堢‖绾︽潫瀵硅处锛?|

---

## 13. 涓嶈寤虹殑鍔熻兘锛堝啓鍦ㄨ璁℃枃妗?PPT 鍗冲彲鐨勬竻鍗曪級

濡傛灉鐢ㄦ埛鎻愬埌涓嬮潰杩欎簺锛屽憡璇変粬锛?杩欐槸 v1 鍐崇瓥閲屽綊鍦?鏈潵鎵╁睍'鐨勶紝涓嶈繘涓ゅ懆寮€鍙戙€傚啓杩涜璁℃枃妗ｇ殑'鏈潵鎵╁睍'绔犺妭鍗冲彲銆?

- 鐪熷疄鐨勫箍鍛婄珵浠风郴缁熴€佺粨绠楀垎鎴愩€丆PM/CPC 璁¤垂
- 璺ㄤ細璇濆涔犵畻娉曘€佺敤鎴疯涓哄洖璁裤€侀暱鏈熷亸濂藉缓妯?- 瀹屾暣鐨勪紭鎯犲埜寮曟搸銆佽啫鑳€鍒搞€佸啓璇勪环閫佸埜婵€鍔便€佸埜鍖?- 缇庡洟閽卞寘璧婅处鍨粯銆佺湡瀹炴敮浠樻竻缁撶畻銆佸垎璐﹀疄闄呮媶璐?- 浼氬憳浣撶郴寤烘ā銆佹潈鐩婃牳閿€閾捐矾
- 鐪熷疄鍦板浘/POI/瀵艰埅鏈嶅姟

杩欎簺閮?*鍙仛灞曠ず灞?*锛堜竴涓寜閽€佷竴涓爣绛俱€佷竴涓暟瀛楋級锛屼笉寤哄悗闈㈢殑鏈哄埗銆?
---

## 14. 甯歌璇尯锛堣繚鍙嶄竴娆″氨鍥炲ご鐪嬫湰瑙勬牸涔︼級

- 鉂?**鎶?浼樺寲"褰撴垚鑷敱閫氳璇?*鈥斺€斾綘瑙夊緱鑳芥洿"浼橀泤"灏遍噸鏋勶紝缁撴灉鐮村潖浜嗙敤鎴峰凡楠岃瘉鐨勬ā鍧椼€?*鍏堥棶锛屽啀鏀广€?*
- 鉂?**鎶婂ぇ妯″瀷褰撲竾鑳介敜**鈥斺€旇兘鐢ㄨ鍒欒В鍐崇殑浜嬬敤瑙勫垯锛涘ぇ妯″瀷鍙仛璇█鐩稿叧鐨勪袱浠朵簨銆?- 鉂?**鎶?JSON 瀛楁鎮勬倓鏀瑰悕**鈥斺€擲chema 鏄绾︼紝鍓嶇銆佸悗绔€佹暟鎹笁澶勯兘渚濊禆瀹冦€傛敼鍓嶅厛闂€?- 鉂?**鍔?`try/except` 浣?except 閲岀洿鎺ユ姏**鈥斺€斿厹搴曡缁欏嚭鍚堢悊榛樿鍊兼垨 `ok=False`锛屼笉鏄啀鎶涗竴娆°€?- 鉂?**`time.sleep(2)` 璁╃敤鎴?绛夌湡瀹炵偣"**鈥斺€旈敊銆傚欢杩熶笂闄?0.8 绉掋€傝繖鏄‖绾︽潫銆?- 鉂?**鍦?`server.py` 鍐?"if 鍦烘櫙鏄畢瀹?** 杩欑涓氬姟鍒嗘敮鈥斺€斾笟鍔￠€昏緫鍦?`agent/` 閲屻€俙server.py` 鍙炕璇?HTTP銆?- 鉂?**娴嬭瘯鍙祴 happy path**鈥斺€斿繀椤诲悓鏃舵祴鍏滃簳锛欴eepSeek 涓嶅彲鐢ㄣ€佸晢鎴锋壘涓嶅埌銆佹椂娈典笉鍙敤锛屽叏閮ㄩ兘瑕佸湪 `__main__` 楠岃繃銆?
---

## 鏀跺熬

璇诲埌杩欓噷浣犲凡缁忕煡閬撹繖涓」鐩暱浠€涔堟牱銆佸繀椤婚暱浠€涔堟牱銆佺粷瀵逛笉鑳介暱浠€涔堟牱銆傛帴涓嬫潵鐢ㄦ埛浼氭寜 14 澶╂墜鍐岄€愭鍙戞寚浠ょ粰浣狅紝浣犳寜鏈鏍间功鏂藉伐銆?*姣忓畬鎴愪竴娈典唬鐮侊紝鍛婅瘔鐢ㄦ埛鎬庝箞杩愯銆佺湅浠€涔堣緭鍑烘潵楠岃瘉銆?* 椤圭洰鑳戒笉鑳戒氦浠橈紝灏遍潬杩欑"鍋氫竴涓獙鏀朵竴涓?鐨勮妭濂忋€?
鍔犳补銆?
