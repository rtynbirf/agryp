CC      ?= gcc
CFLAGS  ?= -O2 -Wall -Wextra -std=c99

agryp: src/agryp.c
	$(CC) $(CFLAGS) -o $@ $<

demo: agryp
	bash demo/run_demo.sh

clean:
	rm -f agryp

.PHONY: demo clean
