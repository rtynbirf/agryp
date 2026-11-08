/*
 * ed25519tool.c — П37 (волна ×6): CLI границы клетки для подписанных конвертов.
 *
 * Примитив — vendored orlp/ed25519 (zlib, vendor/ed25519/, verbatim;
 * provenance — vendor/ed25519/VENDOR-NOTES.md). Этот файл — единственный
 * собственный C вне ядра (Ст. 1, Поправка №12): тонкий адаптер,
 * никакой криптографии своего сочинения.
 *
 * usage:
 *   ed25519tool keygen                      32B из /dev/urandom → "seed <hex>\npub <hex>\n"
 *   ed25519tool pub <seed-hex>              публичник из seed → 64 hex
 *   ed25519tool sign <seed-hex> [file|-]    подпись сообщения → 128 hex
 *                                           (seed можно env AGRY_ED25519_SEED)
 *   ed25519tool verify <pub-hex> [file|-] <sig-hex>
 *                                           rc: 0 — годна, 1 — подпись не сходится,
 *                                               2 — битый вход (hex/файл/argc)
 *
 * rc=1 (подпись битая) и rc=2 (вход битый) различаются для честных
 * сообщений; надзорная дверь (tools/signed_envelope.py) отказывает при
 * ЛЮБОМ rc != 0 — fail-closed.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "ed25519.h"

#define SEED_LEN  32
#define PUB_LEN   32
#define SIG_LEN   64

static int hexval(int c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* строгий hex: длина ровно 2*out_len, только hex-цифры */
static int parse_hex(const char *s, unsigned char *out, size_t out_len) {
    size_t n = strlen(s), i;
    if (n != out_len * 2) return -1;
    for (i = 0; i < out_len; i++) {
        int hi = hexval((unsigned char)s[2 * i]);
        int lo = hexval((unsigned char)s[2 * i + 1]);
        if (hi < 0 || lo < 0) return -1;
        out[i] = (unsigned char)((hi << 4) | lo);
    }
    return 0;
}

static void print_hex(const unsigned char *b, size_t n) {
    size_t i;
    for (i = 0; i < n; i++) printf("%02x", b[i]);
    printf("\n");
}

/* прочитать сообщение целиком: file == "-" → stdin */
static unsigned char *read_msg(const char *path, size_t *out_len) {
    FILE *f = (strcmp(path, "-") == 0) ? stdin : fopen(path, "rb");
    size_t cap = 4096, len = 0;
    unsigned char *buf;
    if (!f) return NULL;
    buf = malloc(cap);
    if (!buf) { if (f != stdin) fclose(f); return NULL; }
    for (;;) {
        size_t got;
        if (len == cap) {
            unsigned char *nb;
            cap *= 2;
            nb = realloc(buf, cap);
            if (!nb) { free(buf); if (f != stdin) fclose(f); return NULL; }
            buf = nb;
        }
        got = fread(buf + len, 1, cap - len, f);
        len += got;
        if (got == 0) break;
    }
    if (ferror(f)) { free(buf); if (f != stdin) fclose(f); return NULL; }
    if (f != stdin) fclose(f);
    *out_len = len;
    return buf;
}

static int cmd_keygen(void) {
    unsigned char seed[SEED_LEN], pub[PUB_LEN], priv[64];
    FILE *ur = fopen("/dev/urandom", "rb");
    if (!ur) { fprintf(stderr, "ed25519tool: /dev/urandom не открыт\n"); return 2; }
    if (fread(seed, 1, SEED_LEN, ur) != SEED_LEN) {
        fprintf(stderr, "ed25519tool: короткое чтение /dev/urandom\n");
        fclose(ur);
        return 2;
    }
    fclose(ur);
    ed25519_create_keypair(pub, priv, seed);
    printf("seed "); print_hex(seed, SEED_LEN);
    printf("pub ");  print_hex(pub, PUB_LEN);
    return 0;
}

static int cmd_pub(const char *seed_hex) {
    unsigned char seed[SEED_LEN], pub[PUB_LEN], priv[64];
    if (parse_hex(seed_hex, seed, SEED_LEN) != 0) {
        fprintf(stderr, "ed25519tool: seed должен быть 64 hex\n");
        return 2;
    }
    ed25519_create_keypair(pub, priv, seed);
    print_hex(pub, PUB_LEN);
    return 0;
}

static int cmd_sign(const char *seed_hex, const char *path) {
    unsigned char seed[SEED_LEN], pub[PUB_LEN], priv[64], sig[SIG_LEN];
    unsigned char *msg;
    size_t msg_len;
    if (!seed_hex || parse_hex(seed_hex, seed, SEED_LEN) != 0) {
        fprintf(stderr, "ed25519tool: нет seed (argv или env AGRY_ED25519_SEED, 64 hex)\n");
        return 2;
    }
    msg = read_msg(path, &msg_len);
    if (!msg) { fprintf(stderr, "ed25519tool: сообщение не прочитано (%s)\n", path); return 2; }
    ed25519_create_keypair(pub, priv, seed);
    ed25519_sign(sig, msg, msg_len, pub, priv);
    free(msg);
    print_hex(sig, SIG_LEN);
    return 0;
}

static int cmd_verify(const char *pub_hex, const char *path, const char *sig_hex) {
    unsigned char pub[PUB_LEN], sig[SIG_LEN];
    unsigned char *msg;
    size_t msg_len;
    if (parse_hex(pub_hex, pub, PUB_LEN) != 0) {
        fprintf(stderr, "ed25519tool: pub должен быть 64 hex\n");
        return 2;
    }
    if (parse_hex(sig_hex, sig, SIG_LEN) != 0) {
        fprintf(stderr, "ed25519tool: sig должна быть 128 hex\n");
        return 2;
    }
    msg = read_msg(path, &msg_len);
    if (!msg) { fprintf(stderr, "ed25519tool: сообщение не прочитано (%s)\n", path); return 2; }
    int ok = ed25519_verify(sig, msg, msg_len, pub);
    free(msg);
    return ok ? 0 : 1;
}

int main(int argc, char **argv) {
    const char *env_seed;
    if (argc < 2) {
        fprintf(stderr, "usage: ed25519tool keygen|pub <seed>|sign <seed> [file|-]|verify <pub> [file|-] <sig>\n");
        return 2;
    }
    if (strcmp(argv[1], "keygen") == 0 && argc == 2) return cmd_keygen();
    if (strcmp(argv[1], "pub") == 0 && argc == 3) return cmd_pub(argv[2]);
    if (strcmp(argv[1], "sign") == 0 && (argc == 3 || argc == 4)) {
        env_seed = getenv("AGRY_ED25519_SEED");
        return cmd_sign(argc == 4 ? argv[2] : env_seed, argc == 4 ? argv[3] : "-");
    }
    if (strcmp(argv[1], "verify") == 0 && (argc == 4 || argc == 5)) {
        /* verify <pub> <sig>          — сообщение из stdin
           verify <pub> [file|-] <sig> — сообщение из файла */
        if (argc == 4) return cmd_verify(argv[2], "-", argv[3]);
        return cmd_verify(argv[2], argv[3], argv[4]);
    }
    fprintf(stderr, "usage: ed25519tool keygen|pub <seed>|sign <seed> [file|-]|verify <pub> [file|-] <sig>\n");
    return 2;
}
