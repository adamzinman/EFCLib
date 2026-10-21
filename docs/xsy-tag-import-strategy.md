# Strategy: importing tags from a Control Expert Classic v16.2 `.XSY` into Ignition 8.1

Status: **strategy, not built yet.** Sections marked **⚑ confirm** depend on the example `.XSY` and example Ignition tag export, which are not in the repo yet. Commit them under `samples/xsy-import/` and the parser and JSON shapes will be checked against them before any code is written.

## 1. Requirements

| # | Requirement | Where it's met |
|---|---|---|
| R1 | The script lives on the gateway and runs from the Designer. | §3 |
| R2 | When it runs, it asks for a production line number. | §4 step 1 |
| R3 | It reads the `.XSY` exported from Control Expert and lists the new UDTs and new tags to import. | §5, §6 |
| R4 | New UDTs go in a folder named after the line: line `058` → `Data Types/058/`. Every line gets its own copy of each UDT. | §8 |
| R5 | Running the script opens a file browser. If that isn't possible, the file goes in a required location. | §4 step 2 |
| R6 | New tags go in `058/imported/`. You move them into type folders (PV, valve, motor, pump, HMI, ...) by hand. Automatic sorting comes in a later revision. | §8 |
| R7 | Only variables with **HMI Variable** ticked in the PLC are imported, because that is what the OPC UA server exposes. | §5 |
| R8 | It can be run again and again as the work develops, and it updates existing tags and UDTs. | §6, §7 |

## 2. Summary

```
Designer (Script Console)                         Gateway (project library efc.xsyimport)
─────────────────────────                         ──────────────────────────────────────
efc.xsyimport.designerRun()
  1 ask line no.  ──── "058"
  2 file browser → .XSY bytes
    (or: newest .XSY in the drop folder)
  3 sendRequest("xsyImport", plan) ─────────────▶ parse XSY → HMI variables + DDTs
                                                   read all of [EFC]_types_/058 and [EFC]058
                                                   match PLC ⇄ Ignition, classify
  4 show report, save report + JSON  ◀───────────  (nothing written yet)
  5 confirm (+ separate confirm for retypes)
          ──── sendRequest("xsyImport", apply) ─▶ UDTs: create / merge (dependency order)
                                                   tags: create in 058/imported/,
                                                         merge in place wherever they now live
  6 show result                       ◀─────────── re-read, verify, log to "XsyImport"
```

- **Ignition is the state.** No separate state file is kept. Each run compares the PLC export with what is in Ignition right now, so running it twice in a row changes nothing the second time. Tags you have moved, renamed or extended are still recognized (§6).
- **Dry run first, always.** Nothing is written until the report has been shown and confirmed.
- **It only touches what it owns.** It updates the properties that come from the PLC (§7). Alarms, history, scaling, units, extra members, the folder a tag is in and its name all belong to you and are never changed. Nothing is deleted unless that option is switched on.

## 3. Where the script lives (R1)

| Piece | Location | Scope |
|---|---|---|
| `efc/xsyimport` (parser, matcher, planner, apply) | Project Library of the **gateway scripting project** (Config → Gateway Settings → Gateway Scripting Project), e.g. an inheritable `EFC_Tools` project | gateway + Designer |
| Message handler `xsyImport` | Gateway Events → Message in the same project; calls `efc.xsyimport.handle(payload)` | gateway |
| Launcher | One line in the Designer Script Console: `efc.xsyimport.designerRun()` | Designer |

**Why the split.** The Designer only handles the prompts, the file browser and the report. Parsing, matching and tag writes all run **on the gateway**, through `system.util.sendRequest(project="EFC_Tools", messageHandler="xsyImport", payload=...)`. Every run therefore uses the same code and the gateway's tag permissions, and is logged in the gateway log under the `XsyImport` logger. Any project that inherits `EFC_Tools` can run the launcher.

**Security.** Applying changes requires a configured role (e.g. `Engineering`). The handler checks the user and roles sent with the request. A dry run is allowed for any Designer user.

The pure functions (parse, match, plan, build JSON) have no `system.*` calls. They're unit-tested offline under CPython against the sample `.XSY`, the same way `scripts/test_ddtsync.py` tests `ddtsync`.

## 4. Run flow

1. **Line number (R2).** `system.gui.inputBox("Production line number", "")`.
   - It must match `^\d{3}$` (configurable).
   - It's kept as a **string**, so `058` keeps its leading zero.
   - Cancel or an invalid entry stops the run.
