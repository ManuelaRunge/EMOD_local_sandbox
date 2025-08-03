## -----------------------------------------------------------------------------------------------------------------------
## Adapted from https://github.com/EMOD-Hub/emodpy-malaria/blob/main/examples-container/simple_example/example_container.py
## ------------------------------------------------------------------------------------------------------------------------
import os
from emodpy.emod_task import EMODTask
from idmtools.entities.experiment import Experiment
from idmtools.core.platform_factory import Platform
import manifest

params = {}
params['exp_name']  = 'example_integrated_analyzer'
params['sim_years'] = 10
params['pop_size'] = 1000


def set_config_parameters(config, params):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # You have to set simulation type explicitly before you set other parameters for the simulation
    config.parameters.Simulation_Type = "MALARIA_SIM"
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])
    config.parameters.Simulation_Duration = params['sim_years']  * 365

    config.parameters.x_Base_Population = params['pop_size']  / 1000
    config.parameters.Report_Parasite_Smear_Sensitivity = 1
    config.parameters.Birth_Rate_Dependence = "FIXED_BIRTH_RATE"
    config.parameters.Min_Days_Between_Clinical_Incidents = 14

    return config


def build_campaign():
    """
        Addind one intervention, so this template is easier to use when adding other interventions, replacing this one
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.ivermectin as ivermectin

    # passing in schema file to verify that everything is correct.
    campaign.set_schema(manifest.schema_file)
    # adding a scheduled ivermectin intervention
    ivermectin.add_scheduled_ivermectin(campaign=campaign, start_day=3)

    return campaign


def build_demog():
    """
        Builds demographics
    Returns:
        complete demographics
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    demog = Demographics.from_template_node(lat=0, lon=0, pop=100, name=1, forced_id=1)

    return demog


def general_sim():

    platform = Platform('Container', job_directory=manifest.job_directory)

    # create EMODTask
    print("Creating EMODTask (from files)...")
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=None,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=lambda config: set_config_parameters(config, params),
        demog_builder=build_demog
    )
    # create Experiment
    experiment = Experiment.from_task(task, name=params['exp_name'] )
    exp_id = experiment.id
    experiment.run(wait_until_done=True)

    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.core import ItemType
    from analyzer import InsetChartAnalyzer

    channels_inset_chart = ['Statistical Population', 'Births', 'Disease Deaths',
                            'New Infections', 'Newly Symptomatic', 'New Clinical Cases', 'New Severe Cases',
                            'Fever Prevalence', 'True Prevalence', 'PCR Gametocyte Prevalence',
                            'PCR Parasite Prevalence', 'Blood Smear Parasite Prevalence', 'PfHRP2 Prevalence',
                            'Infectious Vectors', 'Daily EIR']

    wdir = os.path.join(manifest.output_directory, exp_id)
    os.makedirs(wdir, exist_ok=True)
    analyzers_to_run = [InsetChartAnalyzer(channels=channels_inset_chart,
                                           exp_tags=['Run_Number'],
                                           start_year=2000,
                                           working_dir=wdir)]

    manager = AnalyzeManager(platform=platform, ids=[(experiment.id, ItemType.EXPERIMENT)], analyzers=analyzers_to_run)
    manager.analyze()


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()

