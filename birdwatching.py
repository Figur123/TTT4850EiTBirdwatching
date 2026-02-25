import numpy as np
import matplotlib.pyplot as plt
import pathlib

class BirdAnalyzer:
    #overweiv of file structure
    sections = np.array(["Selection","View","Channel","Begin Time (s)","End Time (s)","Low Freq (Hz)","High Freq (Hz)","Common Name","Species Code","Confidence","Begin Path","File Offset (s)"])
    
    #file location
    date = "20260205"
    underscore = "_"
    time = "120000"
    wav = ".BirdNET.selection.table.txt"
    prepath = "sounds/testresult/"

    #for end plot
    species = np.array([])
    species_subcount = np.array([])
    species_total_count = np.array([])

    def __init__(self):
        return 0
    
    def __str__(self):
        return f""
    
    def advance_one_hour(self):
        time = str(int(time) + 10000)
        #turn day
        if (self.time == "240000"):
            self.time = "000000"
            self.date = str(int(date)+1)
    
    def analyze_file(self):
        return 0


sections = np.array(["Selection","View","Channel","Begin Time (s)","End Time (s)","Low Freq (Hz)","High Freq (Hz)","Common Name","Species Code","Confidence","Begin Path","File Offset (s)"])
species = np.array([])
species_count = np.zeros([])
species_total_count = np.array([])

count_over_time = np.array([[]])

indexes_of_largest = np.array([])
most_common_species = np.array([])
most_common_species_count = np.array([])

#used for looping trough filepaths
date = "20260205"
underscore = "_"
time = "120000"
wav = ".BirdNET.selection.table.txt"
prepath = "sounds/testresult/"
filename = prepath + date + underscore + time + wav

file_path = pathlib.Path(filename)



while file_path.is_file():
    while file_path.is_file():
        with open(filename, 'r') as txt_file:
            print("reading: " + filename)
            for line in txt_file:
                observation = np.array(line.split('\t'))
                #print(observation)
                current_species = observation[np.where(sections == "Common Name")]
                #print(current_species)
                if (current_species not in species):
                    species = np.append(species, current_species)
                    species_count = np.append(species_count, 0)
                species_count[np.where(species == current_species)] += 1

            #species_count.fill(0)

            #print(txt_file.readline())
            #print(txt_file.readline())
        time = str(int(time) + 10000)
        filename = prepath + date + underscore + time + wav
        file_path = pathlib.Path(filename)
    
    
    time = str("000000")
    date = str(int(date) + 1)
    filename = prepath + date + underscore + time + wav
    file_path = pathlib.Path(filename)

#need to take away headline from species list

species = species[1:]
species_count = species_count[1:]

#sort by occurance
index_sorted_by_size = np.argsort(species_count)
print("len of speciescount ... = ", len(species_count))
print("len of index ... = ", len(index_sorted_by_size))
print("len of species.. = ", len(species))
sorted_species = species[index_sorted_by_size]

#getting index of 10 largest populations
indexes_of_largest = index_sorted_by_size[-10:]
most_common_species = species[indexes_of_largest]
most_common_species_count = species_count[indexes_of_largest]

print(most_common_species)
print(most_common_species_count)

analyzer = BirdAnalyzer()
print(analyzer.time)
analyzer.advance_one_hour()
print(analyzer.time) 

#print(species)
#print(species_count)
    