from __future__ import print_function
from ortools.linear_solver import pywraplp
from student import Student
import csv
import sys
from evaluate import Evaluate

TOTAL_TREE_SPOTS = 25
TREE_SIZE = 7
FIELDS = ['ID','CLASS','CRN','TREE','BRANCH','COURSE_CEILING',
          'MAJOR','MAJOR2','SUBJ','NUMB','SEQ']

# There are 11 distinct course values for a webtree.
# Weights are assigned by y= 200/ (x + 4)
WEIGHTS = [40.0, 100.0/3.0, 200.0/7.0, 200.0/7.0, 25.0, 25.0, 200.0/9.0,
          100.0/3.0, 200.0/7.0, 25.0, 25.0, 200.0/9.0, 200.0/9.0, 20.0,
          200.0/7.0, 25.0, 200.0/9.0, 200.0/9.0, 20.0, 20.0, 200.0/11.0,
          50.0/3.0, 200.0/13.0, 100.0/7.0, 40.0/3.0]

#These are weights for different class years
SENIORITY = {'FRST':1.0,'SOPH':1.1,'JUNI':1.2,'SENI':1.3,'OTHER':1.0}

def read_file(filename):
    """Returns data read in from supplied WebTree data file.

    Parameters:
        filename - string containing the name of the CSV file.

    Returns:
        a) A dictionary mapping student IDs to records, where each record
           contains information about that student's WebTree requests.
        b) A dictionary mapping class years to student IDs, indicating
           which students are seniors, juniors, etc.
        c) A dictionary mapping course CRNs to enrollment capacities.
    """
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=FIELDS)
        student_requests = {}
        students_by_class = {'SENI': set([]), 'JUNI': set([]),
                             'SOPH': set([]), 'FRST': set([]),
                             'OTHER': set([])}
        class_by_student = {}
        courses = {}
        
        student_pref = {}

        reader.next() # consume the first line, which is just column headers

        for row in reader:

            id = int(row['ID'])
            
            class_year = row['CLASS']
            crn = int(row['CRN'])
            tree = int(row['TREE'])
            branch = int(row['BRANCH'])

            class_by_student[id]=class_year
            if id in student_requests: # does this student already exist?
                student_requests[id].add_request(crn, tree, branch)
            else: # nope, create a new record
                s = Student(id, class_year)
                s.add_request(crn, tree, branch)
                student_requests[id] = s
            
            #For building student requests as arrays
            tree_pos = get_tree_pos(tree,branch)
            if id in student_pref: # does this student already exist?
                #Add the course request in the correct tree pos
                student_pref[id][tree_pos] = crn
            else: # nope, create a new record
                pref = [0]*25
                student_pref[id]=pref
                student_pref[id][tree_pos] = crn

            students_by_class[class_year].add(id)
            courses[crn] = int(row['COURSE_CEILING'])
            
    return student_requests, students_by_class,class_by_student, courses, student_pref

def get_tree_pos(tree,branch):
    """
    Returns a position 0-24 based on the tree/brach combination.

    Tree positions are numbered sequentially by starting at tree1 and traversing level-order
    """
    if tree<=3:
        return (TREE_SIZE*(tree-1))+(branch-1)
    else:
        return branch + 20

def main():
  if (len(sys.argv) != 2):
    print()
    print("***********************************************************")
    print("You need to supply a .csv file containing the WebTree data")
    print("as a command-line argument.")
    print
    print ("Example:")
    print ("    python baseline_webtree.py spring-2015.csv")
    print ("***********************************************************")
    print
    return
  
  # Read in data
  student_requests, students_by_class, class_by_student, courses, student_pref = read_file(sys.argv[1])
  
  #Keep an ordered list of crns
  course_index = []
  for course in courses:
    course_index.append(course)
  
  #Sort the crns (may speed up the search?)
  course_index.sort()

  #Keep an ordered list of students
  student_index = []
  for student in student_requests:
    student_index.append(student)

  #Sort student ids (may speed up the search?)
  student_index.sort()

  num_students = len(student_index)
  num_courses = len(course_index)

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



#build courseValue matrix
  courseValue = []
  for student in student_index:
    requests = [-1]*num_courses
    for pos in range(TOTAL_TREE_SPOTS):
      request = student_pref[student][pos]
      if request != 0:
        index = course_index.index(request)
        #if haven't already requested higher in trees
        if requests[index] == -1:
          requests[index] = WEIGHTS[pos]
    courseValue.append(requests)

  num_students = len(courseValue)
  num_courses = len(courseValue[1])
  x = {}

  for i in range(num_students):
    for j in range(num_courses):
      x[i, j] = solver.BoolVar('x[%i,%i]' % (i, j))

  # Objective - We want to maximize the total courseValue for all students
  solver.Maximize(solver.Sum(courseValue[i][j] * SENIORITY[class_by_student[student_index[i]]] * x[i,j] for i in range(num_students)
                                                  for j in range(num_courses)))

  # Constraints

  # Constraint #1 (Done): Each student is assigned to at most 4 courses.
  for i in range(num_students):
    solver.Add(solver.Sum([x[i, j] for j in range(num_courses)]) <= 4)

  # Constraint #2: (Done): Each course is assigned to at most its cap
  for j in range(num_courses):
    solver.Add(solver.Sum([x[i, j] for i in range(num_students)]) <= courses[course_index[j]])

  # Constraint #3: TODO: No duplicating crns
    # No courseID 1 for studentID
    #solver.Add(x[4, 1] == False)

  sol = solver.Solve()

  print('Total courseValue = ', solver.Objective().Value())
  print()
  assignments = {}

  for id in range(num_students):
    assignments[student_index[id]] = []
    
  totalCourseVal = 0
  for i in range(num_students):
    for j in range(num_courses):
      if x[i, j].solution_value() > 0:
        assignments[student_index[i]].append(course_index[j])
        totalCourseVal = totalCourseVal + courseValue[i][j]
        # print('StudentID %d assigned to cousrseID %d.  courseValue = %d' % (
        #       student_index[i],
        #       course_index[j],
        #       courseValue[i][j]))
  
  # Print results to stdout
  for id in assignments:
    print(id, end=' '),
    for course in assignments[id]:
        print(course, end=' ')
    print()

  eval = Evaluate(assignments,courses,student_pref)
  print(eval.FourCourses)
  print(eval.overfill)
  print(eval.requestRatio)
  print()
  print("Total Course Value for all student is %d " % totalCourseVal)
  print()
  print("Time = ", solver.WallTime(), " milliseconds")

if __name__ == '__main__':
  main()