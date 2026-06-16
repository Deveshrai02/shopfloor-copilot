# SOP-QA-007: Quality Hold and Containment Procedure

| Field | Detail |
|---|---|
| **Document ID** | SOP-QA-007 |
| **Revision** | 4 |
| **Effective Date** | 2025-09-18 |
| **Area** | Trim / Final Assembly |
| **Owner** | Quality Engineer |
| **Approved By** | [INSERT NAME/TITLE] |
| **ISA-95 Level** | Level 3 — Manufacturing Operations Management |

---

## 1. Scope

This procedure covers the identification, tagging, quarantine, and structured containment of suspect non-conforming product on trim and final assembly lines. It applies whenever a detected defect has characteristics that suggest it may affect units beyond the single unit currently at station — for example, a supplier batch issue, fixture drift, tooling wear, or a repeated fastener failure pattern.

This procedure is invoked by reference from SOP-FA-014 (Unplanned Line Stoppage Response) and SOP-FA-019 (Torque Verification and Fastener Audit), among others.

---

## 2. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **Operator** | Stops the line upon detecting a suspect defect; applies a red Quality Hold tag to the affected unit; moves the unit to the quarantine area if the line is to continue |
| **Team Leader** | Notifies the Quality Technician immediately upon hold initiation; logs the hold event in MES with defect description and suspected cause |
| **Quality Technician** | Determines containment scope using MES traceability; coordinates physical quarantine of all suspect units; records inspection results per unit in MES |
| **Quality Engineer** | Owns root cause analysis and equipment isolation decisions; approves final disposition of each quarantined unit; opens Non-Conformance Reports (NCRs) where required |

---

## 3. Trigger Conditions

| Trigger | Notes |
|---|---|
| Defect detected that may extend beyond the unit currently at station | Examples: repeated occurrence of same defect type, supplier batch suspect, fixture drift detected, safety-critical non-conformance at any scale |

---

## 4. Step-by-Step Procedure

**Step 1 — Operator Line Stop and Unit Tagging**
Upon detecting a suspect defect, the Operator stops the line and applies a **red Quality Hold tag** to the affected unit. If the production line must continue operating, the Operator moves the tagged unit to the designated quarantine area before restarting. The Operator does not attempt to disposition, rework, or re-inspect the unit independently.

**Step 2 — Team Leader Notification and MES Hold Log**
The Team Leader notifies the Quality Technician immediately — verbally and via [INSERT NOTIFICATION METHOD]. The Team Leader logs the hold event in MES, capturing:
- Defect description
- Suspected cause (if known)
- Affected unit serial number(s)
- Time of detection and workstation

**Step 3 — Containment Scope Determination**
The Quality Technician uses the MES Traceability Module to pull the list of all units built since the last confirmed known-good check point, filtering by time window, batch number, or tool/fixture ID as appropriate to the defect type. This list defines the **suspect scope** — all units that may have been affected.

**Step 4 — Physical Quarantine of Suspect Units**
All units within the suspect scope are pulled from the production flow and moved to the designated quarantine area. Each unit receives a red Quality Hold tag and its MES status is updated to **Quality Hold**. Units may not be shipped, transferred to another line, or released to the customer while in hold status.

**Step 5 — Equipment Isolation (if Applicable)**
If root cause investigation by the Quality Engineer identifies the defect as fixture- or equipment-related, the implicated fixture or equipment is isolated from production (tagged out and removed from service) until the root cause is corrected and verified. The Quality Engineer is responsible for this isolation decision.

**Step 6 — Unit-Level Disposition**
The Quality Engineer reviews each quarantined unit and assigns one of the following dispositions, recorded in MES against the unit serial number:
- **Release** — unit inspected and confirmed conforming
- **Rework** — unit requires correction; rework work order raised and tracked
- **Scrap** — unit cannot be brought to conforming state; scrapped per site scrap procedure

**Step 7 — Non-Conformance Report (NCR)**
A Non-Conformance Report (NCR) is opened on form QA-NCR-01 in any of the following cases:
- The containment scope exceeds **5 units**
- The root cause is supplier-related (batch or incoming material)
- The defect is classified as safety-related (any scope)

The Quality Engineer is the owner of the NCR and is responsible for completing root cause analysis and corrective action sections within [INSERT TIMEFRAME].

---

## 5. Escalation Criteria

| Condition | Escalation Action |
|---|---|
| Containment scope exceeds **20 units** | Plant Quality Manager notified within **1 hour** of scope determination |
| Any safety-related defect (any scope) | Plant Quality Manager notified within **1 hour**; customer quality notification per [INSERT CUSTOMER NOTIFICATION PROCEDURE] if applicable |
| NCR root cause not closed within [INSERT THRESHOLD] days | Escalated to Plant Quality Manager for corrective action review |

---

## 6. Related Documents

| Document | ID |
|---|---|
| Non-Conformance Report Form | QA-NCR-01 |
| MES Traceability Module Guide | [INSERT DOC ID / MES LOCATION] |
| Unplanned Line Stoppage Response | SOP-FA-014 |
| Torque Verification and Fastener Audit | SOP-FA-019 |

---

*End of SOP-QA-007 Rev 4*
