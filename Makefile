CC      ?= gcc
CFLAGS  ?= -O2 -Wall -Wextra -std=c99

agryp: src/agryp.c
	$(CC) $(CFLAGS) -o $@ $<

demo: agryp
	bash demo/run_demo.sh

audit:
	python3 demo/audit_transcript.py demo/demo-transcript.jsonl

clean:
	rm -f agryp

.PHONY: demo audit clean
