    
    import unittest
    from file_watcher import *


    #Ini variables
    thisdir = os.path.dirname(__file__) #Get location of the folder containing this file
    thisdir = os.path.join(thisdir, "TEST_FILES", "TEST")
    print(f"Dir: {thisdir}")

    original_values_unmodified =        [{'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\test.cfg', 'tc': 1619982465.8139253}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\appdirs.py', 'tc': 1619985506.5950322}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\cycler.py', 'tc': 1619985559.2153633}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\threadpoolctl.py', 'tc': 1619985476.1510704}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\typing_extensions.py', 'tc': 1619982495.90831}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\wavio.py', 'tc': 1619985371.3604882}]
    original_values_oneFileDeleted =    [{'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\testingFake.cfg', 'tc': 1619982465.8139253}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\test.cfg', 'tc': 1619982465.8139253}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\appdirs.py', 'tc': 1619985506.5950322}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\cycler.py', 'tc': 1619985559.2153633}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\threadpoolctl.py', 'tc': 1619985476.1510704}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\typing_extensions.py', 'tc': 1619982495.90831}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\wavio.py', 'tc': 1619985371.3604882}]
    original_values_oneFileNew =        [{'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\appdirs.py', 'tc': 1619985506.5950322}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\cycler.py', 'tc': 1619985559.2153633}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\threadpoolctl.py', 'tc': 1619985476.1510704}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\typing_extensions.py', 'tc': 1619982495.90831}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\wavio.py', 'tc': 1619985371.3604882}]
    original_values_oneFileModified =   [{'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\test.cfg', 'tc': 15}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\appdirs.py', 'tc': 1619985506.5950322}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\cycler.py', 'tc': 1619985559.2153633}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\threadpoolctl.py', 'tc': 1619985476.1510704}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\typing_extensions.py', 'tc': 1619982495.90831}, {'filepath': 'c:\\Users\\Mario\\Desktop\\Local\\FileChecker\\TEST_FILES\\Lib\\site-packages\\wavio.py', 'tc': 1619985371.3604882}]



    #Unitests
    class UnitTest(unittest.TestCase):
        def py_files(self):
            #Files with .py extension
            files_py_extension = get_files_path_from_folder(thisdir, "py") 
            self.assertEqual(len(files_py_extension), 5)
        


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

if __name__ == '__main__':

    # create a suite with all tests

    test_classes_to_run = [Test1_1_ElGamalKeyGen, Test1_2_ElGamalSign, 
                           Test1_3_ElGamalVerify, Test1_4_ElGamalExtractPrivKey,

                           Test2_1_0_ZkpProverInit, Test2_1_ZkpProverComputeC, 
                           Test2_2_ZkpProverComputeH, Test2_3_0_kpVerifierInit, 
                           Test2_3_ZkpVerifierChooseb, Test2_4_ZkpVerifierVerify, 
                           Test2_5_Challenge,

                           Test3_1_ZkpCheaterProverB0ComputeC, Test3_2_ZkpCheaterProverB0ComputeH,
                           Test3_3_ZkpCheaterProverB1ComputeC, Test3_4_ZkpCheaterProverB1ComputeH]

    loader = unittest.TestLoader()
    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    all_tests_suite = unittest.TestSuite(suites_list)

    # run the test suite with high verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(all_tests_suite)