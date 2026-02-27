from littup.services import init_db, triad_integrations


def test_integrations_present():
    init_db()
    data = triad_integrations()
    assert "Agentora" in data
    assert "Memoria" in data
    assert "Launchpad" in data
