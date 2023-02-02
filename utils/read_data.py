
import os

def read_data(file_name):

    data = {}

    with open(file_name, 'r') as f:
        if f == None:
            print('File not found')
            return None
                
        data["num_subjects"] = int(f.readline())
        data["num_students_per_subject"] = [int(x) for x in f.readline().split()]
        data["num_rooms"] = int(f.readline())
        data["num_seats_per_room"] = [int(x) for x in f.readline().split()]
        data["num_pairs"] = int(f.readline())
        data["conflicts"] = []
        for i in range (data["num_pairs"]):
            s1, s2 = [int(x) for x in f.readline().split()]
            data["conflicts"].append((s1, s2))
        
    return data