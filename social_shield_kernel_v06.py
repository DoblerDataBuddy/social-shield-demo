from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional

class StructuralState(Enum):
    STABLE_RECIPROCAL = "normal interaction topology"
    SIGNAL_INSUFFICIENT = "insufficient or noisy signal"
    INBOUND_ASYMMETRY = "sustained inbound interaction imbalance"
    COORDINATED_PATTERN = "coordinated structural interaction pattern"
    RELAY_TOPOLOGY = "relay or bridge node topology detected"
    LOW_RECIPROCITY_CLUSTER = "low-reciprocity interaction cluster"
    INTENSITY_THRESHOLD = "interaction intensity threshold exceeded"
    AMPLIFIED_EXPOSURE = "system amplification of interaction access"
    INVALID_CONFIGURATION = "structurally invalid interaction configuration"

RESONANCE_ENTER = 0.60
INTENSITY_ENTER = 0.70
RELAY_ENTER = 0.70
MIN_INBOUND_ACTORS = 3
MIN_RECIPROCITY_RATIO = 0.20
LOW_CLUSTER_MAX = 2
LOW_CLUSTER_INTENSITY = 0.50
LOW_CLUSTER_VARIANCE = 0.60
AMPLIFICATION_ENTER = 0.40

@dataclass(frozen=True)
class StructuralSignals:
    coherence: float
    topology_bridge: float
    phase: float
    phase_drift: float
    variance: float
    exposure_lift: float

@dataclass(frozen=True)
class InteractionSnapshot:
    target_id: str
    inbound_actors: int
    outbound_actors: int
    signals: StructuralSignals
    invalid_geometry: bool
    telemetry_valid: bool = True

def compute_intensity(s: StructuralSignals) -> float:
    return min(1.0, 0.4*abs(s.phase) + 0.4*abs(s.phase_drift) + 0.2*s.variance)

def invalid_snapshot(snap: InteractionSnapshot) -> bool:
    if snap.inbound_actors < 0 or snap.outbound_actors < 0:
        return True
    s = snap.signals
    if not (0 <= s.coherence <= 1): return True
    if not (0 <= s.topology_bridge <= 1): return True
    if not (-1 <= s.phase <= 1): return True
    if not (-1 <= s.phase_drift <= 1): return True
    if not (0 <= s.variance <= 1): return True
    if not (0 <= s.exposure_lift <= 1): return True
    return False

def classify_structure(snap: Optional[InteractionSnapshot]) -> Tuple[StructuralState, str]:
    if snap is None:
        return (StructuralState.INVALID_CONFIGURATION, "Missing interaction snapshot.")
    if not snap.telemetry_valid:
        return (StructuralState.SIGNAL_INSUFFICIENT, "Telemetry unreliable.")
    if invalid_snapshot(snap):
        return (StructuralState.INVALID_CONFIGURATION, "Invalid structural input.")
    if snap.inbound_actors == 0 and snap.outbound_actors == 0:
        return (StructuralState.STABLE_RECIPROCAL, "Stable reciprocal interaction.")
    reciprocity = snap.outbound_actors / max(1, snap.inbound_actors)
    intensity = compute_intensity(snap.signals)
    if snap.invalid_geometry:
        return (StructuralState.INVALID_CONFIGURATION, "Impossible interaction geometry.")
    if (snap.inbound_actors <= LOW_CLUSTER_MAX and reciprocity < MIN_RECIPROCITY_RATIO
            and intensity >= LOW_CLUSTER_INTENSITY and snap.signals.variance >= LOW_CLUSTER_VARIANCE):
        return (StructuralState.LOW_RECIPROCITY_CLUSTER, "Low reciprocity cluster detected.")
    if snap.inbound_actors >= MIN_INBOUND_ACTORS and reciprocity < MIN_RECIPROCITY_RATIO:
        return (StructuralState.INBOUND_ASYMMETRY, "Inbound interaction imbalance.")
    if intensity >= INTENSITY_ENTER:
        return (StructuralState.INTENSITY_THRESHOLD, "Interaction intensity threshold exceeded.")
    if snap.signals.topology_bridge >= RELAY_ENTER:
        return (StructuralState.RELAY_TOPOLOGY, "Relay node topology detected.")
    if snap.signals.coherence >= RESONANCE_ENTER:
        return (StructuralState.COORDINATED_PATTERN, "Coordinated interaction structure.")
    return (StructuralState.STABLE_RECIPROCAL, "Stable reciprocal interaction.")

def system_amplification_flag(state: StructuralState, snap: InteractionSnapshot) -> Optional[StructuralState]:
    if (state in {StructuralState.LOW_RECIPROCITY_CLUSTER, StructuralState.INTENSITY_THRESHOLD}
            and snap.signals.exposure_lift >= AMPLIFICATION_ENTER):
        return StructuralState.AMPLIFIED_EXPOSURE
    return None
