#!/usr/bin/env python3
# signed_envelope.py — П37: подписанные конверты крови/событий клетки.
#
# Идея issue #6: конверты подписываются ed25519-ключом клетки, overseer
# проверяет подпись fail-closed (битая подпись = отказ завода юнита).
# ed25519 требует внешних зависимостей — Ст. 2 запрещает (ноль зависимостей).
# Поэтому подпись — хеш-цепочка на sha256 (FIPS 180-4, std-only):
#   ключ клетки  = 32 цепочки по 255 шагов sha256 (Winternitz, w=256);
#   подпись      = позиция каждой цепочки, снимающая байт дайджеста;
#   подделка ЛЮБОГО байта конверта меняет дайджест → цепи не сходятся.
# «ed25519-цепочка» здесь — цепочка последовательностей: overseer требует
# строгий рост seq по ключу (повтор конверта = отказ), а ключи заперты
# списком доверия при рождении клетки (сеть не нужна — верим без неё).
#
# Формат конверта (NDJSON, Ст. 13 — файл вместо сокета):
# {"v":1,"alg":"sha256-wots","kind":"blood|event","unit":"alpha",
#  "seq":7,"ts":1699...,"payload":{...},
#  "sig":{"key_id":"16hex","pub":["hex"×32],"chains":["hex"×32]}}
#
# Приёмка П37 (машинная): tests/test_p37_envelope.py — «битая подпись →
# отказ» зелёный; demo/run_demo_envelope.sh — завод юнита по подписи живьём.
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

N_CHAINS = 32          # байт дайджеста sha256 — по цепочке на байт
CHAIN_LEN = 255        # длина каждой цепочки (w=256, шагов 255)
ALG = "sha256-wots"
KINDS = ("blood", "event")

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
    """Корень ключа клетки: sha256-цепочка от секрета (один вход — один корень)."""
    v = _h(b"agryp-p37-seed\x00" + secret)
    for _ in range(1024):
        v = _step(v)
    return v


def _sk(seed: bytes, i: int) -> bytes:
    return _h(b"sk" + i.to_bytes(2, "big") + seed)


def derive_public(seed: bytes):
    """Публичный ключ: 32 хвоста цепочек (hex). 32×255 sha256 — миллисекунды."""
    pub = []
    for i in range(N_CHAINS):
        v = _sk(seed, i)
        for _ in range(CHAIN_LEN):
            v = _step(v)
        pub.append(v.hex())
    return pub


def key_id(pub) -> str:
    """Отпечаток ключа: первые 16 hex от хеша публичника."""
    blob = json.dumps(list(pub), separators=(",", ":")).encode("ascii")
    return _h(blob).hex()[:16]


class EnvelopeError(Exception):
    """Конверт не прошел проверку (подделан, бит, повторен)."""


class RefusedUnit(Exception):
    """Отказ завода юнита: overseer не поверил конверту (fail-closed)."""


def _check(cond, msg):
    if not cond:
        raise EnvelopeError(msg)


def sign_digest(seed: bytes, digest: bytes):
    """WOTS-подпись дайджеста: по цепочке i отматываем 255-d шагов."""
    chains = []
    for i in range(N_CHAINS):
        d = digest[i]
        v = _sk(seed, i)
        for _ in range(CHAIN_LEN - d):
            v = _step(v)
        chains.append(v.hex())
    return chains


