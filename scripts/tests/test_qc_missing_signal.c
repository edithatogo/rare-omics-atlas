/* Focused native-R detection semantics for the pinned SeSAMe C producer.
 *
 * Link the real qc/prep/numerics/sigdf/index/util translation units; no
 * numerical functions are replaced. The caller supplies a disposable output
 * directory for the temporary synthetic ordering file.
 *
 * Every background entry is excluded, selecting the documented 1:1000 prior.
 * Present test signals exceed 1000, so their p-value is exactly zero; probes
 * with neither channel present have p=1 under the pinned native R contract.
 * Expected counts below are literal fixture expectations, not summaries of
 * the producer's p-value output.
 *
 * 512 probes retain meaningful R/G pools through the complete QC routine and
 * exceed the producer's existing 1000-value prior buffer requirement. This
 * harness does not qualify arrays below 334 probes or repair that separate
 * upstream allocation limitation.
 */
#include "sesame.h"

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

enum { PROBES = 512 };

typedef struct {
    sesame_sigdf_t signal;
    double mg[PROBES], mr[PROBES], ug[PROBES], ur[PROBES];
    uint8_t channel[PROBES], mask[PROBES], background_mask[PROBES];
    uint8_t expected_absent[PROBES];
} fixture_t;

typedef struct {
    double detected, unmasked_detected, unmasked_denominator;
    double cg_detected, cg_denominator;
    double ch_detected, ch_denominator;
    double rs_detected, rs_denominator;
} expected_t;

static int failures = 0;

static void expect(int condition, const char *test, const char *field)
{
    if (!condition) {
        fprintf(stderr, "FAIL %s: %s\n", test, field);
        failures++;
    }
}

static int write_index(const char *directory, int controls_only,
                       sesame_index_t **index)
{
    char path[4096];
    sesame_err_t error;
    int fd, written;
    FILE *stream;

    written = snprintf(path, sizeof path, "%s/qc-ordering-XXXXXX", directory);
    if (written < 0 || (size_t)written >= sizeof path) return 1;
    fd = mkstemp(path);
    if (fd < 0) return 1;
    stream = fdopen(fd, "w");
    if (!stream) {
        close(fd);
        unlink(path);
        return 1;
    }
    if (fputs("Probe_ID\tM\tU\tcol\n", stream) == EOF) {
        fclose(stream);
        unlink(path);
        return 1;
    }
    for (int i = 0; i < PROBES; i++) {
        static const char *const kinds[] = {"cg", "ch", "rs"};
        const char *kind = controls_only || i == PROBES - 1 ? "ctl" : kinds[i % 3];
        if (fprintf(stream, "%s%06d\t%d\t%d\t%c\n", kind, i,
                    2 * i + 1, 2 * i + 2, i % 2 ? 'G' : 'R') < 0) {
            fclose(stream);
            unlink(path);
            return 1;
        }
    }
    if (fclose(stream) != 0) {
        unlink(path);
        return 1;
    }
    *index = sesame_index_open(path, &error);
    unlink(path);
    return *index ? 0 : 1;
}

static void initialise(fixture_t *fixture, const sesame_index_t *index)
{
    memset(fixture, 0, sizeof *fixture);
    fixture->signal.ix = index;
    fixture->signal.n = PROBES;
    fixture->signal.MG = fixture->mg;
    fixture->signal.MR = fixture->mr;
    fixture->signal.UG = fixture->ug;
    fixture->signal.UR = fixture->ur;
    fixture->signal.col = fixture->channel;
    fixture->signal.mask = fixture->mask;
    for (int i = 0; i < PROBES; i++) {
        double high = 1200.0 + 7.0 * (double)(i % 31);
        double low = 20.0 + 3.0 * (double)(i % 17);
        fixture->channel[i] = i % 2 ? SESAME_COL_G : SESAME_COL_R;
        fixture->mg[i] = fixture->ug[i] = i % 2 ? high : low;
        fixture->mr[i] = fixture->ur[i] = i % 2 ? low : high;
        fixture->background_mask[i] = 1;
    }
}

static void make_absent(fixture_t *fixture, int i)
{
    fixture->mg[i] = fixture->mr[i] = fixture->ug[i] = fixture->ur[i] = NAN;
    fixture->expected_absent[i] = 1;
}

static void expect_ratio(double actual, double numerator, double denominator,
                         const char *test, const char *field)
{
    expect(denominator == 0.0 ? isnan(actual) : actual == numerator / denominator,
           test, field);
}

