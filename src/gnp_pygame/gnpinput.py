"""Module containing input routines"""
import pygame
import unittest

HOLD = pygame.USEREVENT + 1  # 31 is the max ID for a USER event
AXISPRESS = HOLD + 1
AXISRELEASE = AXISPRESS + 1
# Design goal: Keep the structure of AXISPRESS and AXISRELEASE similar to other button
# UP and DOWN events. This consistency will make it easier to use the AXIS events.
# (for instance, generating HOLD events will be easier).


def _make_hold_dict_key(event):
    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
        return pygame.KEYDOWN, event.key  # initiating event
    elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
        return pygame.MOUSEBUTTONDOWN, event.button
    elif event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
        return pygame.JOYBUTTONDOWN, (event.joy, event.button)
    elif event.type in (AXISPRESS, AXISRELEASE):
        return AXISPRESS, (event.joy, event.axis, event.value)
    return None


class HoldWatcher(object):
    """Examine events in input queue and synthesize user events"""
    def __init__(self):
        self._holdTimers = {}  # key=synthesized ID, value=float used as countdown timer

    def get(self, events, delta):
        """Pass it an input stream that it will use to Synthesize new events and posts them to event queue"""
        self.step(delta)
        for e in events:
            if _make_hold_dict_key(e) in self._holdTimers.keys():
                del self._holdTimers[_make_hold_dict_key(e)]
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN, AXISPRESS):
                self._holdTimers[_make_hold_dict_key(e)] = 2.0
        return events

    def step(self, delta):
        to_del = []
        for k in self._holdTimers:
            self._holdTimers[k] -= delta
            if self._holdTimers[k] <= 0.0:
                orig_event_type, data = k
                if orig_event_type == pygame.KEYDOWN:
                    new_event = pygame.event.Event(HOLD, origtype=orig_event_type, key=data)
                elif orig_event_type == pygame.MOUSEBUTTONDOWN:
                    new_event = pygame.event.Event(HOLD, origtype=orig_event_type, button=data)
                elif orig_event_type == pygame.JOYBUTTONDOWN:
                    new_event = pygame.event.Event(HOLD, origtype=orig_event_type, joyid=data[0], button=data[1])
                elif orig_event_type == AXISPRESS:
                    new_event = pygame.event.Event(HOLD, origtype=orig_event_type, joyid=data[0], axis=data[1], value=data[2])
                else:
                    raise Exception('Unrecognized event (%d) for HOLD event' % orig_event_type)
                pygame.event.post(new_event)
                to_del.append(k)
        for k in to_del:
            self._holdTimers.pop(k)


class AxisWatcher(object):
    def __init__(self, num_joys, num_axes_per_joy, press_threshold, reset_threshold):
        self._axisLast = [[0]*num_axes_per_joy for x in range(num_joys)]  # _axis_last[joy_id][axis_id]
        self._press_thresh = press_threshold  # value the axis must go beyond to register a pressed event, used only by ProcessAxisStream
        self._reset_thresh = reset_threshold  # value the axis mst go below to clear previous pressed event to be ready for another, used only by ProcessAxisStream

    def _process(self, event):
        """Given an event, returns a list of resulting synthesized events"""
        synth_events = []
        if event.type != pygame.JOYAXISMOTION:
            return synth_events

        if event.value >= -self._reset_thresh and self._axisLast[event.joy][event.axis] == -1:
            self._axisLast[event.joy][event.axis] = 0
            synth_events.append(pygame.event.Event(AXISRELEASE, joy=event.joy, axis=event.axis, value=-1, label='AXISRELEASE'))
        if event.value <= self._reset_thresh and self._axisLast[event.joy][event.axis] == 1:
            self._axisLast[event.joy][event.axis] = 0
            synth_events.append(pygame.event.Event(AXISRELEASE, joy=event.joy, axis=event.axis, value=1, label='AXISRELEASE'))

        if event.value >= self._press_thresh and self._axisLast[event.joy][event.axis] != 1:
            self._axisLast[event.joy][event.axis] = 1
            synth_events.append(pygame.event.Event(AXISPRESS, joy=event.joy, axis=event.axis, value=1, label='AXISPRESS'))
        if event.value <= -self._press_thresh and self._axisLast[event.joy][event.axis] != -1:
            self._axisLast[event.joy][event.axis] = -1
            synth_events.append(pygame.event.Event(AXISPRESS, joy=event.joy, axis=event.axis, value=-1, label='AXISPRESS'))

        return synth_events

    def get(self, events):
        """process event list and post any synthesized events to event queue, returning original event list"""
        for evt in events:
            synth_events = self._process(evt)
            for synth_event in synth_events:
                pygame.event.post(synth_event)
        return events


