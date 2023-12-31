"""Defines trends calculations for stations"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


app = faust.App("stations", broker="kafka://localhost:9092", store="memory://")
topic = app.topic("com.udacity.johnson.cta.jdbc.v1.stations", value_type=Station)
out_topic = app.topic("com.udacity.johnson.cta.stations.table.v1", partitions=1, value_type=TransformedStation)
table = app.Table(
   "stations", default=TransformedStation,
   partitions=1,
   changelog_topic=out_topic,
)


@app.agent(topic)
async def station(stations):
    async for station in stations:
        # Figure out which lines this station belongs too
        if station.red: line = "red"
        elif station.blue: line = "blue"
        elif station.green: line = "green"
        else: line = "error"

        # Package it all into a nice transformed station
        table[station.station_id] = TransformedStation(
            station_id = station.station_id,
            station_name = station.station_name,
            order = station.order,
            line = line
        )
        print(f'{table[station.station_id]}')

if __name__ == "__main__":
    app.main()
