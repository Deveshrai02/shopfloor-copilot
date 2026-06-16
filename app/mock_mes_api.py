# Mock MES (Manufacturing Execution System) API
# --------------------------------------------------
# This is a simulated data source for portfolio/demonstration purposes only.
# All OEE figures, downtime events, defect counts, and quality metrics are
# procedurally generated. No real manufacturing equipment or production data
# is connected. Values are designed to fall within credible manufacturing
# ranges but do not represent any actual plant or line.
# --------------------------------------------------

import random
import uuid
from datetime import datetime, timedelta
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Shopfloor Copilot — Mock MES API",
    description="Simulated Manufacturing Execution System data for portfolio demonstration.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-memory ticket store
# ---------------------------------------------------------------------------

_tickets: list[dict] = []

# ---------------------------------------------------------------------------
# Line configuration
# Valid line IDs and their production characteristics.
# Different lines have different OEE profiles to make the data feel realistic.
# ---------------------------------------------------------------------------

_LINE_PROFILES = {
    "TRIM-01": {"oee_centre": 78, "oee_spread": 6, "shift_volume": 420},
    "TRIM-02": {"oee_centre": 74, "oee_spread": 7, "shift_volume": 400},
    "FA-01":   {"oee_centre": 81, "oee_spread": 5, "shift_volume": 380},
    "FA-02":   {"oee_centre": 69, "oee_spread": 8, "shift_volume": 360},
    "EV-BAT":  {"oee_centre": 72, "oee_spread": 9, "shift_volume": 200},
}

_VALID_LINE_IDS = set(_LINE_PROFILES)

# Downtime reason codes drawn from a realistic automotive ISA-95 taxonomy
_DOWNTIME_REASONS = [
    ("MECH-FAULT",   "Mechanical failure — fixture or tooling"),
    ("ELEC-FAULT",   "Electrical fault — PLC or sensor"),
    ("MAT-SHORTAGE", "Material shortage — lineside stock depleted"),
    ("QUALITY-HOLD", "Quality hold — suspect units quarantined"),
    ("CHANGEOVER",   "Variant changeover"),
    ("OPERATOR-ABT", "Operator absence — station unmanned"),
    ("SCHED-MAINT",  "Scheduled preventive maintenance"),
    ("UNSCHD-MAINT", "Unscheduled corrective maintenance"),
    ("UTIL-FAULT",   "Utilities fault — compressed air / power dip"),
]

# Defect types by line area — weighted toward the most common failure modes
_DEFECT_TYPES = {
    "TRIM": [
        ("surface scratch",        0.30),
        ("clip not fully engaged", 0.25),
        ("panel misalignment",     0.20),
        ("incorrect variant fitted", 0.10),
        ("torn fabric/leather",    0.15),
    ],
    "FA": [
        ("weld porosity",          0.20),
        ("misalignment",           0.25),
        ("fastener under-torque",  0.20),
        ("missing fastener",       0.15),
        ("surface scratch",        0.10),
        ("incorrect assembly sequence", 0.10),
    ],
    "EV": [
        ("HV connector not seated",  0.25),
        ("interlock fault",          0.20),
        ("pack housing damage",      0.15),
        ("torque deviation",         0.25),
        ("traceability scan missed", 0.15),
    ],
}


def _resolve_line(line_id: str) -> dict:
    """Return the line profile or raise 404."""
    if line_id not in _LINE_PROFILES:
        raise HTTPException(
            status_code=404,
            detail=f"Line '{line_id}' not found. Valid lines: {sorted(_VALID_LINE_IDS)}",
        )
    return _LINE_PROFILES[line_id]


def _defect_pool(line_id: str) -> list[tuple[str, float]]:
    """Select the appropriate defect type pool for a line."""
    if line_id.startswith("TRIM"):
        return _DEFECT_TYPES["TRIM"]
    if line_id.startswith("EV"):
        return _DEFECT_TYPES["EV"]
    return _DEFECT_TYPES["FA"]


