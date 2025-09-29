# =====================
DRONE_SELECTED = (255,200,60)
PACKAGE_COLOR = (200,120,60)
DROP_COLOR = (160,80,200)
PATH_COLOR = (200,200,60)
DEPOT_COLOR = (80,160,255)
HUD_COLOR = (230,230,230)


# ---------------------------
# Grid helpers and labels
# ---------------------------
LETTERS = [chr(ord('A') + i) for i in range(GRID_COLS)]
NUMS = [str(i+1) for i in range(GRID_ROWS)]


def cell_center(c, r):
x = c * GRID_CELL + GRID_CELL / 2
y = r * GRID_CELL + GRID_CELL / 2
return (x, y)


def cell_to_label(c, r):
if 0 <= c < len(LETTERS) and 0 <= r < len(NUMS):
return f"{LETTERS[c]}{NUMS[r]}"
return "??"


def label_to_cell(label):
label = label.strip().upper()
if len(label) < 2:
return None
col = label[0]
row = label[1:]
if col not in LETTERS: return None
if row not in NUMS: return None
return (LETTERS.index(col), NUMS.index(row))


def pos_to_cell(pos):
x,y = pos
c = int(x // GRID_CELL)
r = int(y // GRID_CELL)
if 0 <= c < GRID_COLS and 0 <= r < GRID_ROWS:
return (c,r)
return None