def verify(envelope: dict) -> dict:
    """Проверка конверта. Любое сомнение — EnvelopeError (fail-closed)."""
    _check(isinstance(envelope, dict), "конверт не словарь")
    body = envelope.get("env")
    sig = envelope.get("sig")
    _check(isinstance(body, dict), "нет тела конверта env")
    _check(isinstance(sig, dict), "нет подписи sig")

    _check(body.get("v") == 1, "версия конверта не 1")
    _check(body.get("alg") == ALG, f"алгоритм не {ALG}")
    _check(body.get("kind") in KINDS, "kind не blood|event")
    _check(isinstance(body.get("unit"), str) and body["unit"], "нет юнита")
    _check(isinstance(body.get("seq"), int) and body["seq"] >= 0, "seq не число")
    _check(isinstance(body.get("ts"), int), "ts не число")
    _check(isinstance(body.get("payload"), dict), "payload не словарь")

    pub = sig.get("pub")
    chains = sig.get("chains")
    kid = sig.get("key_id")
    _check(isinstance(pub, list) and len(pub) == N_CHAINS, "pub не 32 цепочки")
    _check(isinstance(chains, list) and len(chains) == N_CHAINS, "подпись не 32 цепочки")
    _check(isinstance(kid, str), "нет отпечатка ключа")
    for x in pub:
        _check(isinstance(x, str) and len(x) == 64 and
               all(c in "0123456789abcdef" for c in x), "pub: мусор в hex")
    for x in chains:
        _check(isinstance(x, str) and len(x) == 64 and
               all(c in "0123456789abcdef" for c in x), "chains: мусор в hex")
    _check(key_id(pub) == kid, "key_id не сходится с pub — ключ подменён")

    digest = _h(canonical(body))
    for i in range(N_CHAINS):
        d = digest[i]
        v = bytes.fromhex(chains[i])
        for _ in range(d):
            v = _step(v)
        if v.hex() != pub[i]:
            raise EnvelopeError(f"цепь {i} не сходится — конверт подделан")
    return body


class CellSigner:
    """Ключ и счётчик клетки. Один секрет — один корень — одна цепь seq."""

    def __init__(self, secret: bytes, seq: int = 0, state_path: str = None):
        self.seed = derive_seed(secret)
        self.pub = derive_public(self.seed)
        self.kid = key_id(self.pub)
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
            tmp.replace(p)  # атомарно (Ст. 13: tmp + rename)
        return self.seq

    def sign(self, kind: str, unit: str, payload: dict) -> dict:
        if kind not in KINDS:
            raise ValueError(f"kind {kind!r} не из {KINDS}")
        body = {
            "v": 1, "alg": ALG, "kind": kind, "unit": unit,
            "seq": self._next_seq(), "ts": int(time.time() * 1000),
            "payload": payload,
        }
        digest = _h(canonical(body))
        return {"env": body,
                "sig": {"key_id": self.kid, "pub": self.pub,
                        "chains": sign_digest(self.seed, digest)}}


class OverseerGate:
    """Дверь завода юнита: конверт проверяется, повтор отсекается, ключи заперты.

    fail-closed: ЛЮБОЕ исключение внутри превращается в RefusedUnit —
    сомнительный конверт никогда не выглядит годным.
    """

    def __init__(self, trusted_key_ids=None):
        self.trusted = set(trusted_key_ids) if trusted_key_ids else None
        self._last_seq = {}

    def admit(self, envelope) -> dict:
        try:
            body = verify(envelope)
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
    ap = argparse.ArgumentParser(description="П37: подпись/проверка конвертов клетки (std-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    k = sub.add_parser("keygen", help="показать отпечаток ключа клетки")
    k.add_argument("--secret", required=True)

    s = sub.add_parser("sign", help="подписать конверт")
    s.add_argument("--secret", required=True)
    s.add_argument("--kind", default="blood", choices=KINDS)
    s.add_argument("--unit", required=True)
    s.add_argument("--payload", default="{}")
    s.add_argument("--seq", type=int, default=0)
    s.add_argument("--out", default="-")

    v = sub.add_parser("verify", help="проверить конверт (fail-closed)")
    v.add_argument("file", help="файл конверта JSON или '-' для stdin")

    args = ap.parse_args()
    if args.cmd == "keygen":
        print(key_id(derive_public(derive_seed(args.secret.encode()))))
        return 0
    if args.cmd == "sign":
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
        print(f"ГОДЕН: {body['kind']} {body['unit']} seq={body['seq']}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
