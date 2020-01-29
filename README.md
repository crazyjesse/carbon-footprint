# carbon-footprint

### Install

1. Clone the repo
2. `python3 -m venv env`
3. `pip install -r requirements`

### Usage

Run the following:
```bash
source env/bin/activate
python -m trip_calculation --distance DISTANCE --air-distance AIR_DISTANCE --figure TRUE_OR_FALSE
```

The options set:
* `distance`: the travel distance by land
* `air-distance`: the travel distance by air
* `figure`: if the PDF figure should be generated

### Vehicles

New vehicles can be added by adding YAML files to the vehicles directory.
A vehicle file must have five fields. 

An example of the file for car travel is shown here:
```yaml
name: "Car"
litres_per_100km: 7
co2_per_litre: 2.024
num_passengers: 5
travel_by: 'land'
```