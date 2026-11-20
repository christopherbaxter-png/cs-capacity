from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

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

PCT, HRS, CNT = "0%", "#,##0.0", "0"

# ---------- README ----------
ws = wb.active; ws.title = "README"
rows = [
    ("CSM capacity model: managed book and pooled reactive", TITLE),
    ("", None),
    ("Two operating models run side by side:", BOLD),
    ("Managed book (P1, P2): each account has a named CSM. Demand is proactive plus reactive work plus renewals. Capacity is the managed CSMs' portfolio hours.", BLK),
    ("Pooled reactive (P3, P4): no proactive work. Accounts are served from a shared pool of CSMs that handles reactive demand only. Capacity is the pool's portfolio hours.", BLK),
    ("", None),
    ("How to use", BOLD),
    ("1. Inputs: replace yellow cells. Set the managed and pool CSM split, the account counts and the hours per account.", BLK),
    ("2. Demand: calculates monthly hours for each book. No inputs.", BLK),
    ("3. Capacity: utilisation, status, CSMs needed and accounts per CSM for each book.", BLK),
    ("4. Pool split: compares how the 30 CSMs could be divided between the managed book and the pool.", BLK),
    ("", None),
    ("Colour key: blue text on yellow = input; black = formula; green = link to another tab.", BLK),
    ("", None),
    ("Assumptions", BOLD),
    ("Renewal work sits in the managed book. Change this in Demand if renewals for P3 and P4 are handled by the pool.", BLK),
    ("Pool target utilisation is set separately (default 80%). Reactive queues usually need more slack than planned work.", BLK),
    ("Hours per account are placeholders. Replace them before relying on any utilisation figure.", BLK),
    ("P3 and P4 have no proactive hours: their input cells are shown for reference but not used in demand.", BLK),
]
for i, (t, f) in enumerate(rows, start=1):
    c = ws.cell(row=i, column=1, value=t)
    if f: c.font = f
ws.column_dimensions["A"].width = 120

# ---------- Inputs ----------
wi = wb.create_sheet("Inputs")
wi["A1"] = "Inputs"; wi["A1"].font = TITLE
wi["A2"] = "Yellow cells are inputs. Hours per account are placeholders."; wi["A2"].font = NOTE

wi["A3"] = "Team and capacity"; wi["A3"].font = BOLD
gen = [
    (4, "Contracted hours per CSM per month", 150, "#,##0", "Replace with contracted hours", True),
    (5, "Share of time on portfolio work", 0.70, PCT, "Remainder covers meetings, internal work, training, holidays", True),
    (6, "Target utilisation: managed book", 0.85, PCT, "Leaves buffer for planned and reactive work", True),
    (7, "Total CSM headcount", 30, CNT, "Whole team", True),
    (8, "CSMs in managed book (P1, P2)", 20, CNT, "Placeholder split; change to test options", True),
    (10, "Target utilisation: pooled reactive", 0.80, PCT, "Reactive queues need more slack than planned work", True),
]
for r, lab, val, fmt, note, is_in in gen:
    wi.cell(row=r, column=1, value=lab).font = BLK
    inp(wi.cell(row=r, column=2, value=val), fmt)
    wi.cell(row=r, column=4, value=note).font = NOTE
wi["A9"] = "CSMs in pool (P3, P4)"; wi["A9"].font = BLK
calc(wi["B9"], CNT); wi["B9"] = "=B7-B8"
wi["D9"] = "Total headcount less managed book"; wi["D9"].font = NOTE
wi["A11"] = "Renewals per month (next 90 days, average)"; wi["A11"].font = BLK
inp(wi["B11"], CNT); wi["B11"] = 12
wi["D11"] = "Assumed to sit in the managed book"; wi["D11"].font = NOTE
wi["A12"] = "Hours per renewal"; wi["A12"].font = BLK
inp(wi["B12"], "0.0"); wi["B12"] = 5
wi["D12"] = "Negotiation, Deal Desk, approvals"; wi["D12"].font = NOTE

