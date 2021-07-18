
import matplotlib.pyplot as plt
from ortools.sat.python import cp_model
from collections import namedtuple

Coord = namedtuple('Coord', ['x', 'y'])

# Creates the model.
model = cp_model.CpModel()

def new_coord(c):
  return Coord(model.NewIntVar(0, 10, f'{c}x'), model.NewIntVar(0, 10, f'{c}y'))

def sub_pair(var1, var2):
  if isinstance(var1, int) and isinstance(var2, int):
    return var1 - var2
  name1 = var1.Name() if isinstance (var1, cp_model.IntVar) else str(var1)
  name2 = var2.Name() if isinstance (var2, cp_model.IntVar) else str(var2)
  var = model.NewIntVar(-100, 100, f'{name1}-{name2}')
  model.Add(var == var1 - var2)
  return var

def mul_pair(var1, var2):
  if isinstance(var1, int) and isinstance(var2, int):
    return var1 * var2
  name1 = var1.Name() if isinstance (var1, cp_model.IntVar) else str(var1)
  name2 = var2.Name() if isinstance (var2, cp_model.IntVar) else str(var2)
  var = model.NewIntVar(-10000, 10000, f'({name1})*({name2})')
  model.AddMultiplicationEquality(var, [var1, var2])
  return var

def orientation(P, Q, R, name, full=False):
  Rx_Qx = sub_pair(R.x, Q.x)
  Qy_Py = sub_pair(Q.y, P.y)
  RQQP = mul_pair(Rx_Qx, Qy_Py)
  Qx_Px = sub_pair(Q.x, P.x)
  Ry_Qy = sub_pair(R.y, Q.y)
  QPRQ = mul_pair(Qx_Px, Ry_Qy)
  val = sub_pair(RQQP, QPRQ)
  vars = [Rx_Qx, Qy_Py, RQQP, Qx_Px, Ry_Qy, QPRQ, val] if full else []
  
  clockwise = model.NewBoolVar(f'CW_{name}')
  model.Add(val > 0).OnlyEnforceIf(clockwise)
  collinear = model.NewBoolVar(f'COL_{name}')
  model.Add(val == 0).OnlyEnforceIf(collinear)
  counterclockwise = model.NewBoolVar(f'CCW_{name}')
  model.Add(val < 0).OnlyEnforceIf(counterclockwise)
  result = [clockwise, collinear, counterclockwise]
  model.AddBoolOr(result)
  vars.extend(result)
  return vars

# Problem 11
hole = [Coord(10,0),Coord(10,10),Coord(0,10)]

A = new_coord('A')
B = new_coord('B')
# C = new_coord('C')
# D = new_coord('D')
# vars = [A.x, A.y, B.x, B.y, C.x, C.y, D.x, D.y]
vars = []

for i, h in enumerate(hole):
  vars.append(orientation(A, B, h, f'ABH{i}'))

for i in range(len(hole)):
  j = (i + 1) % len(hole)
  vars.append(orientation(hole[i], hole[j], A, f'H{i}H{j}A'))
  vars.append(orientation(hole[i], hole[j], B, f'H{i}H{j}B'))

model.Add(A.x == 8)
model.Add(A.y == 8)
model.Add(B.x == 10)
model.Add(B.y == 2)

# Create a solver and solve.
solver = cp_model.CpSolver()
status = solver.Solve(model)

print('Status = %s' % solver.StatusName(status))
for varset in vars:
  for v in varset:
    print(v, '=', solver.Value(v), end=' ')
  print()

A = Coord(solver.Value(A.x), solver.Value(A.y))
B = Coord(solver.Value(B.x), solver.Value(B.y))
fig, ax = plt.subplots()
ax.plot([A.x, B.x], [A.y, B.y], 'mo-')
ax.annotate('A', A)
ax.annotate('B', B)
for i in range(len(hole)):
  h1, h2 = hole[i], hole[(i+1)%len(hole)]
  ax.plot([h1.x, h2.x], [h1.y, h2.y], 'co-')
  ax.annotate(f'H{i}', h1)