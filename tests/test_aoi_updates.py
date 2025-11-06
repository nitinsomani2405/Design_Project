from uav_aoi.aoi import AoIState


def test_aoi_increment_and_reset():
    aoi = AoIState.zeros(3)
    aoi.increment(5.0)
    assert aoi.values == [5.0, 5.0, 5.0]
    aoi.reset(1)
    assert aoi.values == [5.0, 0.0, 5.0]
    aoi.increment(2.5)
    assert aoi.values == [7.5, 2.5, 7.5]


