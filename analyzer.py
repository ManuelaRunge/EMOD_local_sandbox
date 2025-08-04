import os
import sys
import argparse
import pickle
import datetime
import pandas as pd
import numpy as np
from idmtools.entities import IAnalyzer
from idmtools.entities.simulation import Simulation
import manifest

def parse_args():
    description = "Analyzer specifications"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-id",
        "--exp_id",
        type=str,
        required=False,
        help="Unique ID of simulation experiment",
        default=None
    )

    parser.add_argument(
        "-name",
        "--exp_name",
        type=str,
        required=False,
        default=None,
        help="Name of experiment to store simulation outputs",
    )
    return parser.parse_args()


class InsetChartAnalyzer(IAnalyzer):

    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, exp_tags=None, channels=None, daily=False, working_dir=".", start_year=2022):
        super(InsetChartAnalyzer, self).__init__(working_dir=working_dir, filenames=["output/InsetChart.json"])
        self.exp_tags = exp_tags or ["Run_Number"]
        self.inset_channels = channels or ['Statistical Population', 'Births', 'Disease Deaths',
                                           'New Infections', 'Newly Symptomatic', 'New Clinical Cases',
                                           'New Severe Cases'
                                           'Fever Prevalence', 'True Prevalence', 'PCR Gametocyte Prevalence',
                                           'PCR Parasite Prevalence', 'Blood Smear Parasite Prevalence',
                                           'PfHRP2 Prevalence',
                                           'Infectious Vectors', 'Daily EIR']
        self.start_year = start_year
        self.daily = daily

    def map(self, data, simulation: Simulation):
        simdata = pd.DataFrame({x: data[self.filenames[0]]['Channels'][x]['Data'] for x in self.inset_channels})

        # Create time variables
        simdata['Time'] = simdata.index
        simdata['Day'] = simdata['Time'] % 365
        simdata['Year'] = simdata['Time'].apply(lambda x: int(x / 365) + self.start_year)
        simdata['date'] = simdata.apply(
            lambda x: datetime.date(int(x['Year']), 1, 1) + datetime.timedelta(int(x['Day']) - 1), axis=1)

        # Add scenario sweeps (parameter that were varied) to data
        for sweep_var in self.exp_tags:
            if sweep_var in simulation.tags.keys():
                simdata[sweep_var] = simulation.tags[sweep_var]
            elif sweep_var == 'Run_Number':
                simdata[sweep_var] = 0
        return simdata

    def reduce(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        adf = pd.concat(selected).reset_index(drop=True)
        adf = adf.rename(columns={'Daily Bites per Human': 'Bites per Human', 'Daily EIR': 'EIR'})
        if self.daily:
            adf.to_csv(os.path.join(self.working_dir, 'EMOD', 'InsetChart_daily.csv'), index=False)

        # Change data to Year-months format, exclude days
        adf['date'] = pd.to_datetime(adf['date'])
        adf['date'] = adf['date'].dt.strftime('%b-%Y')

        # Aggregate data per date and exp_tags using sum and mean specific to outcome channel
        sum_channels = ['Births', 'Disease Deaths', 'New Infections', 'Newly Symptomatic', 'New Clinical Cases',
                        'New Severe Cases', 'Infectious Vectors', 'EIR']
        mean_channels = ['Statistical Population', 'Fever Prevalence', 'True Prevalence', 'PCR Gametocyte Prevalence',
                         'PCR Parasite Prevalence', 'Blood Smear Parasite Prevalence',
                         'PfHRP2 Prevalence']

        sdf = adf.groupby(['date'] + self.exp_tags)[sum_channels].agg('sum').reset_index()
        mdf = adf.groupby(['date'] + self.exp_tags)[mean_channels].agg('mean').reset_index()
        adf = pd.merge(left=sdf, right=mdf, on=(self.exp_tags + ['date']))

        # Save the processed DataFrame to a CSV file named 'All_Age_Outputs.csv'
        adf.to_csv(os.path.join(self.working_dir, 'InsetChart_yearmon.csv'), index=False)


if __name__ == "__main__":

    # Load additional required modules
    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.core import ItemType
    from idmtools.core.platform_factory import Platform

    args = parse_args()
    exp_name = args.exp_name
    exp_id = args.exp_id

    if exp_name is None:
        exp_name = exp_id

    wdir = os.path.join(manifest.output_directory, exp_name)
    os.makedirs(wdir, exist_ok=True)

    # Define which outcome metrics to process in inset_chart (all age per daily timestep)
    channels_inset_chart = ['Statistical Population', 'Births', 'Disease Deaths',
                            'New Infections', 'Newly Symptomatic', 'New Clinical Cases', 'New Severe Cases',
                            'Fever Prevalence', 'True Prevalence', 'PCR Gametocyte Prevalence',
                            'PCR Parasite Prevalence', 'Blood Smear Parasite Prevalence', 'PfHRP2 Prevalence',
                            'Infectious Vectors', 'Daily EIR']

    # Run analyzers
    with Platform('Container', job_directory=manifest.job_directory) as platform:
        analyzers_to_run = [InsetChartAnalyzer(channels=channels_inset_chart,
                                               exp_tags=['Run_Number'],
                                               start_year=2000,
                                               working_dir=wdir)]

    manager = AnalyzeManager(configuration={}, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers_to_run,
                             partial_analyze_ok=True)

    manager.analyze()
