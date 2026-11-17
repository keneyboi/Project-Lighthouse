import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import Client, TestCase
from apps.core.models import EstablishmentProfile, SafeHaven


class LocationManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sanctuary_admin', password='testpassword123')
        self.profile = EstablishmentProfile.objects.create(
            user=self.user,
            organization_name='Downtown Haven Collective'
        )

        self.other_user = User.objects.create_user(username='other_admin', password='testpassword123')
        self.other_profile = EstablishmentProfile.objects.create(
            user=self.other_user,
            organization_name='Other Org'
        )

        # Haven 1 owned by self.user
        self.haven1 = SafeHaven.objects.create(
            establishment=self.profile,
            name='Uptown Safe Desk',
            barangay='Guadalupe',
            city='Cebu City',
            province='Cebu',
            latitude=Decimal('10.3235'),
            longitude=Decimal('123.8821'),
            safe_phrase='"Blue Door"',
            is_active=True
        )

        # Haven 2 owned by self.other_user
        self.haven_other = SafeHaven.objects.create(
            establishment=self.other_profile,
            name='Foreign Haven',
            barangay='Mandaue',
            city='Mandaue City',
            province='Cebu',
            latitude=Decimal('10.3400'),
            longitude=Decimal('123.9300'),
            is_active=True
        )

    def test_anonymous_redirect(self):
        response = self.client.get('/location/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_manage_locations_view_authenticated(self):
        self.client.login(username='sanctuary_admin', password='testpassword123')
        response = self.client.get('/location/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'location/manage_locations.html')
        self.assertContains(response, 'Uptown Safe Desk')
        self.assertNotContains(response, 'Foreign Haven')  # Isolation check

    def test_create_location_ajax(self):
        self.client.login(username='sanctuary_admin', password='testpassword123')
        payload = {
            'name': 'New Harbor Point',
            'barangay': 'Lahug',
            'city': 'Cebu City',
            'province': 'Cebu',
            'latitude': 10.3340,
            'longitude': 123.8995,
            'safe_phrase': '"Safe Journey"',
            'special_instructions': 'Private intake room',
            'is_active': True
        }
        response = self.client.post(
            '/location/create/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['haven']['name'], 'New Harbor Point')

        # Verify in DB
        created = SafeHaven.objects.get(id=data['haven']['id'])
        self.assertEqual(created.establishment, self.profile)
        self.assertEqual(created.latitude, Decimal('10.3340'))

    def test_edit_location_get_and_post(self):
        self.client.login(username='sanctuary_admin', password='testpassword123')
        
        # GET details
        get_res = self.client.get(f'/location/edit/{self.haven1.id}/')
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()['haven']['name'], 'Uptown Safe Desk')

        # POST updates
        update_data = {
            'name': 'Updated Safe Desk',
            'barangay': 'Guadalupe Central',
            'city': 'Cebu City',
            'province': 'Cebu',
            'latitude': 10.3250,
            'longitude': 123.8830,
            'safe_phrase': '"Green Light"',
            'is_active': False
        }
        post_res = self.client.post(
            f'/location/edit/{self.haven1.id}/',
            data=json.dumps(update_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(post_res.status_code, 200)
        self.assertTrue(post_res.json()['success'])

        self.haven1.refresh_from_db()
        self.assertEqual(self.haven1.name, 'Updated Safe Desk')
        self.assertFalse(self.haven1.is_active)

    def test_toggle_status_ajax(self):
        self.client.login(username='sanctuary_admin', password='testpassword123')
        self.assertTrue(self.haven1.is_active)

        response = self.client.post(
            f'/location/update-status/{self.haven1.id}/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['is_active'])

        self.haven1.refresh_from_db()
        self.assertFalse(self.haven1.is_active)

    def test_delete_location(self):
        self.client.login(username='sanctuary_admin', password='testpassword123')
        haven_id = self.haven1.id

        response = self.client.post(
            f'/location/delete/{haven_id}/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        self.assertFalse(SafeHaven.objects.filter(id=haven_id).exists())

    def test_cannot_modify_other_user_haven(self):
        self.client.login(username='sanctuary_admin', password='testpassword123')
        
        # Try to delete other user's haven
        res = self.client.post(f'/location/delete/{self.haven_other.id}/')
        self.assertEqual(res.status_code, 404)

        # Try to toggle other user's haven
        res_toggle = self.client.post(f'/location/update-status/{self.haven_other.id}/')
        self.assertEqual(res_toggle.status_code, 404)
