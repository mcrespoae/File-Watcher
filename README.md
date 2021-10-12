# File-Watcher
The software has three parts:
- Takes paths located in /data/paths.txt and watchs the files.
- Pull the reposotory or update the worskpace located in /data/config/worskpace_path.txt with Plastic SCM.
- Check for differences between the files previosly watched. If any diff is located (delete, new or modify), the software will show the data/mismatched.txt in the screen with the differences.

## How to install it
- Install Python 3.9 or higher.
- Locate yourself in the path of the FileWatcher project within the console.     
- ```powershell
    pipenv install
    ```
    
 ## Requirements info
 This software only works on Windows and with Plastic SCM.
 
 ## Next steps
 Add unittest support
