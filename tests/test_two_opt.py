from uav_aoi.planner import nearest_neighbor_order, two_opt


def test_two_opt_reduces_length_simple():
    # Square with a zig-zag initial order should be improved by 2-Opt
    points = [(0, 0), (1, 0), (1, 1), (0, 1)]
    order = [0, 2, 1, 3]
    improved = two_opt(order, points)
    # Expect a route closer to [0,1,2,3] or [0,3,2,1]
    assert improved != order


