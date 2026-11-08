#!/usr/bin/env python3
# signed_envelope.py — П37: подписанные конверты крови/событий клетки.
#
# Идея issue #6: конверты подписываются ed25519-ключом клетки, overseer
# проверяет подпись fail-closed (битая подпись = отказ завода юнита).
#
# Волна ×6 (2026-11-11): подпись — НАСТОЯЩИЙ ed25519 (RFC 8032).
#   Примитив — vendored orlp/ed25519 (zlib, verbatim, vendor/ed25519/),
#   собранный в единственный CLI границы клетки tools/ed25519tool
#   (Ст. 1, Поправка №12: ядро src/agryp.c не тронуто; Ст. 2 цела:
#   сборка из локальных файлов, ldd → только libc).
#   Правильность примитива доказана машиной векторами RFC 8032 §7.1
#   (TEST 1/2/3) в tests/test_p37_ed25519.py + перекрёстной сверкой
#   с python-cryptography, когда та есть.
# Волна ×4 дала WOTS на sha256 (std-only) — он сохранён как легаси
# (WotsCellSigner, конверты v1, alg=sha256-wots): verify() честно
# проверяет оба формата, но дверь по умолчанию доверяет ТОЛЬКО ed25519 —
# неизвестный алгоритм = отказ (fail-closed, поле alg — не рекомендация).
#
# «Цепочка» из ТЗ — цепь последовательностей: overseer требует строгий
# рост seq по ключу (повтор конверта = отказ, replay закрыт), а ключи
# заперты списком доверия при рождении клетки (сеть не нужна — верим
# без неё).
#
# Формат конверта v2 (NDJSON, Ст. 13 — файл вместо сокета):
# {"v":2,"alg":"ed25519","kind":"blood|event","unit":"alpha",
#  "seq":7,"ts":1699...,"payload":{...},
#  "sig":{"key_id":"16hex","pub":"64hex","sig":"128hex"}}
#
# Формат легаси v1:
# {"v":1,"alg":"sha256-wots", ..., "sig":{"key_id","pub":["hex"×32],"chains":["hex"×32]}}
#
# Приёмка П37 (машинная): tests/test_p37_ed25519.py — «битая подпись →
# отказ» зелёный; demo/run_demo_envelope.sh — завод юнита по подписи живьём.
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ALG = "ed25519"           # подписант волны ×6 (RFC 8032)
ALG_WOTS = "sha256-wots"  # легаси волны ×4 (std-only WOTS на sha256)
KINDS = ("blood", "event")
N_CHAINS = 32             # (WOTS) байт дайджеста sha256 — по цепочке на байт
CHAIN_LEN = 255           # (WOTS) длина каждой цепочки (w=256, шагов 255)
ENV_VERSION = 2

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "ed25519tool"   # make ed25519tool

# Разделение доменов: шаг цепочки и корень ключа не смешиваются.
_STEP = b"\x01"


def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def _step(v: bytes) -> bytes:
    return _h(_STEP + v)


