"""Mapping Of EBUS Circuit Names To Human-readable Names."""


class CircuitMap(dict):
    """
    Mapping of EBUS-circuit names To human-readable Names.

    >>> c = CircuitMap({
    ...     'broadcast': '*',
    ...     'bai': 'Heater',
    ...     'mc': 'Mixer',
    ...     'hwc': 'Water',
    ... })
    >>> for circuitname, humanname in c.items():
    ...     print(circuitname, '=', humanname)
    broadcast = *
    bai = Heater
    mc = Mixer
    hwc = Water
    >>> tuple(c)
    ('broadcast', 'bai', 'mc', 'hwc')

    Custom mappigns are added dictionary-like.

    >>> c = CircuitMap()
    >>> c['bai'] = 'Heater'
    >>> c['boo'] = 'My Boo'
    >>> c['mc.4'] = 'Mixer Unit 2'
    """

    def get_humanname(self, circuitname):
        """
        Return human-readable name for `circuitname`.

        The `.X` suffix distinguishes multiple instances of the same unit, this is handled gracefully.

        Returns:
            str: human-readable name

        >>> c = CircuitMap({
        ...     'broadcast': '*',
        ...     'bai': 'Heater',
        ...     'mc': 'Mixer',
        ...     'hwc': 'Water',
        ... })
        >>> c.get_humanname('bai')
        'Heater'
        >>> c.get_humanname('bai.3')
        'Heater#3'
        >>> c.get_humanname('mc.4')
        'Mixer#4'
        >>> c.get_humanname('unknown')
        'unknown'
        >>> c.get_humanname('unknown.4')
        'unknown.4'
        """
        # lookup full name
        humanname = self.get(circuitname, None)
        # loopup basename
        if humanname is None and "." in circuitname:
            basename, suffix = circuitname.split(".")
            humanname = self.get(basename, None)
            if humanname is not None:
                humanname = f"{humanname}#{suffix}"
        # use circuitname as default
        if humanname is None:
            humanname = circuitname
        return humanname
