#!/bin/bash
# Multi-seed confirmation for held-out subjects that showed a one-seed
# anatomy-vs-null lift in the leave-subject-out screen.
set -e

cd "$(dirname "$0")/.."

SUBJECTS="${SUBJECTS:-CSHL045 DY_008 MFD_05 KS014}"
ARMS="${ARMS:-shared_baseline region_only pure_anatomy waveform_only}"
SEEDS="${SEEDS:-0 1 2}"
OUT_ROOT="${OUT_ROOT:-runs/lso_promising_a100}"
TARGET_MODE="${TARGET_MODE:-stimulus_side}"

export SUBJECTS ARMS SEEDS OUT_ROOT TARGET_MODE
bash scripts/run_leave_subject_out_a100.sh
