"""MDI Icon Utility."""
from . import types


def get_icon(fielddef, state=None):
    """
    Return Appropriate mdi-icon_ for `fielddef` at `state`.

    .. _mdi-icon: https://materialdesignicons.com/


    >>> from pyebus import FieldDef, types
    >>> get_icon(FieldDef(0, 'name', types.FloatType(), unit='°C'))
    'mdi:thermometer'
    >>> get_icon(FieldDef(0, 'name', types.TimeType()))
    'mdi:timer'
    >>> get_icon(FieldDef(0, 'name', types.EnumType(('on', 'off'))))
    'mdi:toggle-switch'
    >>> get_icon(FieldDef(0, 'name', types.EnumType(('on', 'off'))), 'off')
    'mdi:toggle-switch-off'
    >>> get_icon(FieldDef(0, 'name', types.EnumType(('on', 'off'))), 'on')
    'mdi:toggle-switch'
    """
    type_ = fielddef.type_
    if fielddef.unit in ("°C", "K", "°F"):
        return "mdi:thermometer"
    elif isinstance(type_, (types.TimeType, types.DateType, types.DateTimeType, types.HourMinuteType)):
        return "mdi:timer"
    elif isinstance(type_, types.EnumType):
        if tuple(sorted(type_.values)) in [("off", "on"), ("no", "yes")]:
            if state in (False, "off", "no"):
                return "mdi:toggle-switch-off"
            else:
                return "mdi:toggle-switch"
    return None