wi["A14"] = "Accounts and hours by segment"; wi["A14"].font = BOLD
hdr(wi, 15, ["Segment", "Book", "Accounts", "Proactive hours per account per month", "Reactive hours per account per month", "Notes"])
segs = [
    ("P1", "Managed", 448, 1.33, 3.0, "Named CSM per account"),
    ("P2", "Managed", 1436, 1.22, 1.5, "Named CSM per account"),
    ("P3", "Pooled reactive", 1753, None, 0.75, "No proactive work; served by the pool"),
    ("P4", "Pooled reactive", 4176, None, 0.4, "No proactive work; includes 277 blank-tier accounts"),
]
for i, (seg, book, n, pro, re_, note) in enumerate(segs, start=16):
    wi.cell(row=i, column=1, value=seg).font = BLK
    wi.cell(row=i, column=2, value=book).font = BLK
    inp(wi.cell(row=i, column=3, value=n), "#,##0")
    if pro is not None:
        inp(wi.cell(row=i, column=4, value=pro), "0.00")
    else:
        wi.cell(row=i, column=4, value="n/a").font = NOTE
    inp(wi.cell(row=i, column=5, value=re_), "0.00")
    wi.cell(row=i, column=6, value=note).font = NOTE
wi["A21"] = "Accounts are from the team breakdown. Hours per account are placeholders to replace with time-tracking data."; wi["A21"].font = NOTE
for col, w in zip("ABCDEF", [40, 18, 14, 22, 22, 46]):
    wi.column_dimensions[col].width = w

# ---------- Demand ----------
wd = wb.create_sheet("Demand")
wd["A1"] = "Monthly demand (hours)"; wd["A1"].font = TITLE
wd["A2"] = "Formulas only. Driven by the Inputs tab."; wd["A2"].font = NOTE
hdr(wd, 3, ["Workload", "P1", "P2", "P3", "P4", "Total"])
wd["A4"] = "Proactive work"; wd["A4"].font = BLK
wd["A5"] = "Reactive work"; wd["A5"].font = BLK
calc(wd["B4"], HRS); wd["B4"] = "=Inputs!C16*Inputs!D16"
calc(wd["C4"], HRS); wd["C4"] = "=Inputs!C17*Inputs!D17"
calc(wd["D4"], HRS); wd["D4"] = 0
calc(wd["E4"], HRS); wd["E4"] = 0
calc(wd["F4"], HRS); wd["F4"] = "=SUM(B4:E4)"
calc(wd["B5"], HRS); wd["B5"] = "=Inputs!C16*Inputs!E16"
calc(wd["C5"], HRS); wd["C5"] = "=Inputs!C17*Inputs!E17"
calc(wd["D5"], HRS); wd["D5"] = "=Inputs!C18*Inputs!E18"
calc(wd["E5"], HRS); wd["E5"] = "=Inputs!C19*Inputs!E19"
calc(wd["F5"], HRS); wd["F5"] = "=SUM(B5:E5)"
wd["A6"] = "Renewal work (managed book)"; wd["A6"].font = BLK
calc(wd["F6"], HRS, GRN); wd["F6"] = "=Inputs!B11*Inputs!B12"
wd["A8"] = "Managed book (P1, P2)"; wd["A8"].font = BOLD
calc(wd["F8"], HRS, BOLD); wd["F8"] = "=SUM(B4:C5)+F6"
wd["A9"] = "Pooled reactive (P3, P4)"; wd["A9"].font = BOLD
calc(wd["F9"], HRS, BOLD); wd["F9"] = "=SUM(D5:E5)"
wd["A10"] = "Total demand"; wd["A10"].font = BOLD
calc(wd["F10"], HRS, BOLD); wd["F10"] = "=F8+F9"; wd["F10"].border = TOP
wd["A12"] = "P3 and P4 proactive cells are fixed at zero because pooled accounts receive reactive work only."; wd["A12"].font = NOTE
wd.column_dimensions["A"].width = 34
for col in "BCDEF": wd.column_dimensions[col].width = 14

# ---------- Capacity ----------
wc = wb.create_sheet("Capacity")
wc["A1"] = "Capacity check"; wc["A1"].font = TITLE
wc["A2"] = "Each book is measured against its own CSMs and target."; wc["A2"].font = NOTE
hdr(wc, 3, ["Managed book (P1, P2)", "Value", "How it is calculated"])
mb = [
    (4, "Managed book demand (hours per month)", "=Demand!F8", HRS, "Demand tab", GRN),
    (5, "Accounts in managed book", "=Inputs!C16+Inputs!C17", "#,##0", "P1 + P2 accounts", BLK),
    (6, "CSMs in managed book", "=Inputs!B8", CNT, "From Inputs", GRN),
    (7, "Portfolio hours per CSM (at 100%)", "=Inputs!B4*Inputs!B5", HRS, "Contracted hours x share on portfolio", BLK),
    (8, "Managed hours available", "=B6*B7", HRS, "CSMs x hours per CSM", BLK),
    (9, "Utilisation", "=B4/B8", PCT, "Demand / hours available", BLK),
    (10, "Target utilisation", "=Inputs!B6", PCT, "From Inputs", GRN),
    (11, "Status", '=IF(B9>B10,"Over capacity","Within capacity")', None, "Over capacity if above target", BLK),
    (12, "Accounts per managed CSM", "=B5/B6", "0", "Accounts / CSMs", BLK),
    (13, "Demand per managed CSM (hours per month)", "=B4/B6", HRS, "Demand / CSMs", BLK),
    (14, "CSMs needed at target", "=ROUNDUP(B4/(B7*B10),0)", CNT, "Demand / (hours per CSM x target)", BLK),
]
for r, lab, f, fmt, how, font in mb:
    wc.cell(row=r, column=1, value=lab).font = BLK
    calc(wc.cell(row=r, column=2, value=f), fmt, font)
    wc.cell(row=r, column=3, value=how).font = NOTE

