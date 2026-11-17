import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import Client, TestCase
from apps.core.models import AlertStatus, EmergencyAlert, EstablishmentProfile, SafeHaven, VerificationStatus


class SafeHavenApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testorg', password='password123')
        self.profile = EstablishmentProfile.objects.create(
            user=self.user,
            organization_name='Test Sanctuary Org',
            contact_phone='0917-111-2222',
            verification_status=VerificationStatus.VERIFIED
        )

        # Haven 1: Near (10.3200, 123.8800)
        self.haven_near = SafeHaven.objects.create(
            establishment=self.profile,
            name='Near Haven',
            barangay='Guadalupe',
            city='Cebu City',
            province='Cebu',
            latitude=Decimal('10.3200'),
            longitude=Decimal('123.8800'),
            safe_phrase='"Secret Alpha"',
            is_active=True
        )

        # Haven 2: Far (10.3800, 123.9500)
        self.haven_far = SafeHaven.objects.create(
            establishment=self.profile,
            name='Far Haven',
            barangay='Talamban',
            city='Cebu City',
            province='Cebu',
            latitude=Decimal('10.3800'),
            longitude=Decimal('123.9500'),
            safe_phrase='"Secret Beta"',
            is_active=True
        )

        # Haven 3: Inactive
        self.haven_inactive = SafeHaven.objects.create(
            establishment=self.profile,
            name='Inactive Haven',
            barangay='Lahug',
            city='Cebu City',
            province='Cebu',
            latitude=Decimal('10.3300'),
            longitude=Decimal('123.8900'),
            safe_phrase='"Secret Gamma"',
            is_active=False
        )

    def test_geojson_endpoint_structure(self):
        response = self.client.get('/api/safe-havens/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertEqual(data['count'], 2)  # Inactive haven excluded

        feature = data['features'][0]
        self.assertEqual(feature['type'], 'Feature')
        self.assertEqual(feature['geometry']['type'], 'Point')
        self.assertIn('coordinates', feature['geometry'])
        self.assertIn('properties', feature)
        self.assertIn('safe_phrase', feature['properties'])
        self.assertIn('special_instructions', feature['properties'])

    def test_proximity_ordering(self):
        # Query near (10.3210, 123.8810), which is very close to haven_near
        response = self.client.get('/api/safe-havens/?lat=10.3210&lon=123.8810')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)
        # First haven should be haven_near
        self.assertEqual(data['features'][0]['properties']['id'], self.haven_near.id)
        self.assertIsNotNone(data['features'][0]['properties']['distance_km'])
        self.assertTrue('km away' in data['features'][0]['properties']['distance_text'])
        # Distance to near haven should be less than far haven
        dist_near = data['features'][0]['properties']['distance_km']
        dist_far = data['features'][1]['properties']['distance_km']
        self.assertLess(dist_near, dist_far)

    def test_text_search_filter(self):
        response = self.client.get('/api/safe-havens/?q=Talamban')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['features'][0]['properties']['name'], 'Far Haven')

    def test_discreet_ping_success(self):
        payload = {
            'haven_id': self.haven_near.id,
            'descriptors': ['Immediate Safe Room', 'Discrete Transport'],
            'notes': 'Approaching quietly'
        }
        response = self.client.post(
            '/api/discreet-ping/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('session_token', data)

        alert = EmergencyAlert.objects.get(id=data['alert_id'])
        self.assertEqual(alert.safe_haven, self.haven_near)
        self.assertEqual(alert.status, AlertStatus.RECEIVED)
        self.assertIn('Immediate Safe Room', alert.notes)

    def test_discreet_ping_inactive_haven(self):
        payload = {
            'haven_id': self.haven_inactive.id
        }
        response = self.client.post(
            '/api/discreet-ping/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['success'])

    def test_haven_address_property(self):
        self.assertEqual(self.haven_near.address, 'Guadalupe, Cebu City, Cebu')
