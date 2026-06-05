#!/bin/bash
# Narrow matched-cache confirmation for the strongest seed-0 holdouts.
set -e

cd "$(dirname "$0")/.."

export SUBJECTS="${SUBJECTS:-MFD_06 KS014 CSH_ZAD_019}"
export ARMS="${ARMS:-shared_baseline pure_anatomy region_only}"
export SEEDS="${SEEDS:-1 2}"
export TARGET_MODE="${TARGET_MODE:-stimulus_side}"
export OUT_ROOT="${OUT_ROOT:-runs/lso_matched_support80_best6_confirm}"

bash scripts/run_leave_subject_out_a100.sh