2. **File (R5).**
   - **Main path: file browser.** `system.file.openFile("xsy", defaultFolder)` opens the normal Windows file chooser from the Designer Script Console, starting in the last folder used. The Designer reads the bytes (`system.file.readFileAsBytes`) and sends them gzip+base64 in the payload. Files of a few MB are fine.
   - **Fallback: drop folder.** Used when there's no file browser, e.g. a run triggered from a Gateway Message Handler or a Perspective button. Put the export in `<Ignition install>/data/efc/xsy-import/058/` on the gateway, and the newest `*.xsy` there is used. `designerRun(source="gateway")` picks this path on purpose. Whichever file is used, its name and timestamp are in the report.
3. **Parse** on the gateway (§5).
4. **Read Ignition.** `system.tag.getConfiguration(path, True)` on `[EFC]_types_/058` and on all of `[EFC]058` (every subfolder, not just `imported/`).
5. **Match and classify** (§6). Build the JSON for every create and update.
6. **Report.**
   - The Designer shows the counts and the lists in §6.
   - It saves `<xsy>_058_<yyyyMMdd-HHmm>_report.txt`, `_udts.json` and `_tags.json` next to the `.XSY`, or in the drop folder.
   - The JSON files are normal Tag Browser import files, so you can import by hand or review them.
7. **Confirm → apply.**
   - The main confirm covers new and updated items.
   - **Retypes** need a second confirm (§7). If you decline, everything else is still applied.
   - UDTs are written first, in dependency order (nested DDTs first), then tags.
   - Every returned `QualityCode` is checked. Ignition is re-read and the result is shown.
   - A one-line summary and the full report go to the `XsyImport` log.

## 5. Reading the `.XSY` (R3, R7) **⚑ confirm against the sample**

A Control Expert variables export (`VariablesExchangeFile`) normally looks like this:

```xml
<VariablesExchangeFile>
  <fileHeader company="Schneider Automation" product="Control Expert ... V16.2" content="Variable source file" .../>
  <DDTSource DDTName="DDT_Station" version="...">
    <structure>
      <variables name="NetWeight" typeName="REAL"><comment>Net weight</comment></variables>
      <variables name="Valve"     typeName="DDT_Valve"/>
      <variables name="Used"      typeName="ARRAY[0..9] OF BOOL"/>
    </structure>
  </DDTSource>
  <dataBlock>
    <variables name="Station_1" typeName="DDT_Station">
      <comment>Fill station 1</comment>
      <attribute name="..." value="..."/>   <!-- the HMI Variable flag is expected here -->
    </variables>
  </dataBlock>
</VariablesExchangeFile>
```

**HMI Variable filter (R7)**
- Only `dataBlock` variables with the HMI flag set are imported. Exactly how v16.2 writes that flag (attribute name and value) has to be read from the sample. The parser takes it from config (`hmiFlag`), so an export-format change only needs a config change.
- The flag is set on the top-level variable. If a DDT variable is flagged, the OPC UA server exposes the whole structure, so every member of that DDT is imported.
- **Safety check:** if the file contains **no** HMI flag information at all, the run stops. The usual cause is the export option that leaves attributes out. The tool never falls back to importing every variable.
- A variable that is in Ignition but no longer flagged as HMI in the PLC (or deleted from the PLC) is reported as **Not exposed** (§6).

**Parser**
- Use `xml.etree.ElementTree` on the bytes (works in Jython 2.7). Fall back to the regex reader in `ddtsync.load_export`.
- **Model:**
  - `ddts{name: [member(name, typeName, comment)]}`
  - `variables[(name, typeName, comment, hmi)]`
- **Types:**
  - elementary types
  - `STRING[n]`
  - one-dimensional `ARRAY[a..b] OF T`
  - DDT names
  - FB instance types (DFB/EFB) are **skipped with a reason**, because an `.XSY` doesn't define their members
- **Data types:** shared with `ddtsync` (`_ALIASES`):
  - `BOOL`/`EBOOL` → Boolean
  - `INT` → Int2
  - `UINT`/`WORD`/`DINT` → Int4
  - `UDINT`/`DWORD` → Int8
  - `REAL` → Float4
  - `LREAL` → Float8
  - `STRING` → String
  - `TIME` → Int4
  - `DATE`/`DT` → DateTime
- **Comments** become `documentation`.

## 6. Matching and classification (R3, R8)

**PLC identity, not tag path.** A tag is matched to its PLC variable by where it reads from, not by its name or folder:

| Ignition item | Identity key |
|---|---|
| UDT instance | its `BasePath` parameter (the PLC variable name) |
| OPC atomic tag | its `opcItemPath` with the `ns=2;s=` prefix removed |
| UDT definition | its name in `_types_/058/` |

