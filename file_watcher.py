
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
            #if we have search the whole list and no matches, the file has been deleted
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
    unsuable_paths = []
    for path in path_list:
        if os.path.exists(path):
            usable_paths.append(path)
        else:
            unsuable_paths.append(path)
    if len(usable_paths) == 0:
        print(f"No valid paths found in {path_list}")
        print("Aborting...")
        exit()

    return usable_paths


def retrieve(file_path):
    #Executes all the functions to retrieve the watch files
    paths = read_paths_from_file(file_path)
    paths = get_all_paths_from_list(paths)
    paths = delete_duplicates(paths)
    paths = check_paths(paths)
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
    os.chdir(thisdir) #Change to the location
    thisdir_data = os.path.join(thisdir, "data")#Get the data path location
    original_file_path = os.path.join(thisdir_data, "paths.txt")#Get the path location
    workspace_path = get_workspace(thisdir_data)
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



#TESTING
else:
    #Ini variables
    thisdir = os.path.dirname(__file__) #Get location of the folder containing this file
    thisdir = os.path.join(thisdir, "TEST_FILES", "TEST")
    print(f"Dir: {thisdir}")

    original_values_unmodified =        [{'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\test.cfg', 'tc': 1619982465.8139253}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\appdirs.py', 'tc': 1619985506.5950322}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\cycler.py', 'tc': 1619985559.2153633}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\threadpoolctl.py', 'tc': 1619985476.1510704}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\typing_extensions.py', 'tc': 1619982495.90831}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\wavio.py', 'tc': 1619985371.3604882}]
    original_values_oneFileDeleted =    [{'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\testingFake.cfg', 'tc': 1619982465.8139253}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\test.cfg', 'tc': 1619982465.8139253}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\appdirs.py', 'tc': 1619985506.5950322}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\cycler.py', 'tc': 1619985559.2153633}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\threadpoolctl.py', 'tc': 1619985476.1510704}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\typing_extensions.py', 'tc': 1619982495.90831}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\wavio.py', 'tc': 1619985371.3604882}]
    original_values_oneFileNew =        [{'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\appdirs.py', 'tc': 1619985506.5950322}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\cycler.py', 'tc': 1619985559.2153633}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\threadpoolctl.py', 'tc': 1619985476.1510704}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\typing_extensions.py', 'tc': 1619982495.90831}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\wavio.py', 'tc': 1619985371.3604882}]
    original_values_oneFileModified =   [{'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\test.cfg', 'tc': 15}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\appdirs.py', 'tc': 1619985506.5950322}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\cycler.py', 'tc': 1619985559.2153633}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\threadpoolctl.py', 'tc': 1619985476.1510704}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\typing_extensions.py', 'tc': 1619982495.90831}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\wavio.py', 'tc': 1619985371.3604882}]



    #Unitests

    #Files with .py extension
    files_py_extension = get_files_path_from_folder(thisdir, "py") 
    print(f"Number of files with py extension={len(files_py_extension)}")#assert = 5

    #Files with .cfg extension
    files_cfg_extension = get_files_path_from_folder(thisdir, ".cfg") 
    print(f"Number of files with cfg extension={len(files_cfg_extension)}")#assert = 1

    #Files without extension
    files_no_extension = get_files_path_from_folder(thisdir) 
    print(f"Number of total files={len(files_no_extension)}")#assert = 6

    #Add files to the watcher
    files_to_watch = add_files_to_watch(files_py_extension, files_cfg_extension)
    print(f"Number of files with cfg and py extension={len(files_to_watch)}")#assert = 6


    #Get files from path
    files_no_extension = get_files_from_path_and_add_to_the_list(thisdir, original_list=[], extension="")
    print(f"Number of all files={len(files_no_extension)}")#assert = 6
    #duplicate some to test the method
    files_no_extension = get_files_from_path_and_add_to_the_list(thisdir, files_no_extension, extension="")
    print(f"Number of all files duplicated={len(files_no_extension)}")#assert = 12

    clean_files = delete_duplicates(files_no_extension)
    print(f"Number of all files cleaned={len(clean_files)}")#assert = 6

    #Get the time and path of the original ones
    original_file_values = get_modification_time(clean_files)

    #Store the info
    store_original_data(original_file_values, "debug")

    #Retreive the info
    restored_info = read_original_data("debug")
    print(f"Number of files read={len(restored_info)}")#assert = 6

    #Check if any has been modified
    result = integrity_check_files(original_values_unmodified, restored_info)
    print(f"Number of mismatches={len(result)}: {result}")#assert = 0

    result = integrity_check_files(original_values_oneFileDeleted, restored_info)
    print(f"Number of mismatches={len(result)}: {result}")#assert = 1 Deleted

    result = integrity_check_files(original_values_oneFileNew, restored_info)
    print(f"Number of mismatches={len(result)}: {result}")#assert = 1 New

    result = integrity_check_files(original_values_oneFileModified, restored_info)
    print(f"Number of mismatches={len(result)}: {result}")#assert = 1 Modified