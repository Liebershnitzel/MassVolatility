#!/usr/bin/env python3
import os
import subprocess
import glob
import re
import json
import shutil

#===============================================================#
#Created by Ben Lieberman
#Revision 1.0
#===============================================================#


#CREATE THE OUTPUT DIRECTORY

dir_name = "Outputs"
output_base_dir = "/root/volatility3/"
output_dir = os.path.join(output_base_dir, dir_name)
os.makedirs(output_dir, exist_ok=True)

#DETERMINE THE OS OF EACH MEMORY DUMP AND MAP IT TO A SYMBOLS FILE#
def get_os_profile(memory_dump):
    print("DETERMINING THE SYMBOLS FILE FOR {memory_dump} THIS MAY TAKE AWHILE PLEASE BE PATIENT")
    command = f"/root/volatility3/vol.py -f {memory_dump} windows.info"  # Or use linux.info for Linux dumps
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    print(output)
    match = re.search(r"Symbols\tfile://(.+)", output)
    if match:
        symbol_path = match.group(1)
    else:
        symbol_path = None
        print(f"Could not find symbol path in output for memory dump: {memory_dump}")
    
    return symbol_path
#==================================================================================================================#



#==============================GATHER THE ALREADY DETERMINED OS TO EACH MEMORY DUMP================================#
determinedOS = "/root/volatility3/memorydumps/determinedOS.json"
if os.path.exists(determinedOS):
    with open(determinedOS, 'r') as file:
        memory_dump_symbol_paths = json.loads(file.read().replace("'", '"'))
else:
    memory_dump_symbol_paths = {}

#==================================================================================================================#



memory_dumps_dir = "/root/volatility3/memorydumps"
memory_dumps = [f for f in glob.glob(f"{memory_dumps_dir}/*") if not f.endswith('determinedOS.json')]


for memory_dump in memory_dumps:
    if memory_dump not in memory_dump_symbol_paths:
        symbol_path = get_os_profile(memory_dump)
        if symbol_path:
            memory_dump_symbol_paths[memory_dump] = symbol_path


with open(determinedOS, 'w') as file:
    json.dump(memory_dump_symbol_paths, file, indent=4)
#####THIS SECTION ABOVE DETERMINES WHETHER THE SYMBOL FILE HAS BEEN DEFINED INSIDE THE DeterminedOS JSON File



# Print the dictionary to verify it's been populated correctly
for dump, path in memory_dump_symbol_paths.items():
    print(f"Memory Dump: {dump}, Symbol Path: {path}")
# List of plugins to run
chose = input("Would you like to specify a plugin or a a list of plugins? 1 or 2: ")
if int(chose) == 1:
    plugins = str(input("input a plugin: "))
elif int(chose) == 2:
    plugin_input = input("Input a list of plugins, separated by commas: ")
    plugins = [plugin.strip() for plugin in plugin_input.split(",")]


#Running Volatility Based on Defined Plugins

def run_volatility_plugin(memory_dump, plugins, symbol_path):
    symbol_dir = os.path.join("/tmp", os.path.basename(memory_dump) + "_symbols")
    os.makedirs(symbol_dir, exist_ok=True)    
    memory_dump_name = os.path.basename(memory_dump).split('.')[0]
    output_file_path = os.path.join(output_dir, f"{memory_dump_name}_{plugins}.txt")
    shutil.copy(symbol_path, symbol_dir)
    symbol_file_in_new_dir = os.path.join(symbol_dir, os.path.basename(symbol_path))
    command = f"/root/volatility3/vol.py -f {memory_dump} -s {symbol_dir} {plugins}"
    with open(output_file_path, 'w') as output_file:
        subprocess.run(command, shell=True, stdout=output_file)
    
    with open(output_file_path, 'r') as output_file:
        print(output_file.read())


  


for memory_dump in memory_dumps:
    symbol_path = memory_dump_symbol_paths.get(memory_dump)
    if symbol_path:
        if isinstance(plugins, str):
            print(f"Running plugin on: {memory_dump}")
            run_volatility_plugin(memory_dump, str(plugins), symbol_path)
        elif isinstance(plugins, list):
            for plugin in plugins:
                run_volatility_plugin(memory_dump, plugin, symbol_path)
    else:
        print(f"No symbol path found for memory dump: {memory_dump}. Skipping...")
