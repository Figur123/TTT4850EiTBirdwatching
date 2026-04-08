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
        self.corresponding_color = np.array([])
        self.corresponding_day = np.array([])
        
        self.hour_axis = np.array([])
        self.day_axis = np.array([]) 

    def __str__(self):#does not to anything spesial just used to debug
        """
        index = np.argsort(self.species_total)
        sorted_species = self.species_total[index]
        sorted_count = self.species_total_count[index]

        string = "spesies total: \n" + str(sorted_species) + "\n"
        string = string + "spesies total count" + str(sorted_count) + "\n"
        """
        string = np.str_(self.activity_over_time)

        return string

    #makes a 3D plot with hour (24 hour clock) on x axis, date in february on y axis
    #and the occurance of birdsounds on z
    def plot_over_time(self, color):
        title = self.color + self.color_number
        xlabel = "time 24 h clock"
        ylabel = "date in feb"
        zlabel = "number of birdsounds"

        savepath = "figures/" + title +".png"

        times = np.arange(24)#for all hours of the day
        dates = self.corresponding_day
        TIMES, DATES = np.meshgrid(times, dates)
        activities = self.activity_over_time
        
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        
        ax.plot_surface(TIMES, DATES, activities, cmap='viridis', edgecolor=color)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)

        ax.set_zlim(0,175)#scaling all to same 

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
    
    def advance_color(self):#change current color+number to the next one
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

    def analyze_file(self): #analyses file and stores the data in internal vectors
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

    def analyze_color(self):# a shoortcut to analyse all files in one color
        dateBool = True
        while dateBool:
            dateBool = self.advance_one_recording()
            if dateBool:
                self.analyze_file()

    def store_data(self):#when microphones did not go to 23 
        self.activity_over_time = np.vstack((self.activity_over_time, self.activity_during_day))
        section = self.color + str(self.color_number)
        self.corresponding_color = np.append(self.corresponding_color, section)
        self.corresponding_day = np.append(self.corresponding_day, float(self.date[-2:]) - 1)#need to subtract as its added before function call

        #clean some arrays
        self.activity_during_day = np.zeros(24)

def create_plot():
    #2D plot
    fig2D = plt.figure()
    ax2D = plt.axes()
    
    return fig2D, ax2D

def plot_average(ax2D: plt.axes, B0: BirdAnalyzer,B1: BirdAnalyzer,B2: BirdAnalyzer,B3: BirdAnalyzer):
    B0.activity_over_time -= 2
    B1.activity_over_time -= 2
    B2.activity_over_time -= 2
    B3.activity_over_time -= 2

    days = np.empty((0, 24), dtype=float)
    
    #all activities are same length
    #calculate averages
    for v in range(len(B0.activity_over_time)):
        day = np.zeros(24)
        
        
        for h in range(len(B0.activity_over_time[0])):
            active_mics = 0
            local_sum = 0
            #check each mic
            if (B0.activity_over_time[v][h] != -2):
                active_mics += 1
                local_sum += B0.activity_over_time[v][h]
            if (B1.activity_over_time[v][h] != -2):
                active_mics += 1
                local_sum += B1.activity_over_time[v][h]
            if (B2.activity_over_time[v][h] != -2):
                active_mics += 1
                local_sum += B2.activity_over_time[v][h]
            if (B3.activity_over_time[v][h] != -2):
                active_mics += 1
                local_sum += B3.activity_over_time[v][h]
            
            
            #handle zero mics
            if active_mics == 0:
                day[h] = 0
            else:
                day[h] = local_sum / active_mics
        
        days = np.vstack((days, day))
        #print(days)

    times = np.arange(24)#for all hours of the day
    dates = B0.corresponding_day
    TIMES, DATES = np.meshgrid(times, dates)
    activities = days


    day_sums = np.array([np.sum(act) for act in activities])
    ax2D.plot(dates, day_sums, B0.color, linewidth = 4, label = B0.color + " mics")
    
    return 0

def save_plot(fig2D: plt.figure, ax2D: plt.axes):
    #plotting
    title = "average birdsounds on corresponding mic color"
    xlabel = "date in feb"
    ylabel = "average birdsounds"
    zlabel = "number of birdsounds"

    ax2D.set_facecolor('lightgray')
    ax2D.grid()
    ax2D.set_xlabel(xlabel)
    ax2D.set_ylabel(ylabel)
    fig2D.legend(facecolor = "darkgray", bbox_to_anchor = (0.9,0.8), loc = "center right", title = "color meaning")
    
    ax2D.set_title(title)

    savepath = "figures/" + "BothColors-2D" +".png"
    plt.savefig(savepath)
    return 0

#create the white analyzers
white1_analyzer = BirdAnalyzer("white", "1")
white2_analyzer = BirdAnalyzer("white", "2")
white3_analyzer = BirdAnalyzer("white", "3")
white4_analyzer = BirdAnalyzer("white", "4")

#create the red analyzers
red1_analyzer = BirdAnalyzer("red", "1")
red2_analyzer = BirdAnalyzer("red", "2")
red3_analyzer = BirdAnalyzer("red", "3")
red4_analyzer = BirdAnalyzer("red", "4")

#analyse white
white1_analyzer.analyze_color()
white2_analyzer.analyze_color()
white3_analyzer.analyze_color()
white4_analyzer.analyze_color()

#analyse red
red1_analyzer.analyze_color()
red2_analyzer.analyze_color()
red3_analyzer.analyze_color()
red4_analyzer.analyze_color()

#used for coloring the 3D plots
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
        
#white 3D plot
white1_analyzer.plot_over_time(plot_colors[0])
white2_analyzer.plot_over_time(plot_colors[1])
white3_analyzer.plot_over_time(plot_colors[2])
white4_analyzer.plot_over_time(plot_colors[3])

#red 3D plot
red1_analyzer.plot_over_time(plot_colors[4])
red2_analyzer.plot_over_time(plot_colors[5])
red3_analyzer.plot_over_time(plot_colors[6])
red4_analyzer.plot_over_time(plot_colors[7])

#2D collective -average plot
fig2D, ax2D = create_plot()
plot_average(ax2D, white1_analyzer, white2_analyzer, white3_analyzer, white4_analyzer)
plot_average(ax2D, red1_analyzer, red2_analyzer, red3_analyzer, red4_analyzer)
save_plot(fig2D, ax2D)




