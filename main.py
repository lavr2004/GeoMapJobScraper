from script00_00_docker_launch import main as step00_prepare_environment_before_launch
step00_prepare_environment_before_launch()

from script00_00_main import main as step01_parsing_data
step01_parsing_data()

from script00_01_combine_databases import combine_databases as step02_combine_data_from_different_databases
step02_combine_data_from_different_databases()

import script00_02_mappagegenerator

print(f"OK - process of parsing, evidence, combining data and generation map finished...")