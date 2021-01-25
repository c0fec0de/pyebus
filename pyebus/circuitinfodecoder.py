"""Cirucit Information Decoder."""
import re

from .circuitinfo import CircuitInfo

_RE_CIRCUIT = re.compile(
    r'^address ([0-9a-f]{2}): .*"MF=([^;]+);ID=([^;]+);SW=([^;]+);HW=([^"]+)", loaded.*".*\.([a-z]+(\.\d+)?)\.csv"'
)

# pylint: disable=C0301


def decode_circuitinfos(info):
    """
    Decode Circuit Information.

    Args:
        info: dict or list of strings.

    >>> info = {
    ...     "version": "ebusd 21.1.v21.1-12-gccfc025",
    ...     "update check": "version 3.4 available",
    ...     "signal": "acquired",
    ...     "symbol rate": "48",
    ...     "max symbol rate": "229",
    ...     "min arbitration micros": "301",
    ...     "max arbitration micros": "3550",
    ...     "min symbol latency": "2",
    ...     "max symbol latency": "15",
    ...     "reconnects": "0",
    ...     "masters": "7",
    ...     "messages": "1006",
    ...     "conditional": "14",
    ...     "poll": "171",
    ...     "update": "10",
    ...     "address 03": "master #11",
    ...     'address 08': 'slave #11, scanned "MF=Vaillant;ID=BAI00;SW=0204;HW=9602", loaded "vaillant/bai.0010015600.inc" ([HW=9602]), "vaillant/08.bai.csv"',
    ...     "address 10": "master #2",
    ...     'address 15': 'slave #2, scanned "MF=Vaillant;ID=UI   ;SW=0508;HW=6201", loaded "vaillant/15.ui.csv"',
    ...     "address 17": "master #17",
    ...     'address 1c': 'slave #17, scanned "MF=Vaillant;ID=RC C ;SW=0508;HW=6201", loaded "vaillant/1c.rcc.4.csv"',
    ...     'address 23': 'slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/23.vr630.cc.csv"',
    ...     'address 25': 'slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/25.vr630.hwc.csv"',
    ...     'address 26': 'slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/26.vr630.hc.csv"',
    ...     "address 31": "master #8, ebusd",
    ...     "address 36": "slave #8, ebusd",
    ...     "address 37": "master #18",
    ...     'address 3c': 'slave #18, scanned "MF=Vaillant;ID=RC C ;SW=0508;HW=6201", loaded "vaillant/3c.rcc.5.csv"',
    ...     'address 50': 'slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/50.vr630.mc.csv"',
    ...     'address 51': 'slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/51.vr630.mc.3.csv"',
    ...     'address 52': 'slave, scanned "MF=Vaillant;ID=MC2  ;SW=0500;HW=6301", loaded "vaillant/52.mc2.mc.4.csv"',
    ...     'address 53': 'slave, scanned "MF=Vaillant;ID=MC2  ;SW=0500;HW=6301", loaded "vaillant/53.mc2.mc.5.csv"',
    ...     "address 70": "master #4",
    ...     'address 75': 'slave #4, scanned "MF=Vaillant;ID=RC C ;SW=0508;HW=6201", loaded "vaillant/75.rcc.csv"',
    ...     "address f0": "master #5",
    ...     'address f5': 'slave #5, scanned "MF=Vaillant;ID=RC C ;SW=0508;HW=6201", loaded "vaillant/f5.rcc.3.csv"',
    ... }
    >>> for circuitinfo in decode_circuitinfos(info):
    ...     print(circuitinfo)
    CircuitInfo(circuit='bai', manufacturer='Vaillant', model='BAI00', swversion='0204', hwversion='9602', address=8)
    CircuitInfo(circuit='cc', manufacturer='Vaillant', model='VR630', swversion='0500', hwversion='6301', address=35)
    CircuitInfo(circuit='hc', manufacturer='Vaillant', model='VR630', swversion='0500', hwversion='6301', address=38)
    CircuitInfo(circuit='hwc', manufacturer='Vaillant', model='VR630', swversion='0500', hwversion='6301', address=37)
    CircuitInfo(circuit='mc', manufacturer='Vaillant', model='VR630', swversion='0500', hwversion='6301', address=80)
    CircuitInfo(circuit='mc.3', manufacturer='Vaillant', model='VR630', swversion='0500', hwversion='6301', address=81)
    CircuitInfo(circuit='mc.4', manufacturer='Vaillant', model='MC2', swversion='0500', hwversion='6301', address=82)
    CircuitInfo(circuit='mc.5', manufacturer='Vaillant', model='MC2', swversion='0500', hwversion='6301', address=83)
    CircuitInfo(circuit='rcc', manufacturer='Vaillant', model='RC C', swversion='0508', hwversion='6201', address=117)
    CircuitInfo(circuit='rcc.3', manufacturer='Vaillant', model='RC C', swversion='0508', hwversion='6201', address=245)
    CircuitInfo(circuit='rcc.4', manufacturer='Vaillant', model='RC C', swversion='0508', hwversion='6201', address=28)
    CircuitInfo(circuit='rcc.5', manufacturer='Vaillant', model='RC C', swversion='0508', hwversion='6201', address=60)
    CircuitInfo(circuit='ui', manufacturer='Vaillant', model='UI', swversion='0508', hwversion='6201', address=21)
    """
    circuitinfos = []
    if isinstance(info, dict):
        info = [f"{key}: {value}" for key, value in info.items()]
    for line in info:
        mat = _RE_CIRCUIT.match(line)
        if mat:
            address, manufacturer, model, swversion, hwversion, circuit, _ = mat.groups()
            circuitinfos.append(
                CircuitInfo(
                    circuit.strip(),
                    manufacturer.strip(),
                    model.strip(),
                    swversion.strip(),
                    hwversion.strip(),
                    int(address, 16),
                )
            )
    return tuple(sorted(circuitinfos, key=lambda circuitinfo: circuitinfo.circuit))
