import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os

class InfluxDBClient:
    def __init__(self):
        self._bucket    = "myroom"
        self._org       = "newini"

        client = influxdb_client.InfluxDBClient(
            url     = "http://192.168.7.25:8086",
            token   = os.environ['INFLUXDB_TOKEN'],
            org     = self._org
        )

        self._write_api = client.write_api(write_options=SYNCHRONOUS)

    def write(self, point, field, value):
        p = influxdb_client.Point(point).field(field, value)
        try:
            self._write_api.write(bucket=self._bucket, org=self._org, record=p)
        except Exception as e:
            logging.error('Cannot write to InfluxDB server. %s' % e)
