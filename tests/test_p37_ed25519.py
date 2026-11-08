#!/usr/bin/env python3
# test_p37_ed25519.py — приёмка П37 волны ×6: НАСТОЯЩИЙ ed25519 (RFC 8032).
#
# Три слоя доказательства «битая подпись → отказ завода юнита»:
#   1. примитив: CLI tools/ed25519tool (vendored orlp/ed25519, zlib)
#      обязан воспроизводить векторы RFC 8032 §7.1 (TEST 1/2/3) — pub и
#      подпись до последнего байта; подделка сообщения/подписи = rc!=0;
#   2. конверт: v2 {alg:ed25519} — подделка любого поля (payload/unit/seq/
#      pub/sig/key_id) = EnvelopeError; дверь OverseerGate — RefusedUnit;
#      мусор и отсутствие примитива — тоже RefusedUnit (fail-closed);
#   3. перекрёстная сверка с python-cryptography (когда библиотека есть):
#      подпись CLI обязана совпасть с подписью независимой реализации.
#
# Ключи: RFC-векторы — публичные константы RFC; прочие ключи теста —
# одноразовые детерминированные генераты, помечены TEST ONLY. В репо нет
# ни одного рабочего ключа клетки (Секреты: инвариант §1.3 AGENTS.md).
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import signed_envelope as se  # noqa: E402
import agentcard as ac  # noqa: E402

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    HAVE_CRYPTO = True
except Exception:  # noqa: BLE001 — необязательная зависимость для пробы
    HAVE_CRYPTO = False

# RFC 8032 §7.1 — публичные тест-векторы Ed25519 (не секреты).
RFC8032 = [
    {"name": "TEST 1 (empty msg)",
     "seed": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
     "pub":  "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
     "msg":  b"",
     "sig":  "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
             "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"},
    {"name": "TEST 2 (1 byte 0x72)",
     "seed": "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
     "pub":  "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
     "msg":  bytes([0x72]),
     "sig":  "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
             "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"},
    {"name": "TEST 3 (2 bytes 0xaf82)",
     "seed": "c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
     "pub":  "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
     "msg":  bytes.fromhex("af82"),
     "sig":  "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac"
             "18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a"},
]

TEST_ONLY_SEED = bytes.fromhex(
    "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90")  # TEST ONLY


def make_envelope(unit="alpha", payload=None, seq=0, seed=TEST_ONLY_SEED):
    signer = se.CellSigner(seq=seq, seed=seed)  # TEST ONLY ключ
    env = signer.sign("blood", unit,
                      payload if payload is not None
                      else {"heart_rate": 72, "attempt": 1})
    return signer, env


class TestEd25519PrimitiveRFC8032(unittest.TestCase):
    """Слой 1: vendored примитив обязан совпадать с RFC 8032 до байта."""

    def test_tool_built(self):
        self.assertTrue(se.TOOL.exists(),
                        "нет tools/ed25519tool — соберите: make ed25519tool")

    def test_vectors_pub_and_sig(self):
        for vec in RFC8032:
            pub = se.ed25519_pub(bytes.fromhex(vec["seed"])).hex()
            self.assertEqual(pub, vec["pub"], f"{vec['name']}: pub не из RFC")
            sig = se.ed25519_sign(bytes.fromhex(vec["seed"]), vec["msg"]).hex()
            self.assertEqual(sig, vec["sig"], f"{vec['name']}: подпись не из RFC")

    def test_vectors_verify_good(self):
        for vec in RFC8032:
            ok = se.ed25519_verify(bytes.fromhex(vec["pub"]), vec["msg"],
                                   bytes.fromhex(vec["sig"]))
            self.assertTrue(ok, f"{vec['name']}: годная подпись отвергнута")

    def test_tampered_message_refused(self):
        vec = RFC8032[1]
        bad_msg = bytes([0x73])  # соседний байт
        ok = se.ed25519_verify(bytes.fromhex(vec["pub"]), bad_msg,
                               bytes.fromhex(vec["sig"]))
        self.assertFalse(ok, "подмена сообщения прошла проверку примитива")

    def test_tampered_signature_refused(self):
        vec = RFC8032[2]
        sig = bytearray(bytes.fromhex(vec["sig"]))
        sig[0] ^= 0x01
        ok = se.ed25519_verify(bytes.fromhex(vec["pub"]), vec["msg"], bytes(sig))
        self.assertFalse(ok, "подмена подписи прошла проверку примитива")

    def test_wrong_key_refused(self):
        vec = RFC8032[0]
        other_pub = bytes.fromhex(RFC8032[1]["pub"])
        ok = se.ed25519_verify(other_pub, vec["msg"], bytes.fromhex(vec["sig"]))
        self.assertFalse(ok, "чужой публичник принял подпись")

    @unittest.skipUnless(HAVE_CRYPTO, "python-cryptography недоступна — пропускаем")
    def test_cross_check_with_cryptography(self):
        """Независимая реализация обязана дать ту же подпись и подтвердить ours."""
        msg = b"agryp wave x6 cross-check \xf0\x9f\x8c\x8a"
        key = Ed25519PrivateKey.from_private_bytes(TEST_ONLY_SEED)
        ref_sig = key.sign(msg)
        tool_sig = se.ed25519_sign(TEST_ONLY_SEED, msg)
        self.assertEqual(tool_sig, ref_sig,
                         "CLI разошёлся с python-cryptography — примитив не ed25519")
        pub = key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        ok = se.ed25519_verify(pub, msg, tool_sig)
        self.assertTrue(ok, "собственная подпись не прошла проверку")


