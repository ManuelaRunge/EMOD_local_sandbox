## -----------------------------------------------------------------------------------------------------------------------
## Adapted from https://github.com/ahadi-analytics/MultiMalModPy/blob/main/EMOD/utils.py
## ------------------------------------------------------------------------------------------------------------------------
import os
import time
import subprocess
from pathlib import Path


def write_analyze_local(manifest, exp_id, exp_name=None):

    job_name = f"analyzer"
    if exp_name is None:
        py_command = f"python analyzer.py -id {exp_id}"
        sim_out_dir = os.path.join(manifest.output_directory, exp_id)
    else:
        py_command = f"python analyzer.py -id {exp_id}   -name {exp_name}"
        sim_out_dir = os.path.join(manifest.output_directory, exp_name)

    fname = f'run_analyzer.ps1'

    wdir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    file_path = Path(os.path.join(wdir, fname))
    os.makedirs(sim_out_dir, exist_ok=True)
    os.makedirs(os.path.join(wdir, 'log'), exist_ok=True)

    # Define the content of the PowerShell script
    powershell_content = f"""
    # Job settings
    $job_name = "{job_name}"
    $work_dir = "{wdir}"
    $jobdir = "{os.path.join(manifest.job_directory)}"
    $log_dir = Join-Path $wdir "log"

    # Navigate to the subdirectory
    Set-Location -Path "$work_dir"

    # Run the Python command
    {py_command} 
     """

    # Write the PowerShell script
    with open(Path(file_path), 'w') as file:
        file.write(powershell_content)

    print(f"PowerShell script written to {file_path}")


def get_container_jobs_status(container_id):
    """
    Run `idmtools container jobs` and parse output to get running simulations count.
    Returns number of running simulations (int).
    """
    try:
        result = subprocess.run(
            ["idmtools", "container", "jobs", container_id],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
        # Simple parse: count how many lines contain 'running' under SIMULATION entity
        running_sims = 0
        for line in output.splitlines():
            if "SIMULATION" in line and "running" in line:
                running_sims += 1
        return running_sims
    except Exception as e:
        print(f"Error checking container jobs: {e}")
        return -1


def run_analyze_EMOD_local_with_polling(exp, container_id, poll_interval=30, timeout=7200):
    """
    Poll container jobs for running simulations; when all done, run analyzer script.
    """
    print(f"Polling container {container_id} for running simulations...")

    elapsed = 0
    while True:
        running_sims = get_container_jobs_status(container_id)
        if running_sims == 0:
            print("All simulations completed.")
            break
        elif running_sims < 0:
            print("Error checking running jobs; continuing polling.")
        else:
            print(f"{running_sims} simulations still running. Elapsed time: {elapsed}s")

        if elapsed >= timeout:
            print("Timeout waiting for simulations to finish. Exiting.")
            return
        time.sleep(poll_interval)
        elapsed += poll_interval

    script_path = os.path.join(exp.job_directory, 'run_analyze_EMOD.ps1')
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True,
            text=True
        )
        print("Analyzer STDOUT:\n", result.stdout)
        print("Analyzer STDERR:\n", result.stderr)
    except Exception as e:
        print(f"Failed to run analyzer script: {e}")
