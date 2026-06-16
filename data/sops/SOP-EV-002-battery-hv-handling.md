# SOP-EV-002: EV Battery Pack Handling and High-Voltage Isolation

| Field | Detail |
|---|---|
| **Document ID** | SOP-EV-002 |
| **Revision** | 2 |
| **Effective Date** | 2026-02-20 |
| **Area** | EV Battery Assembly |
| **Owner** | EHS Coordinator |
| **Approved By** | [INSERT NAME/TITLE] |
| **ISA-95 Level** | Level 3 — Manufacturing Operations Management |

---

## 1. Scope

This procedure covers the safe handling, lifting, and high-voltage (HV) isolation verification for EV battery packs during all line transit and installation activities. It applies to every battery pack movement on the EV Battery Assembly line without exception.

**Schedule pressure, production targets, and staffing constraints do not override any step in this procedure.**

This procedure does not cover battery pack repair, disassembly, or off-line diagnostic testing; refer to the applicable EV Engineering Work Instruction for those activities.

---

## 2. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **HV-Certified Operator** | Sole authorised role for physical handling of battery packs; confirms own certification at station before starting any task; performs all lifting, installation, and connector operations |
| **Battery Line Team Leader** | Owns all line restart decisions following any HV event; confirms corrective actions are in place before authorising restart |
| **EHS Coordinator** | Holds sign-off authority for any isolation fault or HV-related line stop; must be notified immediately upon any isolation indicator failure or suspected HV fault |
| **Battery Engineer** | Co-holds restart sign-off authority alongside the EHS Coordinator following any isolation fault, interlock fault, or damaged-pack event |

---

## 3. Trigger Conditions

| Trigger | Notes |
|---|---|
| Any battery pack movement, lifting, or installation | Applies to every occurrence without exception |
| Suspected HV system fault | Includes unexpected indicator states, unusual sounds, smells, or heat from a pack |

---

## 4. Step-by-Step Procedure

**Step 1 — Certification Confirmation**
Before beginning any pack handling task, confirm that the assigned operator holds current HV certification. Perform a badge check at the station. An operator whose HV certification has lapsed must not begin the task; the Battery Line Team Leader is responsible for assigning a certified replacement.

**Step 2 — Pre-Lift Visual Inspection**
Visually inspect the entire pack housing for damage, swelling, deformation, electrolyte leakage, or exposed wiring before the lift fixture is attached. Any anomaly is a stop-and-notify condition — see Step 5.

**Step 3 — Lift Fixture Attachment**
Attach only the designated battery lift fixture to the pack. Manual handling of battery packs is **prohibited** under all circumstances, including time-pressure situations. Confirm the fixture is correctly seated and locked before initiating the lift.

**Step 4 — HV Isolation Status Verification**
Before making any contact with the pack's connector interfaces, confirm HV isolation status via the isolation indicator on the pack dashboard. The indicator must display **green (isolated)** before proceeding.

**Step 5 — Isolation Fault Response**
If the isolation indicator does not confirm green:
1. Do not proceed with any connector or wiring work.
2. Do not return the pack to the line.
3. Apply LOTO per SOP-EHS-001.
4. Notify the EHS Coordinator immediately via [INSERT NOTIFICATION METHOD].
5. Await EHS Coordinator and Battery Engineer sign-off before any further action.

**Step 6 — Pack Installation and Torque Sequence**
Install the pack per the torque sequence specified on Battery Build Sheet EV-BS-014. The specified bolt sequence must not be deviated from; incorrect sequencing risks uneven casing load distribution and structural compromise of the pack housing.

**Step 7 — HV Interlock Reconnection and Confirmation**
Reconnect the HV interlock connector as the **last** action in the installation sequence. Confirm that the interlock status light on the station HMI shows the expected state before releasing the pack from the lift fixture.

**Step 8 — MES Traceability Entry**
Log the following in MES before the unit proceeds to the next station:
- Battery pack serial number
- Operator ID
- Installation timestamp
- Isolation check result
- Interlock confirmation status

---

## 5. Escalation Criteria

| Condition | Escalation Action |
|---|---|
| Damaged pack (any visible anomaly from Step 2) | Line stop; EHS Coordinator and Battery Engineer sign-off required before restart |
| Failed HV isolation check | Line stop; LOTO applied; EHS Coordinator notified immediately; no restart without dual sign-off |
| Interlock fault on station HMI | Line stop; EHS Coordinator and Battery Engineer sign-off required before restart |

**No exceptions to the dual sign-off requirement apply, regardless of production schedule pressure.**

---

## 6. Related Documents

| Document | ID |
|---|---|
| HV Lockout-Tagout Procedure | SOP-EHS-001 |
| Battery Build Sheet | EV-BS-014 |
| HV Operator Certification Register | [INSERT DOC ID / SYSTEM LOCATION] |

---

*End of SOP-EV-002 Rev 2*
