
#!/usr/bin/env python3
import os
import subprocess
import glob
import re
import json
import shutil
import argparse
#===============================================================#
#Created by Ben Lieberman
#Revision 3.0
#===============================================================#


#===============================================================#
#Create the Arguments required
directories = argparse.ArgumentParser(description="Automatically parses with selected plugin/plugins on several memory dumps")
directories.add_argument("-v", "--volatility-dir",help="volatility3 directory location",required=True)
directories.add_argument("-o","--output-dir",help="output directory location",required=True)
directories.add_argument("-m","--memory-dumps",help="memory dumps location",required=True)
directories.add_argument("--output-mode", help="Specify output mode (json or text)", choices=['json', 'text'], default='text')
args = directories.parse_args()
print(args.output_dir)
print(args.volatility_dir)
print(args.memory_dumps)
#===============================================================#
#==============================GATHER THE ALREADY DETERMINED OS TO EACH MEMORY DUMP================================#
def osdetermination(determinedOS):
    with open(determinedOS, 'r') as file:
        memory_dump_symbol_paths = json.loads(file.read().replace("'", '"'))
        return memory_dump_symbol_paths

#CREATE THE OUTPUT DIRECTORY & determinedOS.json
detOS = "determinedOS.json"
detOSpath = os.path.join(args.memory_dumps, detOS)
if os.path.exists(detOSpath):
    jsonmemdumppaths = osdetermination(detOSpath)
else:
    with open(detOSpath, 'w') as file:
        jsonmemdumppaths = {}
        pass

dir_name = "Outputs"
output_directory = os.path.join(args.output_dir, dir_name)
os.makedirs(output_directory, exist_ok=True)


#==================================================================================================================#

#===============================================================#
#DETERMINE THE OS OF EACH MEMORY DUMP AND MAP IT TO A SYMBOLS FILE#
def get_os_profile(memory_dump):
    print(f"DETERMINING THE SYMBOLS FILE FOR {memory_dump} THIS MAY TAKE AWHILE PLEASE BE PATIENT")
    print(args.volatility_dir)
    command = f"python3 {args.volatility_dir}vol.py -f {memory_dump} windows.info"  # Or use linux.info for Linux dumps
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



memory_dumps = [f for f in glob.glob(f"{args.memory_dumps}/*") if not f.endswith('determinedOS.json')]


for memory_dump in memory_dumps:
    if memory_dump not in jsonmemdumppaths:
        symbol_path = get_os_profile(memory_dump)
        if symbol_path:
            jsonmemdumppaths[memory_dump] = symbol_path


with open(detOSpath, 'w') as file:
    json.dump(jsonmemdumppaths, file, indent=4)
#####THIS SECTION ABOVE DETERMINES WHETHER THE SYMBOL FILE HAS BEEN DEFINED INSIDE THE DeterminedOS JSON File



# Print the dictionary to verify it's been populated correctly
for dump, path in jsonmemdumppaths.items():
    print(f"Memory Dump: {dump}, Symbol Path: {path}")
# List of plugins to run
chose = input("Would you like to specify a plugin or a a list of plugins? 1 or 2: ")
if int(chose) == 1:
    plugins = str(input("input a plugin: "))
elif int(chose) == 2:
    plugin_input = input("Input a list of plugins, separated by commas: ")
    plugins = [plugin.strip() for plugin in plugin_input.split(",")]


#Running Volatility Based on Defined Plugins

def run_volatility_plugin(memory_dump, plugins, symbol_path, output_mode):
    symbol_dir = os.path.join("/tmp", os.path.basename(memory_dump) + "_symbols")
    os.makedirs(symbol_dir, exist_ok=True)
    memory_dump_name = os.path.basename(memory_dump).split('.')[0]
    shutil.copy(symbol_path, symbol_dir)
    symbol_file_in_new_dir = os.path.join(symbol_dir, os.path.basename(symbol_path))

    if output_mode == "json":
        print(output_mode)
        output_file_path = os.path.join(output_directory, f"{memory_dump_name}_{plugins}.json")
        print("Currently Running", plugins)
        command = f"python3 {args.volatility_dir}vol.py -f {memory_dump} -r json -s {symbol_dir} {plugins}"
        try:
            with open(output_file_path, 'w') as output_file:
                subprocess.run(command, shell=True, stdout=output_file)
            with open(output_file_path, 'r') as file:
                data = json.load(file)
            for item in data:
                item['Host'] = memory_dump_name
                item['Plugin'] = plugins
            with open(output_file_path, 'w') as file:
                json.dump(data,file)
            with open(output_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            modified_content = content.replace("[{", "{")
            modified_content = modified_content.replace("}]", "}")
            modified_content = modified_content.replace("}, {", "}\n{")

            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
        except:
            print("plugin probably didn't work")

    else:
       output_file_path = os.path.join(output_directory, f"{memory_dump_name}_{plugins}.txt")
       command = f"python3 {args.volatility_dir}vol.py -f {memory_dump} -s {symbol_dir} {plugins}"
       with open(output_file_path, 'w') as output_file:
            subprocess.run(command, shell=True, stdout=output_file)
       with open(output_file_path, 'r') as output_file:
            print(output_file.read())





for memory_dump in memory_dumps:
    symbol_path = jsonmemdumppaths.get(memory_dump)
    if symbol_path:
        if isinstance(plugins, str):
            print(f"Running plugin on: {memory_dump}")
            run_volatility_plugin(memory_dump, str(plugins), symbol_path, args.output_mode)
        elif isinstance(plugins, list):
            for plugin in plugins:
                run_volatility_plugin(memory_dump, plugin, symbol_path, args.output_mode)
    else:
        print(f"No symbol path found for memory dump: {memory_dump}. Skipping...")
