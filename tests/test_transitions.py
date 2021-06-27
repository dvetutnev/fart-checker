from transitions import Machine
from unittest.mock import Mock


def test_action():
    class Model(object):
        pushByte = Mock()

    states = ["Wait start byte", "Receive"]
    transitions = [
        {"trigger": "ByteEvent", "source": "Wait start byte", "dest": "Receive", "before": "pushByte"},
    ]

    fsm = Model()
    defFSM = Machine(model=fsm, states=states, transitions=transitions, initial="Wait start byte")

    assert fsm.state == "Wait start byte"

    fsm.trigger("ByteEvent")

    assert fsm.state == "Receive"

    fsm.pushByte.assert_called()


def test_event_with_data():
    class Model(object):
        pushByte = Mock()

    states = ["Wait start byte", "Receive"]
    transitions = [
        {"trigger": "ByteEvent", "source": "Wait start byte", "dest": "Receive", "before": "pushByte"},
    ]

    fsm = Model()
    defFSM = Machine(model=fsm, states=states, transitions=transitions, initial="Wait start byte")

    fsm.trigger("ByteEvent", 0xF7)

    fsm.pushByte.assert_called_with(0xF7)


def test_conditions():
    class Model(object):
        isStartByte = Mock()
        pushByte = Mock()

    states = ["Wait start byte", "Receive"]
    transitions = [
        {"trigger": "ByteEvent", "source": "Wait start byte", "dest": "Receive", "conditions": "isStartByte", "before": "pushByte"},
    ]

    fsm = Model()
    defFSM = Machine(model=fsm, states=states, transitions=transitions, initial="Wait start byte")

    fsm.isStartByte.side_effect = [False, False, True]

    fsm.trigger("ByteEvent", 0x11)
    fsm.trigger("ByteEvent", 0x22)

    fsm.pushByte.assert_not_called()

    fsm.trigger("ByteEvent", 0x33)

    fsm.pushByte.assert_called_once()
