from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment

wb = Workbook()
F = "Arial"
BLUE = Font(name=F, size=10, color="0000FF")
BLK = Font(name=F, size=10, color="000000")
GRN = Font(name=F, size=10, color="008000")
BOLD = Font(name=F, size=10, bold=True)
TITLE = Font(name=F, size=14, bold=True)
NOTE = Font(name=F, size=9, italic=True, color="595959")
HDR_FILL = PatternFill("solid", fgColor="D9E1F2")
INPUT_FILL = PatternFill("solid", fgColor="FFFF00")
thin = Side(style="thin", color="BFBFBF")
TOP = Border(top=Side(style="thin", color="000000"))

def hdr(ws, row, values):
    for i, v in enumerate(values):
        c = ws.cell(row=row, column=1 + i, value=v)
        c.font = BOLD; c.fill = HDR_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center")

def inp(c, fmt=None):
    c.font = BLUE; c.fill = INPUT_FILL
    if fmt: c.number_format = fmt

def calc(c, fmt=None, font=BLK):
    c.font = font
    if fmt: c.number_format = fmt

# ---------- README ----------
ws = wb.active; ws.title = "README"
rows = [
    ("CSM capacity model", TITLE),
    ("", None),
    ("Purpose: estimate how much CSM time the portfolio needs each month, compare it with available time, and show how many accounts each CSM can hold at target utilisation.", BLK),
    ("", None),
    ("How to use", BOLD),
    ("1. Inputs tab: replace the yellow cells with real values. Start with headcount, contracted hours and the account counts and hours by segment.", BLK),
    ("2. Demand tab: calculates monthly hours by segment for proactive and reactive work, plus renewal work. No inputs here.", BLK),
    ("3. Capacity tab: compares demand with available hours and flags whether the team is over capacity.", BLK),
    ("4. Scenarios tab: edit the blue cells to test growth, headcount loss or a cutover.", BLK),
    ("", None),
    ("Colour key", BOLD),
    ("Blue text on yellow = input you should change", BLK),
    ("Black text = formula", BLK),
    ("Green text = link to another tab", BLK),
    ("", None),
    ("Important", BOLD),
    ("All starting numbers are illustrative placeholders, not real data. Account counts, headcount, hours per touchpoint and reactive hours all need replacing.", BLK),
    ("Proactive hours per account are placeholders for the average monthly CSM time per account across the five journey stages. Health-score bands are not used.", BLK),
    ("The model assumes an even spread of work across the team. Reactive load is an average per account, so spikes will not show.", BLK),
]
for i, (t, f) in enumerate(rows, start=1):
    c = ws.cell(row=i, column=1, value=t)
    if f: c.font = f
ws.column_dimensions["A"].width = 120

# ---------- Inputs ----------
wi = wb.create_sheet("Inputs")
wi["A1"] = "Inputs"; wi["A1"].font = TITLE
wi["A2"] = "Yellow cells are inputs. All values are placeholders to replace."; wi["A2"].font = NOTE

wi["A3"] = "General assumptions"; wi["A3"].font = BOLD
gen = [
    ("Contracted hours per CSM per month", 150, "#,##0", "Replace with contracted hours"),
    ("Share of time on portfolio work", 0.70, "0%", "Remainder covers meetings, internal work, training, holidays"),
    ("Target utilisation", 0.85, "0%", "Leaves buffer for reactive work"),
    ("CSM headcount", 30, "0", "Number of CSMs carrying a portfolio"),
    ("Renewals per month (next 90 days, average)", 12, "0", "From renewal calendar / 3"),
    ("Hours per renewal", 5, "0.0", "Negotiation, Deal Desk, approvals"),
]
for i, (lab, val, fmt, note) in enumerate(gen, start=4):
    wi.cell(row=i, column=1, value=lab).font = BLK
    inp(wi.cell(row=i, column=2, value=val), fmt)
    wi.cell(row=i, column=4, value=note).font = NOTE

