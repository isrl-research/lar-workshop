#!/usr/bin/env python3
"""
Task: Enrich fortification substances with nutrient metadata
Model: gemini-2.0-flash
Temperature: 0
Batch size: 20
Input: input_substances.txt (58 substances)
Created: 2026-03-13
"""

import os
import sys
import time
import random
import xml.etree.ElementTree as ET
from collections import Counter

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai not installed. Run: pip install google-generativeai")
    sys.exit(1)

# ── Configuration ───────────────────────────────────────────────────────────────
MODEL_NAME   = "gemini-2.0-flash"
TEMPERATURE  = 0
BATCH_SIZE   = 20
INPUT_FILE   = "./input_substances.txt"
RAW_OUT      = "./output_raw.txt"
FMT_OUT      = "./output_formatted.txt"
SYS_XML      = "./system_instructions.xml"

EXPECTED_TOTAL = 58

# ── API Key ─────────────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
if not api_key:
    print("ERROR: Set GEMINI_API_KEY (or API_KEY) environment variable before running.")
    sys.exit(1)

genai.configure(api_key=api_key)

# ── Load System Instructions ─────────────────────────────────────────────────────
def load_system_instructions(path=SYS_XML):
    tree = ET.parse(path)
    root = tree.getroot()
    parts = []
    for child in root:
        text = "".join(child.itertext()).strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts)

# ── Gemini Client ─────────────────────────────────────────────────────────────────
def make_model(system_prompt):
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(temperature=TEMPERATURE)
    )

# ── Exponential Backoff ───────────────────────────────────────────────────────────
def call_with_backoff(fn, max_retries=8, base_delay=2.0, max_delay=120.0):
    consecutive_429s = 0
    for attempt in range(max_retries):
        try:
            result = fn()
            consecutive_429s = 0
            return result
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                consecutive_429s += 1
                if consecutive_429s >= 3:
                    print(f"\n  3 consecutive 429s. Pausing 60s...\n")
                    time.sleep(60)
                    consecutive_429s = 0
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                print(f"  Rate limited. Retry in {delay:.1f}s (attempt {attempt+1}/{max_retries})")
                time.sleep(delay)
            else:
                print(f"  Non-429 error: {err}")
                raise
    raise RuntimeError("Max retries exceeded")

# ── Raw Output ─────────────────────────────────────────────────────────────────────
def append_raw(response_text, record_id):
    with open(RAW_OUT, "a", encoding="utf-8") as f:
        f.write(f"--- RECORD {record_id} ---\n")
        f.write(response_text.strip())
        f.write("\n\n")

# ── Formatted Output ───────────────────────────────────────────────────────────────
def save_batch(lines):
    with open(FMT_OUT, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"  Saved {len(lines)} records to {FMT_OUT}")

# ── Parse Response ─────────────────────────────────────────────────────────────────
def parse_response(raw, record_id):
    """
    Extract the output line for this record from the raw response.
    Expected format: ID::[id] | CANONICAL::... | ...
    Returns the line as-is if it matches, or a flagged fallback line if not.
    """
    lines = [ln.strip() for ln in raw.strip().splitlines() if ln.strip()]
    # Find the line that starts with ID::
    for line in lines:
        if line.startswith("ID::"):
            return line
    # If no clean match, wrap the raw output with a flag
    safe = raw.strip().replace("\n", " ")[:200]
    return f"ID::{record_id} | CANONICAL::PARSE_ERROR | NUTRIENT_TYPE::UNSURE | REG_CATEGORY::UNSURE | SOURCE_TYPE::UNSURE | FSSAI_MANDATE::NONE | IS_GROUP::false | NOTES::Parse error — raw: {safe}"

# ── Load Input ─────────────────────────────────────────────────────────────────────
def load_input(path=INPUT_FILE):
    """
    Input format: "NN. SubstanceName"
    Returns list of dicts: {"id": "NN", "name": "SubstanceName", "text": full line}
    """
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if ". " in line:
                id_part, name_part = line.split(". ", 1)
                records.append({
                    "id": id_part.strip(),
                    "name": name_part.strip(),
                    "text": line
                })
            else:
                records.append({"id": str(len(records)+1), "name": line, "text": line})
    return records