static void run_case(const char *name, fixture_t *fixture, expected_t expected)
{
    fixture_t before;
    sesame_qc_t result;
    sesame_err_t error;
    double pvalues[PROBES];
    int previous_failures = failures;
    int rc;

    memcpy(&before, fixture, sizeof before);
    rc = sesame_poobah_pvals(&fixture->signal, fixture->background_mask,
                             PROBES, 1, pvalues, &error);
    expect(rc == SESAME_OK, name, "native p-value call succeeds");
    if (rc == SESAME_OK) {
        for (int i = 0; i < PROBES; i++) {
            expect(pvalues[i] == (fixture->expected_absent[i] ? 1.0 : 0.0),
                   name, "p-value matches independently fixed prior expectation");
        }
    }

    rc = sesame_qc_calc(&fixture->signal, fixture->background_mask, PROBES,
                        NULL, 0, &result, &error);
    expect(rc == SESAME_OK, name, "complete native QC call succeeds");
    if (rc == SESAME_OK) {
        expect(result.num_dtna == 0.0, name, "num_dtna");
        expect(result.frac_dtna == 0.0, name, "frac_dtna");
        expect(result.num_dt == expected.detected, name, "num_dt");
        expect_ratio(result.frac_dt, expected.detected, PROBES, name, "frac_dt");
        expect(result.num_dt_mk == expected.unmasked_detected, name, "num_dt_mk");
        expect_ratio(result.frac_dt_mk, expected.unmasked_detected,
                      expected.unmasked_denominator, name, "frac_dt_mk");
        expect(result.num_dt_cg == expected.cg_detected, name, "num_dt_cg");
        expect_ratio(result.frac_dt_cg, expected.cg_detected,
                      expected.cg_denominator, name, "frac_dt_cg");
        expect(result.num_dt_ch == expected.ch_detected, name, "num_dt_ch");
        expect_ratio(result.frac_dt_ch, expected.ch_detected,
                      expected.ch_denominator, name, "frac_dt_ch");
        expect(result.num_dt_rs == expected.rs_detected, name, "num_dt_rs");
        expect_ratio(result.frac_dt_rs, expected.rs_detected,
                      expected.rs_denominator, name, "frac_dt_rs");
        expect(result.num_probes == PROBES, name, "complete probe universe");
        expect(isnan(result.GCT), name, "absent extension input leaves GCT missing");
    }
    expect(memcmp(before.mg, fixture->mg, sizeof before.mg) == 0 &&
           memcmp(before.mr, fixture->mr, sizeof before.mr) == 0 &&
           memcmp(before.ug, fixture->ug, sizeof before.ug) == 0 &&
           memcmp(before.ur, fixture->ur, sizeof before.ur) == 0,
           name, "input signals unchanged");
    expect(memcmp(before.channel, fixture->channel, sizeof before.channel) == 0 &&
           memcmp(before.mask, fixture->mask, sizeof before.mask) == 0 &&
           memcmp(before.background_mask, fixture->background_mask,
                  sizeof before.background_mask) == 0 &&
           before.signal.status == fixture->signal.status,
           name, "input channels, masks and status unchanged");
    if (failures == previous_failures) printf("PASS %s\n", name);
}

int main(int argc, char **argv)
{
    fixture_t fixture;
    sesame_index_t *index = NULL, *controls = NULL;
    const expected_t baseline = {512, 512, 512, 171, 171, 170, 170, 170, 170};
    const expected_t absent = {508, 508, 512, 170, 171, 169, 170, 169, 170};

    if (argc != 2) {
        fprintf(stderr, "usage: test_qc_missing_signal DISPOSABLE_DIRECTORY\n");
        return 2;
    }
    if (write_index(argv[1], 0, &index) || write_index(argv[1], 1, &controls)) {
        fprintf(stderr, "cannot create synthetic ordering\n");
        sesame_index_close(index);
        sesame_index_close(controls);
        return 2;
    }

    initialise(&fixture, index);
    run_case("finite baseline", &fixture, baseline);

    initialise(&fixture, index);
    make_absent(&fixture, 0);   /* cg */
    make_absent(&fixture, 1);   /* ch */
    make_absent(&fixture, 2);   /* rs */
    make_absent(&fixture, 511); /* control: belongs to the overall denominator */
    run_case("absent signals remain denominator members", &fixture, absent);

    fixture.mask[0] = fixture.mask[511] = 1; /* two absent probes */
    fixture.mask[3] = 1;                   /* one detected cg probe */
    run_case("existing masks change only the masked denominator", &fixture,
              (expected_t){508, 507, 509, 170, 171, 169, 170, 169, 170});

    initialise(&fixture, index);
    fixture.mr[0] = fixture.ur[0] = NAN;
    fixture.mg[0] = fixture.ug[0] = 1500.0;
    fixture.mg[1] = fixture.ug[1] = NAN;
    fixture.mr[1] = fixture.ur[1] = 1500.0;
    fixture.mg[2] = fixture.ug[2] = fixture.mr[2] = NAN;
    fixture.ur[2] = 1500.0;
    fixture.mr[3] = fixture.ur[3] = fixture.mg[3] = NAN;
    fixture.ug[3] = 1500.0;
    run_case("a present channel or allele retains detection", &fixture, baseline);

    initialise(&fixture, index);
    memset(fixture.mask, 1, sizeof fixture.mask);
    run_case("all masked gives an undefined masked fraction", &fixture,
              (expected_t){512, 0, 0, 171, 171, 170, 170, 170, 170});

    initialise(&fixture, controls);
    run_case("empty probe families have zero counts and undefined fractions", &fixture,
              (expected_t){512, 512, 512, 0, 0, 0, 0, 0, 0});

    initialise(&fixture, index);
    for (int i = 0; i < PROBES - 1; i += 3) make_absent(&fixture, i);
    run_case("an entirely absent family has a defined zero fraction", &fixture,
              (expected_t){341, 341, 512, 0, 171, 170, 170, 170, 170});

    sesame_index_close(index);
    sesame_index_close(controls);
    if (failures) {
        fprintf(stderr, "QC missing-signal regressions: %d failed assertions\n", failures);
        return 1;
    }
    printf("QC missing-signal regressions: 7 cases passed\n");
    return 0;
}
