#!/bin/bash
# Matched-region compact LSO diagnostic.
#
# Uses the generic leave-subject-out loop, but keeps the arm set narrow enough
# for a first complete matched-cache pass.
set -e

cd "$(dirname "$0")/.."

export ARMS="${ARMS:-shared_baseline pure_anatomy region_only}"
export SEEDS="${SEEDS:-0}"
export TARGET_MODE="${TARGET_MODE:-stimulus_side}"
export OUT_ROOT="${OUT_ROOT:-runs/lso_matched_support80_best6_seed0}"

bash scripts/run_leave_subject_out_a100.sh
