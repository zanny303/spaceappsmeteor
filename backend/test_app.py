# backend/test_app.py
import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestAppEndpoints:
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'services' in data
        assert 'ai_model_status' in data
        assert 'version' in data
        
        print(f"✅ Health check: {data['status']}, AI: {data['ai_model_status']}")
    
    def test_full_analysis_missing_asteroid_id(self, client):
        """Test full analysis with missing asteroid ID."""
        response = client.post('/api/full_analysis', json={})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'asteroid_id is required' in data['error']
    
    def test_full_analysis_empty_asteroid_id(self, client):
        """Test full analysis with empty asteroid ID."""
        response = client.post('/api/full_analysis', json={'asteroid_id': ''})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_full_analysis_invalid_asteroid_id(self, client):
        """Test full analysis with invalid asteroid ID format."""
        response = client.post('/api/full_analysis', json={'asteroid_id': 'invalid!@#'})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_full_analysis_success(self, client):
        """Test successful full analysis with Apophis."""
        response = client.post('/api/full_analysis', json={'asteroid_id': '99942'})
        
        # Should return successful response
        assert response.status_code == 200
        
        data = response.get_json()
        
        # Verify response structure
        assert 'asteroid_info' in data
        assert 'mission_recommendation' in data
        assert 'ai_predicted_consequences' in data
        assert 'visualization_data' in data
        assert 'mission_parameters' in data
        assert 'analysis_metadata' in data
        
        # Verify asteroid info
        asteroid_info = data['asteroid_info']
        assert asteroid_info['name'] == '99942 Apophis (2004 MN4)'
        assert 'diameter_m' in asteroid_info
        assert 'velocity_kms' in asteroid_info
        
        # Verify mission recommendation
        mission_rec = data['mission_recommendation']
        assert 'source' in mission_rec
        assert 'interceptor_type' in mission_rec
        assert 'confidence_score' in mission_rec
        assert 'rationale' in mission_rec
        
        # Verify AI consequences
        consequences = data['ai_predicted_consequences']
        assert 'economic_damage_usd' in consequences
        assert 'predicted_casualties' in consequences
        assert 'impact_energy_megatons' in consequences
        
        # Verify mission parameters
        params = data['mission_parameters']
        assert 'lti_days' in params
        assert 'required_dv_ms' in params
        assert 'calculated_mass_kg' in params
        
        # Verify analysis metadata
        metadata = data['analysis_metadata']
        assert 'version' in metadata
        assert 'model_type' in metadata
        assert 'ai_model_loaded' in metadata
        
        print(f"✅ Full analysis: {asteroid_info['name']}")
        print(f"   Mission: {mission_rec['source']} - {mission_rec['interceptor_type']}")
        print(f"   Confidence: {mission_rec['confidence_score']}%")
        print(f"   AI Model: {'Loaded' if metadata['ai_model_loaded'] else 'Not loaded'}")
    
    def test_recalculate_trajectory_missing_params(self, client):
        """Test trajectory recalc with missing parameters."""
        response = client.post('/api/recalculate_trajectory', json={})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_recalculate_trajectory_invalid_state_vector(self, client):
        """Test trajectory recalc with invalid state vector."""
        invalid_data = {
            'initial_state_vector': [1, 2, 3],  # Wrong length
            'required_dv_ms': 0.005
        }
        
        response = client.post('/api/recalculate_trajectory', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_generate_pdf_no_data(self, client):
        """Test PDF generation with no mission plan data."""
        response = client.post('/api/generate_pdf', json={})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_rate_limiting(self, client):
        """Test rate limiting on analysis endpoint."""
        # Make multiple rapid requests
        for i in range(15):
            response = client.post('/api/full_analysis', json={'asteroid_id': '99942'})
        
        # Should eventually get rate limited (status 429)
        assert response.status_code == 429
        
        data = response.get_json()
        assert 'error' in data
        assert 'Rate limit exceeded' in data['error']
    
    def test_invalid_json(self, client):
        """Test endpoints with invalid JSON."""
        response = client.post('/api/full_analysis', data='invalid json', 
                             content_type='application/json')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_cors_headers(self, client):
        """Test that CORS headers are present."""
        response = client.get('/api/health')
        
        # Should have CORS headers in development
        assert 'Access-Control-Allow-Origin' in response.headers
        
        origin = response.headers.get('Access-Control-Allow-Origin')
        assert origin in ['http://localhost:3000', 'http://127.0.0.1:3000']