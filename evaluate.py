
class Evaluate:
   
    def __init__(self, assignments, courses, student_requests):
        self.assignments = assignments
        self.numFourCourses()
        
        self.courses = courses
        self.overfill = []
        self.verifyClassCap()

        self.requestRatio = 0
        self.requests = student_requests
        self.avgReceivedRequestedRatio()
        
   
    
    def numFourCourses(self):
        """
        Returns the number of students with full schedules
        """
        num = 0
        for i in self.assignments:
            if len(self.assignments[i]) == 4:
                num+=1
        self.FourCourses = num

    def verifyClassCap(self):
        """
        Returns a list of courses that have more students than their course ceiling.

        This list should always be empty if the algorithm operates within the constraints
        """
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
    
    def avgReceivedRequestedRatio(self):
        """
        Returns the average number of courses received per course requested for a given WebTree solution
        """
        totalRatio= 0
        for student in self.requests:
            ctr = 0
            #Counts number of classes requested
            for request in self.requests[student]:
                if request != 0:
                    ctr+=1
            #Num courses received divided by num courses requested
            ratio = float(len(self.assignments[student]))/float(ctr)
            totalRatio+=ratio
        self.requestRatio = totalRatio/len(self.assignments)



    
    # if __name__ == '__main__':
    #     assignments = {}
    #     main(assignments)
