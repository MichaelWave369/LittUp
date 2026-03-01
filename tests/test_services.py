from littup.services import triad_integrations


def test_integrations_present():
    data = triad_integrations()
    assert "Agentora" in data
    assert "Memoria" in data
    assert "Launchpad" in data
