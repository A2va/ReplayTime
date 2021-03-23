# Copyright (C) 2020  A2va

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import tkinter as tk
import tkinter.filedialog as filedialog
import zipfile
import os
import datetime
# ************************
# Alert Class
# ************************
class Alert(tk.Toplevel): 
      
    def __init__(self,title,message): 
          
        super().__init__() 
        self.title(title) 
        self.geometry("250x50")
        self.button=tk.Button(self,text="OK",command=lambda : self.destroy())
        self.label = tk.Label(self, text =message) 
        self.label.pack() 
        self.button.pack()

# ************************
# Replay Table Class
# ************************
class Replay_Table(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.canvas = tk.Canvas(self,bd=0,highlightthickness=0,width=250,height=250) 
        self.viewPort = tk.Frame(self.canvas)
        #ScrollBar
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) 
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y") 
        self.canvas.pack(side="left", fill="both", expand=True)                     
        self.canvas_window = self.canvas.create_window((0,0), window=self.viewPort, anchor="nw",tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                      

        self.onFrameConfigure(None)    

        self.column_1 =[]
        self.column_2 =[]
        self.column_3 =[]
    def onFrameConfigure(self, event):                                              
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))  
    #Delete Table
    def del_table(self, list):
        count=len(list)
        for i in range(count):
            list[i].grid_forget()
        list.clear()
    #Make table
    def make_table(self,number,name): 
        if number > len(self.column_1):
            for i in range(len(self.column_1),number):
                self.make_label(i+1, 0, 10,'',False,self.column_1)
                self.make_entry(i+1, 1, 10,'',True,self.column_2)
                self.make_label(i+1, 2,10,'',False,self.column_3)
        elif number < len(self.column_1):
            for i in range(len(self.column_1)-1,number-1,-1):
                self.column_1[i].grid_forget()
                self.column_2[i].grid_forget()
                self.column_3[i].grid_forget()
                self.column_1.pop()
                self.column_2.pop()
                self.column_3.pop()
        for i in range(number):
            self.column_1[i].config(text=name +' ' +str(i+1))
    #Make Entry
    def make_entry(self, row, column, width,text,state,list):
        e = tk.Entry(self.viewPort, width=width)
        if text: e.insert(0, text)
        e['state'] = tk.NORMAL if state else tk.DISABLED
        e.coords = (row-1, column)
        e.grid(row=row, column=column)
        list.append(e)
    #Make Label
    def make_label(self,row,column,width,text,state,list):
        l = tk.Label(self.viewPort,width=width,text=text)
        l.coords = (row-1, column)
        l.grid(row=row, column=column)
        list.append(l)
        
