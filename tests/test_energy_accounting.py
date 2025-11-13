from uav_aoi.env import (
    energy_fly_Wh,
    energy_hover_Wh,
    energy_tx_Wh,
    flight_time_s,
    propulsion_power,
    _compute_induced_velocity,
    _compute_induced_power,
)


def test_energy_totals_toy_path():
    """Test energy calculations with Zeng propulsion model."""
    # Create a test UAV config
    uav_cfg = {
        'mass_kg': 1.5,
        'g': 9.81,
        'rotor_radius_m': 0.15,
        'blade_tip_speed': 140.0,
        'rotor_solidity': 0.05,
        'P0': 10.0,
        'Pi': None,  # Will be computed
        'd0': 0.3,
        'air_density': 1.225,
    }
    
    # Test config for transmission
    tx_cfg = {
        'P_circuit_W': 1.0,
        'amp_efficiency': 0.4,
        'P_out_W': 1.0,
    }
    
    d = 120.0
    v = 12.0
    
    # Test flight time
    t_f = flight_time_s(d, v)
    assert abs(t_f - 10.0) < 1e-6
    
    # Test energy calculations with Zeng model
    e_f = energy_fly_Wh(d, v, uav_cfg)
    e_h = energy_hover_Wh(10.0, uav_cfg)
    e_t = energy_tx_Wh(5.0, tx_cfg)
    
    # Simple consistency checks
    assert e_f > 0 and e_h > 0 and e_t > 0
    assert e_f < 10.0  # Should be reasonable for 120m at 12 m/s


def test_propulsion_power_hover():
    """Test that propulsion_power(0) ≈ P0 + Pi (hover power)."""
    uav_cfg = {
        'mass_kg': 1.5,
        'g': 9.81,
        'rotor_radius_m': 0.15,
        'blade_tip_speed': 140.0,
        'rotor_solidity': 0.05,
        'P0': 10.0,
        'Pi': None,
        'd0': 0.3,
        'air_density': 1.225,
    }
    
    v0 = _compute_induced_velocity(uav_cfg)
    Pi = _compute_induced_power(uav_cfg, v0)
    P_hover_expected = uav_cfg['P0'] + Pi
    
    # Power at zero speed should be approximately hover power
    P_at_zero = propulsion_power(0.0, uav_cfg, v0=v0, Pi=Pi)
    
    # Should be very close to P0 + Pi (within 1% due to numerical precision)
    assert abs(P_at_zero - P_hover_expected) / P_hover_expected < 0.01


def test_propulsion_power_monotonicity():
    """Test that P(v) increases monotonically for large v (drag dominates)."""
    uav_cfg = {
        'mass_kg': 1.5,
        'g': 9.81,
        'rotor_radius_m': 0.15,
        'blade_tip_speed': 140.0,
        'rotor_solidity': 0.05,
        'P0': 10.0,
        'Pi': None,
        'd0': 0.3,
        'air_density': 1.225,
    }
    
    v0 = _compute_induced_velocity(uav_cfg)
    Pi = _compute_induced_power(uav_cfg, v0)
    
    # Test at increasing speeds
    P_v10 = propulsion_power(10.0, uav_cfg, v0=v0, Pi=Pi)
    P_v20 = propulsion_power(20.0, uav_cfg, v0=v0, Pi=Pi)
    P_v30 = propulsion_power(30.0, uav_cfg, v0=v0, Pi=Pi)
    
    # Power should increase with speed (drag term v^3 dominates)
    assert P_v20 > P_v10
    assert P_v30 > P_v20


def test_energy_hover_vs_simple_model():
    """Compare new hover energy with old simple model for sanity check."""
    uav_cfg = {
        'mass_kg': 1.5,
        'g': 9.81,
        'rotor_radius_m': 0.15,
        'blade_tip_speed': 140.0,
        'rotor_solidity': 0.05,
        'P0': 10.0,
        'Pi': None,
        'd0': 0.3,
        'air_density': 1.225,
    }
    
    t_hover = 10.0
    e_hover_new = energy_hover_Wh(t_hover, uav_cfg)
    
    # Should be reasonable (not negative, not infinite)
    assert e_hover_new > 0
    assert e_hover_new < 100.0  # Sanity check: 10 seconds should not consume 100 Wh
    
    # Compare with old simple model approximation (P_hover ≈ 20-30 W typical)
    # New model should give similar order of magnitude
    e_hover_approx_old = (25.0 * t_hover) / 3600.0
    # Allow wide range for different UAV configs
    assert abs(e_hover_new - e_hover_approx_old) / e_hover_approx_old < 5.0  # Within 5x is reasonable


def test_transmission_energy():
    """Test transmission energy with circuit power and PA efficiency."""
    tx_cfg = {
        'P_circuit_W': 1.0,
        'amp_efficiency': 0.4,
        'P_out_W': 2.0,  # Output power
    }
    
    t_tx = 5.0
    e_tx = energy_tx_Wh(t_tx, tx_cfg)
    
    # Expected: P_tx = 1.0 + 2.0/0.4 = 1.0 + 5.0 = 6.0 W
    # E_tx = 6.0 * 5.0 / 3600.0 = 30.0 / 3600.0 ≈ 0.00833 Wh
    expected_P_tx = 1.0 + (2.0 / 0.4)  # 6.0 W
    expected_E_tx = (expected_P_tx * t_tx) / 3600.0
    
    assert abs(e_tx - expected_E_tx) < 1e-6