# ── Post-Run Statistics ────────────────────────────────────────────────────────────
def print_statistics(formatted_path, expected_total):
    from collections import Counter

    try:
        with open(formatted_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        print(f"WARNING: {formatted_path} not found — no statistics.")
        return

    total = len(lines)
    print(f"\n{'='*60}")
    print(f"OUTPUT STATISTICS")
    print(f"{'='*60}")
    print(f"Total lines written : {total}")
    print(f"Expected            : {expected_total}")
    if total != expected_total:
        print(f"  *** WARNING: count mismatch ({total - expected_total:+d}) ***")

    def extract_field(line, field_name):
        marker = f"{field_name}::"
        if marker not in line:
            return None
        after = line.split(marker, 1)[1]
        return after.split(" | ")[0].strip()

    # NUTRIENT_TYPE distribution
    nt_counter = Counter()
    for line in lines:
        val = extract_field(line, "NUTRIENT_TYPE")
        if val:
            nt_counter[val] += 1
    print(f"\nNUTRIENT_TYPE distribution:")
    for val, count in nt_counter.most_common():
        pct = 100 * count / total if total > 0 else 0
        flag = "  [?-prefix]" if val.startswith("?") else ""
        print(f"  {val:35s}: {count:3d}  ({pct:.1f}%){flag}")

    # REG_CATEGORY distribution
    rc_counter = Counter()
    for line in lines:
        val = extract_field(line, "REG_CATEGORY")
        if val:
            rc_counter[val] += 1
    print(f"\nREG_CATEGORY distribution:")
    for val, count in rc_counter.most_common():
        pct = 100 * count / total if total > 0 else 0
        flag = "  [?-prefix]" if val.startswith("?") else ""
        print(f"  {val:35s}: {count:3d}  ({pct:.1f}%){flag}")

    # SOURCE_TYPE distribution
    st_counter = Counter()
    for line in lines:
        val = extract_field(line, "SOURCE_TYPE")
        if val:
            st_counter[val] += 1
    print(f"\nSOURCE_TYPE distribution:")
    for val, count in st_counter.most_common():
        pct = 100 * count / total if total > 0 else 0
        print(f"  {val:35s}: {count:3d}  ({pct:.1f}%)")

    # FSSAI_MANDATE presence
    mandate_counter = Counter()
    for line in lines:
        val = extract_field(line, "FSSAI_MANDATE")
        if val and val != "NONE":
            for food in val.split("|"):
                mandate_counter[food.strip()] += 1
    print(f"\nFSSAI_MANDATE food coverage:")
    if mandate_counter:
        for food, count in mandate_counter.most_common():
            print(f"  {food:20s}: {count:3d} substances")
    else:
        print("  None")

    # Flag markers
    unsure_count = sum(1 for ln in lines if "UNSURE" in ln)
    parse_err_count = sum(1 for ln in lines if "PARSE_ERROR" in ln)
    q_prefix_count = sum(1 for ln in lines if "::?" in ln)
    group_true = sum(1 for ln in lines if "IS_GROUP::true" in ln)
    print(f"\nFlag summary:")
    print(f"  UNSURE (any field)  : {unsure_count:3d}  ({100*unsure_count/total:.1f}%)" if total > 0 else "  UNSURE: 0")
    print(f"  ?-prefixed values   : {q_prefix_count:3d}")
    print(f"  PARSE_ERROR         : {parse_err_count:3d}")
    print(f"  IS_GROUP::true      : {group_true:3d}")

    print(f"{'='*60}\n")

# ── Main ────────────────────────────────────────────────────────────────────────────
def main():
    print(f"Loading system instructions from {SYS_XML}...")
    system_prompt = load_system_instructions()

    print(f"Loading input from {INPUT_FILE}...")
    records = load_input()
    print(f"  {len(records)} records loaded.")

    if len(records) != EXPECTED_TOTAL:
        print(f"  WARNING: expected {EXPECTED_TOTAL} records, found {len(records)}")

    gemini = make_model(system_prompt)

    total_batches = (len(records) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\nStarting: {len(records)} records, batch_size={BATCH_SIZE}, {total_batches} batches\n")

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        print(f"Batch {batch_num}/{total_batches} — {len(batch)} records...")

        batch_results = []
        for record in batch:
            user_msg = record["text"]

            def api_call(msg=user_msg):
                response = gemini.generate_content(msg)
                return response.text

            raw = call_with_backoff(api_call)
            append_raw(raw, record["id"])
            formatted = parse_response(raw, record["id"])
            batch_results.append(formatted)
            print(f"    {record['id']}. {record['name'][:50]}")

        save_batch(batch_results)
        print(f"  Batch {batch_num}/{total_batches} complete ({i + len(batch)}/{len(records)} total)\n")

    print(f"\nDone. Raw: {RAW_OUT} | Formatted: {FMT_OUT}")
    print_statistics(FMT_OUT, EXPECTED_TOTAL)

if __name__ == "__main__":
    main()
