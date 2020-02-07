import os
import sys
import warnings

import click
import inquirer
import yaml


@click.command()
@click.option('--figure', is_flag=True, type=click.BOOL)
def main(figure):
    """
    Reads vehicle data and prompts the user with questions about their journey

    :param figure: flag to trigger the creation of PNG and PDF graphs
    """

    vehicles_remaining = load_vehicle_data()
    vehicles_remaining, vehicles_selected = add_vehicle(vehicles_remaining)

    while True:
        if finished_adding_vehicles():
            break

        if len(vehicles_remaining) == 1:
            print(f"Automatically adding last vehicle: {vehicles_remaining[0]['name']}")
            vehicles_selected.append(vehicles_remaining[0])
            vehicles_remaining.remove(vehicles_remaining[0])
            break

        vehicles_remaining, vehicles_selected = add_vehicle(vehicles_remaining, vehicles_selected)

    vehicles_selected = ask_for_distances(vehicles_selected)
    vehicles_selected = determine_emissions(vehicles_selected)
    print_emissions(vehicles_selected)

    if figure:
        make_figure(vehicles_selected)

    return 0


def load_vehicle_data():
    """
    Read all defined vehicle types from file
    :return vehicle_data (list of dicts):
    """

    def verify_vehicle_dict(vehicle):
        """ Check that the YAML file has all the required data for the calculation """
        required_data = ['name', 'litres_per_100km', 'co2_per_litre', 'num_passengers', 'travel_by']
        for field in required_data:
            assert field in vehicle
        assert isinstance(vehicle['name'], str)
        assert isinstance(vehicle['litres_per_100km'], (int, float))
        assert isinstance(vehicle['co2_per_litre'], (int, float))
        assert isinstance(vehicle['num_passengers'], (int, float))
        assert isinstance(vehicle['travel_by'], str)
        assert vehicle['travel_by'] in ('air', 'land', 'sea')

    vehicle_data = list()
    vehicle_files = os.listdir('vehicles')
    for vehicle in vehicle_files:
        with open("vehicles/" + vehicle, 'r') as stream:
            try:
                vehicle_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        verify_vehicle_dict(vehicle_dict)
        vehicle_data.append(vehicle_dict)
    return vehicle_data


def add_vehicle(vehicles_remaining, vehicles_selected=None):
    """ Prompt user to add vehicle to emissions calculation """
    if vehicles_selected is None:
        vehicles_selected = list()
    vehicle_names = [vehicle['name'] for vehicle in vehicles_remaining]
    question = [inquirer.List('vehicle', message='Choose a vehicle', choices=vehicle_names)]
    answer = inquirer.prompt(question)
    vehicle_dict = next(item for item in vehicles_remaining if item["name"] == answer['vehicle'])
    vehicles_selected.append(vehicle_dict)
    vehicles_remaining.remove(vehicle_dict)
    return vehicles_remaining, vehicles_selected


def finished_adding_vehicles():
    """ Ask user if they would like to add another vehicle to the calculation """
    question = [inquirer.List('continue', message='Add another vehicle', choices=['Yes', 'No'])]
    answer = inquirer.prompt(question)
    if answer['continue'] is 'Yes':
        return False
    else:
        return True


def ask_for_distances(vehicles):
    """ Ask user for the travel distances for the different vehicles """
    for vehicle in vehicles:
        name = vehicle['name'].lower()
        question = [inquirer.Text('distance', message=f"Distance by {name}")]
        answer = inquirer.prompt(question)
        if answer['distance'] == '':
            vehicle['distance'] = 0
        else:
            vehicle['distance'] = float(answer['distance'])
    return vehicles


def determine_emissions(vehicles):
    """ Generate dictionary storing vehicle names and emissions for the trip """

    def calculate_emissions(distance, fuel_consumption, co2_per_litre, num_passengers):
        """ Calculate the emissions for the given vehicle for the trip """
        litres_per_100km_to_litres_per_km = 1 / 100
        return distance * fuel_consumption * litres_per_100km_to_litres_per_km \
            * co2_per_litre * (1 / num_passengers)

    for vehicle in vehicles:
        vehicle['emissions'] = calculate_emissions(vehicle['distance'],
                                                   vehicle['litres_per_100km'],
                                                   vehicle['co2_per_litre'],
                                                   vehicle['num_passengers'])
    return vehicles


def print_emissions(vehicles):
    """ Print the emissions for the selected vehicles to the console """
    for vehicle in vehicles:
        print(f"{vehicle['name']} ({vehicle['distance']:0.0f} km): "
              f"{vehicle['emissions']:0.3f} kg/passenger")


def make_figure(vehicle_list):
    """ Generate PNG and PDF figures based on the user inputs """
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    print(f"\nGenerating figures...")

    # font display settings
    mpl.rc('text', usetex=True)
    mpl.rc('font', size=14)
    mpl.rc('axes', linewidth=1.5)
    mpl.rcParams['text.latex.preamble'] = [r'\usepackage{sfmath} \boldmath']

    emissions = [round(vehicle['emissions']) for vehicle in vehicle_list]
    names = [vehicle['name'] for vehicle in vehicle_list]

    # design, colours, and labels
    y_ticks = emissions
    y_label = r'\textbf{CO$_2$ emissions (kg / passenger)}'
    y_limits = (0, max(emissions) + 20)
    x_limits = (-1, len(vehicle_list))
    bar_width = 0.75
    colours = ('#377eb8', '#4daf4a', '#e41a1c')
    icon_width = 1
    icon_height = 0.7

    bars = plt.bar(range(len(vehicle_list)), emissions, bar_width)
    for bar, colour in zip(bars, colours):
        bar.set_color(colour)
    plt.xticks(range(len(vehicle_list)), names)
    plt.yticks(y_ticks)
    plt.ylim(y_limits)
    plt.xlim(x_limits)
    plt.ylabel(y_label)

    axes = plt.gca()
    axes.spines['right'].set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.tick_params('y', length=10, width=1.375, which='major', direction='in')
    axes.tick_params('x', length=5, width=1.375, which='major')

    # Bold font for x labels
    x_labels = [r'\textbf{{ {} }}'.format(name) for name in names]
    axes.set_xticklabels(x_labels)

    icons = os.listdir('icons')
    icons.sort()

    for ii, (icon, y) in enumerate(zip(icons, emissions)):
        try:
            image = plt.imread("icons/" + icon)
        except IOError as exc:
            print(exc)

        img_height, img_width, _ = image.shape
        max_dim = max(img_height, img_width)

        icon_axes = inset_axes(axes,
                               width=img_width * icon_width / max_dim,
                               height=img_height * icon_height / max_dim,
                               bbox_to_anchor=(ii, y + 2), loc=8,
                               bbox_transform=axes.transData,
                               borderpad=0)
        plt.imshow(image, interpolation='none')
        icon_axes.set_axis_off()

    fig = plt.gcf()
    fig.set_size_inches(5, 4.5)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig.tight_layout()
    plt.savefig('plots/emissions.pdf', dpi=300)
    plt.savefig('plots/emissions.png', dpi=300)


if __name__ == '__main__':
    sys.exit(main())
