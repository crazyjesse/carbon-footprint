# carbon-footprint

### Install

The commands listed below will:
1. Clone the repo
2. Create a virtual environment
3. Activate the virtual environment
4. Install the required packages

```bash
git clone https://github.com/carbon-footprint/carbon-footprint.git
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```


### Usage

To run the script type the command:
```bash
python3 footprint.py
```
The program will prompt you for information about your trip.

Optionally you can add the `--figure` flag to generate PNG and PDF figures of the emissions data.
```bash
python3 footprint.py --figure
```


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
