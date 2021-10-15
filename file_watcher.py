
import os
import pickle
import sys
import subprocess

def add_files_to_watch(original_files_to_watch, new_files_to_add):
    #Add files to watch
    original_files_to_watch.extend(new_files_to_add)
    return original_files_to_watch


def get_files_path_from_folder(dir_path, extension=""):
    #Get a folder and returns the files recursively
    #Always gets full path
    file_list = []

    if extension == "":
        # r=root, d=directories, f = files
        for r, d, f in os.walk(dir_path):
            for file in f:
                file_list.append(os.path.join(r, file))
    else:
        # r=root, d=directories, f = files
        for r, d, f in os.walk(dir_path):
            for file in f:
                if file.endswith(extension):
                    file_list.append(os.path.join(r, file))

    return file_list


def get_modification_time(file_list):
    original_info_files_list = []
    for f in file_list:
        original_info_files_list.append({'filepath': f, 'tc':os.path.getmtime(f)})
    return original_info_files_list
    
def store_original_data(original_info_files_list, file="watch"):
    with open(file, "wb") as f:
        pickle.dump(original_info_files_list, f)

def read_original_data(file="watch"):
    with open(file, "rb") as f:
        store_data = pickle.load(f)

    return store_data

def delete_duplicates(file_list=[]):
    return list(dict.fromkeys(file_list))

def get_files_from_path_and_add_to_the_list(path, original_list=[], extension=""):
    file_list = []
    if os.path.isdir(path):
        file_list = get_files_path_from_folder(path, extension="")
        original_list = add_files_to_watch(original_list, file_list)

    elif os.path.isfile(path):
        file_extension = os.path.splitext(path)
        if file_extension == extension:
            original_list.extend(path)

    return original_list

def integrity_check_files(original_files_list, restored_files_list):
    #Iterate for each element and check if it exists and its TC.
    diff_list = []
    restored_files_list_copy = restored_files_list.copy()
    is_founded = False

    #Iterates the original file list
    for d_original in original_files_list:
        f_original = d_original["filepath"]
        tc_original = d_original["tc"]
        #Iterates the restored files list to look for matches
        for d_restored in restored_files_list:
            f_restored = d_restored["filepath"]
            tc_restored = d_restored["tc"]
            #if filepath original is the same as restored, check the timecode
            if f_original == f_restored:
                is_founded = True
                #if timecode is the same, the status is unmodified, else, is modified
                if tc_original != tc_restored:
                    diff_list.append({"filepath": f_original, "status":"modified"})
                else:
                    pass
                    #diff_list.append({"filepath": f_original, "status":"unmodified"})
                restored_files_list_copy.remove(d_restored)
                break
                
            
            #delete itmes from the copy list, if any left at the end, it is a new item
            

        if not is_founded:
            #if we have search the whole list and no matches, the file has been deleted.
            diff_list.append({"filepath": f_original, "status":"deleted"})
        else:
            #diff_list.append({"filepath": f_restored, "status":"new"})
            is_founded = False

    
    #if there are files in the restored list after searching the whole original list, we mark them as new
    if len(restored_files_list_copy) > 0:
        for d_restored in restored_files_list_copy:
            f_restored = d_restored["filepath"]
            diff_list.append({"filepath": f_restored, "status":"new"})

    return diff_list

def read_paths_from_file(file):
    path_list = []
    with open(file, "r") as f:
        for line in f:
            path_list.append(line.rstrip())
    return path_list

def get_all_paths_from_list(path_list):
    complete_list=[]
    for path in path_list:
        complete_list = get_files_from_path_and_add_to_the_list(path)
    return complete_list

def write_mismatches(path_list, file_to_write):
    with open(file_to_write, "w") as f:
        for item in path_list:
            f.write("%s\n" % item)

def check_paths(path_list):
    #Check if every path is valid.
    #Returns the usable path list. We can
    usable_paths = []
    unusable_paths = []
    for path in path_list:
        if os.path.exists(path):
            usable_paths.append(path)
        else:
            unusable_paths.append(path)
    if len(usable_paths) == 0:
        print(f"No valid paths found in {path_list}")
        print("Aborting...")
        exit()

    return usable_paths, unusable_paths


def retrieve(file_path):
    #Executes all the functions to retrieve the watch files
    paths = read_paths_from_file(file_path)
    paths, _ = check_paths(paths)
    paths = get_all_paths_from_list(paths)
    paths = delete_duplicates(paths)
    paths = get_modification_time(paths)
    store_original_data(paths)
    #print(len(paths)) #Debug
    return paths

def pull(workspace_path, thisdir):
    #cd_answer = subprocess.run(["cd", workspace_path])
    os.chdir(workspace_path)#Change to workspace dir
    #cm update --last to pull changes from workspace. We have to be in the workspace directory and no pending changes
    pull_answer = subprocess.run(["cm", "update", "--last"])
    if pull_answer.returncode != 0:
        print("The exit code was: %d" % pull_answer.returncode)
        print(f"Error while pulling the workspace {workspace_path}. Please make sure you don't have any pending changes.")
        print("Aborting...")
        exit()
    os.chdir(thisdir) #Change the location of the folder containing this file again

def diff(original_file_path, old_paths, mismatched_file_path, thisdir):

    #original_paths = read_original_data()
    new_paths = read_paths_from_file(original_file_path)
    new_paths, unsusable_paths = check_paths(new_paths)
    new_paths = get_all_paths_from_list(new_paths)
    new_paths = delete_duplicates(new_paths)
    new_paths = get_modification_time(new_paths)

    result = integrity_check_files(old_paths, new_paths)
    save_logs(old_paths, new_paths, thisdir)
    if len(result) == 0:
        print("No diferences found.")
        
    else:
        write_mismatches(result, mismatched_file_path)
        os.startfile(mismatched_file_path)
        print(f"Differences stored in {mismatched_file_path}.")

def save_logs(old_paths, new_paths, thisdir):
    old_log = os.path.join(thisdir, "logs", "old_paths.txt")
    new_log = os.path.join(thisdir, "logs", "new_paths.txt")

    with open(old_log, "w") as f:
        for item in old_paths:
            f.write("%s\n" % item)
    
    with open(new_log, "w") as f:
        for item in new_paths:
            f.write("%s\n" % item)

def get_workspace(thisdir):
    workspace_path = os.path.join(thisdir, "config", "workspace_path.txt")
    with open(workspace_path, "r") as f:
        for line in f:
            return line.rstrip()


    
if __name__ == "__main__":

    #Ini variables
    thisdir = os.path.dirname(__file__) #Get location of the folder containing this file
    os.chdir(thisdir) #Change to the location of this file
    thisdir_data = os.path.join(thisdir, "data")#Get the data path location
    original_file_path = os.path.join(thisdir_data, "paths.txt")#Get the path location
    workspace_path = get_workspace(thisdir_data) #Gets the workspace stored in .\config\workspace_path.txt
    mismatched_file_path = os.path.join(thisdir_data, "mismatched.txt")

    #Call functions
    print(20*"-"+"FileChecker"+20*"-")
    print("Retreiving paths...")
    paths_retrieved = retrieve(original_file_path)#Get the paths for the watch paths
    print(f"{len(paths_retrieved)} paths retreieved.")
    print("Commencing pull operation...")
    pull(workspace_path, thisdir)#Pull the workspace
    print("Computing differences...")
    diff(original_file_path, paths_retrieved, mismatched_file_path, thisdir)
    print("Finished")