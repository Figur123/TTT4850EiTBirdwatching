import numpy as np
import matplotlib.pyplot as plt
import pathlib

class BirdAnalyzer:
    def __init__(self):
        #overweiv of file structure
        self.sections = np.array(["Selection","View","Channel","Begin Time (s)","End Time (s)","Low Freq (Hz)","High Freq (Hz)","Common Name","Species Code","Confidence","Begin Path","File Offset (s)"])
    
        #file location
        self.date = "20260205"
        self.underscore = "_"
        self.time = "000000"
        self.wav = ".BirdNET.selection.table.txt"
        self.color = "white"
        self.slash = "/"
        self.color_number = "1"
        self.prepath = "result/"
        self.filename = self.prepath + self.color + self.slash + self.color + self.color_number + self.slash + self.date + self.slash + self.date + self.underscore + self.time + self.wav
        self.valid_filename = False

        #for end plot
        #sorted by species
        self.species_sub = np.array([])
        self.species_day = np.array([])
        self.species_total = np.array([])
        self.species_sub_count = np.array([])
        self.species_day_count = np.array([])
        self.species_total_count = np.array([])

        #only activity sorted by ourly time
        self.activity_during_day = np.zeros(24)#for all hours of the day
        self.activity_over_time = np.zeros(24)#2D matrix time horizontaly and day vertical
        
    
    def __str__(self):
        return f""
    
    def update_filename(self):
        self.filename = self.prepath + self.color + self.slash + self.color + self.color_number + self.slash + self.date + self.slash + self.date + self.underscore + self.time + self.wav

    def advance_one_recording(self): 
        file_exist_in_path = False   
        #advance more if file was corrupt and could not be analyzed
        while (not file_exist_in_path):
            
            if self.time == "-1":
                self.time = "00001"

            #handles stupid first syntax
            elif (self.time == "000001"):
                self.time = "00000"
        
            else:
                self.time = str(int(self.time) + 10000)

            #give the pre '0'
            if (int(self.time) < 100000):
                self.time = '0' + self.time

            #turn day
            if (int(self.time) >= 240000):
                self.time = "-1"
                self.date = str(int(self.date)+1)

            self.update_filename()
            file_path = pathlib.Path(self.filename)
            file_exist_in_path = file_path.is_file()

            if int(self.date[-2:]) >= 21:#last two digits in date var
                print("this file return False")
                self.valid_filename = False
                return False #return False when there are no more in the given color
            
        self.update_filename()
        self.valid_filename = True
        return True #return true if recording was found
    
    def advance_color(self):
        self.color_number = str(int(self.color_number) + 1)
        self.time = "-1"
        self.date = "20260205"

        if int(self.color_number) >= 5:
            if self.color == "red":
                return False # done advancing color
            
            self.color = "red"
            self.color_number = '1'
        
        print("swithching to: ", self.color, self.color_number)
        self.update_filename()
        return True


    def analyze_file(self):
        with open(self.filename, 'r') as txt_file:
            print("reading: " + self.filename)
            for line in txt_file:
                observation = np.array(line.split('\t'))
                current_species = observation[np.where(self.sections == "Common Name")]

                if (current_species not in self.species_sub):
                    self.species_sub = np.append(self.species_sub, current_species)
                    self.species_sub_count = np.append(self.species_sub_count, 0)

                    if (current_species not in self.species_day):
                        self.species_day = np.append(self.species_day, current_species)
                        self.species_day_count = np.append(self.species_day_count, 0)

                        if (current_species not in self.species_total):
                            self.species_total = np.append(self.species_total, current_species)
                            self.species_total_count = np.append(self.species_total_count, 0)

                self.species_sub_count[np.where(self.species_sub_count == current_species)] += 1
                self.species_day_count[np.where(self.species_day == current_species)] += 1
                self.species_total_count[np.where(self.species_total == current_species)] += 1
                
                #store activity data
                time_index = int(self.time) // 10000 #should give index from 0 to 23
                self.activity_during_day[time_index] = np.sum(self.species_sub_count)

                if time_index == 23:
                    self.activity_over_time = np.vstack(self.activity_over_time, self.activity_during_day)
                    
                

            #species_count.fill(0)

            #print(txt_file.readline())
            #print(txt_file.readline())
        return 0


analyzer = BirdAnalyzer()
print("path is: ", analyzer.filename)

colorBool = True
dateBool = True
while colorBool:
    while dateBool:
        dateBool = analyzer.advance_one_recording()
        print("path is: ", analyzer.filename)
    colorBool = analyzer.advance_color()
    dateBool = True


