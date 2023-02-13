import sys
import os
from ortools.linear_solver import pywraplp
import math
import time
import argparse

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

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
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

        return (solution_str, status)

    else:
        print('The problem does not have an optimal solution.')          
        return (None, status)        


def test_phase(num_run_per_data: int, config_index: int, time_limit: int = 600):
    configs = [(10, 2, 4), (10, 2, 12), (10, 2, 24), (10, 2, 40),
            (16, 3, 12), (16, 3, 24), (16, 3, 40), (16, 3, 60),
            (20, 4, 24), (20, 4, 40), (20, 4, 60), (20, 4, 80),
            (30, 6, 40), (30, 6, 60), (30, 6, 80), 
            (40, 8, 60), (40, 8, 80), (40, 8, 120),
            (50, 10, 80), (50, 10, 120),
            (60, 12, 80),(60, 12, 120), 
            (70, 16, 80), (70, 16, 120), 
            (80, 20, 80), (80, 20, 120),
            (200, 20, 80), (200, 20, 120)]
    
    
    for i in range (0, 5):
        for run in range(1, num_run_per_data + 1):
            start_time = time.time()

            path_to_data = './data/set_conflicts/'
            
            num_subjects, num_rooms, num_conflict = configs[config_index]

            file_name = 'data_{}_{}_{}_({}).txt'.format(num_subjects, num_rooms, num_conflict, i)

            data = read_data(path_to_data + file_name)

            solution_str, status = cp(num_subjects=data["num_subjects"], num_rooms=data["num_rooms"], 
                                    nums_student_per_subject=data["num_students_per_subject"],
                                    num_seats_per_room=data["num_seats_per_room"], subject_pairs=data["conflicts"],
                                    time_limit=time_limit)

            if solution_str is not None: 
                output_path = "solution/cp/set_conflict/" + file_name[:-4] + "_solution.csv"

                with open(output_path, 'w') as f:
                    f.write(solution_str)
        
                end_time = time.time()
                
            elif solution_str == 'Time Limit':
                end_time = start_time + time_limit + 120
            else:
                end_time = None
            
            aggregate_path = "solution/aggregate.csv"
            
            with open(aggregate_path, 'a') as f:
                if end_time is None:
                    f.write("cp," + file_name + "," + str(num_subjects) + "," + 
                            str(num_rooms) + "," + str(num_conflict) + "," + 
                            str(run) + "," + str(start_time) + "," + 
                            "," + str(time_limit) + ',' + str(status) + "\n")
                else:
                    f.write("cp," + file_name + "," + str(num_subjects) + "," + 
                            str(num_rooms) + "," + str(num_conflict) + "," + 
                            str(run) + "," + str(start_time) + "," + str(end_time) + 
                            "," + str(end_time - start_time) + ',' + str(status) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--num_run_per_data', type=int, default=5, help="number of run per data")
    parser.add_argument('-c','--config_index', type=int, default=0, help="index of config for data")
    parser.add_argument('-t','--time_limit', type=int, default=600, help="time limit for each run")
    
    args = parser.parse_args()
    
    test_phase(num_run_per_data=args.num_run_per_data, 
               config_index=args.config_index,
               time_limit=args.time_limit)    
       
            