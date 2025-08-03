import os

selected_platform = 'CONTAINER'
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


# This is a user-modifiable Python file designed to be a set of simple input file and directory settings that you can choose and change.
#
# the location of the file containing AssetCollection id for the dtk sif (singularity image)
sif_id = os.path.join(os.pardir, '..', 'examples', 'dtk_sif.id')
# The script is going to use this to store the downloaded schema file. Create 'download' directory or change to your preferred (existing) location.
schema_file = "download/schema.json"
# The script is going to use this to store the downloaded Eradication binary. Create 'download' directory or change to your preferred (existing) location.
# eradication_path="download/Eradication"
eradication_path = "download/Eradication"
# Create 'Assets' directory or change to a path you prefer. idmtools will upload files found here.
assets_input_dir = os.path.join("simulations_local/Assets")
plugins_folder = "download/reporter_plugins"

ep4_path = "python_scripts"
# requirements = "./requirements.txt"

job_directory = os.path.join(ROOT_DIR,"simulations_local/experiments")
os.makedirs(job_directory, exist_ok=True)

output_directory = os.path.join(ROOT_DIR, "simulations_local/simulation_outputs")
os.makedirs(output_directory, exist_ok=True)
