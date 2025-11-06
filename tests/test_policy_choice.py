from uav_aoi.planner import policy_awn


def test_awn_prefers_higher_aoi_and_closer():
    aoi = [1.0, 10.0]
    uav_pos = (0.0, 0.0)
    nodes = [(100.0, 0.0), (10.0, 0.0)]
    # With beta=1, gamma=1, node 1 has much higher AoI and closer distance
    j = policy_awn(aoi, uav_pos, nodes, beta=1.0, gamma=1.0)
    assert j == 1