wi["A11"] = "Accounts and hours by segment"; wi["A11"].font = BOLD
hdr(wi, 12, ["Segment", "Accounts", "Proactive hours per account per month", "Reactive hours per account per month", "Proactive work on? (1 = yes, 0 = reactive only)", "Notes"])
segments = [
    ("P1", 448, 1.33, 3.0, "Team account breakdown; hours per account still placeholder"),
    ("P2", 1436, 1.22, 1.5, "Team account breakdown; hours per account still placeholder"),
    ("P3", 1753, 1.17, 0.75, "Team account breakdown; hours per account still placeholder"),
    ("P4", 4176, 1.11, 0.4, "Team account breakdown; includes 277 blank-tier accounts"),
]
for i, (seg, n, pro, re_, note) in enumerate(segments, start=13):
    wi.cell(row=i, column=1, value=seg).font = BLK
    inp(wi.cell(row=i, column=2, value=n), "0")
    inp(wi.cell(row=i, column=3, value=pro), "0.00")
    inp(wi.cell(row=i, column=4, value=re_), "0.00")
    inp(wi.cell(row=i, column=5, value=1 if seg in ("P1", "P2") else 0), "0")
    wi.cell(row=i, column=6, value=note).font = NOTE
wi["A17"] = "Proactive hours are the average monthly CSM time per account across the journey stages. Set the switch to 0 for segments where CSMs only carry out reactive work (P3 and P4 currently). Reactive hours cover escalations, fraud and support tickets, inbox triage and feature questions."
wi["A17"].font = NOTE
for col, w in zip("ABCDEF", [44, 16, 26, 26, 30, 40]):
    wi.column_dimensions[col].width = w

# ---------- Demand ----------
wd = wb.create_sheet("Demand")
wd["A1"] = "Monthly demand (hours)"; wd["A1"].font = TITLE
wd["A2"] = "Formulas only. Driven by the Inputs tab."; wd["A2"].font = NOTE
hdr(wd, 3, ["Workload", "P1", "P2", "P3", "P4", "Total"])
wd["A4"] = "Proactive work"; wd["A4"].font = BLK
wd["A5"] = "Reactive work"; wd["A5"].font = BLK
for j, col in enumerate("BCDE"):
    src = 13 + j
    calc(wd[f"{col}4"], "#,##0.0"); wd[f"{col}4"] = f"=Inputs!$B${src}*Inputs!$C${src}*Inputs!$E${src}"
    calc(wd[f"{col}5"], "#,##0.0"); wd[f"{col}5"] = f"=Inputs!$B${src}*Inputs!$D${src}"
calc(wd["F4"], "#,##0.0"); wd["F4"] = "=SUM(B4:E4)"
calc(wd["F5"], "#,##0.0"); wd["F5"] = "=SUM(B5:E5)"
wd["A6"] = "Renewal work (all segments)"; wd["A6"].font = BLK
calc(wd["F6"], "#,##0.0", GRN); wd["F6"] = "=Inputs!B8*Inputs!B9"
wd["A7"] = "Total demand"; wd["A7"].font = BOLD
for col in "BCDE":
    c = wd[f"{col}7"]; c.value = f"=SUM({col}4:{col}5)"; calc(c, "#,##0.0", BOLD); c.border = TOP
wd["F7"] = "=SUM(F4:F6)"; calc(wd["F7"], "#,##0.0", BOLD); wd["F7"].border = TOP
wd["A9"] = "Note: renewal work is shown in total only, as it is not split by segment."; wd["A9"].font = NOTE
wd.column_dimensions["A"].width = 34
for col in "BCDEF": wd.column_dimensions[col].width = 14

