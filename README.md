We will be using the open data from Citi Bike.

Download the stations' information [here](https://gbfs.citibikenyc.com/gbfs/en/station_information.json).

Download trips' data from 2024-01 [here](https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.csv.zip).

Create a virtual environment:
```
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

And run the simulation with the following command:
```
python3 newplace.py
```