- The key is matched case-insensitively against the PLC variable name, because Control Expert names are case-insensitive.
- The search covers **all of `[EFC]058/`**. So `Station_1`, once moved from `058/imported/` to `058/Stations/` or renamed `Station_01`, is still found and updated where it is. It is never created a second time in `imported/`.
- Memory, expression and query tags you add yourself have no PLC key and are ignored.

| Class | Meaning | Applied |
|---|---|---|
| **New UDT** | DDT not yet in `_types_/058/` | created |
| **Updated UDT** | Members added, or members whose data type, comment or nested type changed | merged (§7) |
| **Stale UDT members** | Member is in Ignition but no longer in the DDT | reported; deleted only with `pruneMembers=True` |
| **New tag** | HMI variable with no matching tag anywhere under `058/` | created in `058/imported/` |
| **Updated tag** | Tag matched; a PLC-owned property differs (§7) | merged where it is |
| **Retype** | Tag matched, but the PLC type changed (a DDT changed to another DDT, or elementary ↔ DDT) | only after the second confirm |
| **Unchanged** | Tag or UDT matched with no difference | counted only |
| **Not exposed** | Tag has a PLC key but there's no HMI variable for it (unflagged or deleted in the PLC) | reported; deleted only with `pruneTags=True` |
| **Duplicate** | Two or more tags have the same PLC key | all are updated; listed so you can tidy up |
| **Name clash** | A new tag's name is already used in `imported/` by a tag for another PLC variable | skipped; reported |
| **Skipped** | FB or unknown type, a multi-dimensional array, a name Ignition doesn't allow, or a DDT whose nested DDT was itself skipped | reported with the reason |

- A new or updated UDT is written only when every DDT it nests is valid in this run. Instances of a skipped DDT are skipped too.
- **Renamed in the PLC.** The tool sees the new name as a new tag and the old one as *Not exposed*. The report pairs them up as possible renames, so you can rename the old tag by hand before running again and keep its history and alarms.

## 7. Updating existing items (R8)

The tool owns only the properties that come from the PLC. Updates use `system.tag.configure(parentPath, [partialConfig], "m")` (merge), and send **only** those properties. Everything else on the tag stays as it is.

| Item | Properties the tool owns (it writes these) | Yours (never touched) |
|---|---|---|
| UDT definition (`_types_/058/X`) | its members' existence, `dataType`, `valueSource`, `opcServer`/`opcItemPath` bindings, `documentation`, nested `typeId` and parameter bindings; the `BasePath`/`OPCServer` parameters | alarms, history, scaling, eng. units, format, extra members (expression/memory), other parameters |
| UDT instance | `typeId` (retype only), `BasePath`, `documentation` | name, folder, overrides on members, other parameters |
| OPC atomic tag | `dataType`, `opcServer`, `opcItemPath`, `documentation` | name, folder, everything else |

**Options** (in config, or per run in the confirm dialog):

| Option | Default | Effect |
|---|---|---|
| `syncDocumentation` | `True` | PLC comments overwrite `documentation`. Turn it off once comments are kept in Ignition. |
| `allowRetype` | ask | A retype changes the instance's `typeId`. Overrides on members that the new type doesn't have are lost, so it always needs its own confirm. |
| `pruneMembers` | `False` | Deletes stale UDT members. Each line has its own UDT copy, so this affects only that line. History and alarm bindings on those members are lost. |
| `pruneTags` | `False` | Deletes *Not exposed* tags. |

**⚑ Check on the dev gateway (build step 3).** `"m"` must update the members it's given in a UDT definition and keep the members it isn't given. The fallback, if 8.1 merge doesn't behave like that for UDT members, is to configure each changed member by its own path (`[EFC]_types_/058/DDT_Station/NetWeight`), which is a guaranteed merge.

## 8. Folder structure (R4, R6)

```
[EFC]_types_/                (Tag Browser → Data Types)
  058/                       every line has its own copy of each UDT
    DDT_Station              typeId "058/DDT_Station"
    DDT_Valve                typeId "058/DDT_Valve"
[EFC]058/                    (Tags)
  imported/                  all new tags land here
    Station_1                UdtInstance, typeId "058/DDT_Station", BasePath "Station_1"
    PT101                    AtomicTag, OPC
  Valves/                    created by you; moved tags are still found and updated (§6)
    AV002
```

- Every `typeId` the tool writes is line-qualified, including nested UDT members inside another UDT. Line 058 therefore never uses line 057's definitions.
- **The destination folder comes from a rule list in config.** Revision 1 has one rule, `[(".*", "imported")]`. A later revision can route new tags by type, e.g. `[("^DDT_Valve", "Valves"), ("^DDT_PV|REAL$", "ProcessValues"), ...]`, without changing the matcher. Tags that already exist are never moved by the tool.
- Folder names starting with a digit, such as `058`, are allowed. Expressions should quote paths as `{[EFC]058/...}`.

