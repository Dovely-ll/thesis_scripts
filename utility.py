import os
import re
import sys
import time
from collections import defaultdict

# python3 auto_annotate.py hadoop-hdfs junit4 ../app/hadoop/hadoop-hdfs-project/hadoop-hdfs . ctest/saved_mapping 
# mvn surefire:test -Dmode=default -Dctest.mapping.dir=ctest/saved_mapping -Dctest.config.save=false
# Paths to projects' modules
PROJECT_PATHS = ["../hbase/hbase-server",
                 "../alluxio/core/common",
                 "../hive/common",
                 "../kylin/core-common",
                 "../flink/flink-core",
                 "../hadoop/hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-core",
                 "../hadoop/hadoop-yarn-project/hadoop-yarn/hadoop-yarn-common",
                 "../camel/core", # ../camel/core/camel-core
                 "../zeppelin/zeppelin-interpreter",
                 "../spark/common/network-common", # ../spark/core
                 "../druid/processing", # ../druid/server
                 "../tomcat/modules/jdbc-pool", # ../tomcat/java
                 "../redisson/redisson",
                 "../spring-framework/spring-core", # ../spring-framework/spring-jms?
                 "../netty/transport", # ../netty/codec-http
                 "../kafka/clients", # ../kafka/connect
                 "../rocketmq/common", # ../rocketmq/remoting
                 "../nifi/nifi-commons" # ../nifi/nifi-commons ../nifi/nifi-registry ../nifi/minifi
                 ]

# Element Class
class ClassNode:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.interfaces = []
        self.testNumber = 0
    
    def add_child(self, child):
        self.children.append(child)

    def add_interface(self, interface):
        self.interfaces.append(interface)
    
    def add_test(self, num):
        self.testNumber += num

    def flatten(self):
        """
        Flatten the tree structure starting from this node.
        :return: A list of all ClassNode objects in the subtree, including this node.
        """
        nodes = [self]  # Start with the current node
        for child in self.children:
            nodes.extend(child.flatten())  # Recursively add child nodes
        return nodes
    
    def __repr__(self):
        return f"ClassNode(name={self.name}), interfaces={self.interfaces}), testNumber={self.testNumber}"

def build_tree(path):
    class_hierarchy = defaultdict(list)
    classes = {}

    # Walk through the directory tree
    for root, dirs, files in os.walk(path):
        if 'test' not in root:
            continue
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                # if "/test/" not in file_path:
                #     continue
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Check if the file contains at least one @Test annotation
                    if not any('@Test' in line for line in lines):
                        continue
                    package_name = root.replace(path, '').replace(os.sep, '.').strip('.')
                    for line in lines:
                        # Match class declarations
                        class_match = re.match(r'\s*public\s+(abstract\s+|final\s+)?class\s+(\w+)', line)
                        if class_match:
                            class_name = class_match.group(2)
                            full_class_name = f"{package_name}.{class_name}"
                            classes[full_class_name] = ClassNode(full_class_name)

                        # Match "extends" relationships
                        extends_match = re.match(r'\s*public\s+(abstract\s+|final\s+)?class\s+(\w+)\s+extends\s+(\w+)', line)
                        if extends_match:
                            class_name = extends_match.group(2)
                            superclass_name = extends_match.group(3)
                            full_class_name = f"{package_name}.{class_name}"
                            # If the superclass is not fully qualified, assume it's in the same package
                            if '.' not in superclass_name:
                                superclass_name = f"{package_name}.{superclass_name}"

                            class_hierarchy[superclass_name].append(full_class_name)
    
    # Link classes based on the hierarchy
    for superclass, subclasses in class_hierarchy.items():
        if superclass in classes:
            for subclass in subclasses:
                if subclass in classes:
                    classes[superclass].add_child(classes[subclass])

    # Find and return the root classes (those without a superclass)
    root_classes = [cls for cls in classes.values() if cls.name not in class_hierarchy]
    return root_classes

def print_tree(node, indent=""):
    print(indent + node.name)
    for child in node.children:
        print_tree(child, indent + "    ")

def all_nodes(nodes):
    allNodes = []
    for node in nodes:
        allNodes.extend(node.flatten())
    return allNodes
    

