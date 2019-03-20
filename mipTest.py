from __future__ import print_function
from ortools.linear_solver import pywraplp

def main():
  solver = pywraplp.Solver('SolveAssignmentProblemMIP',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

# Students are rows, courses are cols
  courseValue = [
                [[100, 0], [33, 2], [33, 3], [25, 4], [20, 6]],
                [[100, 0], [50, 1], [33, 2], [25, 4], [20, 6]],
                [[33, 2], [100, 0], [50, 7], [25, 4], [20, 6]],
                [[100, 0], [-1, -1], [33, 3], [-1, -1], [20, 6]], 
                # If a student filled fewer than 4 courses in the webtree, set it to -1, 
                # so that we don't assign that course
                # Similarily, for the course student did not fill in webtree, set it to -1
                [[-1, -1], [100, 0], [50, 7], [25, 9], [20, 6]],
                [[33, 2], [25, 9], [100, 0], [-1, -1], [20, 6]]
                ]

#   team1 = [0, 2, 4]
#   team2 = [1, 3, 5]
#   team_max = 2

  num_students = len(courseValue)
  num_courses = len(courseValue[1])
  x = {}

  for i in range(num_students):
    for j in range(num_courses):
      x[i, j] = solver.BoolVar('x[%i,%i]' % (i, j))

  # Objective - We want to maximize the total courseValue for all students
  solver.Maximize(solver.Sum([courseValue[i][j][0] * x[i,j] for i in range(num_students)
                                                  for j in range(num_courses)]))

  # Constraints

  # Each student is assigned to at most 4 courses.
  # Don't need to assign 4 courses for students who have filled out 4, and according
  # Don't need to parse csv to from student to count how many course they have filled out.
  for i in range(num_students):
    solver.Add(solver.Sum([x[i, j] for j in range(num_courses)]) <= 4)

  # TODO: Each course is assigned to at most its cap
  for j in range(num_courses):
    solver.Add(solver.Sum([x[i, j] for i in range(num_students)]) <= 2)

# # we don't need this
# # Each team takes on two tasks.
#   solver.Add(solver.Sum([x[i, j] for i in team1 for j in range(num_courses)]) <= team_max)
#   solver.Add(solver.Sum([x[i, j] for i in team2 for j in range(num_courses)]) <= team_max)

  sol = solver.Solve()

  print('Total courseValue = ', solver.Objective().Value())
  print()

  totalCourseVal = 0
  for i in range(num_students):
    for j in range(num_courses):
      if x[i, j].solution_value() > 0:
        totalCourseVal = totalCourseVal + courseValue[i][j][0]
        print('StudentID %d assigned to cousrseID %d.  courseValue = %d' % (
              i,
              j,
              courseValue[i][j][0]))

  print()
  print("Total Course Value for all student is %d " % totalCourseVal)
  print()
  print("Time = ", solver.WallTime(), " milliseconds")

if __name__ == '__main__':
  main()