# MassVolatility
Automatically runs plugins against multiple memory dumps and saves the output to a text file, the script also saves the symbol file path for faster results. 

**To Use**
- Place the volatility 3 source files in the /root directory and give the vol.py binary executable permissions
- Create a directory named "memorydumps" in the volatility3 folder, this is where the memory dumps will be stored for analysis


**Information**

- The script copies each symbol file into the /tmp directory, this is to allow for faster results as volatility3 spends a large amount of time determining the proper symbol file.
- The script will automatically determine the OS and symbol file and store this inside the determinedOS.json file.
- All outputs will be stored in the Outputs directory located in the volatility folder, currently it has the output just stored as plain text files but I plan on updating this functionality.
