# backend/sample_data.py - COMPLETE FIXED VERSION
"""
Sample asteroid data for Apollo asteroid 99942 Apophis.
Used as fallback when NASA API is unavailable or for testing.
"""

# Real data sample for Asteroid 99942 Apophis (2004 MN4)
apophis_data = {
    "id": "2099942",
    "name": "99942 Apophis (2004 MN4)",
    "neo_reference_id": "2099942",
    "designation": "99942 Apophis",
    "name_limited": "Apophis",
    "absolute_magnitude_h": 19.7,
    
    "estimated_diameter": {
        "kilometers": {
            "estimated_diameter_min": 0.310273612,
            "estimated_diameter_max": 0.6937923332
        },
        "meters": {
            "estimated_diameter_min": 310.2736119973,
            "estimated_diameter_max": 693.7923331601
        },
        "miles": {
            "estimated_diameter_min": 0.192795,
            "estimated_diameter_max": 0.431102
        },
        "feet": {
            "estimated_diameter_min": 1017.957,
            "estimated_diameter_max": 2276.222
        }
    },
    
    "is_potentially_hazardous_asteroid": True,
    "is_sentry_object": True,
    
    "close_approach_data": [
        {
            "close_approach_date": "2029-04-13",
            "close_approach_date_full": "2029-Apr-13 21:46",
            "epoch_date_close_approach": 1870314360000,
            
            "relative_velocity": {
                "kilometers_per_second": "7.429",
                "kilometers_per_hour": "26744.400000",
                "miles_per_hour": "16621.858"
            },
            
            "miss_distance": {
                "astronomical": "0.000211664",
                "lunar": "0.082337296",
                "kilometers": "31664.5",
                "miles": "19677.4"
            },
            
            "orbiting_body": "Earth"
        }
    ],
    
    "orbital_data": {
        "orbit_id": "76",
        "orbit_determination_date": "2023-05-10 06:54:17",
        "first_observation_date": "2004-03-15",
        "last_observation_date": "2023-03-22",
        "data_arc_in_days": 6947,
        "observations_used": 6313,
        "orbit_uncertainty": "0",
        
        "minimum_orbit_intersection": ".000211664",
        "jupiter_tisserand_invariant": "4.893",
        "epoch_osculation": "2460000.5",
        "eccentricity": ".1913418326607589",
        "semi_major_axis": ".9220643078838003",
        "inclination": "3.338266848246426",
        "ascending_node_longitude": "204.4498476653895",
        "orbital_period": "323.596223845963",
        "perihelion_distance": ".746028054637722",
        "perihelion_argument": "126.4052314925678",
        "aphelion_distance": "1.098100561129879",
        "perihelion_time": "2460008.744237656831",
        "mean_anomaly": "145.2240657069799",
        "mean_motion": "1.112194497393101",
        "equinox": "J2000",
        
        "orbit_class": {
            "orbit_class_type": "ATE",
            "orbit_class_description": "Near-Earth asteroid orbits similar to that of 2062 Aten",
            "orbit_class_range": "a (semi-major axis) < 1.0 AU; q (perihelion) > 0.983 AU"
        }
    },
    
    # Additional computed fields for our application
    "spectral_type": "S",  # Stony type asteroid
    "albedo": 0.23,  # Typical for S-type asteroids
    "rotation_period": 30.4,  # Hours
    "physical_characteristics": {
        "density_kg_m3": 2700,
        "mass_kg": 2.7e10,
        "composition": "Silicate rocks with nickel-iron"
    }
}

# Additional sample asteroids for testing - FIXED with close_approach_data
sample_asteroids = {
    "101955": {  # Bennu - OSIRIS-REx target
        "id": "2101955",
        "name": "101955 Bennu (1999 RQ36)",
        "absolute_magnitude_h": 20.4,
        "estimated_diameter": {
            "meters": {
                "estimated_diameter_min": 420.0,
                "estimated_diameter_max": 580.0
            }
        },
        "close_approach_data": [{
            "close_approach_date": "2135-09-25",
            "close_approach_date_full": "2135-Sep-25 12:00",
            "relative_velocity": {
                "kilometers_per_second": "7.2",
                "kilometers_per_hour": "25920.0"
            },
            "miss_distance": {
                "kilometers": "750000",
                "miles": "466028"
            },
            "orbiting_body": "Earth"
        }],
        "is_potentially_hazardous_asteroid": True,
        "spectral_type": "B"  # Carbonaceous
    },
    
    "25143": {  # Itokawa - Hayabusa target
        "id": "2025143", 
        "name": "25143 Itokawa (1998 SF36)",
        "absolute_magnitude_h": 19.2,
        "estimated_diameter": {
            "meters": {
                "estimated_diameter_min": 330.0,
                "estimated_diameter_max": 530.0
            }
        },
        "close_approach_data": [{
            "close_approach_date": "2030-04-15",
            "close_approach_date_full": "2030-Apr-15 08:30",
            "relative_velocity": {
                "kilometers_per_second": "8.1",
                "kilometers_per_hour": "29160.0"
            },
            "miss_distance": {
                "kilometers": "1500000",
                "miles": "932057"
            },
            "orbiting_body": "Earth"
        }],
        "is_potentially_hazardous_asteroid": False,
        "spectral_type": "S"  # Stony
    },
    
    "65803": {  # Didymos - DART mission target
        "id": "2065803",
        "name": "65803 Didymos (1996 GT)",
        "absolute_magnitude_h": 18.0,
        "estimated_diameter": {
            "meters": {
                "estimated_diameter_min": 780.0,
                "estimated_diameter_max": 850.0
            }
        },
        "close_approach_data": [{
            "close_approach_date": "2123-11-20",
            "close_approach_date_full": "2123-Nov-20 15:45",
            "relative_velocity": {
                "kilometers_per_second": "6.1",
                "kilometers_per_hour": "21960.0"
            },
            "miss_distance": {
                "kilometers": "11000000",
                "miles": "6835083"
            },
            "orbiting_body": "Earth"
        }],
        "is_potentially_hazardous_asteroid": False,
        "spectral_type": "S"  # Stony
    }
}

def get_sample_asteroid(asteroid_id):
    """Get sample data for specified asteroid ID."""
    if asteroid_id == "99942":
        return apophis_data.copy()
    elif asteroid_id in sample_asteroids:
        return sample_asteroids[asteroid_id].copy()
    else:
        # Return Apophis as default
        return apophis_data.copy()