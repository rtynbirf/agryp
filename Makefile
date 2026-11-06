CC      ?= gcc
CFLAGS  ?= -O2 -Wall -Wextra -std=c99

agryp: src/agryp.c
	$(CC) $(CFLAGS) -o $@ $<

demo: agryp
	bash demo/run_demo.sh

demo-ctl: agryp
	bash demo/run_demo_ctl.sh

demo-finish: agryp
	bash demo/run_demo_finish.sh

audit:
	python3 demo/audit_transcript.py demo/demo-transcript.jsonl

audit-ctl:
	python3 demo/audit_transcript.py demo/ctl-transcript.jsonl
	python3 demo/negative_ctl_test.py

audit-finish:
	python3 demo/audit_transcript.py demo/finish-transcript.jsonl

clean:
	rm -f agryp

.PHONY: demo demo-ctl demo-finish audit audit-ctl audit-finish clean
