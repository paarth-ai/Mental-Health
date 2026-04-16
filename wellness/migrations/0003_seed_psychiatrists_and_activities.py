# Generated data migration: seed sample psychiatrists and physical activities

from decimal import Decimal
from django.db import migrations


def seed_psychiatrists(apps, schema_editor):
    Psychiatrist = apps.get_model('wellness', 'Psychiatrist')
    data = [
        {'name': 'Dr. Sarah Chen', 'specialty': 'Anxiety & Depression', 'address': '123 Main St, New York, NY',
         'latitude': Decimal('40.7128'), 'longitude': Decimal('-74.0060'), 'phone': '+1-212-555-0101', 'email': 'schen@example.com'},
        {'name': 'Dr. James Wilson', 'specialty': 'General Psychiatry', 'address': '456 Oak Ave, Los Angeles, CA',
         'latitude': Decimal('34.0522'), 'longitude': Decimal('-118.2437'), 'phone': '+1-310-555-0202', 'email': 'jwilson@example.com'},
        {'name': 'Dr. Maria Garcia', 'specialty': 'Mood Disorders', 'address': '789 Pine Rd, Chicago, IL',
         'latitude': Decimal('41.8781'), 'longitude': Decimal('-87.6298'), 'phone': '+1-312-555-0303', 'email': 'mgarcia@example.com'},
        {'name': 'Dr. David Kim', 'specialty': 'Trauma & PTSD', 'address': '321 Elm St, Houston, TX',
         'latitude': Decimal('29.7604'), 'longitude': Decimal('-95.3698'), 'phone': '+1-713-555-0404', 'email': 'dkim@example.com'},
        {'name': 'Dr. Emily Brown', 'specialty': 'Child & Adolescent', 'address': '555 Maple Dr, Phoenix, AZ',
         'latitude': Decimal('33.4484'), 'longitude': Decimal('-112.0740'), 'phone': '+1-602-555-0505', 'email': 'ebrown@example.com'},
    ]
    for item in data:
        name = item.pop('name')
        Psychiatrist.objects.get_or_create(name=name, defaults=item)


def seed_activities(apps, schema_editor):
    PhysicalActivity = apps.get_model('wellness', 'PhysicalActivity')
    data = [
        {'name': 'Walking', 'description': 'A gentle outdoor walk improves mood and energy. Start with 15–20 minutes.', 'intensity': 'light', 'duration_suggestion': '15–30 min', 'order': 1},
        {'name': 'Stretching outdoors', 'description': 'Light stretching in a park or garden helps reduce tension and anxiety.', 'intensity': 'light', 'duration_suggestion': '10–15 min', 'order': 2},
        {'name': 'Yoga in the park', 'description': 'Outdoor yoga combines movement, breath, and nature for mental clarity.', 'intensity': 'light', 'duration_suggestion': '20–45 min', 'order': 3},
        {'name': 'Outdoor Meditation', 'description': 'Sitting quietly in nature calms the mind and reduces anxiety. Focus on breathing and natural sounds.', 'intensity': 'light', 'duration_suggestion': '10–30 min', 'order': 3.5},
        {'name': 'Cycling', 'description': 'Bike ride at a comfortable pace. Great for energy and concentration.', 'intensity': 'moderate', 'duration_suggestion': '20–40 min', 'order': 4},
        {'name': 'Jogging', 'description': 'Steady jogging outdoors releases endorphins and supports sleep and mood.', 'intensity': 'moderate', 'duration_suggestion': '15–30 min', 'order': 5},
        {'name': 'Hiking', 'description': 'Trail walking in nature reduces stress and improves overall wellbeing.', 'intensity': 'moderate', 'duration_suggestion': '30–60 min', 'order': 6},
        {'name': 'Swimming', 'description': 'Outdoor or pool swimming is a full-body, low-impact activity.', 'intensity': 'moderate', 'duration_suggestion': '20–40 min', 'order': 7},
        {'name': 'Dancing outdoors', 'description': 'Outdoor dancing boosts mood, energy, and social connection while improving cardiovascular health.', 'intensity': 'vigorous', 'duration_suggestion': '20–45 min', 'order': 8.5},
        {'name': 'Running', 'description': 'Running outdoors boosts energy and can improve sleep and focus.', 'intensity': 'vigorous', 'duration_suggestion': '20–45 min', 'order': 8},
        {'name': 'Rock Climbing', 'description': 'Outdoor rock climbing builds confidence, focus, and problem-solving skills while providing intense physical exercise.', 'intensity': 'vigorous', 'duration_suggestion': '45–90 min', 'order': 9.5},
        {'name': 'Team sports', 'description': 'Basketball, soccer, or similar outdoor sports add social connection and exercise.', 'intensity': 'vigorous', 'duration_suggestion': '45–60 min', 'order': 9},
    ]
    for item in data:
        name = item.pop('name')
        PhysicalActivity.objects.get_or_create(name=name, defaults=item)


def reverse_seed(apps, schema_editor):
    Psychiatrist = apps.get_model('wellness', 'Psychiatrist')
    PhysicalActivity = apps.get_model('wellness', 'PhysicalActivity')
    Psychiatrist.objects.all().delete()
    PhysicalActivity.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0002_add_user_profile_psychiatrist_activities'),
    ]

    operations = [
        migrations.RunPython(seed_psychiatrists, reverse_seed),
        migrations.RunPython(seed_activities, reverse_seed),
    ]
