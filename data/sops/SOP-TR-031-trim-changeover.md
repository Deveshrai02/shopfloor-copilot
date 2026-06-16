# SOP-TR-031: Door Trim and Interior Panel Fitment Changeover

| Field | Detail |
|---|---|
| **Document ID** | SOP-TR-031 |
| **Revision** | 5 |
| **Effective Date** | 2025-11-02 |
| **Area** | Trim |
| **Owner** | Trim Team Leader |
| **Approved By** | [INSERT NAME/TITLE] |
| **ISA-95 Level** | Level 3 — Manufacturing Operations Management |

---

## 1. Scope

This procedure covers the full changeover sequence when switching interior trim variant on the final trim line — for example, transitioning between cloth and leather door card builds. It applies to both scheduled variant changeovers (per the sequencing schedule) and unplanned variant mix changes communicated by Production Control.

This procedure does not cover panel repair, rework of incorrectly fitted trim, or changeovers involving structural body components.

---

## 2. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **Line Operator** | Clears outgoing variant parts from lineside staging; configures fixtures and jig settings for the incoming variant per the changeover card |
| **Trim Team Leader** | Owns the changeover window; confirms changeover timing from the sequencing schedule; signs off completion in MES; escalates if the changeover window is exceeded |
| **Material Handler** | Delivers the new variant kit to the designated staging location; verifies kit contents match the build sheet before handover to the Operator |
| **Quality Technician** | Performs first-off inspection against Control Plan TR-CP-12; signs off in MES upon a passing first-off; authorises hold and re-adjust cycle on failure |

---

## 3. Trigger Conditions

| Trigger | Notes |
|---|---|
| Scheduled variant changeover | Per the sequencing schedule provided by Production Control |
| Unplanned variant mix change | Communicated by Production Control; treated identically to a scheduled changeover for procedural purposes |

---

## 4. Step-by-Step Procedure

**Step 1 — Changeover Time Slot Confirmation**
The Trim Team Leader confirms the changeover time slot and incoming variant designation from the sequencing schedule before initiating any physical changeover activity. For unplanned variant changes, Production Control provides the variant designation and target start time in writing (via [INSERT COMMUNICATION METHOD — e.g., MES work order / radio / printed schedule]).

**Step 2 — Outgoing Variant Clearance**
The Operator clears all outgoing variant parts, clips, and consumables from lineside staging racks. Parts are returned to the designated storage location or handed to the Material Handler. Staging racks must be empty and confirmed clear before incoming variant kit is delivered to the same location.

**Step 3 — Incoming Variant Kit Delivery and Verification**
The Material Handler delivers the new variant kit to the designated staging location. Before handing over to the Operator, the Material Handler verifies that the kit contents (part numbers, quantities, and colour/grade where applicable) match the build sheet for the incoming variant. Any discrepancy is reported to the Trim Team Leader before the kit is accepted at line.

**Step 4 — Fixture and Jig Reconfiguration**
The Operator updates fixture and jig settings per the changeover card (TR-031-A) for the incoming variant. Settings include, but are not limited to:
- Clip engagement torque settings (where the tool is adjustable)
- Panel location datum stops
- Any variant-specific jig inserts or adapters

The Operator confirms each setting change against the changeover card before proceeding to first-off.

**Step 5 — First-Off Inspection**
The Quality Technician performs a first-off inspection on the first complete unit built with the new variant configuration. The inspection is conducted against Control Plan TR-CP-12 and includes, as a minimum:
- Clip engagement (full engagement confirmed at all clip points)
- Panel gap and flush (within the tolerance specified in the control plan)
- Fastener torque (where torque tools are used in trim fitment)

**Step 6 — First-Off Pass: Line Resumption**
If the first-off unit passes all criteria, the Quality Technician signs off the result in MES (including the unit serial number, inspector ID, and timestamp). The Trim Team Leader authorises resumption of normal takt. The signed-off first-off unit proceeds as a conforming unit.

**Step 7 — First-Off Failure: Hold and Re-Adjust**
If the first-off unit fails any inspection criterion:
1. The line is held; do not produce further units with the current fixture configuration.
2. The Operator re-adjusts the fixture or jig setting per the changeover card guidance for the failed criterion.
3. A new first-off unit is produced and re-inspected by the Quality Technician per Step 5.
4. If **two consecutive first-off units fail**, escalate to the Quality Engineer per Section 5 before any further adjustment attempts.

---

## 5. Escalation Criteria

| Condition | Escalation Action |
|---|---|
| Changeover duration exceeds **8 minutes** from start to Trim Team Leader sign-off | Trim Team Leader notified (if not already on scene); cause logged in MES against the changeover event |
| Two consecutive first-off failures | Escalate to Quality Engineer; line held pending Quality Engineer review of fixture setup and changeover card accuracy |
| Kit discrepancy identified in Step 3 | Trim Team Leader notified; Production Control informed; changeover does not proceed until correct kit is confirmed at lineside |

---

## 6. Related Documents

| Document | ID |
|---|---|
| Trim Changeover Card | TR-031-A |
| Trim Control Plan | TR-CP-12 |

---

*End of SOP-TR-031 Rev 5*
