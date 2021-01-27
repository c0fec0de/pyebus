"""
Circuit Information.

Every EBUS Device has a common set of meta information:

* circuit: The unique circuit name within the bus infrastructure. Duplicates are separated be a suffix `.<idx>`.
* manufacturer: The circuit manufacturer
* model: The circuit model
* swversion: Software Version
* hwversion: Hardware Version
* address: EBUS address
"""
import collections

CircuitInfo = collections.namedtuple("CircuitInfo", "circuit manufacturer model swversion hwversion address")
