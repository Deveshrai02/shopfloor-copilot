# OP-FA-026: End-of-Shift Handover and OEE Reconciliation

| Field | Detail |
|---|---|
| **Document ID** | OP-FA-026 |
| **Revision** | [INSERT REV] |
| **Effective Date** | [INSERT DATE] |
| **Owner** | Production Supervisor |
| **Approved By** | [INSERT NAME/TITLE] |
| **ISA-95 Level** | Level 3 — Manufacturing Operations Management |

---

## 1. Scope

This procedure governs the structured handover between outgoing and incoming shift teams at every scheduled shift change. It includes the reconciliation of Overall Equipment Effectiveness (OEE) metrics and downtime reason codes within the Manufacturing Execution System (MES) to ensure data integrity and operational continuity.

**Applicable Lines:**
- Trim Assembly
- Final Assembly
- EV Battery Lines

This procedure does not cover unplanned or emergency shift changes; those are handled under [INSERT EMERGENCY SHIFT CHANGE PROCEDURE ID].

---

## 2. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **Outgoing Team Leader** | Reviews shift OEE data; corrects downtime coding errors; prepares and presents the handover; physically walks the line with the incoming counterpart |
| **Incoming Team Leader** | Attends the line walk; confirms comprehension of all open items; signs the handover sheet in MES |
| **Production Supervisor** | Reviews final shift OEE figure; adds loss-category commentary if OEE is below site target; retains sign-off authority; owns escalation actions |

---

## 3. Trigger Conditions

| Trigger | Frequency |
|---|---|
| Scheduled shift change | Every shift, without exception |

This procedure is mandatory at every shift boundary regardless of production volume, line status, or staffing level.

---

## 4. Step-by-Step Procedure

**Step 1 — Review Shift OEE Summary (T-15 min)**
The Outgoing Team Leader opens the MES OEE Dashboard no later than 15 minutes before scheduled shift end and reviews the shift OEE summary for all applicable lines. Confirm that the figures displayed match expectations based on known events during the shift.

**Step 2 — Reconcile Downtime Reason Codes**
Cross-check all downtime events logged during the shift against their assigned reason codes. Correct any miscoded entries before the shift is closed in MES. Downtime entries must be attributed to an approved reason code from the site master list; entries coded as "Unknown" or "Other" require resolution before shift close.

**Step 3 — Document Open Items on Handover Sheet**
Record all of the following on Handover Sheet FA-HO-03, either digitally in MES or as a printed supplement:
- Active quality holds and the affected part numbers or stations
- In-progress or incomplete maintenance work orders, including WO numbers
- Unresolved material shortages and their downstream impact

**Step 4 — Conduct Physical Line Walk**
The Outgoing Team Leader walks the full line with the Incoming Team Leader. The walk must include:
- Any workstation currently running below standard takt time, with the reason identified
- Any temporary workarounds, fixture substitutions, or manual interventions in place
- Visual confirmation of material levels at lineside supermarkets or point-of-use racks

**Step 5 — Incoming Team Leader Sign-Off**
Upon completion of the line walk, the Incoming Team Leader confirms understanding of all open items documented in Step 3 and signs the handover sheet within MES. This signature constitutes formal acceptance of shift ownership and open-item responsibility.

**Step 6 — Production Supervisor OEE Review**
The Production Supervisor reviews the closed shift's OEE figure. If OEE is below the site target of [INSERT THRESHOLD]%:
- The Supervisor adds a brief written note to the shift report identifying the **primary loss category**: Availability, Performance, or Quality.
- The note must include the top contributing event or reason code for that category.

**Step 7 — Open Item Ageing Check**
Any open item carried forward from the handover sheet that remains unresolved after **2 consecutive shifts** is formally escalated to the Production Supervisor for corrective action assignment. The Production Supervisor is responsible for designating an owner and target resolution date.

---

## 5. Escalation Criteria

| Condition | Escalation Action |
|---|---|
| OEE falls below site target ([INSERT THRESHOLD]%) for **3 consecutive shifts on the same line** | Production Supervisor initiates a formal review meeting with the Plant Manager and Industrial Engineering within [INSERT TIMEFRAME] of the third consecutive miss |
| Open item unresolved after 2 consecutive shifts | Escalated to Production Supervisor per Step 7 |
| Downtime reason code cannot be resolved by Outgoing Team Leader | Production Supervisor is notified before shift close to assign resolution ownership |

---

## 6. Related Documents

| Document | ID |
|---|---|
| MES OEE Dashboard Guide | [INSERT DOC ID] |
| Shift Handover Sheet | FA-HO-03 |
| Downtime Reason Code Master List | [INSERT DOC ID] |
| Emergency Shift Change Procedure | [INSERT DOC ID] |

---

*End of OP-FA-026*