def analyze_java_files(path):
    # Initialize the data structure with a counter for @Test occurrences and space for future statistics
    stats = {
        "test_count": 0,
        "test_class": 0,
        "test_method": 0,
        "other_stat": 0  # Placeholder for future statistics
    }
    
    # Walk through the directory tree
    for root, dirs, files in os.walk(path):
        if 'test' not in root:
            continue
        for file in files:
            if file.endswith(".java"):
                
                # Open and read each Java file
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    for line in f:
                        # Check if the entire line matches "@Test"
                        # if line.strip() == "@Test":
                        if "@Test" in line:
                            stats["test_count"] += 1
                # print(f'{file} + {stats["test_count"]}')

    return stats

def annotate_test_classes(path):
    IMPORT_NORMAL = {"junit4": "import org.junit.runner.RunWith;\nimport edu.illinois.CTestJUnit4Runner2;\nimport edu.illinois.CTestClass;\nimport edu.illinois.CTest;\n\n"}
    IMPORT_ABSTRACT = {"junit4": "import edu.illinois.CTest;\n\n"}
    added = False
    cnt = 0
    for root, dirs, files in os.walk(path):
        if 'test' not in root:
            continue
        for file in files:
            added = False
            if file.endswith(".java"):
                with open(os.path.join(root, file), 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    if not any('@Test' in line for line in lines):
                        continue
                    f.seek(0)
                    for i, line in enumerate(lines):
                        class_match = re.match(r'\s*public\s+(abstract\s+|final\s+)?class\s+(\w+)', line)
                        if not added and "import " in line:
                            line = line + IMPORT_NORMAL["junit4"]
                            added = True
                            print(f'Import added for class: {file}')
                            cnt += 1
                            # f.write(line)
                        elif class_match is not None:
                            class_name = class_match.group(2)
                            line = "@RunWith(CTestJUnit4Runner2.class)\n@CTestClass()\n" + line
                            print(f'RunWith added for class: {class_name}')
                            # f.write(line)
                        f.write(line)
    print(f'Total test classes added: {cnt}')


# change @Test to @Ctest, and preserve original arguments
def annotate_test_methods(path):
    for root, dirs, files in os.walk(path):
        if 'test' not in root:
            continue
        for file in files:
            if file.endswith(".java"):
                with open(os.path.join(root, file), 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
                        if "@Override" in line or "@SuppressWarnings" in line or "/**" in line or "/*" in line or " *" in line or "*/" in line:
                            line = line
                        else:
                            line = re.sub(r'@Test', '@CTest', line)
                        f.write(line)
                    f.truncate()
                            # continue
                        # match_str = re.search("@Test *\( *\w+", line)
                        # if match_str is not None:
                        #     match_str = match_str.group()
                        #     line = line.replace(match_str[:match_str.index("(") + 1], "@CTest(file=\"" + ctest_mapping_dir + "/" + class_name + "_" + test_method_name + ".json\", ")
                        #     class_method_pair[class_name].remove(test_method_name)
                        # elif "@Test" in contents[index - offset]:
                        #     match_str = re.search("@Test *\( *\)", contents[index - offset])
                        #     if match_str is None:
                        #         match_str = "@Test"
                        #     else:
                        #         match_str = match_str.group()
                        #     contents[index - offset] = contents[index - offset].replace(match_str, "@CTest(file=\"" + ctest_mapping_dir + "/" + class_name + "_" + test_method_name + ".json\")")
                        #     class_method_pair[class_name].remove(test_method_name)

def experiment_1_1(path):
    root_classes = build_tree(path)
    # print("Class Hierarchy:")
    # for root in root_classes:
    #     print_tree(root)
    # print(len(root_classes))
    classes = all_nodes(root_classes)
    # for clazz in classes:
    #     print(clazz)
    print(f"Number of test classes: {len(classes)}")

def experiment_1_2(path):
    result = analyze_java_files(path)
    
    print(f"Number of @Test occurrences: {result['test_count']}")
    # Print additional statistics if needed

def experiment_1_3(path):
    start_time = time.time()
    annotate_test_classes(path)
    annotate_test_methods(path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {round(elapsed_time, 6)} seconds")

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) == 1:
        path = input("Enter the path to the directory containing Java files: ")
    else:
        if sys.argv[1] == "0":
            for path in PROJECT_PATHS:
                print(path)
                experiment_1_1(path)
                experiment_1_2(path)
                # experiment_1_3(path)
                # print(f"Total methods: {0}, modified: {0}, perc.: {0}")
        else:
            path = sys.argv[1]   
            
            # experiment_1_1(path)           
            # experiment_1_2(path)
            experiment_1_3(path)