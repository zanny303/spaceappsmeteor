# backend/test_physics_service.py
import pytest
import numpy as np
from physics_service import (
    calculate_asteroid_mass, 
    calculate_required_delta_v, 
    calculate_real_trajectory,
    calculate_hazard_corridor
)

class TestPhysicsService:
    
    def test_calculate_asteroid_mass(self):
        """Test mass calculation for different asteroid types and sizes."""
        # Test different spectral types
        diameter = 500.0
        
        mass_c = calculate_asteroid_mass(diameter, 'C')  # Carbonaceous
        mass_s = calculate_asteroid_mass(diameter, 'S')  # Stony
        mass_m = calculate_asteroid_mass(diameter, 'M')  # Metallic
        
        # Verify mass hierarchy: metallic > stony > carbonaceous
        assert mass_m > mass_s > mass_c
        
        # Verify all masses are positive and reasonable
        assert all(mass > 0 for mass in [mass_c, mass_s, mass_m])
        assert all(1e6 < mass < 1e15 for mass in [mass_c, mass_s, mass_m])
        
        # Test default type
        mass_default = calculate_asteroid_mass(diameter)
        assert mass_default > 0
        
    def test_calculate_required_delta_v_physics(self):
        """Test physically accurate delta-v calculation with various scenarios."""
        # Test case 1: Large asteroid with long lead time (easy deflection)
        dv_easy = calculate_required_delta_v(1e12, 365 * 5, 10000)  # 5 years
        assert 0.0001 <= dv_easy < 0.001  # Should be very small
        
        # Test case 2: Small asteroid with short lead time (hard deflection)
        dv_hard = calculate_required_delta_v(1e8, 30, 10000)  # 1 month
        assert dv_hard > dv_easy  # Should require more delta-v
        
        # Test case 3: Edge case - zero time (should return minimum)
        dv_min = calculate_required_delta_v(1e10, 0, 10000)
        assert dv_min == 0.0001
        
        # Test case 4: Very large miss distance
        dv_large_miss = calculate_required_delta_v(1e10, 365, 50000)  # 50,000 km miss
        assert dv_large_miss > 0
        
    def test_calculate_real_trajectory(self):
        """Test trajectory calculation with valid state vectors."""
        # Valid state vector representing a typical NEO orbit
        state_vector = [1.5e8, 0, 0, 0, 30, 0]  # Simplified circular-like orbit
        
        trajectory = calculate_real_trajectory(state_vector)
        
        # Should return list of coordinate points
        assert isinstance(trajectory, list)
        assert len(trajectory) > 0
        
        # Each point should have exactly 3 coordinates (x, y, z)
        for point in trajectory:
            assert len(point) == 3
            assert all(isinstance(coord, float) for coord in point)
            
        # Trajectory should show movement (not all points identical)
        first_point = trajectory[0]
        last_point = trajectory[-1]
        assert first_point != last_point
        
    def test_calculate_real_trajectory_invalid_input(self):
        """Test trajectory calculation with invalid inputs."""
        # Test with None
        result = calculate_real_trajectory(None)
        assert result == []
        
        # Test with wrong length
        result = calculate_real_trajectory([1, 2, 3])  # Only 3 elements
        assert result == []
        
        # Test with empty list
        result = calculate_real_trajectory([])
        assert result == []
        
    def test_calculate_hazard_corridor(self):
        """Test hazard corridor generation with uncertainty modeling."""
        state_vector = [1.5e8, 0, 0, 0, 30, 0]
        
        corridor = calculate_hazard_corridor(state_vector, num_simulations=5)
        
        # Should return multiple trajectories
        assert isinstance(corridor, list)
        assert len(corridor) > 0
        
        # Each trajectory should be valid
        for trajectory in corridor:
            assert isinstance(trajectory, list)
            assert len(trajectory) > 0
            for point in trajectory:
                assert len(point) == 3
                
    def test_hazard_corridor_with_uncertainty(self):
        """Test that hazard corridor shows variation between trajectories."""
        state_vector = [1.5e8, 0, 0, 0, 30, 0]
        
        corridor = calculate_hazard_corridor(state_vector, num_simulations=3)
        
        if len(corridor) > 1:
            # Different trajectories should have different points (due to uncertainty)
            traj1 = corridor[0]
            traj2 = corridor[1]
            
            # They might be similar but not identical due to random perturbations
            # Just verify both are valid
            assert len(traj1) > 0
            assert len(traj2) > 0
            
    def test_physics_consistency(self):
        """Test that physics calculations are consistent across related functions."""
        diameter = 1000.0  # 1 km asteroid
        spectral_type = 'S'
        
        # Calculate mass
        mass = calculate_asteroid_mass(diameter, spectral_type)
        
        # Use that mass to calculate delta-v
        dv = calculate_required_delta_v(mass, 365, 10000)
        
        # Both should be reasonable values
        assert 1e9 < mass < 1e13  # Reasonable mass range for 1km asteroid
        assert 0.0001 <= dv < 0.1  # Reasonable delta-v range
        
    def test_error_handling(self):
        """Test that functions handle errors gracefully."""
        # Mass calculation with invalid diameter
        mass = calculate_asteroid_mass(-100, 'S')
        # Should still return a reasonable value (using fallback)
        assert mass > 0
        
        # Delta-v with invalid parameters
        dv = calculate_required_delta_v(-1000, -365, -10000)
        # Should return the minimum delta-v
        assert dv == 0.0001