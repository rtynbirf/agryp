CC      ?= gcc
CFLAGS  ?= -O2 -Wall -Wextra -std=c99

# П37 волна ×6: vendored orlp/ed25519 (zlib, verbatim) — примитив подписанных
# конвертов. Один CLI границы клетки (Ст. 1, Поправка №12); ядро не тронуто.
VENDOR      = vendor/ed25519
ED25519_SRC = $(VENDOR)/fe.c $(VENDOR)/ge.c $(VENDOR)/sc.c $(VENDOR)/sha512.c \
              $(VENDOR)/keypair.c $(VENDOR)/sign.c $(VENDOR)/verify.c

agryp: src/agryp.c
	$(CC) $(CFLAGS) -o $@ $<

ed25519tool: tools/ed25519tool.c $(ED25519_SRC) $(VENDOR)/ed25519.h
	$(CC) $(CFLAGS) -I$(VENDOR) -o $@ tools/ed25519tool.c $(ED25519_SRC)

# Приёмка П37 (машинная): «битая подпись → отказ» + карточка по схеме A2A.
test-p37: agryp ed25519tool
	python3 -m unittest discover -s tests -p 'test_p37*.py' -v

demo-envelope: agryp ed25519tool
	bash demo/run_demo_envelope.sh

demo: agryp
	bash demo/run_demo.sh

demo-ctl: agryp
	bash demo/run_demo_ctl.sh

demo-finish: agryp
	bash demo/run_demo_finish.sh

demo-ready: agryp
	bash demo/run_demo_ready.sh

demo-reload: agryp
	bash demo/run_demo_reload.sh

demo-jail: agryp
	bash demo/run_demo_jail.sh

demo-stream: agryp
	bash demo/run_demo_stream.sh

# Виток 10: счётная правда ядра — метрики .prom, журнал-ротация с пломбой,
# сигнатуры договоров. Приёмки Т06 (предложение «метрики как .prom»).
demo-metrics: agryp
	bash demo/run_demo_metrics.sh

demo-rotate: agryp
	bash demo/run_demo_rotate.sh

demo-sign: agryp
	bash demo/run_demo_sign.sh

journal-audit:
	sh tools/journal_audit.sh demo/rotate-units

# Контракт каталога (П-04/T04): 2444 позиции — счёт заперт CI (tools/catalog_guard.py)
catalog-guard:
	python3 tools/catalog_guard.py

# Виток 9 (ЦУ 011): jail-приёмка границы Ст. 9 — сироты 0 за клеткой
# (userns-обёртка среды; ядро не менялось).
demo-jail-host: agryp
	bash demo/run_demo_jail_host.sh

bridge-test:
	bash tools/test_bridge.sh

# Виток 8 (ТЗ-8): бенчмарк против сверстников — ферма 100, метрики M1-M7.
# bench-stdiobus требует бинарь сверстника: STDIOBUS_BIN или клон в /tmp/peers.
bench: agryp
	sh tools/bench/run_bench.sh

bench-stdiobus:
	sh tools/bench/run_stdiobus.sh

audit:
	python3 demo/audit_transcript.py demo/demo-transcript.jsonl

audit-ctl:
	python3 demo/audit_transcript.py demo/ctl-transcript.jsonl
	python3 demo/negative_ctl_test.py

audit-finish:
	python3 demo/audit_transcript.py demo/finish-transcript.jsonl

audit-ready:
	python3 demo/audit_transcript.py demo/ready-transcript.jsonl

audit-reload:
	python3 demo/audit_transcript.py demo/reload-transcript.jsonl

audit-jail:
	python3 demo/audit_transcript.py demo/jail-transcript.jsonl

audit-stream:
	python3 demo/audit_transcript.py demo/stream-transcript.jsonl

audit-jail-host:
	python3 demo/audit_jail_host.py demo/jail-host-transcript.jsonl

clean:
	rm -f agryp ed25519tool

.PHONY: demo demo-ctl demo-finish demo-ready demo-reload demo-jail demo-stream demo-jail-host demo-metrics demo-rotate demo-sign demo-envelope journal-audit audit audit-ctl audit-finish audit-ready audit-reload audit-jail audit-stream audit-jail-host bridge-test bench bench-stdiobus test-p37 clean

# Виток 11 (тикет 018): проверяльщик проверяет себя — негативные пробы
# обязаны краснеть по делу, канарейка обязана быть зелёной (fail-closed).
audit-neg:
	sh tools/negative_probes.sh
