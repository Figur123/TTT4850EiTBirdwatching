import numpy as np
import matplotlib.pyplot as plt
import pathlib
from mpl_toolkits import mplot3d


class BirdAnalyzer:
    def __init__(self, color = "white", color_num = "1"):
        #overweiv of file structure
        self.sections = np.array(["Selection","View","Channel","Begin Time (s)","End Time (s)","Low Freq (Hz)","High Freq (Hz)","Common Name","Species Code","Confidence","Begin Path","File Offset (s)"])
    
        #file location
        self.date = "20260205"
        self.underscore = "_"
        self.time = "000000"
        self.wav = ".BirdNET.selection.table.txt"
        self.color = color
        self.slash = "/"
        self.color_number = color_num
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

        #only activity sorted by hourly time
        self.activity_during_day = np.zeros(24)#for all hours of the day
        self.activity_over_time = np.empty((0, 24), dtype=float)#2D matrix time horizontaly and day vertical
        self.correspondig_color = np.array([])
        self.correspondig_day = np.array([])
        
        self.hour_axis = np.array([])
        self.day_axis = np.array([])
        
    def erase_dummy_data(self):
        pass

    def __str__(self):
        """
        index = np.argsort(self.species_total)
        sorted_species = self.species_total[index]
        sorted_count = self.species_total_count[index]

        string = "spesies total: \n" + str(sorted_species) + "\n"
        string = string + "spesies total count" + str(sorted_count) + "\n"
        """
        string = np.str_(self.activity_over_time)

        return string
    


    def plot_over_time(self, color):
        title = self.color + self.color_number
        xlabel = "time 24 h clock"
        ylabel = "date in feb"
        zlabel = "number of birdsounds"

        savepath = "../figures/" + title +".png"

        times = np.arange(24)#for all hours of the day
        dates = self.correspondig_day
        TIMES, DATES = np.meshgrid(times, dates)
        activities = self.activity_over_time
        
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        
        ax.plot_surface(TIMES, DATES, activities, cmap='viridis', edgecolor=color)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)

        ax.view_init(elev=10, azim=10)#look directly at y
        plt.savefig(savepath)
        #plt.show()
        return 0

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

                #logic for datastorage clear temporary storage
                self.species_day_count = np.array([])
                self.species_day = np.array([])

                #store data to be stored
                self.store_data()

            #more logic
            self.species_sub = np.array([])
            self.species_sub_count = np.array([])

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
        
        #print("swithching to: ", self.color, self.color_number)
        self.update_filename()
        return True

    def analyze_file(self):
        with open(self.filename, 'r') as txt_file:
            #print("reading: " + self.filename)
            for line in txt_file:
                observation = np.array(line.split('\t'))
                current_species = observation[np.where(self.sections == "Common Name")][0]

                #see if current spesies need to be added to the different lists
                if (current_species not in self.species_sub):
                    self.species_sub = np.append(self.species_sub, current_species)
                    self.species_sub_count = np.append(self.species_sub_count, 0)

                    if (current_species not in self.species_day):
                        self.species_day = np.append(self.species_day, current_species)
                        self.species_day_count = np.append(self.species_day_count, 0)

                        if (current_species not in self.species_total):
                            self.species_total = np.append(self.species_total, current_species)
                            self.species_total_count = np.append(self.species_total_count, 0)
                
                #add to the count
                self.species_sub_count[np.where(self.species_sub == current_species)] += 1
                self.species_day_count[np.where(self.species_day == current_species)] += 1
                self.species_total_count[np.where(self.species_total == current_species)] += 1
                
        #store activity data
        time_index = int(self.time) // 10000 #should give index from 0 to 23
        self.activity_during_day[time_index] = np.sum(self.species_sub_count)

        return 0

    def analyze_color(self):
        dateBool = True
        while dateBool:
            dateBool = self.advance_one_recording()
            if dateBool:
                self.analyze_file()

    def store_data(self):#when microphones did not go to 23 
        #if one day is passed stack the result to activity over time 
        #print(self.activity_during_day)
        self.activity_over_time = np.vstack((self.activity_over_time, self.activity_during_day))
        section = self.color + str(self.color_number)
        self.correspondig_color = np.append(self.correspondig_color, section)
        self.correspondig_day = np.append(self.correspondig_day, float(self.date[-2:]))

        #clean some arrays
        self.activity_during_day = np.zeros(24)

white1_analyzer = BirdAnalyzer("white", "1")
white2_analyzer = BirdAnalyzer("white", "2")
white3_analyzer = BirdAnalyzer("white", "3")
white4_analyzer = BirdAnalyzer("white", "4")

red1_analyzer = BirdAnalyzer("red", "1")
red2_analyzer = BirdAnalyzer("red", "2")
red3_analyzer = BirdAnalyzer("red", "3")
red4_analyzer = BirdAnalyzer("red", "4")

white1_analyzer.analyze_color()
white2_analyzer.analyze_color()
white3_analyzer.analyze_color()
white4_analyzer.analyze_color()

red1_analyzer.analyze_color()
red2_analyzer.analyze_color()
red3_analyzer.analyze_color()
red4_analyzer.analyze_color()

#white2_analyzer.analyze_color()
#white3_analyzer.analyze_color()
#white4_analyzer.analyze_color()

#white1_analyzer.erase_dummy_data()

#print(white1_analyzer.correspondig_day)
#print(white1_analyzer.activity_over_time)


plot_colors = np.array([
            "#f7f7f7",
            "#d9d9d9",
            "#bdbdbd",
            "#969696",
            "#fc9272",
            "#fb6a4a",
            "#de2d26",
            "#a50f15"
        ])

white1_analyzer.plot_over_time(plot_colors[0])
white2_analyzer.plot_over_time(plot_colors[1])
white3_analyzer.plot_over_time(plot_colors[2])
white4_analyzer.plot_over_time(plot_colors[3])

red1_analyzer.plot_over_time(plot_colors[4])
red2_analyzer.plot_over_time(plot_colors[5])
red3_analyzer.plot_over_time(plot_colors[6])
red4_analyzer.plot_over_time(plot_colors[7])


"""
colorBool = True
dateBool = True
while colorBool:
    while dateBool:
        dateBool = analyzer.advance_one_recording()
        if dateBool and colorBool:
            analyzer.analyze_file()
    colorBool = analyzer.advance_color()
    dateBool = True
"""
#analyzer.plot_over_time()



