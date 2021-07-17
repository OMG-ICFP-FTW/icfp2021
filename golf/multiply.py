from ortools.sat.python import cp_model
from collections import namedtuple

Coord = namedtuple('Coord', ['x', 'y'])

# Creates the model.
model = cp_model.CpModel()

def new_coord(c):
  return Coord(model.NewIntVar(0, 100, f'{c}x'), model.NewIntVar(0, 100, f'{c}y'))

def sub_pair(var1, var2):
  var = model.NewIntVar(-100, 100, f'{var1.Name()}-{var2.Name()}')
  model.Add(var == var1 - var2)
  return var

def mul_pair(var1, var2):
  var = model.NewIntVar(-10000, 10000, f'{var1.Name()}*{var2.Name()}')
  model.AddMultiplicationEquality(var, [var1, var2])
  return var

def orientation(A, B, C, name):
  Cx_Bx = sub_pair(C.x, B.x)
  By_Ay = sub_pair(B.y, A.y)
  Bx_Ax = sub_pair(B.x, A.x)
  Cy_By = sub_pair(C.y, B.y)
  CBBA = mul_pair(Cx_Bx, By_Ay)
  BACB = mul_pair(Bx_Ax, Cy_By)
  vars = [Cx_Bx, By_Ay, Bx_Ax, Cy_By, CBBA, BACB]

  collinear = model.NewBoolVar(f'collinear_{name}')
  model.Add(CBBA == BACB).OnlyEnforceIf(collinear)
  clockwise = model.NewBoolVar(f'clockwise_{name}')
  model.Add(CBBA > BACB).OnlyEnforceIf(clockwise)
  counterclockwise = model.NewBoolVar(f'counterclockwise_{name}')
  model.Add(CBBA < BACB).OnlyEnforceIf(counterclockwise)
  result = [collinear, clockwise, counterclockwise]
  model.AddBoolOr(result)
  vars.extend(result)
  return vars

A = new_coord('A')
B = new_coord('B')
C = new_coord('C')
vars = [A.x, A.y, B.x, B.y, C.x, C.y]

vars.extend(orientation(A, B, C, 'ABC'))

model.Add(A.x == 0)
model.Add(A.y == 0)
model.Add(B.x == 0)
model.Add(B.y == 2)
model.Add(C.x == 2)
model.Add(C.y == 0)

# Create a solver and solve.
solver = cp_model.CpSolver()
status = solver.Solve(model)

print('Status = %s' % solver.StatusName(status))
for v in vars:
    print(v, '=', solver.Value(v))