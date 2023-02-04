import sys
import os
from ortools.linear_solver import pywraplp
import math
import time
import argparse

utils_path = os.path.join(os.getcwd())
sys.path.insert(1, utils_path)

from utils.read_data import read_data

STATUS_DICT = {
    pywraplp.Solver.OPTIMAL: "OPTIMAL",
    pywraplp.Solver.FEASIBLE: "FEASIBLE",
    pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
    pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
    pywraplp.Solver.ABNORMAL: "ABNORMAL",
    pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
}

def solve_with_mip(num_subjects: int, num_rooms: int, nums_student_per_subject: int, 
                   num_seats_per_room: int, subject_pairs: int,
                   num_sections_per_day: int = None, num_days: int = None, 
                   save_model: bool = False, time_limit: int = 600):
    
    if (not num_sections_per_day):
        num_sections_per_day = 4

    if (not num_days):
        num_days = math.ceil(num_subjects / num_sections_per_day)
        
    max_sum_sections = num_subjects
    
    # Create a new linear solver
    solver = pywraplp.Solver('Scheduling', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    x = {}

    for subject in range(num_subjects):
        for room in range(num_rooms):
            for section_id in range(max_sum_sections):
                x[(subject, room, section_id)] = solver.IntVar(0, 1, 'x[%i, %i, %i]' % (subject, room, section_id))
                
    y = solver.IntVar(0, max_sum_sections, 'y')
    
    # Constraints 1: Each subject must be assigned once
    for subject in range(num_subjects):
        temp = []
        
        for room in range(num_rooms):
            c = solver.Sum([x[(subject, room, section_id)] for section_id in range(max_sum_sections)])
            temp.append(c)
        
        solver.Add(solver.Sum(temp) == 1)        
        
    # Constraints 2: Each room must have most one subject in each section
    for room in range(num_rooms):
        for section_id in range(max_sum_sections):
            solver.Add(solver.Sum([x[(subject, room, section_id)] 
                                   for subject in range(num_subjects)]) <= 1)

    # Constraints 3: Each subject assigned to a room must have enough seats
    for subject in range(num_subjects):
        for room in range(num_rooms):
            solver.Add(solver.Sum([x[(subject, room, section_id)] * nums_student_per_subject[subject] 
                                   for section_id in range(max_sum_sections)]) <= num_seats_per_room[room])
    
    # Constraints 4: Two subjects cannot be assigned to the same room in the same section
    for section_id in range(max_sum_sections):
        for subject1, subject2 in subject_pairs:
            solver.Add(solver.Sum([x[(subject1, room, section_id)] + x[(subject2, room, section_id)]
                                   for room in range(num_rooms)]) <= 1)

    # Constraints 5: Minimize the number of sections
    for subject in range(num_subjects):
        for room in range(num_rooms):
            for section_id in range(max_sum_sections):
                solver.Add(y >= x[(subject, room, section_id)] * section_id)
    
    # Set time limit
    solver.set_time_limit(time_limit * 1000)

    # Objective function
    solver.Minimize(y)
    
    if save_model:
        with open('mip.mps', 'w') as f:
            f.write(solver.ExportModelAsMpsFormat(False, False))
    
    # Solve the problem
    status = solver.Solve()
    
    print("Status = ", STATUS_DICT[status] , end='\n')
    
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        solution = []
    
        print('Objective value =', solver.Objective().Value())
        for subject in range(num_subjects):
            for room in range(num_rooms):
                for section_id in range(max_sum_sections):
                    if x[(subject, room, section_id)].solution_value() > 0:
                        print('Subject %i is assigned to room %i in section %i' % (subject, room, section_id))
                        
                        solution.append((subject, room, section_id // num_sections_per_day, section_id % num_sections_per_day))
        
        solution.sort(key=lambda x: x[2] * num_sections_per_day + x[3])
        
        solution_str = ''        
        solution_str += "subjects,number_student,rooms,num_seat,day,section" + "\n"
        for subjects, room, day, section in solution:
            solution_str += str(subjects) + "," + str(nums_student_per_subject[subjects]) + "," + str(room) + "," + \
                str(num_seats_per_room[room]) + "," + str(day) + "," + str(section) + "\n"

        return (solution_str, status)
    elif status == pywraplp.Solver.NOT_SOLVED:
        print('Time Limit')
        return ('Time Limit', status)
    
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

            solution_str, status = solve_with_mip(num_subjects=data["num_subjects"], num_rooms=data["num_rooms"], 
                                    nums_student_per_subject=data["num_students_per_subject"],
                                    num_seats_per_room=data["num_seats_per_room"], subject_pairs=data["conflicts"],
                                    time_limit=time_limit)

            if solution_str is not None: 
                output_path = "solution/mip/set_conflict/" + file_name[:-4] + "_solution.csv"

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
                    f.write("mip," + file_name + "," + str(num_subjects) + "," + 
                            str(num_rooms) + "," + str(num_conflict) + "," + 
                            str(run) + "," + str(start_time) + "," + 
                            "," + str(time_limit) + ',' + str(status) + "\n")
                else:
                    f.write("mip," + file_name + "," + str(num_subjects) + "," + 
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
