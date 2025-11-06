from uav_aoi.env import energy_fly_Wh, energy_hover_Wh, energy_tx_Wh, flight_time_s


def test_energy_totals_toy_path():
    d = 120.0
    v = 12.0
    Pm = 180.0
    Ph = 140.0
    Pt = 2.0
    t_f = flight_time_s(d, v)
    e_f = energy_fly_Wh(d, v, Pm)
    e_h = energy_hover_Wh(10.0, Ph)
    e_t = energy_tx_Wh(5.0, Pt)
    # Simple consistency checks
    assert abs(t_f - 10.0) < 1e-6
    assert e_f > 0 and e_h > 0 and e_t > 0
    assert e_f < (Pm * 20.0) / 3600.0


