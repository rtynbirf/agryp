#!/usr/bin/env python3
# agentcard.py — П37: A2A AgentCard для `agrypctl status`.
#
# Карта строится ТОЛЬКО из живого супервизора: `./agryp status --dir DIR`
# (тот же файл-договор семьи, второй источник правды не заводится) и
# свежего .agryp-metrics.prom (виток 10). Endpoint «живое» — file:// URI
# артефакта, который существует прямо сейчас; несвежий/мертвый — отказ.
#
# Схема: schemas/a2a-agentcard.schema.json (A2A v1.0 AgentCard по мотивам;
# транспорт agryp — файл, Ст. 13; расширения — x-agryp). Валидатор —
# std-only подмножество draft-07: type/required/properties/items/enum/
# const/pattern/minItems/minLength/minimum/additionalProperties.
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "a2a-agentcard.schema.json"
METRICS_MAX_AGE_MS = 120_000  # супервизор пишет .prom каждую итерацию — 2 минуты запас

CARD_VERSION = "1.0.0"


# ---------- мини-валидатор JSON Schema (draft-07 подмножество) ----------

def _validate(instance, schema, path="$", errors=None):
    if errors is None:
        errors = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(instance, dict):
            errors.append(f"{path}: ожидался object")
            return errors
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: нет обязательного поля {req!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for k in instance:
                if k not in props:
                    errors.append(f"{path}: лишнее поле {k!r} (additionalProperties=false)")
        for k, v in instance.items():
            if k in props:
                _validate(v, props[k], f"{path}.{k}", errors)
    elif t == "array":
        if not isinstance(instance, list):
            errors.append(f"{path}: ожидался array")
            return errors
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: меньше minItems ({len(instance)})")
        for i, item in enumerate(instance):
            _validate(item, schema.get("items", {}), f"{path}[{i}]", errors)
    elif t == "string":
        if not isinstance(instance, str):
            errors.append(f"{path}: ожидался string")
            return errors
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: короче minLength")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: не матчится pattern {schema['pattern']!r}")
    elif t == "integer":
        if isinstance(instance, bool) or not isinstance(instance, int):
            errors.append(f"{path}: ожидался integer")
            return errors
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: меньше minimum")
    elif t == "boolean":
        if not isinstance(instance, bool):
            errors.append(f"{path}: ожидался boolean")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: const {schema['const']!r} нарушен")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: значение вне enum")
    return errors


def validate_card(card: dict, schema_path: Path = None):
    schema = json.loads((schema_path or SCHEMA).read_text(encoding="utf-8"))
    return _validate(card, schema)


# ---------- живая карта ----------

def _status(dir_path: Path):
    """Живой статус: тот же источник, что agrypctl status (Ст. 13)."""
    sup = ROOT / "agryp"
    if not sup.exists():
        raise SystemExit("agentcard: соберите ядро: make")
    out = subprocess.run([str(sup), "status", "--dir", str(dir_path)],
                         capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise SystemExit(f"agentcard: status rc={out.returncode}: {out.stderr.strip()[:200]}")
    lines = [json.loads(l) for l in out.stdout.splitlines() if l.strip()]
    if not lines or lines[0].get("sup") != "agryp":
        raise SystemExit("agentcard: статус не от agryp — фасад лгать не будет")
    return lines[0], lines[1:]


def _file_uri(p: Path) -> str:
    return "file://" + str(p.resolve())


def build_card(dir_path: Path, version: str = CARD_VERSION) -> dict:
    head, units = _status(dir_path)
    metrics = dir_path / ".agryp-metrics.prom"
    if not metrics.exists():
        raise SystemExit(f"agentcard: {metrics} не существует — супервизор мёртв, карта лжива")
    age_ms = int((time.time() - metrics.stat().st_mtime) * 1000)
    if age_ms > METRICS_MAX_AGE_MS:
        raise SystemExit(f"agentcard: .prom несвежий ({age_ms} мс) — endpoint мёртв")

    skills = [{
        "id": "core:supervision",
        "name": "process supervision",
        "description": "PID1-подобный супервизор: spawn/казнь/бюджеты/журнал NDJSON",
        "tags": ["pid1", "supervisor", "ndjson"],
    }]
    for u in units:
        skills.append({
            "id": f"unit:{u.get('unit', '?')}",
            "name": str(u.get("unit", "?")),
            "description": f"клетка юнита: state={u.get('state')}, attempt={u.get('attempt')}",
            "tags": ["supervised", str(u.get("state", "?")).lower()],
        })

    return {
        "type": "AgentCard",
        "protocolVersion": "1.0",
        "name": "agryp",
        "description": "PID1-подобный супервизор AI-агентов: один файл C, ноль зависимостей, файл-как-API",
        "version": version,
        "url": _file_uri(metrics),
        "preferredTransport": "file+ndjson",
        "capabilities": {
            "streaming": True,             # токен-стрим, виток 7 (Ст. 14)
            "pushNotifications": False,    # Ст. 13: никаких сокетов
            "stateTransitionHistory": True # журнал NDJSON + печать-цепь
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["application/x-ndjson", "text/plain"],
        "skills": skills,
        "provider": {"organization": "rtynbirf", "url": "https://github.com/rtynbirf/agryp"},
        "x-agryp": {
            "identity": {
                "sup": "agryp",
                "pid": head.get("pid", 0),
                "uptime_ms": head.get("uptime_ms", 0),
                "cell_dir": str(dir_path.resolve()),
            },
            "endpoints": {
                "status": "command: ./agryp status --dir " + str(dir_path),
                "metrics": _file_uri(metrics),
                "journal": _file_uri(dir_path / ".agryp-journal.ndjson"),
                "ctl": "file:" + str((dir_path / ".agryp-ctl").resolve()),
            },
            "security": "конверты подписаны sha256-цепочкой (П37, tools/signed_envelope.py); overseer fail-closed",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="П37: A2A AgentCard из живого супервизора")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="построить карту из живого супервизора")
    b.add_argument("--dir", required=True)
    b.add_argument("--out", default="-")
    b.add_argument("--version", default=CARD_VERSION)

    c = sub.add_parser("check", help="проверить карту по схеме A2A")
    c.add_argument("file")
    c.add_argument("--schema", default=str(SCHEMA))

    args = ap.parse_args()
    if args.cmd == "build":
        card = build_card(Path(args.dir), args.version)
        errs = validate_card(card)
        if errs:
            for e in errs:
                print(f"СХЕМА: {e}", file=sys.stderr)
            return 1
        out = json.dumps(card, ensure_ascii=False, indent=2, sort_keys=True)
        (sys.stdout if args.out == "-" else open(args.out, "w", encoding="utf-8")).write(out + "\n")
        return 0
    if args.cmd == "check":
        card = json.loads(Path(args.file).read_text(encoding="utf-8"))
        errs = validate_card(card, Path(args.schema))
        if errs:
            for e in errs:
                print(f"СХЕМА: {e}", file=sys.stderr)
            return 1
        print(f"карта валидна: {card['name']} v{card['version']}, skills={len(card['skills'])}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
