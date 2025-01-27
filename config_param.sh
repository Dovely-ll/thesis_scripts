#!/bin/bash

# Define the project directory
project_dir=$1

# Check if the project directory is provided
if [ -z "$project_dir" ]; then
    echo "Usage: $0 <path_to_project>"
    exit 1
fi

# Count variables in .properties files (key-value pairs)
properties_count=$(find "$project_dir" -type f -name "*.properties" -exec grep -E "^[a-zA-Z0-9_.-]+=[^#]" {} + | wc -l)

# Count variables in .xml files (property elements and attributes)
xml_count=$(find "$project_dir" -type f -name "*.xml" -exec grep -E "<property.*name=\"[^\"]+\"|<param.*name=\"[^\"]+\"" {} + | wc -l)

# Count static final constants and System properties in .java files
java_count=$(find "$project_dir" -type f -name "*.java" -exec grep -E "public static final|System\.getProperty|System\.getenv" {} + | wc -l)

# Sum up all the counts
total_count=$((properties_count + xml_count + java_count))

# Output the results
echo "Configuration Parameters Found:"
echo "  - .properties files: $properties_count"
echo "  - .xml files: $xml_count"
echo "  - .java files: $java_count"
echo "  - Total: $total_count"