# Helper functions for testing
def _axismotion(value):
    return pygame.event.Event(pygame.JOYAXISMOTION, joy=0, axis=0, value=value)


def _axispress(value):
    return pygame.event.Event(AXISPRESS, joy=0, axis=0, value=value, label='AXISPRESS')


def _axisrelease(value):
    return pygame.event.Event(AXISRELEASE, joy=0, axis=0, value=value, label='AXISRELEASE')


class AxisWatcherTests(unittest.TestCase):
    longMessage = True  # appends custom assert message to end of default message

    def _run_data_driven_tests(self, *args):
        chunk_size = 2
        for idx in range(0, len(args), chunk_size):
            event, expected = args[idx:idx + chunk_size]
            result = self.w._process(event)
            # print 'result', result
            # print 'expected', expected
            self.assertListEqual(result, expected, 'Assertion failed at list index #%d. %d item(s) in result list. %d item(s) in expected list.' % (idx, len(result), len(expected)))

    def setUp(self):
        self.w = AxisWatcher(1, 1, 8, 5)
        self.pressneg = _axispress(-1)
        self.presspos = _axispress(1)
        self.releaseneg = _axisrelease(-1)
        self.releasepos = _axisrelease(1)

    def test_empty_result(self):
        self._run_data_driven_tests(
            _axismotion(0),
            [],
        )

    def test_empty_result_with_motion(self):
        self._run_data_driven_tests(
            _axismotion(0),
            [],
            _axismotion(7),
            [],
            _axismotion(-7),
            [],
            _axismotion(0),
            [],
        )

    def test_press(self):
        self._run_data_driven_tests(
            _axismotion(0),
            [],
            _axismotion(8),
            [self.presspos],
        )

    def test_press_negative(self):
        self._run_data_driven_tests(
            _axismotion(0),
            [],
            _axismotion(-8),
            [self.pressneg],
        )

    def test_press_with_no_starting_motion_event(self):
        self._run_data_driven_tests(
            _axismotion(8),
            [self.presspos],
        )

    def test_press_with_no_starting_motion_event_negative(self):
        self._run_data_driven_tests(
            _axismotion(-8),
            [self.pressneg],
        )

    def test_press_and_release(self):
        self._run_data_driven_tests(
            _axismotion(8),
            [self.presspos],
            _axismotion(5),
            [self.releasepos],
        )

    def test_press_and_movement_towards_release_with_no_release(self):
        self._run_data_driven_tests(
            _axismotion(8),
            [self.presspos],
            _axismotion(7),
            [],
            _axismotion(9),
            [],
        )

    def test_press_and_movement_towards_release_with_no_release_negative(self):
        self._run_data_driven_tests(
            _axismotion(-8),
            [self.pressneg],
            _axismotion(-7),
            [],
            _axismotion(-9),
            [],
        )

    def test_both_extremes(self):
        self._run_data_driven_tests(
            _axismotion(0),
            [],
            _axismotion(8),
            [self.presspos],
            _axismotion(0),
            [self.releasepos],
            _axismotion(-8),
            [self.pressneg],
            _axismotion(0),
            [self.releaseneg],
            _axismotion(8),
            [self.presspos],
            _axismotion(0),
            [self.releasepos],
        )

    def test_fast_transition_between_extremes(self):
        self._run_data_driven_tests(
            _axismotion(0),
            [],
            _axismotion(8),
            [self.presspos],
            _axismotion(-8),
            [self.releasepos, self.pressneg],
            _axismotion(8),
            [self.releaseneg, self.presspos],
            _axismotion(-8),
            [self.releasepos, self.pressneg],
            _axismotion(0),
            [self.releaseneg],
        )

    def test_fast_transition_between_extremes_reverse_direction(self):
        self._run_data_driven_tests(
            _axismotion(0),
            [],
            _axismotion(-8),
            [self.pressneg],
            _axismotion(8),
            [self.releaseneg, self.presspos],
            _axismotion(0),
            [self.releasepos],
        )

    def test_long_sequence(self):
        self._run_data_driven_tests(
            _axismotion(7),
            [],
            _axismotion(-7),
            [],
            _axismotion(9),
            [self.presspos],
            _axismotion(10),
            [],
            _axismotion(-7),
            [self.releasepos],
            _axismotion(-8),
            [self.pressneg],
            _axismotion(-10),
            [],
            _axismotion(-6),
            [],
            _axismotion(-9),
            [],
            _axismotion(2),
            [self.releaseneg],
            _axismotion(-8),
            [self.pressneg],
            _axismotion(10),
            [self.releaseneg, self.presspos],
            _axismotion(4),
            [self.releasepos],
            _axismotion(10),
            [self.presspos],
        )


if __name__ == '__main__':
    unittest.main()
    # unittest.main(defaultTest='JoystickStickStreamTests.test_increasing')
