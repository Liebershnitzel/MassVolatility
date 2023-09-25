# MassVolatility
Automatically runs plugins against multiple memory dumps and saves the output to a text file, the script also saves the symbol file path for faster results. 

**To Use**
- Download volatility3, ensure you have all symbol files located in the symbols directory
- The memory dumps will need to be located in the same directory
![MassVolatility](https://github.com/Liebershnitzel/MassVolatility/assets/49920398/2af07c05-520b-4bf8-a76f-47021ac6ae63)


**Information**

- The script copies each symbol file into the /tmp directory, this is to allow for faster results as volatility3 spends a large amount of time determining the proper symbol file.
- The script will automatically determine the OS and symbol file and store this inside the determinedOS.json file located in the memorydumps folder.
- All outputs will be stored in the Outputs directory, currently it has the output just stored as plain text files but I plan on updating this functionality.
- The script currently only works on windows
