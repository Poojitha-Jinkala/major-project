"""
Seed script — run with: python manage.py shell < seed_data.py
Creates sample elections and candidates for testing.
"""
import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')
django.setup()

from django.contrib.auth.models import User
from voting.models import Election, Candidate

# ── Create superuser ──────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@voting.com', 'Admin@1234')
    print("Superuser created: admin / Admin@1234")
else:
    admin = User.objects.get(username='admin')
    print("Superuser already exists.")

now = timezone.now()

# ── Election 1: Active ────────────────────────────────────────────────────────
e1, _ = Election.objects.get_or_create(
    title="General Assembly Election 2024",
    defaults=dict(
        description="Vote for your representative in the General Assembly. This election determines the state's legislative leaders for the next five years.",
        start_date=now - timedelta(hours=2),
        end_date=now + timedelta(days=3),
        is_active=True,
        show_results=False,
        created_by=admin,
    )
)
print(f"Election 1: {e1.title}")

candidates_e1 = [
    dict(name="Rajiv Sharma", party="National Progress Party", party_symbol="🌟", age=52, qualification="M.A. Political Science", bio="Former district collector with 20 years of public service experience.", manifesto="Focus on infrastructure, education, and healthcare for all citizens."),
    dict(name="Priya Nair", party="People's Democratic Front", party_symbol="✊", age=44, qualification="MBA, Harvard", bio="Successful entrepreneur turned politician, advocating for youth and women empowerment.", manifesto="Digital India, women's safety, and rural development are our priorities."),
    dict(name="Mohammed Salim", party="United Secular Alliance", party_symbol="🕊️", age=58, qualification="LLB, Delhi University", bio="Veteran lawyer and civil rights activist with 30 years of field experience.", manifesto="Justice, equality, and communal harmony for every Indian citizen."),
    dict(name="Sunita Devi", party="Farmer's Welfare Party", party_symbol="🌾", age=49, qualification="B.Sc. Agriculture", bio="Grassroots leader and former sarpanch representing farming communities.", manifesto="Loan waivers, MSP guarantee, and rural employment schemes."),
]

for c_data in candidates_e1:
    Candidate.objects.get_or_create(election=e1, name=c_data['name'], defaults=c_data)
print(f"  → {len(candidates_e1)} candidates added")

# ── Election 2: Active ────────────────────────────────────────────────────────
e2, _ = Election.objects.get_or_create(
    title="Municipal Corporation Election 2024",
    defaults=dict(
        description="Cast your vote for the Municipal Corporation councillor in your ward. Your vote shapes local governance, roads, water, and waste management.",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1),
        is_active=True,
        show_results=False,
        created_by=admin,
    )
)
print(f"Election 2: {e2.title}")

candidates_e2 = [
    dict(name="Arun Kumar Reddy", party="Telangana Rashtra Samithi", party_symbol="🚗", age=41, qualification="B.Tech Civil Engineering", bio="Infrastructure specialist focused on smart city development.", manifesto="Smart city initiative, clean water, and 24/7 power supply."),
    dict(name="Lakshmi Bai", party="Indian National Congress", party_symbol="🖐️", age=55, qualification="M.Sc Chemistry", bio="Social activist and school principal. Three decades of community service.", manifesto="Free education, health camps, and women self-help groups."),
    dict(name="Venkat Rao", party="Bharatiya Janata Party", party_symbol="🪷", age=48, qualification="B.Com, CA", bio="Chartered accountant and local business leader.", manifesto="Tax reforms, business-friendly policies, and digital governance."),
]

for c_data in candidates_e2:
    Candidate.objects.get_or_create(election=e2, name=c_data['name'], defaults=c_data)
print(f"  → {len(candidates_e2)} candidates added")

# ── Election 3: Upcoming ──────────────────────────────────────────────────────
e3, _ = Election.objects.get_or_create(
    title="University Student Union Election 2024",
    defaults=dict(
        description="Students vote for their representatives in the University Student Union for the academic year 2024-25.",
        start_date=now + timedelta(days=5),
        end_date=now + timedelta(days=6),
        is_active=True,
        show_results=False,
        created_by=admin,
    )
)
print(f"Election 3 (upcoming): {e3.title}")

candidates_e3 = [
    dict(name="Ravi Teja", party="Students For Change", party_symbol="📚", age=22, qualification="B.Tech 3rd Year", bio="Student activist fighting for campus reforms and hostel facilities.", manifesto="Better canteen, WiFi on campus, and reduced exam fees."),
    dict(name="Anusha Sharma", party="Youth Progressive Alliance", party_symbol="🌈", age=21, qualification="B.Sc 2nd Year", bio="Women's rights activist and NCC cadet.", manifesto="Gender equality, anti-ragging measures, and mental health support."),
    dict(name="Kiran Babu", party="National Students Federation", party_symbol="✏️", age=23, qualification="M.Tech 1st Year", bio="Research scholar passionate about academic excellence.", manifesto="Research funding, internship tie-ups, and placement improvements."),
]

for c_data in candidates_e3:
    Candidate.objects.get_or_create(election=e3, name=c_data['name'], defaults=c_data)
print(f"  → {len(candidates_e3)} candidates added")

# ── Election 4: Ended with results ───────────────────────────────────────────
e4, _ = Election.objects.get_or_create(
    title="Panchayat Election 2023",
    defaults=dict(
        description="Panchayat Raj elections for village council representatives.",
        start_date=now - timedelta(days=30),
        end_date=now - timedelta(days=29),
        is_active=False,
        show_results=True,
        created_by=admin,
    )
)
print(f"Election 4 (ended): {e4.title}")

candidates_e4 = [
    dict(name="Ganga Devi", party="Independent", party_symbol="⭐", age=45, qualification="10th Standard", bio="Local farmer and community leader."),
    dict(name="Ramu Yadav", party="Village Progress Party", party_symbol="🌻", age=50, qualification="12th Standard", bio="Former school teacher."),
]

for c_data in candidates_e4:
    Candidate.objects.get_or_create(election=e4, name=c_data['name'], defaults=c_data)
print(f"  → {len(candidates_e4)} candidates added")

print("\n✅ Seed data complete!")
print("   Admin: admin / Admin@1234")
print("   Run server: python manage.py runserver")
print("   Import voters: python manage.py import_voters voters_data.csv")
