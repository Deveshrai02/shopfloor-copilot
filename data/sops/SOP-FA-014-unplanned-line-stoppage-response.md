# SOP-FA-014: Unplanned Line Stoppage Response

| Field | Detail |
|---|---|
| **Document ID** | SOP-FA-014 |
| **Revision** | 3 |
| **Effective Date** | 2026-01-14 |
| **Area** | Final Assembly |
| **Owner** | Production Supervisor |
| **Approved By** | [INSERT NAME/TITLE] |
| **ISA-95 Level** | Level 3 — Manufacturing Operations Management |

---

## 1. Scope

This procedure defines the required response sequence when a Final Assembly line stops unexpectedly during a production shift. It covers operator containment actions, Team Leader first-response, fault categorisation, Maintenance Technician diagnosis, and restart confirmation.

**This procedure does not cover:** scheduled changeovers, planned maintenance windows, break-related line pauses, or operator-initiated quality holds (see SOP-QA-007 for the latter).

---

## 2. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **Line Operator** | Initiates stop confirmation via the Andon system; remains at station; provides first-hand account of conditions at time of stoppage |
| **Team Leader** | First responder; attends within 2 minutes; categorises the fault; coordinates material, maintenance, or quality response; restarts the line and validates first units off restart |
| **Maintenance Technician** | Diagnoses and clears mechanical and electrical faults; applies LOTO before working on any energised or moving equipment; signs off fault clearance in MES with correct downtime reason code |
| **Production Supervisor** | Owns all escalations beyond 15-minute downtime threshold; authorises actions when downtime approaches the 45-minute formal incident threshold |

---

## 3. Trigger Conditions

| Trigger | Notes |
|---|---|
| Line stops without an operator-initiated stop command | Includes safety interlock trips, e-stop activations, and control system faults |
| Andon triggered by any station | Regardless of cause |
| Conveyor halt exceeding 2 minutes with no scheduled cause | If no fault is identifiable within 2 minutes, treat as unplanned stoppage |

---

## 4. Step-by-Step Procedure

**Step 1 — Operator Andon Confirmation**
Upon any unplanned line stop, the Operator presses the Andon or line-stop confirm button at their station to formally register the stoppage event in MES. The Operator remains at their station and does not attempt to diagnose or clear the fault independently.

**Step 2 — Team Leader First Response**
The Team Leader attends the affected station within **2 minutes** of the Andon activation. The Team Leader assesses the situation and categorises the fault into one of the following:
- **Mechanical / Electrical** — equipment failure, sensor fault, drive fault
- **Material shortage** — lineside stock depleted, missing kit
- **Quality hold** — defect requiring containment before the line can continue

**Step 3 — Mechanical / Electrical Fault Response**
If the fault category is mechanical or electrical:
1. Team Leader logs the fault in MES with an initial description and the affected workstation.
2. Team Leader pages the on-shift Maintenance Technician via [INSERT NOTIFICATION METHOD].
3. No other personnel attempt repair or adjustment of the equipment.

**Step 4 — Material Shortage Response**
If the fault category is a material shortage:
1. Team Leader checks the lineside kanban card or MES material status for the affected part.
2. Team Leader contacts the Material Handler and communicates the specific part number and quantity required.
3. Team Leader monitors kanban replenishment and confirms material receipt at lineside before authorising line restart.

**Step 5 — Quality-Related Stoppage Response**
If the fault category is a quality hold or suspected non-conformance, follow **SOP-QA-007 (Quality Hold and Containment Procedure)** in full before any line restart.

**Step 6 — Maintenance Diagnosis and LOTO**
The Maintenance Technician diagnoses the fault. Before performing any work on energised, pressurised, or moving equipment, the Maintenance Technician applies Lockout-Tagout (LOTO) per **SOP-MT-022**. No other personnel may work on or around the isolated equipment while LOTO is applied.

**Step 7 — Fault Clearance Sign-Off in MES**
Once the fault is resolved, the Maintenance Technician removes LOTO (following SOP-MT-022 restoration steps) and records the following in MES:
- Fault description and root cause
- Corrective action taken
- Downtime reason code (selected from the MES Downtime Reason Code List)
- Fault clearance timestamp and Maintenance Technician ID

**Step 8 — Restart and First-Unit Verification**
The Team Leader authorises and initiates the line restart. The first **3 units** produced after restart are subject to a visual quality check by the Team Leader before normal takt resumes. Any anomaly on the first-off units triggers re-entry to SOP-QA-007.

---

## 5. Escalation Criteria

| Condition | Escalation Action |
|---|---|
| Downtime exceeds **15 minutes** | Automatic escalation to Production Supervisor; Team Leader notifies verbally and via MES alert |
| Downtime exceeds **45 minutes** | Escalation to Plant Manager; formal incident ticket opened in [INSERT SYSTEM]; Production Supervisor owns the ticket |
| Quality-related stoppage at any duration | Follow SOP-QA-007; Quality Engineer sign-off required before restart if safety-critical fasteners are implicated |

---

## 6. Related Documents

| Document | ID |
|---|---|
| Quality Hold and Containment Procedure | SOP-QA-007 |
| Lockout-Tagout (LOTO) Procedure | SOP-MT-022 |
| MES Downtime Reason Code List | [INSERT DOC ID / MES LOCATION] |

---

*End of SOP-FA-014 Rev 3*
