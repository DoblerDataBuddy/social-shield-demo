"""
run_social_shield_demo.py
================================================
Social Shield v0.6 — Full System Integration Demo

Executes full pipeline:
snapshots → kernel → capsules → ledger → Merkle → verifier

✔ Deterministic classification
✔ Replayable audit trace
✔ Hash-chain ledger
✔ Merkle commitment
✔ Independent verification
"""

import json
import hashlib

from social_shield_kernel_v06 import (
    classify_structure,
    system_amplification_flag,
    InteractionSnapshot,
    StructuralSignals
)

# ─────────────────────────────────────────────
# Crypto primitives
# ─────────────────────────────────────────────
def sha256(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()

def canonical_json(data) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def merkle_root(leaves):
    if not leaves:
        return None
    level = leaves[:]
    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i + 1] if i + 1 < len(level) else a
            next_level.append(sha256(a + b))
        level = next_level
    return level[0]

# ─────────────────────────────────────────────
# Test scenarios
# ─────────────────────────────────────────────
SCENARIOS = [
    InteractionSnapshot("user_A", 2, 2,
        StructuralSignals(0.2, 0.1, 0.1, 0.1, 0.2, 0.1), False),
    InteractionSnapshot("user_B", 5, 0,
        StructuralSignals(0.2, 0.1, 0.2, 0.1, 0.3, 0.1), False),
    InteractionSnapshot("user_C", 1, 0,
        StructuralSignals(0.2, 0.1, 0.7, 0.6, 0.8, 0.5), False),
    InteractionSnapshot("user_D", 3, 2,
        StructuralSignals(0.3, 0.9, 0.2, 0.2, 0.2, 0.2), False),
    InteractionSnapshot("user_E", 4, 3,
        StructuralSignals(0.8, 0.2, 0.2, 0.1, 0.2, 0.2), False),
]
FROZEN_TIMESTAMP = 1742400000
SCHEMA_VERSION = "SS-0.6"

# ─────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────
def run():

    print("\n=== Social Shield v0.6 — Demo ===\n")

    # ── Stage 1: Classification ──
    print("Stage 1 — Classification\n")

    classifications = []

    for snap in SCENARIOS:
        state, reason = classify_structure(snap)
        amp = system_amplification_flag(state, snap)

        classifications.append((snap, state, reason, amp))

        flag = f" [flag: {amp.name}]" if amp else ""
        print(f"{snap.target_id:<10} {state.name}{flag}")

    # ── Stage 2: Capsules ──
    print("\nStage 2 — Capsules\n")

    capsules = []
    capsule_hashes = []

    for snap, state, reason, amp in classifications:

        snap_dict = {
            "target_id": snap.target_id,
            "inbound_actors": snap.inbound_actors,
            "outbound_actors": snap.outbound_actors,
            "telemetry_valid": snap.telemetry_valid,
            "invalid_geometry": snap.invalid_geometry,
            "usw": vars(snap.signals)
        }

        snap_hash = sha256(canonical_json(snap_dict))

        trace = {
            "target_id": snap.target_id,
            "state": state.value,
            "reason": reason,
            "persistence": 1,
            "enforcement": "none",
            "abetment": amp.value if amp else "",
            "snapshot_hash": snap_hash,
            "schema": SCHEMA_VERSION,
        }

        trace_hash = sha256(canonical_json(trace))

        capsule_payload = {
            "trace_hash": trace_hash,
            "timestamp": FROZEN_TIMESTAMP,
            "schema": SCHEMA_VERSION,
        }

        capsule_hash = sha256(canonical_json(capsule_payload))
        capsule_hashes.append(capsule_hash)

        capsule = {
            **trace,
            "trace_hash": trace_hash,
            "timestamp": FROZEN_TIMESTAMP,
            "capsule_hash": capsule_hash,
            "snapshot": snap_dict,
        }

        capsules.append(capsule)

        print(f"{snap.target_id:<10} {capsule_hash[:16]}...")

    # ── Stage 3: Ledger ──
    print("\nStage 3 — Ledger\n")

    ledger = []
    prev = None

    for i, c in enumerate(capsules):
        entry = {
            "index": i,
            "capsule_hash": c["capsule_hash"],
            "previous_hash": prev
        }

        entry_hash = sha256(canonical_json(entry))
        entry["entry_hash"] = entry_hash

        ledger.append(entry)
        prev = entry_hash

        print(f"[{i}] {entry_hash[:16]}...")

    # ── Stage 4: Merkle ──
    print("\nStage 4 — Merkle Root\n")

    root = merkle_root(capsule_hashes)
    print("Root:", root)

    # ── Save artifacts ──
    with open("audit_capsules.json", "w") as f:
        json.dump(capsules, f, indent=2)

    with open("ledger.json", "w") as f:
        json.dump(ledger, f, indent=2)

    # ── Stage 5: Verification ──
    print("\nStage 5 — Verification\n")

    # Ledger check
    prev = None
    for e in ledger:
        check = sha256(canonical_json({
            "index": e["index"],
            "capsule_hash": e["capsule_hash"],
            "previous_hash": prev
        }))
        assert check == e["entry_hash"]
        prev = e["entry_hash"]

    print("✔ Ledger OK")

    # Capsule check
    for c in capsules:
        check = sha256(canonical_json({
            "trace_hash": c["trace_hash"],
            "timestamp": c["timestamp"],
            "schema": c["schema"]
        }))
        assert check == c["capsule_hash"]

    print("✔ Capsules OK")

    # Merkle check
    assert merkle_root([c["capsule_hash"] for c in capsules]) == root
    print("✔ Merkle OK")

    # Replay check
    for c in capsules:
        d = c["snapshot"]

        snap = InteractionSnapshot(
            d["target_id"],
            d["inbound_actors"],
            d["outbound_actors"],
            StructuralSignals(**d["usw"]),
            d["invalid_geometry"],
            d["telemetry_valid"]
        )

        state, reason = classify_structure(snap)
        amp = system_amplification_flag(state, snap)

        replay = {
            "target_id": c["target_id"],
            "state": state.value,
            "reason": reason,
            "persistence": c["persistence"],
            "enforcement": c["enforcement"],
            "abetment": amp.value if amp else "",
            "snapshot_hash": c["snapshot_hash"],
            "schema": c["schema"],
        }

        assert sha256(canonical_json(replay)) == c["trace_hash"]

    print("✔ Replay OK")

    print("\n=== PIPELINE PASSED ===\n")


if __name__ == "__main__":
    run()