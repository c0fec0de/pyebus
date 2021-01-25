"""Message Prioritizer."""
import collections
import logging
from datetime import datetime, timedelta

from .msgdef import resolve_prio

_LOGGER = logging.getLogger(__name__)


class Prioritizer:

    """
    Prioritizer, creating best prio according to message change interval.

    Prio 1 is highest.
    The number of priorities is defined by the number of thresholds + 1.

    Args:
        thresholds: Iterable with seconds or :any:`timedelta` between priority levels.
    Keyword Args:
        intervals: Number of intervals the message update rate need to deviate in a row to get a new prio.
    """

    # pylint: disable=R0902
    def __init__(self, msgdefs, thresholds, intervals=3):
        self._msgdefs = msgdefs
        self._thresholds = tuple(_cast_threshold(threshold) for threshold in thresholds)
        self.intervals = intervals
        self.clear()

    def clear(self):
        """Clear."""
        self._msgtimestamps = {}
        self._msgprios = {}
        self._upfilter = collections.defaultdict(lambda: 0)
        self._dnfilter = collections.defaultdict(lambda: 0)
        self._msgpriochanges = {}

    @property
    def thresholds(self):
        """Thresholds."""
        return self._thresholds

    @property
    def maxprio(self):
        """
        Maximum Prio.

        The number of thresholds + 1.
        """
        return len(self._thresholds) + 1

    def set_prio(self, msgdef, prio):
        """Set Message Priority."""
        if msgdef.read:
            self._msgprios[msgdef.ident] = max(min(prio, self.maxprio), 0)
            self._clear_filter(msgdef.ident)

    def get_prio(self, msgdef):
        """Get Message Priority."""
        if msgdef.read:
            return self._get_prio(msgdef)
        else:
            return None

    def _get_prio(self, msgdef):
        try:
            return self._msgprios[msgdef.ident]
        except KeyError:
            return resolve_prio(msgdef)

    def iter_priochanges(self):
        """
        Iterate over done priority changes.

        Yields
            (MsgDef)
        """
        msgpriochanges = self._msgpriochanges
        while msgpriochanges:
            yield msgpriochanges.popitem()[1]

    def notify(self, msg):
        """Notify about received message."""
        msgdef = msg.msgdef
        if msg.valid and msgdef.read:
            msgtimestamps = self._msgtimestamps
            ident = msg.ident
            values = tuple(field.value for field in msg.fields)
            timestamp = datetime.now()
            if ident not in msgtimestamps:
                # unknown, store first entry
                msgtimestamps[ident] = (timestamp, values)
                prio = msgdef.setprio or msgdef.prio or self._get_prio(msg.msgdef)
                self._msgprios[ident] = prio
                _LOGGER.debug("Init   %s, prio=%d", ident, prio)
            else:
                (lasttimestamp, lastvalues) = msgtimestamps[ident]
                age = timestamp - lasttimestamp
                prio = self._get_prio(msg.msgdef)
                is_const = values == lastvalues
                older = prio < self.maxprio and age > self._thresholds[prio - 1]
                newer = prio > 1 and age < self._thresholds[prio - 2]
                _LOGGER.debug(
                    "Notify %s: age=%r prio=%r is_const=%r older=%r newer=%r", ident, age, prio, is_const, older, newer
                )
                # check for increment
                #   - reset filter, if not const
                #   - increment, if constant value is older than actual threshold for number of intervals
                if not is_const or older:
                    if self._filter(self._upfilter, ident, is_const or older):
                        _LOGGER.debug("Inc!   %s", ident)
                        self._set_prio(ident, prio + 1)
                    msgtimestamps[ident] = (timestamp, values)
                # check for decrement
                #   - reset filter, if constant value
                if self._filter(self._dnfilter, ident, not is_const and newer):
                    _LOGGER.debug("Dec!   %s", ident)
                    self._set_prio(ident, prio - 1)

    def _set_prio(self, ident, prio):
        self._msgprios[ident] = prio
        msgdef = self._msgdefs.get_ident(ident)
        self._msgpriochanges[ident] = msgdef.replace(setprio=prio)

    def _clear_filter(self, ident):
        self._upfilter[ident] = 0
        self._dnfilter[ident] = 0

    def _filter(self, cnts, ident, cond):
        cnt = cnts[ident]
        if cond and cnt < self.intervals:
            cnt += 1
            cond = False
        else:
            cnt = 0
        cnts[ident] = cnt
        return cond


def _cast_threshold(threshold):
    if not isinstance(threshold, timedelta):
        threshold = timedelta(seconds=threshold)
    return threshold
