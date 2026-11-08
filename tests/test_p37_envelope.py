#!/usr/bin/env python3
# test_p37_envelope.py — приёмка П37 (машинная, std-only unittest).
#
# Главный тест из issue #6: «битая подпись → отказ». OverseerGate
# fail-closed: подделка любого байта конверта, чужой ключ, повтор seq,
# мусор вместо конверта — всё это отказ завода юнита, а не «исключение мимо».
# Плюс: A2A AgentCard валидируется схемой; endpoint живой.
import copy
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import signed_envelope as se  # noqa: E402
import agentcard as ac  # noqa: E402


def make_envelope(payload=None, seq=0):
    signer = se.CellSigner(b"cell-secret-01", seq=seq)
    env = signer.sign("blood", "alpha", payload if payload is not None
                      else {"heart_rate": 72, "attempt": 1})
    return signer, env


class TestSignedEnvelope(unittest.TestCase):
    def test_good_envelope_verifies(self):
        signer, env = make_envelope()
        body = se.verify(env)
        self.assertEqual(body["unit"], "alpha")
        self.assertEqual(body["kind"], "blood")

    def test_tampered_payload_refused(self):
        _, env = make_envelope()
        env["env"]["payload"]["heart_rate"] = 666  # подмена одного байта смысла
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_tampered_unit_refused(self):
        _, env = make_envelope()
        env["env"]["unit"] = "beta"
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_tampered_seq_refused(self):
        _, env = make_envelope()
        env["env"]["seq"] = 99
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_tampered_signature_chain_refused(self):
        _, env = make_envelope()
        chain = list(env["sig"]["chains"])
        chain[0] = ("0" if chain[0][0] != "0" else "1") + chain[0][1:]
        env["sig"]["chains"] = chain
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_key_substitution_refused(self):
        _, env = make_envelope()
        other = se.CellSigner(b"rogue-secret")
        env["sig"]["pub"] = other.pub
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_rogue_key_refused_by_gate(self):
        signer, env = make_envelope()
        rogue = se.CellSigner(b"attacker")
        bad = rogue.sign("event", "alpha", {"lie": True})
        gate = se.OverseerGate(trusted_key_ids=signer.trusted_keys)
        with self.assertRaises(se.RefusedUnit):
            gate.admit(bad)

    def test_replay_refused_by_gate(self):
        signer, env = make_envelope(seq=5)
        gate = se.OverseerGate(trusted_key_ids=signer.trusted_keys)
        gate.admit(env)
        with self.assertRaises(se.RefusedUnit):  # повтор того же конверта
            gate.admit(env)
        older = signer.sign("event", "alpha", {"n": 1})  # signer.seq уже > 5
        # подпись свежего конверта после отката счётчика = повтор цепи
        older["env"]["seq"] = 3
        with self.assertRaises(se.RefusedUnit):
            se.OverseerGate(trusted_key_ids=signer.trusted_keys).admit(older)

    def test_gate_fail_closed_on_garbage(self):
        signer, _ = make_envelope()
        gate = se.OverseerGate(trusted_key_ids=signer.trusted_keys)
        for garbage in (None, [], "строка", 42, {}, {"env": {}},
                        {"env": {"v": 2}}, json.loads(json.dumps({"sig": None}))):
            with self.assertRaises(se.RefusedUnit):
                gate.admit(garbage)

    def test_refused_never_leaks_raw_exception(self):
        """Fail-closed: наружу — только RefusedUnit, никаких «случайных» типов."""
        gate = se.OverseerGate()
        try:
            gate.admit({"env": {"v": 1}})
        except Exception as e:
            self.assertIsInstance(e, se.RefusedUnit)
        else:
            self.fail("мусор прошёл дверь — overseer солгал")

    def test_seq_state_file_persisted(self):
        with tempfile.TemporaryDirectory() as td:
            sp = str(Path(td) / "state" / "seq")
            s1 = se.CellSigner(b"sec", state_path=sp)
            s1.sign("blood", "a", {})
            s2 = se.CellSigner(b"sec", state_path=sp)
            self.assertGreater(s2.seq, 0)


class TestAgentCard(unittest.TestCase):
    @staticmethod
    def _status_lines():
        head = {"sup": "agryp", "pid": 4242, "units": 1, "uptime_ms": 1500}
        unit = {"unit": "alpha", "state": "RUNNING", "pid": 4243, "attempt": 1,
                "budget_sec": 60}
        return head, unit

    def _live_fixture(self, with_metrics=True):
        """Контекст: живой .prom в живом временном каталоге + подменённый _status."""
        import contextlib

        @contextlib.contextmanager
        def ctx():
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td)
                head, unit = self._status_lines()
                metrics = tmp / ".agryp-metrics.prom"
                if with_metrics:
                    metrics.write_text(
                        "# HELP agryp_up_ms uptime\n# TYPE agryp_up_ms gauge\n"
                        "agryp_up_ms 1500\n", encoding="utf-8")
                real_status = ac._status
                ac._status = lambda d: (head, [unit])
                try:
                    yield tmp, metrics
                finally:
                    ac._status = real_status
        return ctx()

    def test_card_validates_against_schema(self):
        with self._live_fixture() as (tmp, metrics):
            card = ac.build_card(tmp)
            self.assertEqual(ac.validate_card(card), [],
                             "карта не прошла схему A2A")
            self.assertTrue(card["url"].startswith("file://"))
            self.assertTrue(metrics.exists(), "endpoint указывает в пустоту")
            self.assertIn("unit:alpha", [s["id"] for s in card["skills"]])

    def test_card_dead_endpoint_refused(self):
        """Мёртвый супервизор не получает карту — фасад не врёт."""
        with self._live_fixture(with_metrics=False) as (tmp, metrics):
            with self.assertRaises(SystemExit):
                ac.build_card(tmp)
            self.assertFalse(metrics.exists())

    def test_card_schema_rejects_broken(self):
        with self._live_fixture() as (tmp, metrics):
            card = ac.build_card(tmp)
        broken = copy.deepcopy(card)
        del broken["protocolVersion"]
        self.assertTrue(ac.validate_card(broken), "поломанная карта прошла схему?!")
        broken2 = copy.deepcopy(card)
        broken2["protocolVersion"] = "0.2"
        self.assertTrue(ac.validate_card(broken2), "чужой протокол прошёл схему?!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
