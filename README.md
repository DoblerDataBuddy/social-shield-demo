# Social Shield v0.6 — Deterministic Audit Demo

This repository demonstrates a deterministic structural classification system with a replayable audit pipeline.
This is a prototype demonstration pipeline operating on synthetic data.

## Limitations
It does not constitute production cryptographic infrastructure, has not been validated on real-world datasets, has no measured error rates, and has not been evaluated for legal admissibility.
It is intended solely to demonstrate deterministic classification and replayable audit behavior in a controlled setting.

## Key Property

This demo reproduces identical results across runs, including a fixed Merkle root:

9479758740ca3c03296838b12018bb58be98ed781a45d69bfc8b31c1e155119c

This means:
- The same inputs always produce the same classifications
- The audit trail is fully reproducible
- The global commitment (Merkle root) is stable and verifiable

## What this demo shows

- Deterministic classification (same input → same output)
- Audit capsule generation
- Hash-chain ledger
- Merkle root commitment
- Independent replay verification

## Run the demo

```bash
python run_social_shield_demo.py
