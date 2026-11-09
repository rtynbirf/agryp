CC      ?= gcc
CFLAGS  ?= -O2 -Wall -Wextra -std=c99

agryp: src/agryp.c
	$(CC) $(CFLAGS) -o $@ $<

demo: agryp
	bash demo/run_demo.sh

demo-ctl: agryp
	bash demo/run_demo_ctl.sh

demo-v6: agryp
	bash demo/run_demo_v6.sh

audit:
	python3 demo/audit_transcript.py demo/demo-transcript.jsonl

audit-ctl:
	python3 demo/audit_transcript.py demo/ctl-transcript.jsonl
	python3 demo/negative_ctl_test.py

audit-v6:
	python3 demo/audit_transcript.py demo/v6-transcript.jsonl --units demo/v6-units

clean:
	rm -f agryp

.PHONY: demo demo-ctl demo-v6 audit audit-ctl audit-v6 clean