def _weighted_choice(pool: list[tuple[str, float]]) -> str:
    items, weights = zip(*pool)
    return random.choices(items, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------

class OEEResponse(BaseModel):
    line_id: str
    timestamp: datetime
    oee_pct: float = Field(description="Overall Equipment Effectiveness as a percentage")
    availability_pct: float
    performance_pct: float
    quality_pct: float
    shift_target_units: int
    units_produced: int


class DefectEvent(BaseModel):
    defect_type: str
    count: int


class QualityResponse(BaseModel):
    line_id: str
    timestamp: datetime
    units_inspected: int
    total_defects: int
    quality_pass_rate_pct: float
    defect_breakdown: list[DefectEvent]


class DowntimeEvent(BaseModel):
    event_id: str
    started_at: datetime
    duration_minutes: float
    reason_code: str
    reason_description: str
    resolved: bool


class DowntimeResponse(BaseModel):
    line_id: str
    window_hours: int
    total_downtime_minutes: float
    event_count: int
    events: list[DowntimeEvent]


class TicketRequest(BaseModel):
    line_id: str
    issue_description: str = Field(min_length=10, max_length=1000)
    severity: Literal["low", "medium", "high"]


class TicketResponse(BaseModel):
    ticket_id: str
    line_id: str
    issue_description: str
    severity: str
    created_at: datetime
    status: str


class EndpointInfo(BaseModel):
    path: str
    method: str
    description: str


class RootResponse(BaseModel):
    service: str
    note: str
    endpoints: list[EndpointInfo]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", response_model=RootResponse)
def root():
    """List all available API endpoints."""
    return RootResponse(
        service="Shopfloor Copilot Mock MES API",
        note=(
            "Simulated data only — not connected to real manufacturing equipment. "
            "For portfolio demonstration purposes."
        ),
        endpoints=[
            EndpointInfo(path="/oee/{line_id}",         method="GET",  description="Current OEE and sub-metrics for a line"),
            EndpointInfo(path="/quality/{line_id}",      method="GET",  description="Recent defect count, types, and pass rate"),
            EndpointInfo(path="/downtime/{line_id}",     method="GET",  description="Downtime events in the requested window (hours param)"),
            EndpointInfo(path="/tickets",                method="POST", description="Raise a maintenance or quality ticket"),
            EndpointInfo(path="/tickets",                method="GET",  description="List all tickets raised this session"),
            EndpointInfo(path="/lines",                  method="GET",  description="List all valid line IDs"),
        ],
    )


@app.get("/lines")
def list_lines():
    """Return all configured line IDs."""
    return {"lines": sorted(_VALID_LINE_IDS)}


@app.get("/oee/{line_id}", response_model=OEEResponse)
def get_oee(line_id: str):
    """
    Return current OEE and its Availability × Performance × Quality breakdown.

    Values are generated around each line's configured centre point with a
    realistic spread. OEE = A × P × Q (computed, not independently randomised)
    so the relationship between sub-metrics is internally consistent.
    """
    profile = _resolve_line(line_id)

    # Generate sub-metrics first, then derive OEE — mirrors how real MES
    # systems calculate it rather than setting OEE directly.
    availability = round(random.gauss(mu=88, sigma=4), 1)
    performance  = round(random.gauss(mu=92, sigma=3), 1)

    # Back-calculate the quality rate needed to land near the line's OEE target
    target_oee = random.gauss(mu=profile["oee_centre"], sigma=profile["oee_spread"])
    implied_quality = (target_oee / 100) / ((availability / 100) * (performance / 100)) * 100

    # Clamp all values to plausible bounds
    availability   = max(60.0, min(99.0, availability))
    performance    = max(60.0, min(99.0, performance))
    quality        = max(60.0, min(99.9, round(implied_quality, 1)))
    oee            = round((availability / 100) * (performance / 100) * (quality / 100) * 100, 1)
    oee            = max(40.0, min(99.0, oee))

    units_produced = int(profile["shift_volume"] * (oee / 100) * random.uniform(0.95, 1.05))

    return OEEResponse(
        line_id=line_id,
        timestamp=datetime.utcnow(),
        oee_pct=oee,
        availability_pct=availability,
        performance_pct=performance,
        quality_pct=quality,
        shift_target_units=profile["shift_volume"],
        units_produced=units_produced,
    )


@app.get("/quality/{line_id}", response_model=QualityResponse)
def get_quality(line_id: str):
    """
    Return recent defect summary for a line.

    Defect types are weighted toward the most common failure modes for that
    area (trim, final assembly, or EV battery).
    """
    profile = _resolve_line(line_id)
    pool    = _defect_pool(line_id)

    units_inspected = int(profile["shift_volume"] * random.uniform(0.85, 1.0))

    # Defect rate: typically 1–4% of units inspected; EV lines run tighter
    base_defect_rate = 0.015 if line_id.startswith("EV") else 0.025
    defect_rate      = random.gauss(mu=base_defect_rate, sigma=0.005)
    defect_rate      = max(0.005, min(0.08, defect_rate))
    total_defects    = max(0, int(units_inspected * defect_rate))

    # Distribute defects across 2–4 defect types
    num_types = min(len(pool), random.randint(2, 4))
    chosen    = random.sample(pool, k=num_types)
    # Re-normalise weights for the chosen subset
    total_w   = sum(w for _, w in chosen)
    breakdown: list[DefectEvent] = []
    remaining = total_defects
    for i, (defect_type, weight) in enumerate(chosen):
        if i == len(chosen) - 1:
            count = remaining
        else:
            count     = round(total_defects * (weight / total_w))
            remaining = max(0, remaining - count)
        if count > 0:
            breakdown.append(DefectEvent(defect_type=defect_type, count=count))

    pass_rate = round((1 - defect_rate) * 100, 2)

    return QualityResponse(
        line_id=line_id,
        timestamp=datetime.utcnow(),
        units_inspected=units_inspected,
        total_defects=total_defects,
        quality_pass_rate_pct=pass_rate,
        defect_breakdown=breakdown,
    )


@app.get("/downtime/{line_id}", response_model=DowntimeResponse)
def get_downtime(
    line_id: str,
    hours: int = Query(default=24, ge=1, le=168, description="Lookback window in hours (1–168)"),
):
    """
    Return simulated downtime events within the requested lookback window.

    Event count and durations are calibrated so that a typical 8-hour shift
    sees 2–5 events totalling 20–60 minutes — consistent with an 80–90%
    availability figure.
    """
    _resolve_line(line_id)

    now = datetime.utcnow()
    window_start = now - timedelta(hours=hours)

    # Scale expected events with the window size; ~3 events per 8-hour shift
    expected_events = max(1, round((hours / 8) * random.gauss(mu=3, sigma=1)))
    events: list[DowntimeEvent] = []

    # Spread events randomly across the window
    event_times = sorted(
        window_start + timedelta(seconds=random.randint(0, hours * 3600))
        for _ in range(expected_events)
    )

    for started_at in event_times:
        code, desc = random.choice(_DOWNTIME_REASONS)

        # Duration depends on fault category
        if code in ("MECH-FAULT", "ELEC-FAULT", "UNSCHD-MAINT"):
            duration = round(random.gauss(mu=22, sigma=8), 1)   # longer unplanned stops
        elif code in ("SCHED-MAINT", "CHANGEOVER"):
            duration = round(random.gauss(mu=12, sigma=3), 1)   # bounded planned stops
        else:
            duration = round(random.gauss(mu=8, sigma=4), 1)    # short material / quality holds

        duration = max(1.0, min(120.0, duration))
        resolved = (started_at + timedelta(minutes=duration)) < now

        events.append(DowntimeEvent(
            event_id=f"DT-{uuid.uuid4().hex[:8].upper()}",
            started_at=started_at,
            duration_minutes=duration,
            reason_code=code,
            reason_description=desc,
            resolved=resolved,
        ))

    total_downtime = round(sum(e.duration_minutes for e in events), 1)

    return DowntimeResponse(
        line_id=line_id,
        window_hours=hours,
        total_downtime_minutes=total_downtime,
        event_count=len(events),
        events=events,
    )


@app.post("/tickets", response_model=TicketResponse, status_code=201)
def create_ticket(body: TicketRequest):
    """
    Raise a maintenance or quality ticket for a line.

    The ticket is stored in memory for the duration of the server session.
    """
    if body.line_id not in _LINE_PROFILES:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown line_id '{body.line_id}'. Valid lines: {sorted(_VALID_LINE_IDS)}",
        )

    ticket = TicketResponse(
        ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
        line_id=body.line_id,
        issue_description=body.issue_description,
        severity=body.severity,
        created_at=datetime.utcnow(),
        status="open",
    )
    _tickets.append(ticket.model_dump())
    return ticket


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets():
    """Return all tickets raised in the current session."""
    return _tickets
