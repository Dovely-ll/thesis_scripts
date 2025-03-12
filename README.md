# Thesis Artifact Reproduction Guide  
**Thesis Title:** `UNDERSTANDING PORTABILITY OF CONFIGURATION TESTING FOR OPEN-SOURCE JAVA PROJECTS`  
**Affiliation:** University of Illinois at Urbana-Champaign  
**Last Verified:** 2025-03-10  

---

## 1. Metadata
### 1.1 Source Code and Repository
Ctest4J: [Annotation Library](https://github.com/xlab-uiuc/ctest4j/tree/auto_annotate).
A Ctest4J module for automatic processing of target projects and running of Ctests.

Ctest-repos: [Target Projects](https://github.com/ctest-repos).
Contains studied projects with ported and unsuitable ones.

### 1.2 Projects Studied
```json
{
"//comment": "project_supported_path",
"hbase-server": "../app/hbase/hbase-server",
"alluxio-core-common": "../app/alluxio/core/common",
"hive-common": "../app/hive/common",
"camel-core": "../app/camel/core",
"yarn-common": "../app/hadoop/hadoop-yarn-project/hadoop-yarn/hadoop-yarn-common",
"mapreduce-client-core": "../app/hadoop/hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-core",
"flink-core": "../app/flink/flink-core",
"kylin-core-common": "../app/kylin/core-common",
"zeppelin-interpreter": "../app/zeppelin/zeppelin-interpreter"
}

{
"//comment": "projects_unsupported_path",
"druid-processing": "../app/druid",
"kafka": "../app/kafka",
"rocketmq-common": "../app/rocketmq/common",
"spark-core": "../app/spark/core",
"tomcat": "../app/tomcat",
"redisson": "../app/redisson",
"nifi-commons": "../app/nifi/nifi-commons",
"netty-common": "../app/netty/common",
"spring-framework": "../app/spring-framework"
}
```

---

## 2. Setup  
### 2.1 Start a Docker container  
```bash
# pull and start a docker container
docker pull dovely1998/ta_image:alpha
docker run -it --name ta_test dovely1998/ta_image:alpha /bin/bash
```

### 2.2 Set up Ctest4J and analysis scripts
```bash
# clone the Ctest4J repo (need to setup ssh first)
cd /home/ctestrunner
git clone git@github.com:xlab-uiuc/ctest4j.git

# switch to the branch for thesis evaluation
cd ctest4j
git checkout auto_annotate

# install Ctest4J
mvn clean install -DskipTests

# set up analysis scripts
mkdir app && cd app
git clone git@github.com:Dovely-ll/thesis_scripts.git
```

### 2.3 Prepare target projects
Projects can be found in the [ctest-repos](https://github.com/ctest-repos).
```bash
# checkout the target project
git clone {target_project_repo_url}

# checkout the instrumented version
# (for flink, checkout commit aa83fa3d)
cd {target_project_repo}
git checkout ctest-eval

# prepare snapshot dependencies (for Zeppelin Only, only need the parent POM and zeppelin-common module)
cd zeppelin && mvn clean install -DskipTests && cd ../../scripts
```

---

## 3. Validation
### 3.1 Run Ctests
```bash
# use annotation library to automatically run Ctests in tracking and checking modes, mapping files between tests and parameters are generated
# example: python3 auto_annotate.py hive-common junit4 ../app/hive/common . ctest/saved_mapping ({project_test_dir} usually can be ".")
python3 auto_annotate.py {project_name} {test_module} {project_dir} {project_test_dir} {ctest_mapping_dir}
```

Running a configuration test is the same as running a normal test, except that the runner needs to be specified as `ConfigTestRunner.class`. The runner can take a few arguments to control the behavior of the test, which are listed below.

### Arguments
| Arguments            | Description                                                                                                                                                                                                                                                                                                    | Supported Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mode                 | The mode of running configuration test                                                                                                                                                                                                                                                                         | (1) default: this is the default mode of ctest runner, where the runner first inject the configuration value to the test and checks whether all required configuration paraemters are used after the test execution. (2) checking: this mode only checks whether all required configuration parameters are used, but does not inject configuration value to the test and use default configuration value to run every test. (3) injecting: this mode only injects configuration value to the test but does not check required configuration usage. (4) base: this mode switches back to use a default non-ctest runner to run the test as a normal test, no injecting and checking. |
| config.inject.dir    | A directory that contains configuration files that under injection for each configuration test class. Each file should named as the same as the configuration test class. Currently JSON and XML files are supported.                                                                                          | Directory path                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| config.inject.cli    | An argument that allows user to set configuration key value pairs directly.                                                                                                                                                                                                                                    | Configuration key value pairs seperated by comma. For example "param1=value1,param2=value2,...,paramN=valueN"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ctest.mapping.dir   | This is a directory that contains all configuration mapping files for each test. Each file name should be the same as the configuration method name. The runner will automatically search for the file under this direcotry if speicified and checks usage accrodingly. The default value is `./ctest/mapping` | Directory path                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ctest.config.save     | For tests with @Test, whether to save the tracked configuration parameter into a JSON file. This is useful when one does not know what configuraiton parameters are used in the test.                                                                                                                          | True / False                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ctest.suite.tracking | Use only with CTestSuiteRunner. With this set to true, @Test would perform normally, track the usage of configuration parameters during the test execution, and save to `ctest.mapping.dir`; otherwise all @Test would also perform like @CTest.                                                               | True / False                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ctest.config.save.dir | The directory to save the tracked configuration parameter. The default value is `./ctest/saved_mapping`

### 3.2 Run analysis scripts
Step into the thesis folder:
`cd ../app/thesis_scripts`

Analyze parameter number:
`./config_param.h {project_path}`

Analyze project's configuration API:
`python3 method_signatures.py {[keyword1, keyword2...]} {project_path}`

Initiate experiment 1 and 3:
`python3 utility.py {option}`
| Argument        | Value    | Description                |  
|-----------------|----------|----------------------------|  
| Option          | 0        | Run experiment 1 to collection basic stats of the target project. |  
|                 | 1        | Run experiment 3 to evaluate the effectiveness and overhead of Ctest4J.  |  

---

## References  
[1](@ref): [AEA Data Editor Replication Template](https://aeadataeditor.github.io/aea-de-guidance/)  
[2](@ref): [ICPSR Data Management Guidelines](https://www.icpsr.umich.edu)  