def canonical(body: dict) -> bytes:
    return json.dumps(body, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def derive_seed(secret: bytes) -> bytes:
    """Корень ключа клетки: sha256-цепочка от секрета (один вход — один корень).

    1024 шага — простая растяжка входа; это не argon2: секрет клетки —
    длинный случайный вход, а не пароль человека (см. VENDOR-NOTES.md).
    32 байта выхода — готовый ed25519 seed (детерминизм для фикстур/демо).
    """
    v = _h(b"agryp-p37-seed\x00" + secret)
    for _ in range(1024):
        v = _step(v)
    return v


# ------------------------- ed25519 (через vendored CLI) -------------------------

def _tool() -> str:
    """Путь к собранному CLI примитива. Нет бинаря — fail-closed: отказ."""
    if not TOOL.exists():
        raise EnvelopeError(f"нет {TOOL.name} — соберите примитив: make ed25519tool")
    return str(TOOL)


def _hex(b: bytes) -> str:
    return b.hex()


def _run_tool(args, stdin_bytes=None):
    """Вызов CLI. Любая ошибка процесса — EnvelopeError (fail-closed)."""
    try:
        p = subprocess.run(args, input=stdin_bytes, capture_output=True,
                           timeout=30)
    except Exception as e:  # noqa: BLE001 — наружу всё равно RefusedUnit
        raise EnvelopeError(f"примитив ed25519 недоступен: {e}") from e
    return p.returncode, p.stdout, p.stderr


def ed25519_pub(seed: bytes) -> bytes:
    rc, out, err = _run_tool([_tool(), "pub", _hex(seed)])
    if rc != 0:
        raise EnvelopeError(f"pub: примитив вернул rc={rc}: {err[:120]}")
    return bytes.fromhex(out.decode().strip())


def ed25519_sign(seed: bytes, msg: bytes) -> bytes:
    rc, out, err = _run_tool([_tool(), "sign", _hex(seed), "-"], stdin_bytes=msg)
    if rc != 0:
        raise EnvelopeError(f"sign: примитив вернул rc={rc}: {err[:120]}")
    return bytes.fromhex(out.decode().strip())


def ed25519_verify(pub: bytes, msg: bytes, sig: bytes) -> bool:
    """Проверка подписи: rc 0 — годна; ЛЮБОЙ другой rc — не годна."""
    rc, _, _ = _run_tool([_tool(), "verify", _hex(pub), "-", _hex(sig)],
                         stdin_bytes=msg)
    return rc == 0


def key_id(pub_hex: str) -> str:
    """Отпечаток ключа: первые 16 hex от sha256 байтов публичника."""
    return _h(bytes.fromhex(pub_hex)).hex()[:16]


# ------------------------- общие проверки тела -------------------------

class EnvelopeError(Exception):
    """Конверт не прошел проверку (подделан, бит, повторен, незнакомый alg)."""


class RefusedUnit(Exception):
    """Отказ завода юнита: overseer не поверил конверту (fail-closed)."""


def _check(cond, msg):
    if not cond:
        raise EnvelopeError(msg)


def _check_body_common(body: dict):
    _check(body.get("kind") in KINDS, "kind не blood|event")
    _check(isinstance(body.get("unit"), str) and body["unit"], "нет юнита")
    _check(isinstance(body.get("seq"), int) and body["seq"] >= 0, "seq не число")
    _check(isinstance(body.get("ts"), int), "ts не число")
    _check(isinstance(body.get("payload"), dict), "payload не словарь")


def _is_hex(s: str, nbytes: int) -> bool:
    return (isinstance(s, str) and len(s) == 2 * nbytes
            and all(c in "0123456789abcdef" for c in s))


# ------------------------- ed25519-конверты (v2) -------------------------

def verify_ed25519(envelope: dict) -> dict:
    """Проверка v2-конверта. Любое сомнение — EnvelopeError (fail-closed)."""
    body = envelope.get("env")
    sig = envelope.get("sig")
    _check(isinstance(body, dict), "нет тела конверта env")
    _check(isinstance(sig, dict), "нет подписи sig")

    _check(body.get("v") == ENV_VERSION, "версия конверта не 2")
    _check(body.get("alg") == ALG, f"алгоритм не {ALG}")
    _check_body_common(body)

    pub_hex = sig.get("pub")
    sig_hex = sig.get("sig")
    kid = sig.get("key_id")
    _check(_is_hex(pub_hex, 32), "pub: не 32 байта hex")
    _check(_is_hex(sig_hex, 64), "sig: не 64 байта hex")
    _check(isinstance(kid, str) and _is_hex(kid, 8), "key_id: не 8 байт hex")
    _check(key_id(pub_hex) == kid, "key_id не сходится с pub — ключ подменён")

    msg = canonical(body)
    _check(ed25519_verify(bytes.fromhex(pub_hex), msg, bytes.fromhex(sig_hex)),
           "ed25519-подпись не сходится — конверт подделан")
    return body


# ------------------------- WOTS-конверты (v1, легаси ×4) -------------------------

def _sk(seed: bytes, i: int) -> bytes:
    return _h(b"sk" + i.to_bytes(2, "big") + seed)


def derive_public_wots(seed: bytes):
    """Публичный ключ WOTS: 32 хвоста цепочек (hex)."""
    pub = []
    for i in range(N_CHAINS):
        v = _sk(seed, i)
        for _ in range(CHAIN_LEN):
            v = _step(v)
        pub.append(v.hex())
    return pub


def key_id_wots(pub) -> str:
    blob = json.dumps(list(pub), separators=(",", ":")).encode("ascii")
    return _h(blob).hex()[:16]


def sign_digest_wots(seed: bytes, digest: bytes):
    chains = []
    for i in range(N_CHAINS):
        d = digest[i]
        v = _sk(seed, i)
        for _ in range(CHAIN_LEN - d):
            v = _step(v)
        chains.append(v.hex())
    return chains


def verify_wots(envelope: dict) -> dict:
    """Проверка легаси v1 (WOTS). Любое сомнение — EnvelopeError."""
    body = envelope.get("env")
    sig = envelope.get("sig")
    _check(isinstance(body, dict), "нет тела конверта env")
    _check(isinstance(sig, dict), "нет подписи sig")

    _check(body.get("v") == 1, "версия конверта не 1")
    _check(body.get("alg") == ALG_WOTS, f"алгоритм не {ALG_WOTS}")
    _check_body_common(body)

    pub = sig.get("pub")
    chains = sig.get("chains")
    kid = sig.get("key_id")
    _check(isinstance(pub, list) and len(pub) == N_CHAINS, "pub не 32 цепочки")
    _check(isinstance(chains, list) and len(chains) == N_CHAINS, "подпись не 32 цепочки")
    _check(isinstance(kid, str), "нет отпечатка ключа")
    for x in pub:
        _check(_is_hex(x, 32), "pub: мусор в hex")
    for x in chains:
        _check(_is_hex(x, 32), "chains: мусор в hex")
    _check(key_id_wots(pub) == kid, "key_id не сходится с pub — ключ подменён")

    digest = _h(canonical(body))
    for i in range(N_CHAINS):
        d = digest[i]
        v = bytes.fromhex(chains[i])
        for _ in range(d):
            v = _step(v)
        if v.hex() != pub[i]:
            raise EnvelopeError(f"цепь {i} не сходится — конверт подделан")
    return body


# ------------------------- диспетчер + дверь overseer -------------------------

def verify(envelope: dict) -> dict:
    """Диспетчер по алгоритму. Неизвестный alg/v — отказ (fail-closed)."""
    _check(isinstance(envelope, dict), "конверт не словарь")
    body = envelope.get("env")
    _check(isinstance(body, dict), "нет тела конверта env")
    alg = body.get("alg")
    v = body.get("v")
    if alg == ALG and v == ENV_VERSION:
        return verify_ed25519(envelope)
    if alg == ALG_WOTS and v == 1:
        return verify_wots(envelope)
    raise EnvelopeError(f"незнакомый конверт: v={v!r} alg={alg!r} — дверь не угадывает")


class CellSigner:
    """Ключ и счётчик клетки (ed25519, волна ×6). Один секрет — один ключ.

    seed = derive_seed(secret) — детерминизм для фикстур и демо; можно
    передать и готовые 32 байта seed напрямую (одноразовый TEST ONLY ключ
    из тестов — через seed=).
    """

    def __init__(self, secret: bytes = b"cell", seq: int = 0,
                 state_path: str = None, seed: bytes = None):
        self.seed = seed if seed is not None else derive_seed(secret)
        _check(isinstance(self.seed, bytes) and len(self.seed) == 32,
               "seed должен быть 32 байта")
        self.pub_hex = _hex(ed25519_pub(self.seed))
        self.kid = key_id(self.pub_hex)
        self.seq = int(seq)
        self.state_path = state_path
        if state_path and Path(state_path).exists():
            self.seq = max(self.seq, int(Path(state_path).read_text().strip() or 0))

    @property
    def pub(self) -> str:
        return self.pub_hex

    @property
    def trusted_keys(self):
        return {self.kid}

    def _next_seq(self) -> int:
        self.seq += 1
        if self.state_path:
            p = Path(self.state_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(".tmp")
            tmp.write_text(str(self.seq))
            tmp.replace(p)  # атомарно (Ст. 13: tmp + rename)
        return self.seq

    def sign(self, kind: str, unit: str, payload: dict) -> dict:
        if kind not in KINDS:
            raise ValueError(f"kind {kind!r} не из {KINDS}")
        body = {
            "v": ENV_VERSION, "alg": ALG, "kind": kind, "unit": unit,
            "seq": self._next_seq(), "ts": int(time.time() * 1000),
            "payload": payload,
        }
        sig = ed25519_sign(self.seed, canonical(body))
        return {"env": body,
                "sig": {"key_id": self.kid, "pub": self.pub_hex,
                        "sig": _hex(sig)}}


class WotsCellSigner:
    """Легаси волны ×4 (v1, sha256-wots). Дверь по умолчанию его НЕ пускает."""

    def __init__(self, secret: bytes, seq: int = 0, state_path: str = None):
        self.seed = derive_seed(secret)
        self.pub = derive_public_wots(self.seed)
        self.kid = key_id_wots(self.pub)
        self.seq = int(seq)
        self.state_path = state_path
        if state_path and Path(state_path).exists():
            self.seq = max(self.seq, int(Path(state_path).read_text().strip() or 0))

    @property
    def trusted_keys(self):
        return {self.kid}

    def _next_seq(self) -> int:
        self.seq += 1
        if self.state_path:
            p = Path(self.state_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(".tmp")
            tmp.write_text(str(self.seq))
            tmp.replace(p)
        return self.seq

    def sign(self, kind: str, unit: str, payload: dict) -> dict:
        if kind not in KINDS:
            raise ValueError(f"kind {kind!r} не из {KINDS}")
        body = {
            "v": 1, "alg": ALG_WOTS, "kind": kind, "unit": unit,
            "seq": self._next_seq(), "ts": int(time.time() * 1000),
            "payload": payload,
        }
        digest = _h(canonical(body))
        return {"env": body,
                "sig": {"key_id": self.kid, "pub": self.pub,
                        "chains": sign_digest_wots(self.seed, digest)}}


class OverseerGate:
    """Дверь завода юнита: конверт проверяется, повтор отсекается, ключи
    и алгоритмы заперты.

    fail-closed: ЛЮБОЕ исключение внутри превращается в RefusedUnit —
    сомнительный конверт никогда не выглядит годным. По умолчанию
    доверенный алгоритм — только ed25519 (волна ×6): конверт легаси
    sha256-wots или незнакомый alg в дверь не входит.
    """

    def __init__(self, trusted_key_ids=None, trusted_algs=(ALG,)):
        self.trusted = set(trusted_key_ids) if trusted_key_ids else None
        self.trusted_algs = tuple(trusted_algs) or (ALG,)
        self._last_seq = {}

    def admit(self, envelope) -> dict:
        try:
            body = verify(envelope)
            alg = body["alg"]
            if alg not in self.trusted_algs:
                raise EnvelopeError(f"алгоритм {alg!r} не в доверии двери {self.trusted_algs}")
            kid = envelope["sig"]["key_id"]
            if self.trusted is not None and kid not in self.trusted:
                raise EnvelopeError(f"ключ {kid} не в списке доверия клетки")
            seq = body["seq"]
            if kid in self._last_seq and seq <= self._last_seq[kid]:
                raise EnvelopeError(
                    f"повтор конверта: seq {seq} <= {self._last_seq[kid]} — цепь обязана расти")
            self._last_seq[kid] = seq
            return body
        except RefusedUnit:
            raise
        except Exception as e:
            raise RefusedUnit(str(e)) from e


def main() -> int:
    ap = argparse.ArgumentParser(
        description="П37: подпись/проверка конвертов клетки (ed25519 волной ×6, WOTS легаси)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    k = sub.add_parser("keygen", help="показать отпечаток и публичник ключа клетки")
    k.add_argument("--secret", default=None, help="секрет клетки (иначе — случайный)")
    k.add_argument("--wots", action="store_true", help="легаси WOTS-ключ волны ×4")

    s = sub.add_parser("sign", help="подписать конверт")
    s.add_argument("--secret", required=True)
    s.add_argument("--kind", default="blood", choices=KINDS)
    s.add_argument("--unit", required=True)
    s.add_argument("--payload", default="{}")
    s.add_argument("--seq", type=int, default=0)
    s.add_argument("--wots", action="store_true", help="легаси v1 (sha256-wots)")
    s.add_argument("--out", default="-")

    v = sub.add_parser("verify", help="проверить конверт (fail-closed, оба формата)")
    v.add_argument("file", help="файл конверта JSON или '-' для stdin")

    args = ap.parse_args()
    if args.cmd == "keygen":
        if args.wots:
            seed = derive_seed(args.secret.encode() if args.secret else os.urandom(32))
            pub = derive_public_wots(seed)
            print(key_id_wots(pub))
        else:
            seed = derive_seed(args.secret.encode() if args.secret else os.urandom(32))
            print(key_id(_hex(ed25519_pub(seed))))
        return 0
    if args.cmd == "sign":
        if args.wots:
            signer = WotsCellSigner(args.secret.encode(), seq=args.seq)
        else:
            signer = CellSigner(args.secret.encode(), seq=args.seq)
        env = signer.sign(args.kind, args.unit, json.loads(args.payload))
        out = json.dumps(env, ensure_ascii=False, sort_keys=True)
        (sys.stdout if args.out == "-" else open(args.out, "w", encoding="utf-8")).write(out + "\n")
        return 0
    if args.cmd == "verify":
        raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        try:
            body = verify(json.loads(raw))
        except Exception as e:
            print(f"ОТКАЗ: {e}", file=sys.stderr)
            return 1
        print(f"ГОДЕН: v{body['v']} {body['alg']} {body['kind']} {body['unit']} seq={body['seq']}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
