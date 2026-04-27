from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, UTC
import time
import pandas as pd



class InfluxBase:
    """Provide necessary attributes for database connection"""

    def __init__(self):
        self.write_called = False
        self.write_api = None
        self.query_api = None
        self.url = "https://eu-central-1-1.aws.cloud2.influxdata.com/"
        self.token = "mgFpC0vmS6Mn9Yc9XJcd1_wweo35NMOWe-2ET31CO9y6-ppBYYfoTUgDd8i0AqrnA3ze9NzLm3BIPkHnZe1asg=="
        self.org = "Student project"
        self.bucket = "reactor_test"
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

    # "__enter__" and "__exit__"  are magical/special methods. These allow this class to become context manager

    def __enter__(self): # This method executes when program uses "with". It usually prepares the DB connection, but this is already done in "__init__"
                         # This method returns an instance to the "variable" that called the class
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): # This method starts at the end of "with" block" regardless of error.
                                                   # It tidies up the work (closes files, database connection etc.)
                                                   # Python automatically sends information to the attributes had any error occurs.
        self.client.close()
        print("Connection closed.")


class Data_Write(InfluxBase):
    """Send data to database"""

    def __init__(self):
        """Initialize a connection with database"""
        super().__init__()

        self.write_called = True

    def initial_data(self):
        """Manually creates data"""

        point = (
            Point("reactor_metrics_test2")
            .field("fuel_reactivity", 8.905)
            .field("orm_value", 125.0)
            .field("partially_inserted", 1.0)
            .field("inlet_temp_c", 275.0)
            .field("outlet_temp_c", 280.0)
            .field("coolant_flow_m3h", 43000.0)
            .field("tau", 8.0)
            .field("thermal_power_mw", 3000.0)
            .field("reactivity_delta", 1.0)
            .field("xenon_level", 0.5)
            .field("neutron_flux_pct", 100.0)
            .field("severity_level", 0.8)
            .field("subsystem", "a")
            .field("alarm_message", "b")
            .time(datetime.now(UTC), WritePrecision.NS)
        )

        print(point.to_line_protocol())
        self.send_data(point)


    def generated_data(self, **data):
        """Takes data and converts to InfluxDB scheme"""

        point = Point("reactor_metrics_test2")
        for key, value in data.items():
            point = point.field(key, value)
            print(value, key)

        point = point.time(datetime.now(UTC), WritePrecision.NS)

        self.send_data(point)

    def send_data(self, point):
        """Sends the data to database"""

        with self.client.write_api(write_options=SYNCHRONOUS) as self.write_api:
            try:
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            except Exception as e:
                print("Write error: ", e)



class Data_Read(InfluxBase):
    """Take data from database"""

    def __init__(self):
        """Initialize the "___init__()" method from parent class."""

        super().__init__()

    def take_data(self):
        """ Take data from the database"""

        print(self.bucket)
        self.query = '''
            from(bucket: "reactor_test")
              |> range(start: -24h)
              |> filter(fn: (r) => r._measurement == "reactor_metrics_test2")
              |> filter(fn: (r) =>
                  contains(
                    value: r._field,
                    set: [
                      "fuel_reactivity",
                      "orm_value",
                      "partially_inserted",
                      "inlet_temp_c",
                      "outlet_temp_c",
                      "coolant_flow_m3h",
                      "tau",
                      "thermal_power_mw",
                      "reactivity_delta",
                      "xenon_level",
                      "neutron_flux_pct",
                      "severity_level",
                      "subsystem",
                      "alarm_message"
                    ]

                  )

                )
        '''
        with self.client.query_api() as self.query_api:
            try:
                self.tables = self.query_api.query(self.query, org=self.org)
            except Exception as e:
                print("Write error: ", e)

    def influx_to_df(self):
        """Transform InfluxDB output scheme to dictionary for DataFrame"""

        self.conv_data = {}
        time_list = []

        for table in self.tables: # We do not need to create sophisticated code or utilize libraries, because all tables have one consistent timestamp and there is no tag.
            value_list = []
            if not time_list: # "time_list" collects timestamp for each record. If "time_list" is empty, this will fill the list with timestamps
                              # Since this database has one consistent timestamp for each record, we can collect it only once for the entire loop.

                for record in table.records:
                    dt = record.get_time()
                    time_list.append(dt.strftime("%Y-%m-%d %H:%M:%S"))

            # Code below appends values from table to "value_list" list and field to a single variable "field_key"
            # Then we do dictionary nesting, treating appending value as a list to a single key
            # The dictionary is as follows: field_key (key): value_list (value)

            for record in table.records:
                value_list.append(record.get_value())
                field_key = record.get_field()

            self.conv_data[f'{field_key}'] = value_list

        self.conv_data['time'] = time_list

        self.df = pd.DataFrame(self.conv_data)
        self.df.to_csv("out.csv", index=False)



#         for table in tables:
#             for record in table.records:
#                 print(
#                     "time:", record.get_time(),
#                     "value:", record.get_value(),
#                     "type:", type(record.get_value()),
#                     "field:", record.get_field(),
#                     "measurement:", record.get_measurement()
#                 )
#                 break



data = {
    "fuel_reactivity": 5.905,
    "orm_value": 105,
    "partially_inserted": 0,
    "inlet_temp_c": 270.0,
    "outlet_temp_c": 284.0,
    "coolant_flow_m3h": 45000.0,
    "tau": 10.0,
    "thermal_power_mw": 3200.0,
    "reactivity_delta": 0.0,
    "xenon_level": 1.0,
    "neutron_flux_pct": 95.0,
    "severity_level": 1,
    "subsystem": "a",
    "alarm_message": "b",
}

approve = input("Type 'y' if you want to write data, type 'n' if you don't: ")

if approve == "y":
    with Data_Write() as write:
        write.initial_data()
        time.sleep(2)

approve = input("Type 'y' if you want to download data, type 'n' if you don't: ")

if approve == "y":
    with Data_Read() as take:
        take.take_data()
        take.influx_to_df()
        time.sleep(2)



