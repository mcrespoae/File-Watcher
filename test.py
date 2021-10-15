    
import unittest
from file_watcher import *


#Ini variables
thisdir = os.path.dirname(__file__) #Get location of the folder containing this file
testdir = os.path.join(thisdir, "TEST_FILES")
thisdir = os.path.join(testdir,"TEST")
debug_file = os.path.join(testdir, "debug")

#Unitests
class UnitTestGetFiles(unittest.TestCase):
    def py_files(self):
        #Files with .py extension
        files_py_extension = get_files_path_from_folder(thisdir, "py") 
        self.assertEqual(len(files_py_extension), 5)
    
    def cfg_files(self):
        #Files with .cfg extension
        files_cfg_extension = get_files_path_from_folder(thisdir, ".cfg") 
        self.assertEqual(len(files_cfg_extension), 1)

    def no_extension_files(self):
        files_no_extension = get_files_path_from_folder(thisdir)
        self.assertEqual(len(files_no_extension), 6)

    def add_files_to_watcher(self):
        files_py_extension = get_files_path_from_folder(thisdir, "py")
        files_cfg_extension = get_files_path_from_folder(thisdir, ".cfg") 
        files_to_watch = add_files_to_watch(files_py_extension, files_cfg_extension)
        self.assertEqual(len(files_to_watch), 6)

    def get_files_from_path(self):
        #Get files from path
        files_no_extension = get_files_from_path_and_add_to_the_list(thisdir, original_list=[], extension="")
        self.assertEqual(len(files_no_extension), 6)

class TestDuplicates(unittest.TestCase):
    def test_get_duplicates(self):
        files_no_extension = get_files_path_from_folder(thisdir)
        files_duplicate = get_files_from_path_and_add_to_the_list(thisdir, files_no_extension, extension="")
        self.assertEqual(len(files_duplicate), 12)

    def test_delete_duplicates(self):
        files_no_extension = get_files_path_from_folder(thisdir)
        files_no_extension = get_files_from_path_and_add_to_the_list(thisdir, files_no_extension, extension="")
        clean_files = delete_duplicates(files_no_extension)
        self.assertEqual(len(clean_files), 6)

class TestModificationTime(unittest.TestCase):
    def test_get_modification_time_write_and_read(self):
        #Get the time and path of the original ones
        files_no_extension = get_files_path_from_folder(thisdir)
        original_file_values = get_modification_time(files_no_extension)
        #Store the info
        store_original_data(original_file_values, debug_file)
        #Retreive the info
        restored_info = read_original_data(debug_file)
        self.assertEqual(len(restored_info), 6)

class TestIntegrityCheck(unittest.TestCase):    
    def test_integrity_check_files_zero_diff(self):
        #Get the time and path of the original ones
        files_no_extension = get_files_path_from_folder(thisdir)
        original_file_values = get_modification_time(files_no_extension)
        #Store the info
        store_original_data(original_file_values, debug_file)
        #Retreive the info
        restored_info = read_original_data(debug_file)
        #Check if any has been modified
        result = integrity_check_files(original_file_values, restored_info)
        self.assertEqual(len(result), 0)

    def test_integrity_check_files_one_deleted(self):
        #Get the time and path of the original ones
        files_no_extension = get_files_path_from_folder(thisdir)
        original_file_values = get_modification_time(files_no_extension)
        #Store the info
        store_original_data(original_file_values, debug_file)
        #Retreive the info
        restored_info = read_original_data(debug_file)
        #Delete last entry
        del restored_info[-1]
        #Check if any has been modified
        result = integrity_check_files(original_file_values, restored_info)
        self.assertEqual(len(result), 1)
    
    def test_integrity_check_files_one_new(self):
        #Get the time and path of the original ones
        files_no_extension = get_files_path_from_folder(thisdir)
        original_file_values = get_modification_time(files_no_extension)
        #Store the info
        store_original_data(original_file_values, debug_file)
        #Retreive the info
        restored_info = read_original_data(debug_file)
        #Add a new entry
        restored_info.append(restored_info[-1])
        #Check if any has been modified
        result = integrity_check_files(original_file_values, restored_info)
        self.assertEqual(len(result), 1)

    def test_integrity_check_files_one_modified(self):
        #Get the time and path of the original ones
        files_no_extension = get_files_path_from_folder(thisdir)
        original_file_values = get_modification_time(files_no_extension)
        #Store the info
        store_original_data(original_file_values, debug_file)
        #Retreive the info
        restored_info = read_original_data(debug_file)
        #Modify one value
        restored_info[-1]["tc"] = -1
        #Check if any has been modified
        result = integrity_check_files(original_file_values, restored_info)
        self.assertEqual(len(result), 1)

if __name__ == '__main__':

    # create a suite with all tests

    test_classes_to_run = [UnitTestGetFiles, TestDuplicates, TestModificationTime, TestIntegrityCheck]

    loader = unittest.TestLoader()
    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    all_tests_suite = unittest.TestSuite(suites_list)

    # run the test suite with high verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(all_tests_suite)