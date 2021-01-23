"""Dummy Data."""


class DummyData:
    """Dummy Data."""

    def __init__(self):
        self.info = [
            "version: ebusd 21.1.v21.1-12-gccfc025",
            "update check: version 3.4 available",
            "signal: acquired",
            "symbol rate: 48",
            "max symbol rate: 229",
            "min arbitration micros: 301",
            "max arbitration micros: 3550",
            "min symbol latency: 2",
            "max symbol latency: 15",
            "reconnects: 0",
            "masters: 7",
            "messages: 1006",
            "conditional: 14",
            "poll: 171",
            "update: 10",
            "address 03: master #11",
            'address 08: slave #11, scanned "MF=Vaillant;ID=BAI00;SW=0204;HW=9602", loaded "vaillant/bai.0010015600.inc" ([HW=9602]), "vaillant/08.bai.csv"',  # pylint: disable=C0301
            "address 10: master #2",
            'address 15: slave #2, scanned "MF=Vaillant;ID=UI   ;SW=0508;HW=6201", loaded "vaillant/15.ui.csv"',
            "address 17: master #17",
            'address 1c: slave #17, scanned "MF=Vaillant;ID=RC C ;SW=0508;HW=6201", loaded "vaillant/1c.rcc.4.csv"',
            'address 23: slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/23.vr630.cc.csv"',
            'address 25: slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/25.vr630.hwc.csv"',
            'address 26: slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/26.vr630.hc.csv"',
            "address 31: master #8, ebusd",
            "address 36: slave #8, ebusd",
            "address 37: master #18",
            'address 3c: slave #18, scanned "MF=Vaillant;ID=RC C ;SW=0508;HW=6201", loaded "vaillant/3c.rcc.5.csv"',
            'address 50: slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/50.vr630.mc.csv"',
            'address 51: slave, scanned "MF=Vaillant;ID=VR630;SW=0500;HW=6301", loaded "vaillant/51.vr630.mc.3.csv"',
            'address 52: slave, scanned "MF=Vaillant;ID=MC2  ;SW=0500;HW=6301", loaded "vaillant/52.mc2.mc.4.csv"',
            'address 53: slave, scanned "MF=Vaillant;ID=MC2  ;SW=0500;HW=6301", loaded "vaillant/53.mc2.mc.5.csv"',
            "address 70: master #4",
            'address 75: slave #4, scanned "MF=Vaillant;ID=RC C ;SW=0508;HW=6201", loaded "vaillant/75.rcc.csv"',
            "address f0: master #5",
            'address f5: slave #5, scanned "MF=Vaillant;ID=RC C ;SW=0508;HW=6201", loaded "vaillant/f5.rcc.3.csv"',
        ]
        self.state = "signal acquired, 111 symbols/sec (229 max), 7 masters"

        self.finddef = [
            "r,bai,AntiCondensValue,power,s,UCH,,kW,Anhebung der minimalen Leistung",
            "[SW>=413]r,bai,APCLegioProtection,,s,UCH,,,Legionellenschutz für internen Speicher",
            "r,bai,averageIgnitiontime,,s,UCH,10,s,Mittlere Zündzeit",
            "r,bai,BlockTimeHcMax,minutes0,s,UCH,,min,Max. Brennersperrzeit bei einem Vorlaufsollwert von 20°C",
            "r,bai,BoilerType,,s,UCH,,,Boiler typ of the bmu",
            "r,bai,ChangesDSN,,s,UCH,,,Anzahl der DSN (Gerätekennung) Änderungen",
            "r,bai,CirPump,onoff,s,UCH,0=off;1=on,,Status Zirkulationspumpe (über ein externes Modul ansteuerbar)",
            "r,bai,CodingResistor,,s,HEX:3,,,Therme Identifikation Widerstand",
            "r,bai,CounterStartattempts1,temp0,s,UCH,,°C,Anzahl der erfolglosen Zündversuche (im 1. Versuch)",
            "r,bai,CounterStartattempts2,temp0,s,UCH,,°C,Anzahl der erfolglosen Zündversuche (im 2. Versuch)",
            "r,bai,CounterStartAttempts3,temp0,s,UCH,,°C,Anzahl der erfolglosen Zündversuche (im 3. Versuch)",
            "r,bai,CounterStartAttempts4,temp0,s,UCH,,°C,Anzahl der erfolglosen Zündversuche (im 4. Versuch)",
            "r,bai,dcfState,dcfstate,s,UCH,0=nosignal;1=ok;2=sync;3=valid,,DCF Status",
            "r,bai,DCRoomthermostat,onoff,s,UCH,0=off;1=on,,Wärmeanforderung vom externen Regler (Klemme 3-4)",
            "r,bai,DeactivationsTemplimiter,,s,UCH,,,Anzahl der Abschaltungen durch den Sicherheitstemperaturbgrenzers",
            "r,bai,DeltaFlowReturnMax,temp,s,D2C,,°C,Wartungsdaten",
            "r,bai,DisplayMode,,s,UCH,,,Display mode of the aplliance",
            "r,bai,DSN,,s,UIN,,,DSN: Device Specific number",
            "r,bai,DSNOffset,,s,UCH,,,Gerätekennung (DSN)",
            "r,bai,DSNStart,,s,UIN,,,DSN Startadresse",
            "r,bai,EbusSourceOn,onoff,s,UCH,0=off;1=on,,Aktivierung der eBUS Speisung",
            "r,bai,EbusVoltage,onoff,s,UCH,0=off;1=on,,Rückmeldung der eBUS Spannung",
            "r,bai,ExternalFaultmessage,onoff,s,UCH,0=off;1=on,,Signal für die externe Störmeldeeinrichtung",
            "r,bai,ExternGasvalve,onoff,s,UCH,0=off;1=on,,Externes Magnetventil",
            "r,bai,ExtFlowTempDesiredMin,temp,s,D2C,,°C,minimum out of Kl.7 and eBus flow setpoint",
            "r,bai,ExtStorageModulCon,yesno,s,UCH,0=no;1=yes,,Externes Speichermodul (VR65) angeschlosssen",
            "r,bai,extWP,onoff,s,UCH,0=off;1=on,,Externe Heizungspumpe",
            "r,bai,FanHours,hoursum2,s,UIN,,h,Betriebsstunden des Lüfters",
            "scan",
            "rw,bai,FlowTemp,temp,s,D2C,,°C,Vorlauftemperatur,sensor,s,UCH,0=ok;85=circuit;170=cutoff,,Fühlerstatus",
            "rw,bai,FanPWMSum,,s,UIN,,,Predictive Maintenance data for the fan damage recognition",
            "r,bai,FanPWMTest,,s,UCH,,,Predictive Maintenance data for the fan damage recognition",
        ]
        self.finddata = ["bai FlowTemp = 6.125;ok"]

        self.listen = [
            "bai FlowTemp = 0.125;ok",
            "bai FlowTemp = 1.125;ok",
            "bai FlowTemp = 2.125;ok",
            "bai FlowTemp = broken;-",
            "bai FlowTemp2 = broken;-",
            "bai FlowTemp = 3.125;ok",
        ]
