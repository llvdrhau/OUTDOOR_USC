"""
This script runs all the parts of the AgriLoop_PPW model.
The parts are run in the following order:
- Part 1: Superstructure creation
- Part 2.1: Wait and see optimization run
- Part 2.2: Wait and see analysis
- Part 3.1: Stochastic optimization run
- Part 3.2: Stochastic optimization analysis
- Part 4.1 and 4.2: Robust optimization run and analysis of PHA production

"""


import subprocess
import sys

# get the working directory
basePath = sys.path[0]
# saveConsoleOutput
saveConsoleOutput = False

part1 = "part_1_single_obj_opt_full_superstructure.py"
part1_1 = "part_1_single_obj_opt_reduced_superstructure.py"
part2_1 = "part_2_1_wait_and_see_optimization_run.py"
part2_2 = "part_2_2_wait_and_see_analysis.py"
part2_3 = "part_2_3_here_and_now.py"
part2_3_1 = "part_2_3_here_and_now_plots.py"
part3_1 = "part_3_1_stochastic_optimisation_run.py"
part3_2 = "part_3_2_stochastic_optm_analysis.py"
part4_1 = "part_4_1_pha_production_price_sensitivity.py"
part4_2 = "part_4_2_pha_production_costs.py"
part4_3 = "part_4_3_pha_parameter_sensitivity.py"
part4_4 = "part_4_4_pha_parameter_analysis.py"
part4_5 = "part_4_5_cross_sensitivity.py"

# List of script filenames to run

script_filenames = [
                    part1, part1_1,      # single optimization
                    part2_1, part2_2,    # wait and see optimization
                    part2_3, part2_3_1,  # here and now optimization
                    part3_1, part3_2,    # stochastic optimization
                    part4_1,             # sensitivity analysis PHA
                    part4_2,             # production cost analysis PHA
                    part4_3, part4_4,    # SCR analysis PHA
                    part4_5              # cross sensitivity analysis
                    ]


# stores console output in one txt file
if saveConsoleOutput:
    # Open a single output file for all scripts
    with open('console_output.txt', 'w') as f:
        # Run each script sequentially and capture console output
        for script_filename in script_filenames:
            # Write a header to the output file
            f.write(f"\nRunning script: {script_filename}\n")
            f.write("=" * 80 + "\n")
            # Run the script and capture output
            subprocess.run(
                [sys.executable, script_filename],
                check=True,
                cwd=basePath,
                stdout=f,
                stderr=subprocess.STDOUT
            )
            # Write a separator after the script output
            f.write("\n" + "=" * 80 + "\n")
else:
    # Run each script sequentially
    for script_filename in script_filenames:
        subprocess.run([sys.executable, script_filename], check=True, cwd=basePath)
