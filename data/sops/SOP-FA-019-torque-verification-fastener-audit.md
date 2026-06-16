# SOP-FA-019: Torque Verification and Fastener Audit

| Field | Detail |
|---|---|
| **Document ID** | SOP-FA-019 |
| **Revision** | 6 |
| **Effective Date** | 2026-03-05 |
| **Area** | Final Assembly |
| **Owner** | Quality Engineer |
| **Approved By** | [INSERT NAME/TITLE] |
| **ISA-95 Level** | Level 3 — Manufacturing Operations Management |

---

## 1. Scope

This procedure covers routine in-process torque verification and periodic fastener audit for safety-critical joints in the Final Assembly area. Safety-critical joints include, but are not limited to, seatbelt anchorage points and suspension mounts.

This procedure applies to all pulse and electronic torque tools used on safety-critical fastener cycles and to all units produced on lines governed by Control Plan FA-CP-04.

This procedure does not cover non-safety fastener torque verification; refer to the applicable work instruction for standard-torque joints.

---

## 2. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **Operator** | Performs shift-start calibration check on the torque tool; records result in MES; removes tool from service immediately upon calibration failure |
| **Quality Technician** | Performs periodic in-process fastener audits at the frequency defined in Control Plan FA-CP-04; records audit results against unit serial number in MES; initiates line stop and quarantine upon audit failure |
| **Maintenance Technician** | Responds to tool tag-out notifications; performs or coordinates tool calibration; clears tag-out only after verified recalibration |
| **Quality Engineer** | Holds sole authority to authorise line restart following a failed safety-critical torque audit |

---

## 3. Trigger Conditions

| Trigger | Frequency |
|---|---|
| Shift-start calibration check | Every shift, before first unit is produced |
| In-process safety-critical fastener audit | Per Control Plan FA-CP-04 — typically every 50th unit; the control plan value is authoritative |

---

## 4. Step-by-Step Procedure

**Step 1 — Shift-Start Calibration Check**
At the start of each shift, before production begins, the Operator performs a calibration check on the pulse or electronic torque tool by testing it against a calibrated reference torque wrench. The pass/fail result and the reference wrench ID are recorded in MES against the shift and workstation.

**Step 2 — Tool Failure Response**
If the shift-start calibration check fails:
- Remove the tool from service immediately.
- Apply a tag-out tag in accordance with the site lockout/tagout procedure.
- Notify the Maintenance Technician via [INSERT NOTIFICATION METHOD — e.g., MES alert / radio call].
- Do not begin production on the affected station until a calibrated replacement tool is in service and a passing calibration record has been entered in MES.

**Step 3 — Automatic In-Process Torque Logging**
During production, the torque tool automatically logs the applied torque value to MES for each safety-critical fastener cycle, linked to the unit serial number and workstation. The Operator is responsible for confirming the tool signal lamp or MES acknowledgement at each cycle; no manual entry is required for passing cycles.

**Step 4 — Periodic Fastener Audit**
At the frequency defined in Control Plan FA-CP-04 (typically every 50th unit), the Quality Technician pulls the designated audit unit from the line or offline audit station and manually re-verifies torque on all safety-critical joints using a calibrated hand torque wrench. The calibrated hand tool ID must be recorded alongside the audit result.

**Step 5 — Audit Result Entry**
The Quality Technician records the audit result — pass or fail, with actual torque value(s) — against the unit serial number in MES. The entry must be completed before the audit unit is released back to the production flow.

**Step 6 — Audit Failure Response**
If the periodic fastener audit fails on any safety-critical joint:
1. **Stop the line immediately.**
2. **Quarantine all units built since the last passing audit.** Apply physical hold tags and update unit status to Quality Hold in MES.
3. **Follow SOP-QA-007** (Quality Hold and Containment Procedure) for suspect unit disposition, root-cause investigation, and containment actions.
4. **Do not restart the line** until the Quality Engineer has reviewed the failure, authorised the corrective action, and provided written sign-off in MES. This requirement is unconditional — see Section 5.

---

## 5. Escalation Criteria

| Condition | Escalation Action |
|---|---|
| Failed safety-critical torque audit (any joint) | Immediate line stop; Quality Engineer sign-off mandatory before restart, regardless of production impact or schedule pressure |
| Tool calibration failure at shift start | Tool tagged out; Maintenance Technician notified; production on affected station suspended until replacement tool is verified in MES |
| [INSERT THRESHOLD] consecutive audit failures across separate units | Escalate to Plant Quality Manager and notify Customer Quality if applicable |

---

## 6. Related Documents

| Document | ID |
|---|---|
| Quality Hold and Containment Procedure | SOP-QA-007 |
| Final Assembly Control Plan | FA-CP-04 |
| Tool Calibration Log | [INSERT DOC ID / MES LOCATION] |
| Site Lockout/Tagout Procedure | [INSERT DOC ID] |

---

*End of SOP-FA-019 Rev 6*
