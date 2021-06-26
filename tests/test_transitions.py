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