## 9. Ignition JSON that gets generated **⚑ confirm against the example tag file**

Conventions are the same as `ddtsync` and the existing `[EFC]` provider:
- parameters `BasePath` and `OPCServer`
- BMENUA string node ids, e.g. `ns=2;s=Station_1.NetWeight`

```json
{"name": "DDT_Station", "tagType": "UdtType",
 "parameters": {"BasePath": {"dataType": "String", "value": ""},
                "OPCServer": {"dataType": "String", "value": "<line OPC connection>"}},
 "tags": [
  {"name": "NetWeight", "tagType": "AtomicTag", "valueSource": "opc", "dataType": "Float4",
   "documentation": "Net weight",
   "opcServer":   {"bindType": "parameter", "binding": "{OPCServer}"},
   "opcItemPath": {"bindType": "parameter", "binding": "ns=2;s={BasePath}.NetWeight"}},
  {"name": "Valve", "tagType": "UdtInstance", "typeId": "058/DDT_Valve",
   "parameters": {"BasePath":  {"dataType": "String", "value": {"bindType": "parameter", "binding": "{BasePath}.Valve"}},
                  "OPCServer": {"dataType": "String", "value": {"bindType": "parameter", "binding": "{OPCServer}"}}}},
  {"name": "Used", "tagType": "AtomicTag", "valueSource": "opc", "dataType": "BooleanArray",
   "opcServer":   {"bindType": "parameter", "binding": "{OPCServer}"},
   "opcItemPath": {"bindType": "parameter", "binding": "ns=2;s={BasePath}.Used"}}]}

{"name": "Station_1", "tagType": "UdtInstance", "typeId": "058/DDT_Station",
 "parameters": {"BasePath": {"dataType": "String", "value": "Station_1"}},
 "documentation": "Fill station 1"}
```

**Arrays**
- An array of an elementary type becomes one array tag.
- An array of a DDT becomes a folder of instances named `_0`, `_1`, ..., with `BasePath` set to `Arr[i]`, as `ddtsync` does.

## 10. Relationship to `ddtsync`

`ddtsync` (repo `adamzinman/efc-ignition-library`, branch `claude/plc-ddt-udt-migration-e5u64l`; not yet in EFCLib) browses the live PLC over OPC UA and adds missing UDT members. The XSY import now does everything `ddtsync` does to UDTs, works offline from the export and also manages instances. Recommendation: move the shared parts (type map, JSON builders, the `configure` wrapper, report) into `efc/plc/common`. Then keep `ddtsync` only as a check that the live OPC UA server exposes what the `.XSY` says it should.

## 11. Open questions

1. **OPC path and server.** Is the node id always `ns=2;s=<Variable>.<Member>`, or is there a prefix? What is the OPC UA connection name for each line? (Fixed, or a template such as `M580_L{line}`?) The example tag file should answer both.
2. **HMI flag in the export.** The sample `.XSY` shows how v16.2 writes it. Also confirm which export options you use, so the attributes are included.
3. **Defaults.** Should `syncDocumentation` be on? Should pruning stay off, as proposed?
4. **Drop-folder location** for the fallback, if `<Ignition install>/data/efc/xsy-import/<line>/` doesn't suit.

## 12. Build plan

| Step | Output | Check |
|---|---|---|
| 0 | `samples/xsy-import/` with the example `.XSY` and Ignition tags file | – |
| 1 | `tools/xsyimport/xsyimport.py` with the pure functions: parse + HMI filter, match, classify, build JSON | `tools/xsyimport/test_xsyimport.py` (CPython) against the sample: expected lists. A second run against the "applied" result must classify everything as Unchanged. Covers moved, renamed and retyped tags. |
| 2 | Gateway glue: `handle(payload)`, `designerRun()` with file browser + drop-folder fallback, message-handler snippet, role check, logging | a mock `system` as in `test_ddtsync.py` |
| 3 | Dev gateway, line 058: first import; move some tags out of `imported/`; change the export (add a member, add a variable, untick HMI); run again | Tag Browser; a faceplate `_Demo` bound to an updated instance; check the merge behaviour in §7 |
| 4 | `docs/xsy-tag-import.md` user guide (install, run, report meanings), README/inventory entries | – |
| 5 | Later revisions: folder rules by type (R6), shared `efc/plc/common`, optional Perspective admin view | – |