hdr(wc, 16, ["Pooled reactive (P3, P4)", "Value", "How it is calculated"])
pb = [
    (17, "Pool demand (reactive hours per month)", "=Demand!F9", HRS, "Demand tab", GRN),
    (18, "Accounts in pool", "=Inputs!C18+Inputs!C19", "#,##0", "P3 + P4 accounts", BLK),
    (19, "CSMs in pool", "=Inputs!B9", CNT, "Total headcount less managed book", GRN),
    (20, "Pool hours available", "=B19*B7", HRS, "Pool CSMs x hours per CSM", BLK),
    (21, "Utilisation", "=B17/B20", PCT, "Demand / hours available", BLK),
    (22, "Target utilisation", "=Inputs!B10", PCT, "From Inputs", GRN),
    (23, "Status", '=IF(B21>B22,"Over capacity","Within capacity")', None, "Over capacity if above target", BLK),
    (24, "Accounts per pool CSM", "=B18/B19", "0", "Accounts / pool CSMs", BLK),
    (25, "CSMs needed in pool at target", "=ROUNDUP(B17/(B7*B22),0)", CNT, "Demand / (hours per CSM x target)", BLK),
]
for r, lab, f, fmt, how, font in pb:
    wc.cell(row=r, column=1, value=lab).font = BLK
    calc(wc.cell(row=r, column=2, value=f), fmt, font)
    wc.cell(row=r, column=3, value=how).font = NOTE

hdr(wc, 27, ["Whole team", "Value", "How it is calculated"])
wc["A28"] = "Total demand (hours per month)"; wc["A28"].font = BLK
calc(wc["B28"], HRS, GRN); wc["B28"] = "=Demand!F10"
wc["A29"] = "Total hours available"; wc["A29"].font = BLK
calc(wc["B29"], HRS); wc["B29"] = "=B8+B20"
wc["A30"] = "Overall utilisation"; wc["A30"].font = BLK
calc(wc["B30"], PCT); wc["B30"] = "=B28/B29"
wc.column_dimensions["A"].width = 40; wc.column_dimensions["B"].width = 18; wc.column_dimensions["C"].width = 44

# ---------- Pool split ----------
wp = wb.create_sheet("Pool split")
wp["A1"] = "Pool split options"; wp["A1"].font = TITLE
wp["A2"] = "Change the pool headcount in column A (blue) to compare splits of the total team. Managed CSMs = total headcount less pool."; wp["A2"].font = NOTE
hdr(wp, 3, ["CSMs in pool", "CSMs in managed book", "Managed utilisation", "Managed status", "Pool utilisation", "Pool status"])
for i, n in enumerate([4, 6, 8, 10, 12, 14], start=4):
    inp(wp.cell(row=i, column=1, value=n), CNT)
    calc(wp.cell(row=i, column=2, value=f"=Inputs!$B$7-A{i}"), CNT)
    calc(wp.cell(row=i, column=3, value=f'=IF(B{i}>0,Demand!$F$8/(B{i}*Capacity!$B$7),"n/a")'), PCT)
    calc(wp.cell(row=i, column=4, value=f'=IF(B{i}>0,IF(C{i}>Inputs!$B$6,"Over capacity","Within capacity"),"n/a")'))
    calc(wp.cell(row=i, column=5, value=f'=IF(A{i}>0,Demand!$F$9/(A{i}*Capacity!$B$7),"n/a")'), PCT)
    calc(wp.cell(row=i, column=6, value=f'=IF(A{i}>0,IF(E{i}>Inputs!$B$10,"Over capacity","Within capacity"),"n/a")'))
wp["A11"] = "Uses the current hours per account, renewal assumption and total headcount from Inputs."; wp["A11"].font = NOTE
for col in "ABCDEF": wp.column_dimensions[col].width = 20

wb.save("/home/claude/capacity2/CSM_Capacity_Model_v2.xlsx")
print("saved")