# ---------- Capacity ----------
wc = wb.create_sheet("Capacity")
wc["A1"] = "Capacity check"; wc["A1"].font = TITLE
wc["A2"] = "Compares monthly demand with the portfolio hours the team has available."; wc["A2"].font = NOTE
hdr(wc, 3, ["Measure", "Value", "How it is calculated"])
cap_rows = [
    ("Total demand (hours per month)", "=Demand!F7", "#,##0.0", "Demand tab total", GRN),
    ("Total accounts", "=SUM(Inputs!B13:B16)", "0", "Sum of account counts on Inputs", BLK),
    ("Average demand hours per account", "=B4/B5", "0.00", "Total demand / total accounts", BLK),
    ("Portfolio hours per CSM (at 100%)", "=Inputs!B4*Inputs!B5", "#,##0.0", "Contracted hours x share on portfolio", BLK),
    ("CSM headcount", "=Inputs!B7", "0", "From Inputs", GRN),
    ("Total portfolio hours available", "=B7*B8", "#,##0.0", "Hours per CSM x headcount", BLK),
    ("Utilisation", "=B4/B9", "0%", "Demand / portfolio hours available", BLK),
    ("Target utilisation", "=Inputs!B6", "0%", "From Inputs", GRN),
    ("Status", '=IF(B10>B11,"Over capacity","Within capacity")', None, "Over capacity if utilisation exceeds target", BLK),
    ("Demand per CSM (hours per month)", "=B4/B8", "#,##0.0", "Total demand / headcount", BLK),
    ("CSMs needed at target utilisation", "=ROUNDUP(B4/(B7*B11),0)", "0", "Demand / (hours per CSM x target)", BLK),
    ("Accounts per CSM at target (current mix)", "=(B7*B11)/B6", "0", "Hours per CSM at target / average hours per account", BLK),
]
for i, (lab, f, fmt, how, font) in enumerate(cap_rows, start=4):
    wc.cell(row=i, column=1, value=lab).font = BLK
    calc(wc.cell(row=i, column=2, value=f), fmt, font)
    wc.cell(row=i, column=3, value=how).font = NOTE
wc["A17"] = "Approximation: the accounts-per-CSM figure assumes the current account mix stays the same."; wc["A17"].font = NOTE
wc.column_dimensions["A"].width = 40; wc.column_dimensions["B"].width = 18; wc.column_dimensions["C"].width = 56

# ---------- Scenarios ----------
wsn = wb.create_sheet("Scenarios")
wsn["A1"] = "Scenarios"; wsn["A1"].font = TITLE
wsn["A2"] = "Edit the blue cells. Demand scales with the account multiplier plus extra accounts at the current average hours."; wsn["A2"].font = NOTE
hdr(wsn, 3, ["Measure", "Base", "Growth +20%", "Lose one CSM", "MM cutover (+30 accounts)"])
labels = [
    "Account volume multiplier", "Extra accounts (added at current average)", "CSM headcount",
    "Demand (hours per month)", "Portfolio hours available", "Utilisation", "Status",
]
for i, lab in enumerate(labels, start=4):
    wsn.cell(row=i, column=1, value=lab).font = BLK
mult = [1, 1.2, 1, 1]
extra = [0, 0, 0, 30]
for j, col in enumerate("BCDE"):
    inp(wsn[f"{col}4"], "0.00"); wsn[f"{col}4"] = mult[j]
    inp(wsn[f"{col}5"], "0"); wsn[f"{col}5"] = extra[j]
    if col == "D":
        calc(wsn[f"{col}6"], "0"); wsn[f"{col}6"] = "=Inputs!$B$7-1"
    else:
        calc(wsn[f"{col}6"], "0", GRN); wsn[f"{col}6"] = "=Inputs!$B$7"
    calc(wsn[f"{col}7"], "#,##0.0"); wsn[f"{col}7"] = f"=Capacity!$B$4*{col}4+{col}5*Capacity!$B$6"
    calc(wsn[f"{col}8"], "#,##0.0"); wsn[f"{col}8"] = f"={col}6*Capacity!$B$7"
    calc(wsn[f"{col}9"], "0%"); wsn[f"{col}9"] = f"={col}7/{col}8"
    calc(wsn[f"{col}10"]); wsn[f"{col}10"] = f'=IF({col}9>Inputs!$B$6,"Over capacity","Within capacity")'
wsn["A12"] = "Scenario headcount for 'Lose one CSM' is set to one fewer than the Inputs headcount."; wsn["A12"].font = NOTE
wsn.column_dimensions["A"].width = 40
for col in "BCDE": wsn.column_dimensions[col].width = 20

wb.save("/home/claude/capacity/CSM_Capacity_Model.xlsx")
print("saved")
