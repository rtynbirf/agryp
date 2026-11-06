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

demo-reload: agryp
	bash demo/run_demo_reload.sh

demo-jail: agryp
	bash demo/run_demo_jail.sh

demo-stream: agryp
	bash demo/run_demo_stream.sh

bridge-test:
	bash tools/test_bridge.sh

audit:
	python3 demo/audit_transcript.py demo/demo-transcript.jsonl

audit-ctl:
	python3 demo/audit_transcript.py demo/ctl-transcript.jsonl
	python3 demo/negative_ctl_test.py

audit-finish:
	python3 demo/audit_transcript.py demo/finish-transcript.jsonl

audit-reload:
	python3 demo/audit_transcript.py demo/reload-transcript.jsonl

audit-jail:
	python3 demo/audit_transcript.py demo/jail-transcript.jsonl

audit-stream:
	python3 demo/audit_transcript.py demo/stream-transcript.jsonl

clean:
	rm -f agryp

.PHONY: demo demo-ctl demo-finish demo-reload demo-jail demo-stream audit audit-ctl audit-finish audit-reload audit-jail audit-stream bridge-test clean
