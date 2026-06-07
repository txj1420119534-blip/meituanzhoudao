"""
Golden smoke tests for the hackathon demo.

These tests intentionally avoid the LLM path so Pass@1 measures the
deterministic Python fallback and planner contracts used during live demos.
Run from weekend-agent:
    python tests/golden_smoke.py
"""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import agent.parser as parser_module
import agent.tools as tools_module

parser_module._try_llm_parse = lambda text: None
tools_module._llm_share_card = lambda plan: None

from agent.core import Agent
import server as server_module
from fastapi.testclient import TestClient


def kinds(session: dict) -> list[str]:
    if not session.get("plans"):
        return []
    return [s.get("kind") for s in session["plans"][0].get("steps", [])]


def categories(session: dict) -> list[str]:
    if not session.get("plans"):
        return []
    return [s.get("category") for s in session["plans"][0].get("steps", [])]


class GoldenSmoke(unittest.TestCase):
    def test_friends_out_passes_end_to_end(self):
        agent = Agent()
        session = agent.run("今天下午两点在新街口和4个朋友出去逛逛街，吃个饭，人均150，江浙菜，同商圈，无忌口，不想太累，晚上别排队")
        self.assertEqual(session["mode"], "planned")
        self.assertIn("activity", kinds(session))
        self.assertIn("restaurant", kinds(session))
        self.assertGreaterEqual(len(session["plans"]), 2)

    def test_stay_in_never_recommends_offline_restaurant(self):
        agent = Agent()
        session = agent.run("我好困，不想动，但是又菜又爱玩，今天下午两点在家，人均80，看电影点外卖")
        self.assertEqual(session["mode"], "planned")
        self.assertEqual(session["request"]["scene"], "stay_in")
        self.assertTrue(kinds(session))
        self.assertTrue(all(k == "stayin" for k in kinds(session)))
        self.assertNotIn("restaurant", kinds(session))

    def test_script_game_missing_info_goes_to_clarification(self):
        agent = Agent()
        session = agent.run("今天下午想去打本")
        self.assertEqual(session["mode"], "needs_clarification")
        keys = {q["key"] for q in session.get("clarifications_needed", [])}
        self.assertIn("party_size", keys)
        self.assertIn("start_time", keys)
        self.assertIn("budget_per_person", keys)

    def test_movie_only_does_not_auto_add_food_or_milk_tea(self):
        agent = Agent()
        session = agent.run("今天下午两点在新街口2个人去看电影，人均100，同商圈")
        self.assertEqual(session["mode"], "planned")
        self.assertEqual(session["request"]["scene"], "play_only")
        first = session["plans"][0]
        self.assertIn("电影院", categories(session))
        self.assertNotIn("restaurant", kinds(session))
        self.assertFalse(first.get("commercial_recommendations"))

        agent.choose(0)
        session = agent.confirm_and_execute()
        self.assertIsNone(session.get("addon"))
        self.assertNotIn("restaurant", [s.get("kind") for s in session["chosen"].get("steps", [])])

    def test_family_out_respects_kid_and_light_food(self):
        agent = Agent()
        session = agent.run("今天下午两点在新街口3个人带5岁的孩子和老婆出去玩3小时，人均150，江浙菜，清淡，别离家太远")
        self.assertEqual(session["mode"], "planned")
        self.assertEqual(session["request"]["scene"], "family_out")
        self.assertIn("亲子乐园", categories(session))
        for plan in session["plans"]:
            for step in plan.get("steps", []):
                if step.get("kind") in ("activity", "restaurant"):
                    self.assertTrue(step.get("flags", {}).get("kid_friendly", False))

    def test_birthday_adds_cross_category_delivery(self):
        agent = Agent()
        session = agent.run("今天下午六点在新街口和6个朋友给同事过生日，想吃融合菜，拍照，人均220，同商圈，无忌口")
        self.assertEqual(session["mode"], "planned")
        first = session["plans"][0]
        self.assertTrue(first.get("birthday_delivery"))
        self.assertIn("delivery", [s.get("kind") for s in first.get("steps", [])])
        self.assertIn("蛋糕鲜花", [s.get("category") for s in first.get("steps", [])])

    def test_vote_winner_can_return_to_host_confirmation(self):
        server_module.agent = Agent()
        server_module.VOTE_ROOMS.clear()
        client = TestClient(server_module.app)

        res = client.post("/plan", json={"text": "今天下午两点在新街口和4个朋友出去逛逛街，吃个饭，人均150，江浙菜，同商圈，无忌口，不想太累"}).json()
        self.assertTrue(res["ok"], res)
        room = res["session"]["vote_room"]
        self.assertIsNotNone(room)
        room_id = room["room_id"]

        client.post(f"/vote/{room_id}", json={"voter": "小李", "plan_index": 1})
        client.post(f"/vote/{room_id}", json={"voter": "阿岚", "plan_index": 1})
        client.post(f"/vote/{room_id}", json={"voter": "小周", "plan_index": 0})
        voted = client.get(f"/vote/{room_id}").json()
        self.assertTrue(voted["ok"], voted)
        winner = voted["room"]["winner"]
        self.assertEqual(winner["index"], 1)
        self.assertEqual(winner["votes"], 2)

        confirmed = client.post("/confirm", json={"plan_index": winner["index"]}).json()
        self.assertTrue(confirmed["ok"], confirmed)
        self.assertEqual(confirmed["session"]["chosen"]["title"], res["session"]["plans"][1]["title"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
