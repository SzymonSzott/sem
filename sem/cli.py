import click
import sem
import ast
import pprint


@click.group()
def cli():
    """
    An interface to the ns-3 Simulation Execution Manager.
    """
    pass


@cli.command()
@click.option("--results-dir", type=click.Path(dir_okay=True,
                                               resolve_path=True),
              prompt=True,
              help='Directory containing the simulation results.')
@click.option("--show-all", is_flag=True,
              help='Show all results and skip query')
def view(results_dir, show_all):
    """
    View results of simulations.
    """

    campaign = sem.CampaignManager.load(results_dir)

    if show_all:
        output = '\n\n\n'.join([pprint.pformat(item) for item in
                                campaign.db.get_complete_results()])
    else:

        script_params = query_parameters(campaign.db.get_params())

        # Perform the search
        output = '\n\n\n'.join([pprint.pformat(item) for item in
                                campaign.db.get_complete_results(
                                    script_params)])
    click.echo_via_pager(output)


@cli.command()
@click.option("--ns-3-path", type=click.Path(exists=True,
                                             resolve_path=True),
              prompt=True)
@click.option("--results-dir", type=click.Path(dir_okay=True,
                                               resolve_path=True),
              prompt=True)
@click.option("--script", prompt=True)
@click.option("--no-optimization", default=False, is_flag=True)
def run(ns_3_path, results_dir, script, no_optimization):
    """
    Run simulations.
    """
    if sem.utils.DRMAA_AVAILABLE:
        click.echo("Detected available DRMAA cluster: using GridRunner.")
        runner_type = "GridRunner"
    else:
        runner_type = "ParallelRunner"

    # Create a campaign
    campaign = sem.CampaignManager.new(ns_3_path,
                                       script,
                                       results_dir,
                                       runner_type=runner_type,
                                       overwrite=False,
                                       optimized=not no_optimization)

    # Print campaign info
    click.echo(campaign)

    # Run the simulations
    script_params = query_parameters(campaign.db.get_params())
    campaign.run_missing_simulations(script_params,
                                     runs=click.prompt("Runs", type=int))


def query_parameters(param_list):
        # Query parameters
        script_params = {k: [] for k in param_list}

        # Order keys in alphabetical order to ensure reproducibility
        for param in sorted(script_params.keys()):
            user_input = click.prompt("%s" % param, default="None")
            script_params[param] = ast.literal_eval(user_input)

        return script_params
