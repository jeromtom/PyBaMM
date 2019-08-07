#
# Simulations: discharge of a lead-acid battery
#
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pybamm
import shared_plotting
from collections import defaultdict
from shared_solutions import model_comparison, convergence_study

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = None


def plot_voltages(all_variables, t_eval):
    Crates = [0.1, 0.2, 0.5, 1, 2, 5]
    all_variables = {k: v for k, v in all_variables.items() if k in Crates}
    shared_plotting.plot_voltages(all_variables, t_eval)
    file_name = "discharge_voltage_comparison.eps"
    if OUTPUT_DIR is not None:
        plt.savefig(OUTPUT_DIR + file_name, format="eps", dpi=1000)


def plot_variables(all_variables, t_eval):
    # Set up
    Crates = [0.1, 1, 4]
    times = np.array([0, 0.195, 0.375, 0.545])
    var_file_names = {
        "Electrolyte concentration [Molar]"
        + "": "discharge_electrolyte_concentration_comparison.eps",
        "Electrolyte potential [V]": "discharge_electrolyte_potential_comparison.eps",
        "Interfacial current density"
        + "": "discharge_interfacial_current_density_comparison.eps",
    }
    limits_exceptions = {"Electrolyte concentration [Molar]": {"min": 0}}
    all_variables = {k: v for k, v in all_variables.items() if k in Crates}
    for var, file_name in var_file_names.items():
        if var in limits_exceptions:
            exceptions = limits_exceptions[var]
        else:
            exceptions = {}
        shared_plotting.plot_variable(all_variables, times, var, exceptions)
        if OUTPUT_DIR is not None:
            plt.savefig(OUTPUT_DIR + file_name, format="eps", dpi=1000)


def plot_voltage_components(all_variables, t_eval):
    Crates = [0.1, 2, 5]
    model = "Composite"
    shared_plotting.plot_voltage_components(all_variables, t_eval, model, Crates)
    file_name = "discharge_voltage_components.eps"
    if OUTPUT_DIR is not None:
        plt.savefig(OUTPUT_DIR + file_name, format="eps", dpi=1000)


def discharge_states(compute):
    savefile = "discharge_asymptotics_data.pickle"
    if compute:
        models = [
            pybamm.lead_acid.NewmanTiedemann(name="Full"),
            pybamm.lead_acid.LOQS(name="LOQS"),
            pybamm.lead_acid.FOQS(name="FOQS"),
            pybamm.lead_acid.CompositeExtended(name="Composite"),
        ]
        Crates = [0.1, 0.2, 0.5, 1, 2, 4, 5, 10, 20]
        t_eval = np.linspace(0, 1, 100)
        extra_parameter_values = {"Bruggeman coefficient": 0.001}
        all_variables, t_eval = model_comparison(
            models, Crates, t_eval, extra_parameter_values=extra_parameter_values
        )
        with open(savefile, "wb") as f:
            data = (all_variables, t_eval)
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    else:
        try:
            with open(savefile, "rb") as f:
                (all_variables, t_eval) = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                "Run script with '--compute' first to generate results"
            )
    plot_voltages(all_variables, t_eval)
    plot_variables(all_variables, t_eval)
    plot_voltage_components(all_variables, t_eval)


if __name__ == "__main__":
    pybamm.set_logging_level("INFO")
    parser = argparse.ArgumentParser()
    parser.add_argument("--compute", action="store_true", help="(Re)-compute results.")
    args = parser.parse_args()
    discharge_states(args.compute)
    plt.show()
