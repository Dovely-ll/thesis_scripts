import os
import re
import sys
import datetime
from utility import PROJECT_PATHS

def generate_result(directory, keyword, output):
    # Compile a regex pattern to match Java-like method signatures
    # r'^\s*(public|protected|private|static)?\s+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*{'
    # r'^\s*(public|protected|private)?\s*(\w+)\s*\(([^)]*)\)\s*{'
    # method_pattern = re.compile(r'^\s*(public|protected|private|static|\s)*\s*[\w<>\[\]]+\s+\w+\s*\(.*\)\s*{', re.MULTILINE)
    method_pattern = re.compile(r'^\s*((public|protected|private|static)?\s+(static\s+)?(?!\bif\b|\belse\b|\bswitch\b|\bfor\b)\w[\w<>\[\], ?]+\s+\w+\s*\([^)]*\)\s*(throws (\w+|,| )+)?\s*{)', re.MULTILINE)
    constructor_pattern = re.compile(r'^\s*((public|protected|private)?\s*(?!if|for|else|switch)(\w+)\s*\(([^)]*)\)\s*{)', re.MULTILINE)
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file name contains the keyword (case-insensitive)
            if 'test' not in root and '.java' in file and keyword.lower() in file.lower():
                file_path = os.path.join(root, file)
                output.write(f"Processing file: {file_path}\n")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    # contents = f.readlines()
                    content = f.read()

                    # Find all method signatures in the file
                    # methods = []
                    # for content in contents:
                    #     method = re.match(method_pattern, content)
                    #     if method:
                    #         methods.append(method)
                    methods = method_pattern.findall(content)
                    constructors = constructor_pattern.findall(content)
                    
                    if methods:
                        output.write(f"Methods in {file}:\n")
                        for method in methods:
                            output.write(f"  {method[0].strip()}\n")
                    else:
                        output.write(f"No methods found in {file}.\n")
                    if constructors:
                        output.write(f"Constructors in {file}:\n")
                        for constructor in constructors:
                            output.write(f"  {constructor[0].strip()}\n")
                    else:
                        output.write(f"No constructors found in {file}.\n")
                output.write("\n")

def list_method_signatures(directory, keywords, output_file):
    # Open the output file for writing
    with open(output_file, 'w', encoding='utf-8') as output:
        for keyword in keywords:
            generate_result(directory, keyword, output)

if __name__ == "__main__":
    # Get the keyword and directory path from the user
    # keyword = input("Enter the keyword: ")
    # directory = input("Enter the directory path: ")
    # if len(sys.argv) != 3:
    if len(sys.argv) < 3:
        exit(1)
    keywords = sys.argv[1:-1]
    directory = sys.argv[-1]
    
    output_dir = "method_signatures"
    # Generate a timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/method_signatures_{timestamp}.txt"
    
    # Call the function to list method signatures and write to a file
    list_method_signatures(directory, keywords, output_file)
    
    print(f"Method signatures have been written to {output_file}")
