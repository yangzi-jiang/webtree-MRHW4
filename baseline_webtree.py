
import csv
import sys
import random
from student import Student

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


def assign_random_numbers(students_by_class):
    """Returns four randomly permuted orderings representing the order in
    which students will receive courses from the scheduler.

    While each student is assigned four random positions, only two of the
    positions are independently random; the other two are computed as a
    complement of the class size.

    Parameters:
        students_by_class - a dictionary mapping class years to student
                            IDs, indicating which students are seniors,
                            juniors, etc.
                            
    Returns:
        A dictionary mapping class year to a list of four lists, each
        of which represents the scheduling order for the appropriate pass.
    """
    random_ordering = {}
    # Randomly permute the ordering of students in each class year.
    for class_year in students_by_class:
        students = students_by_class[class_year]
        
        # list1 and list3 are independently random permutations; list2 and
        # list4 are the complements of number1 and number3 wrt the class size.
        list1 = list(students)
        random.shuffle(list1)
        list2 = list1[::-1]
        list3 = list(students)
        random.shuffle(list3)
        list4 = list3[::-1]

        random_ordering[class_year] = [list1, list2, list3, list4]

    return random_ordering


def assign_student(student, courses):
    """Returns a course (CRN #) for the specified student.

    The student's stated preferences and current enrollment limits in the
    requested classes are taken into account when making the determination.
    If no class can be found, this function returns None.

    Parameters:
        student - a Student object corresponding to the student being assigned.

    Returns:
        A CRN number (int) representing this student's next assignment. None
        if no course can be found.
    """
    while (student.can_advance_preference()):
        try:
            requested_course = student.get_next_course()
            if (courses[requested_course] > 0): # there is space!
                courses[requested_course] -= 1
                student.advance_preference(True)
                return requested_course
        except KeyError: # student didn't fill in preference, continue
            pass
        
        # No space (or student didn't specify this node), try next course
        student.advance_preference(False)

    # No courses can be assigned
    return None


def run_webtree(student_requests, students_by_class, courses, random_ordering):
    """Runs the WebTree algorithm and returns an assignment of students to
    courses (CRNs).

    Parameters:
        See descriptions from other function headers.

    Returns:
        A dictionary mapping each student id to a list assigned courses (CRNs).
    """
    assignments = {}
    # Initially, no one has any courses assigned
    for id in student_requests:
        assignments[id] = []
        
    # Course assignment is a 4-pass process. Students in the class
    # 'OTHER' get to go after we cycle through SENIORS-->FIRST_YEARS
    # first. The registrar seems to handle them arbitrarily anyway.
    for i in range(4):
        for class_year in ['SENI', 'JUNI', 'SOPH', 'FRST', 'OTHER']:
            students = random_ordering[class_year][i]
            for student_id in students:
                course = assign_student(student_requests[student_id], courses)
                if course != None:
                    assignments[student_id].append(course)

    # Note: apparently, WebTree does a second pass at this point to "fill out"
    # student schedules further (especially those who received fewer than 4
    # courses). But again, details are unclear and no one can quite describe
    # what *precisely* happens during this phase. So we skip that here.
                                        
    return assignments


def main():
    if (len(sys.argv) != 2):
        print
        print "***********************************************************"
        print "You need to supply a .csv file containing the WebTree data"
        print "as a command-line argument."
        print
        print "Example:"
        print "    python baseline_webtree.py spring-2015.csv"
        print "***********************************************************"
        print
        return
    
    # Read in data
    student_requests, students_by_class, courses = read_file(sys.argv[1])

    # Assign random numbers
    random_ordering = assign_random_numbers(students_by_class)

    # Run webtree
    assignments = run_webtree(student_requests, students_by_class,
                              courses, random_ordering)

    # Print results to stdout
    for id in assignments:
        print id,
        for course in assignments[id]:
            print course,
        print

        
if __name__ == "__main__":
    main()