# ************************
# Replay UI Class
# ************************
class Replay_UI(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.table=Replay_Table(self)

        self.parent=parent
        self.json_export={
            "duration":0,
            "name":"",
            "list_replay":[""]
        }
        
        self.text_1=tk.StringVar()
        self.text_2=tk.StringVar()
        self.text_3=tk.StringVar()
        self.text_4=tk.StringVar()

        self.initUI()
    def initUI(self):
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        menubar.add_cascade(label="Open File", command=self.load)     
        menubar.add_cascade(label="Save File", command=self.save)
        menubar.add_cascade(label="Import ReplayMod File", command=self.load_replay_file)

        #Label
        self.name_Label=tk.Label(self,text="Timelapse Name:")
        self.number_Label=tk.Label(self,text="Number of Replay:")
        self.duration_Label = tk.Label(self,text="Duration:")
       
        #Entry
        self.name_Entry=tk.Entry(self, textvariable=self.text_1, width=10)
        self.number_Entry=tk.Entry(self, textvariable=self.text_2, width=10)
        self.duration_Entry = tk.Entry(self, textvariable=self.text_3,width=10)
    
        #Button
        self.generate_Button = tk.Button(self, text="Generate",command=self.generate_table)
        self.calculate_Button = tk.Button(self, text="Calculate",command=self.calculate)
       
        #Grid position
    
        self.name_Label.pack(side=tk.LEFT,anchor="nw")
        self.name_Entry.pack(side=tk.LEFT,anchor="nw")

        self.number_Label.pack(side=tk.LEFT,anchor="nw")
        self.number_Entry.pack(side=tk.LEFT,anchor="nw")

        self.generate_Button.pack(side=tk.LEFT,anchor="nw")
        self.duration_Label.pack(side=tk.LEFT,anchor="nw")
        self.duration_Entry.pack(side=tk.LEFT,anchor="nw")
        self.calculate_Button.pack(side=tk.LEFT,anchor="nw")
        self.table.pack()

    def save(self):
        fileSelection=filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("JSON files","*.json"),("All files","*.*")))
        if fileSelection !="":
            if fileSelection.find(".json") == -1:
                fileSelection +=  ".json"
            self.export_file(fileSelection)
    def load(self):
        fileSelection=filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("JSON files","*.json"),("All files","*.*")))
        self.import_file(fileSelection)
        self.calculate()
    def generate_table(self):
        try:
            number=int(self.number_Entry.get())
            name=self.name_Entry.get()
            self.table.make_table(number,name)
        except:
            Alert("Error","Expected Number in Replay Number")
    def load_replay_file(self):
        self.al=Alert("Information","Select the first replay of the list (Ex: Example_1)")
        self.al.button.bind("<Button-1>",self.import_replay_file)
    #Deserialization
    def import_replay_file(self,event=None):
        self.al.destroy()
        file=filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("ReplayMod files","*.mcpr"),("All files","*.*")))
        name=file[file.rfind('/')+1:].partition("1")[0]
        path_name=file[:file.rfind('/')]
        i=1
        replay_file=[]
        if(os.path.isfile(f'{path_name}/{name}1.mcpr')):
            while(1):
                if(os.path.isfile(f'{path_name}/{name}{i}.mcpr')):
                    file_zip=zipfile.ZipFile(f'{path_name}/{name}{i}.mcpr','r')
                    file=file_zip.open("metaData.json")
                    parsed_json=json.loads(file_zip.open("metaData.json").read())
                    replay_file.append(int(parsed_json["duration"]/1000))
                    i+=1
                else:
                    break
            
            self.clear_entry()
            
            self.table.make_table(len(replay_file),name)
            self.name_Entry.insert(0,name)
            self.number_Entry.insert(0,len(replay_file))

            for i in range(len(replay_file)):
                self.table.column_2[i].insert(0,self.second_to_string(replay_file[i]))
        else:
            Alert("Error","The first file is not selected (Ex: Example_1)")
            
    
    #Deserialization
    def import_file(self,path_name):
        #Clear the entry
        self.clear_entry()
        #Open the file
        file=open(path_name,"r")
        #Parse the file
        parsed_json=json.loads(file.read())
        file.close()
        #Get the name
        name=parsed_json["name"]
        self.name_Entry.insert(0,name)
        #Get the duration
        duration=parsed_json["duration"]
        self.duration_Entry.insert(0,duration)
        duration_list=parsed_json["list_replay"]
        #Get the number of replay
        number=len(duration_list)
        self.number_Entry.insert(0,number)

        if len(self.table.column_1) != number:
           self.table.make_table(number,name)
        #Insert the replay name
        for i in range(number):
            temp=name + ' ' + str(i+1)
            self.table.column_1[i].config(text=temp)
        #Insert the duration to the list
        for i in range(number):
            temp=duration_list[i]
            self.table.column_2[i].insert(0,temp)
    #Export
    def export_file(self,path_name):
        self.calculate()
        #Clear the list for export
        self.json_export["list_replay"].clear()
        #Store the name
        self.json_export["name"]=self.name_Entry.get()
        #Store the duration
        self.json_export["duration"]=self.duration_Entry.get()
        #Store the list duration
        for i in range(len(self.table.column_1)):
                self.json_export["list_replay"].append(self.table.column_2[i].get())

        #Open the file in write mode
        file=open(path_name,"w+")
        #Write to the file and close
        file.write(json.dumps(self.json_export))
        file.close()
    #Calculate
    def calculate(self):
        number_element =len(self.table.column_2)
        
        duration=0.0
        duration_list=[]
        duration_out=0.0
        temp=tk.StringVar()
        msg=0
        try:
            temp=self.duration_Entry.get()
            duration=self.string_to_second(temp)
        except:
            Alert("Error","Expected String like this hh:mm:ss in Duration")
        for i in range(number_element):
            try:
                temp=self.table.column_2[i].get()
                hour=self.string_to_second(temp)
            except:
                msg=1
            duration_list.append(hour)
        if msg==1:
            Alert("Error","Expected String like this hh:mm:ss in table")
        #Calculate the total duration
        ratio=duration/sum(duration_list)

        for i in range(number_element):
            duration_out=duration_list[i]*ratio
            temp=self.second_to_string(duration_out)
            self.table.column_3[i].config(text=temp)
    #String to Hour "hh:mm:ss" -> s
    def string_to_second(self,string):
        h, m, s = string.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    #Second to String s -> "hh:mm:ss"
    def second_to_string(self,second_in):
        return str(datetime.timedelta(seconds=second_in))

    def clear_entry(self):
        #Clear the entry
        self.name_Entry.delete(0, 'end')
        self.number_Entry.delete(0, 'end')
        self.duration_Entry.delete(0, 'end')
        self.table.del_table(self.table.column_1)
        self.table.del_table(self.table.column_2)
        self.table.del_table(self.table.column_3)

root=tk.Tk()

root.resizable(0, 0)
root.title("ReplayTime")
interface = Replay_UI(root)
interface.pack()
interface.mainloop()

interface.destroy()