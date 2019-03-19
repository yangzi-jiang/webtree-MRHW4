from __future__ import absolute_import, division, print_function

import csv
import random
import sys

from ortools.sat.python import cp_model
from student import Student

TOTAL_TREE_SPOTS = 25
FIELDS = ['ID','CLASS','CRN','TREE','BRANCH','COURSE_CEILING',
          'MAJOR','MAJOR2','SUBJ','NUMB','SEQ']

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
        courses = {}
        
        #TODO: May need to read in the students' requests differently
        student_pref = {}

        reader.next() # consume the first line, which is just column headers

        for row in reader:

            id = int(row['ID'])
            
            class_year = row['CLASS']
            crn = int(row['CRN'])
            tree = int(row['TREE'])
            branch = int(row['BRANCH'])
            if id in student_requests: # does this student already exist?
                student_requests[id].add_request(crn, tree, branch)
            else: # nope, create a new record
                s = Student(id, class_year)
                s.add_request(crn, tree, branch)
                student_requests[id] = s

            students_by_class[class_year].add(id)
            courses[crn] = int(row['COURSE_CEILING'])
            
    return student_requests, students_by_class, courses

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
    student_requests, students_by_class, courses = read_file(sys.argv[1])
    
    #May be used in process of building model (especially with for loops)
    num_courses = len(courses)
    num_frst = len(students_by_class['FRST'])
    num_soph = len(students_by_class['SOPH'])
    num_jun = len(students_by_class['JUNI'])
    num_sen = len(students_by_class['SENI'])
    num_other = len(students_by_class['OTHER'])
    all_tree_pos = range(TOTAL_TREE_SPOTS)

    # Creates the model.
    model = cp_model.CpModel()

    #course_assignments[(id,crn,yr,pos)]: student 'id' assigned 'class' is class year 'yr' and had crn in position 
    # 'pos' in request tree
    assignments = {}

    #TODO: NEED NESTED FOR LOOPS HERE: add all boolean variables for possible class assignments
    #for each student
        #for each class in that students tree
            #assignments[(id,crn,yr,pos)] = model.NewBoolVar('assignment_id%icrn%iyr%spos%i' % (id,crn,yr,pos))

    #TODO: Constraints:
    
    #Each class must be smaller than cap size
    #for each course
        #num_students_in_class = sum(assignments[(id,crn,yr,pos)] for id in all students for pos in all_tree_pos)
        #model.ADD(num_students_in_class <= courses[crn])

    #Each student must have four class or less

    #Constrain each of the scnearios (i.e can't have tree slot 1a and 1b at same time )
   #For the first three trees:
    # if 1a:
    #     no 2a
    #     no 3a
    #     if 1aa
    #         no 1ab
    #     elif 1ab
    #         no 1aa
    #     if 1aaa
    #         no 1aab
    #     elif 1aba
    #         no 1abb
   
    #For the fourth tree:   
    # if 4a
    #     no 4b
    #     no 4c
    #     no 4d
    
    
    
    
    
    #This is being used in process of trying to print all of a students requests
    student = student_requests[2]
    print(student)
    while (student.can_advance_preference()):
        try:
            requested_course = student.get_next_course()
            print(requested_course)
            student.advance_preference(False)
        except KeyError: # student didn't fill in preference, continue
            pass
        
        # No space (or student didn't specify this node), try next course
        student.advance_preference(False)


if __name__ == '__main__':
  main()
