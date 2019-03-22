
class Evaluate:
   
    def __init__(self, assignments, courses):
        self.assignments = assignments
        self.numFourCourses()
        self.courses = courses
        self.overfill = []
        
   
    def numFourCourses(self):
        num = 0
        for i in self.assignments:
            if len(self.assignments[i]) == 4:
                num+=1
        self.FourCourses = num

    def verifyClassCap(self):
        students_in_course = {}

        for i in self.assignments:
            for crn in self.assignments[i]:
                if crn in students_in_course:
                    students_in_course[crn]+= 1
                else:
                    students_in_course[crn] = 1
        for crn in students_in_course:
            if students_in_course[crn]>self.courses[crn]:
                self.overfill.append(crn)


    
    # if __name__ == '__main__':
    #     assignments = {}
    #     main(assignments)
