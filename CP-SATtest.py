from __future__ import absolute_import, division, print_function

import csv
import random
import sys

from ortools.sat.python import cp_model
from student import Student

TOTAL_TREE_SPOTS = 25
TREE_SIZE = 7
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
        class_by_student = {}
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
        pass
    return 0

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

    print(student_pref[2])
    
    #May be used in process of building model (especially with for loops)
    num_courses = len(courses)
    num_frst = len(students_by_class['FRST'])
    num_soph = len(students_by_class['SOPH'])
    num_jun = len(students_by_class['JUNI'])
    num_sen = len(students_by_class['SENI'])
    num_other = len(students_by_class['OTHER'])
    num_class_years = 5
    all_tree_pos = range(TOTAL_TREE_SPOTS)
    class_years = ['SENI', 'JUNI', 'SOPH', 'FRST', 'OTHER']

    # Creates the model.
    model = cp_model.CpModel()

    #course_assignments[(id,crn,yr,pos)]: student 'id' assigned 'class' is class year 'yr' and had crn in position 
    # 'pos' in request tree
    assignments = {}

    #TODO: NEED NESTED FOR LOOPS HERE: add all boolean variables for possible class assignments
    #For each class year
    for yr in range(num_class_years):
        students = students_by_class[class_years[yr]]
        #For each student in that class year
        for id in students: 
            #For each of their tree slots
            for pos in range(TOTAL_TREE_SPOTS):
                crn = student_pref[id][pos]
                #If they requested a class, make a boolean var
                if crn != 0:
                    assignments[(id,crn,pos)] = model.NewBoolVar('assignment_id%icrn%ipos%i' % (id,crn,pos))

    #TODO: Constraints:
    
    #Each class must be smaller than cap size
    for crn in courses:
        num_students_in_class = sum(assignments[(id,crn,pos)] for id in class_by_student for pos in all_tree_pos)
        model.ADD(num_students_in_class <= courses[crn])

    #Each student must have four class or less
    for id in class_by_student:
        num_classes_per_student = sum(assignments[(id,crn,pos)] for crn in courses for pos in all_tree_pos)
        model.ADD(num_classes_per_student<=4)

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


if __name__ == '__main__':
  main()