class TestEd25519Envelope(unittest.TestCase):
    """Слой 2: конверт v2 и дверь overseer — fail-closed на всём."""

    def test_good_envelope_verifies(self):
        signer, env = make_envelope()
        body = se.verify(env)
        self.assertEqual(body["unit"], "alpha")
        self.assertEqual(body["kind"], "blood")
        self.assertEqual(body["alg"], "ed25519")
        self.assertEqual(body["v"], 2)

    def test_tampered_payload_refused(self):
        _, env = make_envelope()
        env["env"]["payload"]["heart_rate"] = 666
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

    def test_tampered_signature_refused(self):
        _, env = make_envelope()
        sig = bytearray(bytes.fromhex(env["sig"]["sig"]))
        sig[10] ^= 0x80
        env["sig"]["sig"] = bytes(sig).hex()
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_key_substitution_refused(self):
        _, env = make_envelope()
        other = se.CellSigner(seed=bytes.fromhex(
            "f0e1d2c3b4a5968778695a4b3c2d1e0ff0e1d2c3b4a5968778695a4b3c2d1e0f"))  # TEST ONLY
        env["sig"]["pub"] = other.pub
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_broken_key_id_refused(self):
        _, env = make_envelope()
        env["sig"]["key_id"] = "0" * 16
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_missing_signature_field_refused(self):
        _, env = make_envelope()
        del env["sig"]["sig"]
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)

    def test_rogue_key_refused_by_gate(self):
        signer, _ = make_envelope()
        rogue = se.CellSigner(b"attacker-key")  # TEST ONLY
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
        older = signer.sign("event", "alpha", {"n": 1})
        older["env"]["seq"] = 3  # откат счётчика = повтор цепи
        with self.assertRaises(se.RefusedUnit):
            se.OverseerGate(trusted_key_ids=signer.trusted_keys).admit(older)

    def test_gate_fail_closed_on_garbage(self):
        signer, _ = make_envelope()
        gate = se.OverseerGate(trusted_key_ids=signer.trusted_keys)
        for garbage in (None, [], "строка", 42, {}, {"env": {}},
                        {"env": {"v": 1, "alg": "ed25519"}},
                        json.loads(json.dumps({"sig": None}))):
            with self.assertRaises(se.RefusedUnit):
                gate.admit(garbage)

    def test_gate_refused_never_leaks_raw_exception(self):
        """Fail-closed: наружу — только RefusedUnit, никаких «случайных» типов."""
        gate = se.OverseerGate()
        try:
            gate.admit({"env": {"v": 2, "alg": "ed25519"}})
        except Exception as e:  # noqa: BLE001
            self.assertIsInstance(e, se.RefusedUnit)
        else:
            self.fail("мусор прошёл дверь — overseer солгал")

    def test_missing_primitive_refused_fail_closed(self):
        """Нет бинаря примитива — конверт НЕ годен (fail-closed, не crash)."""
        _, env = make_envelope()
        real = se.TOOL
        try:
            se.TOOL = Path("/nonexistent/ed25519tool")  # noqa: PLC0206
            with self.assertRaises(se.EnvelopeError):
                se.verify(env)
            gate = se.OverseerGate(trusted_key_ids=env["sig"]["key_id"])
            with self.assertRaises(se.RefusedUnit):
                gate.admit(env)
        finally:
            se.TOOL = real

    def test_legacy_wots_refused_by_default_gate(self):
        """Легаси ×4 (sha256-wots) честно верифицируется, но в ed25519-дверь не входит."""
        w = se.WotsCellSigner(b"legacy-cell")  # TEST ONLY
        env = w.sign("blood", "old", {"x": 1})
        body = se.verify(env)  # формат известен — проверяется честно
        self.assertEqual(body["alg"], "sha256-wots")
        gate = se.OverseerGate(trusted_key_ids=w.trusted_keys)  # умолчание ×6
        with self.assertRaises(se.RefusedUnit):
            gate.admit(env)

    def test_unknown_alg_refused(self):
        _, env = make_envelope()
        env["env"]["alg"] = "rsa1024"
        with self.assertRaises(se.EnvelopeError):
            se.verify(env)
        gate = se.OverseerGate()
        with self.assertRaises(se.RefusedUnit):
            gate.admit(env)

    def test_seq_state_file_persisted(self):
        with tempfile.TemporaryDirectory() as td:
            sp = str(Path(td) / "state" / "seq")
            s1 = se.CellSigner(seed=TEST_ONLY_SEED, state_path=sp)  # TEST ONLY
            s1.sign("blood", "a", {})
            s2 = se.CellSigner(seed=TEST_ONLY_SEED, state_path=sp)
            self.assertGreater(s2.seq, 0)

    def test_deterministic_seed_from_secret(self):
        s1 = se.CellSigner(b"cell-secret-02")  # TEST ONLY
        s2 = se.CellSigner(b"cell-secret-02")
        self.assertEqual(s1.pub, s2.pub)
        self.assertEqual(s1.kid, s2.kid)


