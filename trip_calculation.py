import os
import sys
import click
import yaml


@click.command()
@click.option('--distance', required=True, type=click.FloatRange(min=0))
@click.option('--air-distance', required=True, type=click.FloatRange(min=0))
@click.option('--figure', type=click.BOOL, default=False)
def main(distance, air_distance, figure):
    vehicle_list = make_emissions_dict(distance, air_distance)

    for vehicle in vehicle_list:
        print(f"{vehicle['name']} ({vehicle['distance']:0.0f} km): "
              f"{vehicle['emissions']:0.3f} kg/passenger")

    if figure:
        make_figure(vehicle_list)

    return 0


def make_emissions_dict(distance, air_distance):
    """ Generate dictionary storing vehicle names and emissions for the trip """
    vehicles = os.listdir('vehicles')
    vehicles.sort()
    vehicle_list = list()

    for vehicle in vehicles:
        with open("vehicles/" + vehicle, 'r') as stream:
            try:
                vehicle_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        verify_vehicle_dict(vehicle_dict)
        if vehicle_dict['travel_by'] == 'air':
            vehicle_distance = air_distance
        else:
            vehicle_distance = distance
        vehicle_dict['emissions'] = calculate_emissions(vehicle_distance, vehicle_dict)
        vehicle_dict['distance'] = vehicle_distance
        vehicle_list.append(vehicle_dict)

    return vehicle_list


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
    assert vehicle['travel_by'] in ('air', 'land')


def calculate_emissions(distance, vehicle_dict):
    """ Calculate the emissions for the given vehicle for the trip """
    fuel_consumption = vehicle_dict['litres_per_100km']
    co2_per_litre = vehicle_dict['co2_per_litre']
    num_passengers = vehicle_dict['num_passengers']
    carbon_emissions = distance * fuel_consumption * \
                       (co2_per_litre / 100) * \
                       (1 / num_passengers)
    return carbon_emissions


def make_figure(vehicle_list):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    # font display settings
    mpl.rc('text', usetex=True)
    mpl.rc('font', size=14)
    mpl.rc('axes', linewidth=1.5)
    mpl.rcParams['text.latex.preamble'] = [r'\usepackage{sfmath} \boldmath']

    emissions = [vehicle['emissions'] for vehicle in vehicle_list]
    names = [vehicle['name'] for vehicle in vehicle_list]

    # design, colours, and labels
    y_ticks = [round(emission) for emission in emissions]
    y_label = r'\textbf{CO$_2$ emissions (kg / passenger)}'
    y_limits = (0, 150)
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
    fig.tight_layout()
    plt.savefig('plots/emissions.pdf')


if __name__ == '__main__':
    sys.exit(main())
