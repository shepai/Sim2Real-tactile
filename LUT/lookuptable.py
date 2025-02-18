import numpy as np
import random
import string
import pandas as pd
from scipy.spatial import cKDTree
def generate_random_key(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))
example_data=np.zeros((1000,))

class TABLE:
    def __init__(self):
        self.frictions=[]
        self.maps={}
    def insert_class(self,val): #insert a riction where it should be
        inserted=False
        i=0
        new_key=generate_random_key()
        while i<len(self.frictions) and not inserted:
            current_entry=self.frictions[i]
            if current_entry[0]>val:
                self.frictions.insert(i-1,[val,new_key])
                inserted=True
            i+=1
        if not inserted: self.frictions.append([val,new_key])
        return new_key
    def add_dataset_to_table(self,file,y,dirs,pressures,num_pressures): #add a dataset with given parameters into the right place in the lookup table
        unique_keys=np.unique(y)
        time=file.shape[1]
        w=file.shape[2]
        h=file.shape[3]
        try: c=file.shape[4]
        except: pass
        for i in range(len(unique_keys)): #gather all the classes and insert
            key=unique_keys[i]
            #find insertion point
            new_key=self.insert_class(key)
            un_dirs_x=np.unique(dirs[:,0])
            un_dirs_y=np.unique(dirs[:,1])
            try: self.maps[new_key]=np.zeros((len(un_dirs_x),len(un_dirs_y),time,num_pressures,w,h,c),dtype=np.uint8) #create 3d space
            except: self.maps[new_key]=np.zeros((len(un_dirs_x),len(un_dirs_y),time,num_pressures,w,h),dtype=np.uint8) #create 3d space
            #loop through data
            for j in range(len(file)):
                direction=dirs[j]
                for t in range(time):
                    self.maps[new_key][direction[0]][direction[1]][t][pressures[j]]=file[j][t]
        #print("Zeros:",np.where(self.maps[new_key]==0))

    def get_map(self,val): #search for friction
        found=False
        i=0
        while not found and i<len(self.frictions):
            if self.frictions[i][0]==val:
                return self.frictions[i][1]
            i+=1
        raise FileNotFoundError
    def find_nearest(self,map,dirs,time,pressure,i=0): #find the nereates image in the lookup table
        print("DEPTH",i )
        if dirs[0]>=self.maps[map].shape[0]: dirs[0]=self.maps[map].shape[0]-1
        if dirs[1]>=self.maps[map].shape[1]: dirs[1]=self.maps[map].shape[1]-1
        if time>=self.maps[map].shape[2]:time=self.maps[map].shape[2]-1
        if np.sum(self.maps[map][dirs[0]][dirs[1]][time][pressure])==0:
            dirs[0]-=1
            image=self.find_nearest(map,dirs,time,pressure,i=i+1)
            if type(image)==type(None): 
                dirs[0]+=2
                image=self.find_nearest(map,dirs,time,pressure,i=i+1)
                if type(image)==type(None): 
                    dirs[1]-=1
                    dirs[1]-=1
                    image=self.find_nearest(map,dirs,time,pressure,i=i+1)
                    if type(image)==type(None): 
                        dirs[1]+=2
                        image=self.find_nearest(map,dirs,time,pressure,i=i+1)
                        if type(image)==type(None): 
                            time = time-1 if time>0 else time+1
                            image=self.find_nearest(map,dirs,time,pressure,i=i+1)
            if type(image)==type(None): return None
        return self.maps[map][dirs[0]][dirs[1]][time][pressure]
    def look_up(self,friction,dirs=None,pressure=None,time=None):
        if type(dirs)==type(None) and type(dirs)==type(None) and type(dirs)==type(None):
            raise LookupError("You need a variable to search for something")
        map=self.get_map(friction)
        if time>self.maps[map].shape[2]: time=99
        nearest_image=self.find_nearest(map,dirs,time,pressure)
        return nearest_image



class LookupTable:
    def __init__(self):
        self.data = pd.DataFrame(columns=["friction", "dir_x", "dir_y", "time", "pressure", "image"])

    def add_entry(self, friction, direction, time, pressure, image):
        entry = {
            "friction": friction,
            "dir_x": direction[0],
            "dir_y": direction[1],
            "time": time,
            "pressure": pressure,
            "image": image
        }
        self.data = pd.concat([self.data, pd.DataFrame([entry])], ignore_index=True)

    def find_exact(self, friction, direction, time, pressure):
        """Exact match lookup."""
        match = self.data[
            (self.data["friction"] == friction) &
            (self.data["dir_x"] == direction[0]) &
            (self.data["dir_y"] == direction[1]) &
            (self.data["time"] == time) &
            (self.data["pressure"] == pressure)
        ]
        if not match.empty:
            return match.iloc[0]["image"]
        return None

    def find_nearest(self, friction, direction, time, pressure):
        """Nearest neighbor search using KDTree."""
        # Construct the KDTree for fast nearest search
        feature_space = self.data[["friction", "dir_x", "dir_y", "time", "pressure"]].to_numpy()
        tree = cKDTree(feature_space)
        
        query_point = np.array([friction, direction[0], direction[1], time, pressure])
        dist, idx = tree.query(query_point)
        
        return self.data.iloc[idx]["image"]

    def lookup(self, friction, direction, time, pressure):
        image = self.find_exact(friction, direction, time, pressure)
        if image is not None:
            return image
        return self.find_nearest(friction, direction, time, pressure)
    

if __name__ == "__main__":
    table = LookupTable()

    # Add entries
    image_sample = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    table.add_entry(0.15, (1, 0), 5, 3, image_sample)

    # Exact lookup
    result = table.lookup(0.15, (1, 0), 5, 3)
    print("Found image shape:", result.shape)

    # Nearest lookup (if exact match is missing)
    result = table.lookup(0.20, (0, 0), 4, 2)
    print("Nearest image shape:", result.shape)