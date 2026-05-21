"""
Jarvis System Model — Schema v0.1
Host: monarch (RTX 3090 24GB, Ryzen 9 9900X, 96GB DDR5, Ubuntu 24.04)

Eight top-level domains:
  hardware      — static, calibrated once
  tiers         — live state per tier T1–T5 (T6 offline by default)
  workloads     — active / pending / completed rolling window
  schedule      — 24h forward forecast
  quotas        — cloud API budgets and burn rates
  resources     — live VRAM / RAM / CPU
  events        — append-only rolling log (~24h)
  health        — per-component health checks

Doctrine: schema fields are what Jarvis must know to function as a manager.
Adding a field is a deliberate decision. Nothing here is inferred from
cardinal decisions — this layer observes reality regardless of doctrine.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class TierState(str, Enum):
    ACTIVE       = "active"
    SOFT_OFFLOAD = "soft_offload"
    STOPPED      = "stopped"
    FAILED       = "failed"
    STARTING     = "starting"
    STOPPING     = "stopping"
    OFFLINE      = "offline"   # T6 default — not part of current profile

class HealthStatus(str, Enum):
    OK           = "ok"
    DEGRADED     = "degraded"
    UNRESPONSIVE = "unresponsive"
    STOPPED      = "stopped"    # expected stopped (by profile)
    IDLE         = "idle"       # burst-only tier, cleanly offloaded (marker file present)
    ERROR        = "error"
    UNKNOWN      = "unknown"

class OOMRisk(str, Enum):
    LOW      = "low"
    ELEVATED = "elevated"
    IMMINENT = "imminent"

class WorkloadType(str, Enum):
    SCHEDULED   = "scheduled"
    HERMES_CRON = "hermes_cron"
    OPERATOR    = "operator"
    N8N         = "n8n"
    MANUAL      = "manual"

class WorkloadOutcome(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED  = "failed"
    TIMEOUT = "timeout"
    KILLED  = "killed"

class QuotaStatus(str, Enum):
    OK               = "ok"
    APPROACHING_WALL = "approaching_wall"
    WALLED           = "walled"

class OperatorState(str, Enum):
    ACTIVE   = "active"
    IDLE     = "idle"
    SLEEPING = "sleeping"
    UNKNOWN  = "unknown"


# ─── Hardware (static) ────────────────────────────────────────────────────────

class GPUHardware(BaseModel):
    model: str                   = "RTX 3090 FE"
    vram_total_mb: int           = 24576
    vram_reserve_driver_mb: int  = 512
    vram_usable_mb: int          = 24064
    arch: str                    = "Ampere SM86"
    cuda_capability: str         = "8.6"
    pcie_gen: int                = 4
    pcie_lanes: int              = 16
    pcie_bandwidth_gbps: float   = 32.0

class CPUHardware(BaseModel):
    model: str          = "Ryzen 9 9900X"
    cores_total: int    = 12
    cores_reserved: int = 2
    cores_available: int = 10

class RAMHardware(BaseModel):
    total_mb: int             = 98304
    ddr_generation: str       = "DDR5"
    speed_mts: int            = 6000
    bandwidth_gbps: float     = 96.0

class StorageHardware(BaseModel):
    nvme_path: str     = "/home/monarch"
    nvme_total_gb: int = 4096
    models_cache: str  = "~/.cache/huggingface/hub"
    # Models loaded via -hf <org>/<repo>:<quant> shortcut syntax.
    # No ~/models/ migration planned — HF cache is the storage substrate.

class Hardware(BaseModel):
    gpu: GPUHardware      = Field(default_factory=GPUHardware)
    cpu: CPUHardware      = Field(default_factory=CPUHardware)
    ram: RAMHardware      = Field(default_factory=RAMHardware)
    storage: StorageHardware = Field(default_factory=StorageHardware)
    cuda_pinned_version: str = "12.8"
    cuda_pin_packages: int   = 11   # apt-mark hold count; verify quarterly


# ─── Tiers ────────────────────────────────────────────────────────────────────

class TierConfig(BaseModel):
    tier_id: str
    enabled: bool
    model: str
    quant: str
    engine: str            = "llama-server"
    context_size: int      = 0
    expert_offload_pct: int = 0   # % routed experts on CPU (MoE only)
    parallelism_np: int    = 1
    active_lora: Optional[str] = None
    port: int
    cpu_only: bool         = False  # CUDA_VISIBLE_DEVICES= set
    burst_only: bool       = False  # if True, skipped by standard inference-up bringup

class TierRuntime(BaseModel):
    state: TierState              = TierState.UNKNOWN if False else TierState.STOPPED
    pid: Optional[int]            = None
    uptime_sec: Optional[int]     = None
    last_health_check: Optional[datetime] = None
    health_status: HealthStatus   = HealthStatus.UNKNOWN

class TierResources(BaseModel):
    vram_used_mb: int       = 0
    vram_kv_cache_mb: int   = 0
    ram_resident_mb: int    = 0
    cpu_percent_avg_60s: float = 0.0
    page_cache_mb: int      = 0

class TierPerformance(BaseModel):
    tok_per_sec_recent: Optional[float]   = None
    tok_per_sec_baseline: Optional[float] = None
    prompt_eval_tok_per_sec: Optional[float] = None
    completions_in_window: int = 0
    errors_in_window: int      = 0

class Tier(BaseModel):
    config: TierConfig
    runtime: TierRuntime       = Field(default_factory=TierRuntime)
    resources: TierResources   = Field(default_factory=TierResources)
    performance: TierPerformance = Field(default_factory=TierPerformance)


# ─── Workloads ────────────────────────────────────────────────────────────────

class ActiveWorkload(BaseModel):
    workload_id: str
    type: WorkloadType
    source: str
    started_at: datetime
    expected_completion: Optional[datetime] = None
    progress_pct: Optional[int]   = None
    progress_detail: Optional[str] = None
    tier_dependencies: List[str]  = Field(default_factory=list)
    blocks: List[str]             = Field(default_factory=list)
    blocked_by: List[str]         = Field(default_factory=list)
    priority: str                 = "normal"
    sla_target: Optional[str]     = None

class PendingWorkload(BaseModel):
    workload_id: str
    type: WorkloadType
    scheduled_for: Optional[datetime] = None
    expected_duration_sec: Optional[int] = None
    tier_requirements: List[Dict[str, str]] = Field(default_factory=list)
    priority: str           = "normal"
    sla_target: Optional[str] = None
    conflicts_detected: List[str] = Field(default_factory=list)

class CompletedWorkload(BaseModel):
    workload_id: str
    type: WorkloadType
    started_at: datetime
    completed_at: datetime
    duration_sec: int
    outcome: WorkloadOutcome
    sla_met: Optional[bool]      = None
    output_summary: Optional[str] = None
    anomalies: List[str]         = Field(default_factory=list)
    tier_used: Optional[str]     = None

class Workloads(BaseModel):
    active: List[ActiveWorkload]     = Field(default_factory=list)
    pending: List[PendingWorkload]   = Field(default_factory=list)
    completed: List[CompletedWorkload] = Field(default_factory=list)
    completed_retention_hours: int   = 168   # 7 days


# ─── Schedule ─────────────────────────────────────────────────────────────────

class ScheduledEvent(BaseModel):
    event_id: str
    scheduled_for: datetime
    source: str                  # "cron" | "hermes" | "operator"
    expected_duration_sec: Optional[int] = None
    tier_requirements: List[str] = Field(default_factory=list)
    vram_estimate_mb: int        = 0
    priority: str                = "normal"
    sla_target: Optional[str]    = None
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)

class Schedule(BaseModel):
    forecast_window_hours: int   = 24
    generated_at: datetime       = Field(default_factory=datetime.utcnow)
    upcoming: List[ScheduledEvent] = Field(default_factory=list)


# ─── Quotas ───────────────────────────────────────────────────────────────────

class CloudQuota(BaseModel):
    name: str
    provider: str
    period: str                          # "weekly" | "monthly"
    period_start: Optional[datetime]     = None
    period_end: Optional[datetime]       = None
    used_pct: Optional[float]            = None   # for Pro subscriptions
    used_usd: Optional[float]            = None   # for API quotas
    budget_usd: Optional[float]          = None
    burn_rate_per_hour: Optional[float]  = None   # pct/hr or usd/hr
    projected_wall_at: Optional[datetime] = None
    status: QuotaStatus                  = QuotaStatus.OK
    threshold_warning_pct: float         = 80.0
    threshold_critical_pct: float        = 95.0
    last_updated: Optional[datetime]     = None

class Quotas(BaseModel):
    # Populated by quota_listener. Keys match CloudQuota.name.
    quotas: Dict[str, CloudQuota] = Field(default_factory=dict)


# ─── Resources (live) ─────────────────────────────────────────────────────────

class VRAMByTier(BaseModel):
    t1: int = 0
    t2: int = 0
    t3: int = 0
    t4: int = 0
    t5: int = 0
    t6: int = 0
    driver_display: int = 0
    other: int = 0

class VRAMResources(BaseModel):
    total_mb: int          = 24576
    used_mb: int           = 0
    free_mb: int           = 24576
    used_by_tier: VRAMByTier = Field(default_factory=VRAMByTier)
    oom_risk: OOMRisk      = OOMRisk.LOW
    # Baseline operational target — flag when actual usage exceeds this.
    # 80% target = 19,661 MiB used / 4,915 MiB headroom for workload growth.
    baseline_target_pct: float = 80.0
    updated_at: Optional[datetime] = None

class PageCacheEntry(BaseModel):
    model: str
    cached_mb: int

class RAMResources(BaseModel):
    total_mb: int          = 98304
    used_mb: int           = 0
    free_mb: int           = 98304
    cached_mb: int         = 0
    swap_used_mb: int      = 0
    page_cache_models: List[PageCacheEntry] = Field(default_factory=list)
    updated_at: Optional[datetime] = None

class CPUResources(BaseModel):
    load_avg_1m: float  = 0.0
    load_avg_5m: float  = 0.0
    load_avg_15m: float = 0.0
    updated_at: Optional[datetime] = None

class Resources(BaseModel):
    vram: VRAMResources = Field(default_factory=VRAMResources)
    ram: RAMResources   = Field(default_factory=RAMResources)
    cpu: CPUResources   = Field(default_factory=CPUResources)


# ─── Operator ─────────────────────────────────────────────────────────────────

class OperatorPreferences(BaseModel):
    voice_during_active: bool   = True
    voice_during_idle: bool     = False
    voice_during_sleeping: bool = False
    sleeping_window_start: str  = "22:30"
    sleeping_window_end: str    = "06:00"

class Operator(BaseModel):
    state: OperatorState          = OperatorState.UNKNOWN
    state_confidence: float       = 0.0
    last_input_detected: Optional[datetime] = None
    active_session_id: Optional[str] = None
    preferences: OperatorPreferences = Field(default_factory=OperatorPreferences)
    updated_at: Optional[datetime] = None


# ─── Events ───────────────────────────────────────────────────────────────────

class Event(BaseModel):
    event_id: str
    timestamp: datetime          = Field(default_factory=datetime.utcnow)
    type: str                    # e.g. "tier_state_change", "oom_risk_elevated"
    severity: str                = "info"   # "info" | "warning" | "critical"
    tier: Optional[str]          = None
    workload_id: Optional[str]   = None
    detail: Optional[str]        = None
    data: Dict[str, Any]         = Field(default_factory=dict)

class Events(BaseModel):
    retention_hours: int   = 24
    log: List[Event]       = Field(default_factory=list)


# ─── Health ───────────────────────────────────────────────────────────────────

class ComponentHealth(BaseModel):
    name: str
    status: HealthStatus           = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    last_seen_healthy: Optional[datetime] = None
    response_ms: Optional[int]     = None
    detail: Optional[str]          = None
    port: Optional[int]            = None

class Health(BaseModel):
    components: List[ComponentHealth] = Field(default_factory=list)
    last_full_sweep: Optional[datetime] = None
    sweep_interval_sec: int        = 30


# ─── Top-level SystemModel ────────────────────────────────────────────────────

class SystemModel(BaseModel):
    """
    The canonical in-memory model of monarch's state.
    Written to ~/.local/state/jarvis/state.json every 30s by the daemon.
    Read by jarvis-q CLI and (eventually) the Jarvis decision engine.
    """
    schema_version: str     = "0.1.0"
    hardware: Hardware      = Field(default_factory=Hardware)
    tiers: Dict[str, Tier]  = Field(default_factory=dict)
    workloads: Workloads    = Field(default_factory=Workloads)
    schedule: Schedule      = Field(default_factory=Schedule)
    quotas: Quotas          = Field(default_factory=Quotas)
    resources: Resources    = Field(default_factory=Resources)
    operator: Operator      = Field(default_factory=Operator)
    events: Events          = Field(default_factory=Events)
    health: Health          = Field(default_factory=Health)
    last_updated: datetime  = Field(default_factory=datetime.utcnow)
    daemon_pid: Optional[int] = None


# ─── Monarch v18 baseline tier configuration ──────────────────────────────────
# Hardcoded from confirmed inference-up script (May 2026).
# Update these if inference-up changes.

MONARCH_TIERS: Dict[str, TierConfig] = {
    "t1": TierConfig(
        tier_id="t1", enabled=True,
        model="Qwen3.6-27B", quant="UD-Q4_K_XL",
        context_size=36864, parallelism_np=1, port=8080,
    ),
    "t2": TierConfig(
        tier_id="t2", enabled=True,
        model="Qwen3.6-27B", quant="UD-Q4_K_XL",
        context_size=16384, parallelism_np=1, port=8083,
        burst_only=True,
    ),
    "t3": TierConfig(
        tier_id="t3", enabled=True,
        model="Qwen3.6-27B", quant="UD-Q4_K_XL",
        context_size=8192, parallelism_np=1, port=8084, cpu_only=True,
    ),
    "t4": TierConfig(
        tier_id="t4", enabled=True,
        model="Phi-4-mini", quant="Q4_K_M",
        context_size=16384, parallelism_np=4, port=8002,
    ),
    "t5": TierConfig(
        tier_id="t5", enabled=True,
        model="Qwen3-1.7B", quant="Q5_K_M",
        context_size=8192, parallelism_np=1, port=8085, cpu_only=True,
    ),
    "t6": TierConfig(
        tier_id="t6", enabled=False,  # offline by default
        model="Qwen3.6-35B-A3B", quant="UD-Q4_K_XL",
        context_size=65536, parallelism_np=1, port=8086,
        expert_offload_pct=25,
    ),
}

MONARCH_HEALTH_COMPONENTS = [
    {"name": "llama-server-t1",    "port": 8080},
    {"name": "llama-server-t2",    "port": 8083},
    {"name": "llama-server-t3",    "port": 8084},
    {"name": "llama-server-t4",    "port": 8002},
    {"name": "llama-server-t5",    "port": 8085},
    {"name": "litellm",            "port": 4000},
    {"name": "validation-gate",    "port": 4100},
    {"name": "lora-dispatcher",    "port": 4200},
    {"name": "n8n",                "port": 5678},
    {"name": "postgres",           "port": 5432},
]

# Port → tier_id mapping (used by VRAM listener to attribute GPU memory)
PORT_TO_TIER: Dict[int, str] = {
    8080: "t1",
    8083: "t2",
    8084: "t3",
    8002: "t4",
    8085: "t5",
    8086: "t6",
}

# Documented VRAM baselines (MiB) from inference-up measured values
VRAM_BASELINE: Dict[str, int] = {
    "t1": 11500,
    "t2": 5500,
    "t3": 500,
    "t4": 4200,
    "t5": 0,
    "t6": 0,   # offline
    "driver_display": 512,
}
