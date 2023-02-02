import sys
import os
from ortools.linear_solver import pywraplp
import math
import time

utils_path = os.path.join(os.getcwd())
sys.path.insert(1, utils_path)

from utils.read_data import read_data


from ortools.sat.python import cp_model
import math

def cp(num_subjects: int, num_rooms: int, nums_student_per_subject: int, 
        num_seats_per_room: int, subject_pairs: int,
        num_sections_per_day: int = None, num_days: int = None, 
        save_model: bool = False, time_limit: int = 600):
    
    if (not num_sections_per_day):
        num_sections_per_day = 4

    if (not num_days):
        num_days = math.ceil(num_subjects / num_sections_per_day)

    model = cp_model.CpModel()

    # Variables x[i] represent the section assigned to subject i
    x = [model.NewIntVar(0, num_subjects, "x[%i]" % i) for i in range(num_subjects)]

    # Variables y[i][j] represent whether subject i is assigned to room j
    y = [[model.NewIntVar(0, 1, "y[%i][%i]" % (i, j)) for j in range(num_rooms)] for i in range(num_subjects)]

    # Objective variable
    obj_var = model.NewIntVar(0, num_subjects, "num_sections")

    # Constraint 1: Each subject must be assigned once
    for i in range(num_subjects):
        model.Add(sum([y[i][j] for j in range(num_rooms)]) == 1)

    # Constraint 2: Each room must have most one subject in each section 
    # (i.e. two subjects cannot be assigned to the same room in the same section)
    # it means x[i] == x[j] => y[i][k] + y[j][k] <= 1 for all k in range(num_rooms)
    for i in range(num_subjects):
        for j in range(num_subjects):
            if i == j:
                continue
            for k in range(num_rooms):
                b = model.NewBoolVar("b[%i][%i]" % (i, j))
                model.Add(x[i] == x[j]).OnlyEnforceIf(b)
                model.Add(x[i] != x[j]).OnlyEnforceIf(b.Not())                                                  
                model.Add(y[i][k] + y[j][k] <= 1).OnlyEnforceIf(b)


    # Constraint 3: Each subject assigned to a room must have enough seats
    for i in range(num_subjects):
        model.Add(sum([y[i][j] * num_seats_per_room[j] for j in range(num_rooms)]) >= nums_student_per_subject[i])

    # Constraints 4: Two subjects cannot be assigned to the same room in the same section
    for i1, i2 in subject_pairs:
        model.Add(x[i1] != x[i2])

    # Constraint 5: Objective variable object_var = max(x[i] all i in range(num_subjects)))
    for i in range(num_subjects):
        model.Add(obj_var >= x[i])

    # Objective: Minimize the number of sections
    model.Minimize(obj_var)

    
    if save_model:
        with open('cp.txt', 'w') as f:
            model.ExportToFile(f.name)
    

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        solution = []
        
        print("Optimal solution found")
        print("Number of sections: ", solver.Value(obj_var))
 
        for subject in range(num_subjects):
            
            room = None
            
            for j in range(num_rooms):
                if solver.Value(y[subject][j]) == 1:
                    room = j
                    break
            
            section_id = solver.Value(x[subject])
            
            print('Subject %i is assigned to room %i in section %i' % (subject, room, section_id))
            
            
            solution.append((subject, room, section_id // num_sections_per_day, section_id % num_sections_per_day))
        
        solution.sort(key=lambda x: x[2] * num_sections_per_day + x[3])
        
        solution_str = ''        
        solution_str += "subjects,number_student,rooms,num_seat,day,section" + "\n"
        for subjects, room, day, section in solution:
            solution_str += str(subjects) + "," + str(nums_student_per_subject[subjects]) + "," + str(room) + "," + \
                str(num_seats_per_room[room]) + "," + str(day) + "," + str(section) + "\n"

        return solution_str

    else:
        print('The problem does not have an optimal solution.')          
        
        