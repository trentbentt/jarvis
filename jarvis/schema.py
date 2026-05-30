"""
Jarvis System Model — Schema v0.1
Host: monarch (RTX 3090 24GB, Ryzen 9 9900X, 96GB DDR5, Ubuntu 24.04)

Nine top-level domains:
  hardware      — static, calibrated once
  tiers         — live state per tier T1–T5 (T6 offline by default)
  workloads     — active / pending / completed rolling window
  schedule      — 24h forward forecast
  quotas        — cloud API budgets and burn rates
  resources     — live VRAM / RAM / CPU
  events        — append-only rolling log (~24h)
  health        — per-component health checks
  operator      — operator preferences and presence state

Doctrine: schema fields are what Jarvis must know to function as a manager.
Adding a field is a deliberate decision. Nothing here is inferred from
cardinal decisions — this layer observes reality regardless of doctrine.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum, IntEnum
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

class MemoryLayerHealth(str, Enum):
    OK             = "ok"
    DEGRADED       = "degraded"
    UNRESPONSIVE   = "unresponsive"
    NOT_CONFIGURED = "not_configured"   # layer not yet built (e.g. L1 Redis → P1.5-6)
    UNKNOWN        = "unknown"


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
    # Process-observation fields — owned by process.py (master_summary §12.4).
    rss_mb: int                   = 0
    cpu_pct: float                = 0.0
    restart_count_24h: int        = 0
    last_restart_ts: Optional[datetime] = None
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

# ─── Cron reconciliation (cron.py, master_summary §12.4) ──────────────────────
# All datetimes are UTC; cron is parsed in system-local tz then converted.

class CronJob(BaseModel):
    name: str                          # target-script basename
    schedule: str                      # cron expression (5 fields or @macro)
    command: str                       # full command, redirect stripped
    log_path: Optional[str]   = None   # derived from the `>>` redirect
    source: str               = "crontab"   # "crontab" | "/etc/cron.d/<file>"
    next_run: Optional[datetime] = None

class MissedRun(BaseModel):
    name: str
    scheduled_for: datetime
    log_path: Optional[str]        = None
    last_log_mtime: Optional[datetime] = None

class ScheduledRun(BaseModel):
    name: str
    next_run: datetime

class Collision(BaseModel):
    job_a: str
    job_b: str
    run_a: datetime
    run_b: datetime
    gap_sec: int


class Schedule(BaseModel):
    forecast_window_hours: int   = 24
    generated_at: datetime       = Field(default_factory=datetime.utcnow)
    upcoming: List[ScheduledEvent] = Field(default_factory=list)
    # cron.py (master_summary §12.4)
    cron_entries: List[CronJob]      = Field(default_factory=list)
    missed_runs_24h: List[MissedRun] = Field(default_factory=list)
    upcoming_60min: List[ScheduledRun] = Field(default_factory=list)
    collisions: List[Collision]      = Field(default_factory=list)
    stale_entries: List[str]         = Field(default_factory=list)
    cron_updated_at: Optional[datetime] = None


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
    # Spend/token tracking fields — owned by quota.py (master_summary §12.4).
    tokens_in_today: int                 = 0
    tokens_out_today: int                = 0
    spend_today_usd: float               = 0.0
    last_call_ts: Optional[datetime]     = None
    walls_in_window: int                 = 0   # 429 count; not in spend_logs — see quota.py

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
    overnight_window_start: str = "23:00"
    overnight_window_end: str   = "07:00"

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


# ─── Decisions (engine.py + authority.py, master_summary §12.6 / §9.5) ────────
# The decision engine's read-only projection onto the system model. The engine
# is a pure CONSUMER of StateStore snapshots; the only domain it writes is this
# one (pending asks + a read-only ledger projection for jarvis-q). The durable
# N=12 trust counters live in authority.json (NOT state.json — §0.1 rule 5:
# state.json is non-doctrine, pruned/rehydrated on cold-start). ActionRecord is
# the ledger row shape; it is mirrored here purely so the CLI can render it.

class ActionTier(IntEnum):
    TIER_1 = 1   # autonomous-immediate (silent)
    TIER_2 = 2   # autonomous-with-log
    TIER_3 = 3   # surface-and-ask

class ActionLifecycleState(str, Enum):
    COLD_START = "cold_start"
    ELIGIBLE   = "eligible"     # hit N=12; promotion ask pending operator approval
    PROMOTED   = "promoted"
    DEMOTED    = "demoted"

class ProposedAction(BaseModel):
    action_id: str                       # behavior id, e.g. "auto_restart_cpu_dataplane_tier"
    trigger: str                         # "process.py:tier_crashed:t5"
    params: Dict[str, Any] = Field(default_factory=dict)   # {"tier": "t5"}
    dedup_key: str                       # stable per incident; cooldown key
    rationale: str
    proposed_at: datetime

class ActionRecord(BaseModel):           # ledger row (canonical store = authority.json)
    action_id: str
    description: str = ""
    current_tier: ActionTier = ActionTier.TIER_3
    target_tier: ActionTier  = ActionTier.TIER_2     # promotion cap (seed = TIER_2)
    clean_run_count: int = 0             # consecutive clean runs at current tier
    total_runs: int = 0
    last_fired: Optional[datetime] = None
    last_outcome: Optional[str] = None   # "ok" | "failed" | "regretted"
    state: ActionLifecycleState = ActionLifecycleState.COLD_START
    demotion_reason: Optional[str] = None

class PendingAsk(BaseModel):
    action_id: str
    params: Dict[str, Any] = Field(default_factory=dict)
    rationale: str
    proposed_at: datetime
    tier: ActionTier = ActionTier.TIER_3
    kind: str = "run"                    # "run" = per-run approval | "promotion" = N=12 ladder
    blocking: bool = True                # non-blocking = timer + default-proceed (§9.5.1, stub)
    expires_at: Optional[datetime] = None

class Decisions(BaseModel):
    pending_asks: List[PendingAsk] = Field(default_factory=list)
    ledger: List[ActionRecord]     = Field(default_factory=list)   # read-only projection
    last_tick: Optional[datetime]  = None


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


# ─── Memory layers (memory.py, MEMORY_ARCHITECTURE §10.2) ─────────────────────
# The 7-layer monarch memory architecture Jarvis observes as Arbiter. memory.py
# actively probes the layers it owns (L3 pgvector SQL, L4 Hermes HTTP + state.db
# mtime, L6 vault git) and mirrors the rest from existing signals (L2/L5/L7 from
# health components; L1 is a not_configured placeholder until P1.5-6). Per-layer
# health/activity/anomaly signals and cadences are defined in §10.1.

class MemoryLayer(BaseModel):
    layer: str                              # "L1".."L7"
    name: str                               # "Redis", "pgvector", "Hermes", …
    role: str                               # "Truth" | "Index" | "Memory"
    mode: str                               # "probe" | "state" | "placeholder"
    health: MemoryLayerHealth = MemoryLayerHealth.UNKNOWN
    health_signal: Optional[str]   = None   # what the probe checked / its result
    activity_signal: Optional[str] = None   # e.g. "85 chunks", "state.db 21h ago"
    anomaly: Optional[str]         = None   # set when an anomaly is detected
    source_component: Optional[str] = None  # health-component name for mode=state
    last_check: Optional[datetime] = None
    last_seen_healthy: Optional[datetime] = None
    response_ms: Optional[int]     = None


def _default_memory_layers() -> Dict[str, "MemoryLayer"]:
    """Cold-start the 7 layer slots from MONARCH_MEMORY_LAYERS. Also fires when
    load_from_disk() reads a state.json predating the memory domain."""
    return {
        m["layer"]: MemoryLayer(
            layer=m["layer"], name=m["name"], role=m["role"], mode=m["mode"],
            source_component=m.get("component"),
            health=(MemoryLayerHealth.NOT_CONFIGURED if m["mode"] == "placeholder"
                    else MemoryLayerHealth.UNKNOWN),
        )
        for m in MONARCH_MEMORY_LAYERS
    }


class MemoryLayers(BaseModel):
    layers: Dict[str, MemoryLayer]   = Field(default_factory=_default_memory_layers)
    skill_drafts_total: int          = 0
    skill_drafts_stale: List[str]    = Field(default_factory=list)
    last_sweep: Optional[datetime]   = None


# ─── Top-level SystemModel ────────────────────────────────────────────────────

class SystemModel(BaseModel):
    """
    The canonical in-memory model of monarch's state.
    Written to ~/.local/state/jarvis/state.json every 10s by the daemon.
    Read by jarvis-q CLI and (eventually) the Jarvis decision engine.
    """
    # Label field only — read by humans and logs, never acted on by migration
    # logic. Cold-cycle discipline is the migration strategy for this stack. (D4)
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
    memory: MemoryLayers    = Field(default_factory=MemoryLayers)
    decisions: Decisions    = Field(default_factory=Decisions)
    last_updated: datetime  = Field(default_factory=datetime.utcnow)
    daemon_pid: Optional[int] = None


# ─── Monarch v18 baseline tier configuration ──────────────────────────────────
# Hardcoded from confirmed inference-up script (May 2026).
# Update these if inference-up changes.

MONARCH_TIERS: Dict[str, TierConfig] = {
    "t1": TierConfig(
        tier_id="t1", enabled=True,
        model="Qwen3.6-27B", quant="UD-Q4_K_XL",
        context_size=24576, parallelism_np=1, port=8080,
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
    {"name": "monarch-postgres",   "port": 5433},
    {"name": "embed-nomic",        "port": 8087},
    {"name": "codebase-memory",    "port": None},   # stdio MCP; CLI-probed
    {"name": "hermes",             "port": 8642},   # /v1/models, bearer auth
    {"name": "rerank-bge",         "port": 8088},   # llama-server reranker (/health), L7 EverCore rerank
    {"name": "evercore",           "port": 1995},   # L7 EverMemOS; composite probe (ES/Milvus/Mongo/Redis:6380/API:1995)
]

# ─── Memory architecture layers (MEMORY_ARCHITECTURE §10) ─────────────────────
# Source-of-truth for the memory domain memory.py observes. mode:
#   probe       — memory.py actively probes; it owns the signal (§10.2)
#   state       — mirrored from an existing health component; no re-probe
#                 (same non-duplication discipline as tier_health ↔ process)
#   placeholder — not yet built; initializes not_configured (L1 → P1.5-6)
# Boundaries locked 2026-05-29: active probes are {L3, L4, L6}.
MONARCH_MEMORY_LAYERS = [
    {"layer": "L1", "name": "Redis",           "role": "Truth",  "mode": "placeholder"},
    {"layer": "L2", "name": "Postgres",        "role": "Truth",  "mode": "state", "component": "postgres"},
    {"layer": "L3", "name": "pgvector",        "role": "Index",  "mode": "probe"},
    {"layer": "L4", "name": "Hermes",          "role": "Memory", "mode": "probe"},
    {"layer": "L5", "name": "Codebase-Memory", "role": "Index",  "mode": "state", "component": "codebase-memory"},
    {"layer": "L6", "name": "Obsidian vault",  "role": "Truth",  "mode": "probe"},
    {"layer": "L7", "name": "EverCore",        "role": "Memory", "mode": "state", "component": "evercore"},
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