class TestAgentCardSchema(unittest.TestCase):
    """Карта по схеме: канон schemas/ и копия для тестов tests/ — без дрейфа."""

    @staticmethod
    def _status_lines():
        head = {"sup": "agryp", "pid": 4242, "units": 1, "uptime_ms": 1500}
        unit = {"unit": "alpha", "state": "RUNNING", "pid": 4243, "attempt": 1,
                "budget_sec": 60}
        return head, unit

    def _live_fixture(self, with_metrics=True):
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

    def test_schema_copy_matches_canonical(self):
        """Дрейф канона (schemas/) и тестовой копии (tests/) заперт."""
        canon = (ROOT / "schemas" / "a2a-agentcard.schema.json").read_bytes()
        test_copy = (ROOT / "tests" / "a2a-agentcard.schema.json").read_bytes()
        self.assertEqual(canon, test_copy, "копия схемы в tests/ отошла от канона")

    def test_card_validates_against_test_schema(self):
        with self._live_fixture() as (tmp, metrics):
            card = ac.build_card(tmp)
            self.assertEqual(ac.validate_card(
                card, ROOT / "tests" / "a2a-agentcard.schema.json"), [],
                "карта не прошла схему A2A (копия tests/)")
            self.assertTrue(card["url"].startswith("file://"))
            self.assertTrue(metrics.exists(), "endpoint указывает в пустоту")
            self.assertIn("unit:alpha", [s["id"] for s in card["skills"]])
            # волна ×6: карта объявляет ed25519-подпись конвертов
            self.assertEqual(card["x-agryp"]["signing"]["alg"], "ed25519")
            self.assertEqual(card["x-agryp"]["signing"]["envelope_version"], 2)

    def test_card_dead_endpoint_refused(self):
        """Мёртвый супервизор не получает карту — фасад не врёт."""
        with self._live_fixture(with_metrics=False) as (tmp, metrics):
            with self.assertRaises(SystemExit):
                ac.build_card(tmp)
            self.assertFalse(metrics.exists())

    def test_card_schema_rejects_broken(self):
        with self._live_fixture() as (tmp, _):
            card = ac.build_card(tmp)
        broken = copy.deepcopy(card)
        del broken["protocolVersion"]
        self.assertTrue(ac.validate_card(broken), "поломанная карта прошла схему?!")
        broken2 = copy.deepcopy(card)
        broken2["protocolVersion"] = "0.2"
        self.assertTrue(ac.validate_card(broken2), "чужой протокол прошёл схему?!")
        broken3 = copy.deepcopy(card)
        del broken3["x-agryp"]["signing"]  # карта без декларации подписи — вне схемы ×6
        self.assertTrue(ac.validate_card(broken3), "карта без signing прошла схему?!")
        broken4 = copy.deepcopy(card)
        broken4["x-agryp"]["signing"]["alg"] = "md5"
        self.assertTrue(ac.validate_card(broken4), "чужой alg подписи прошёл схему?!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
