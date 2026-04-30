import csv
import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voting.models import VoterProfile, VoterImport


class Command(BaseCommand):
    help = 'Import voter data from a Kaggle-style CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('--max', type=int, default=5000, help='Max records to import')

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        max_records = options['max']

        imported = 0
        failed = 0
        total = 0

        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)[:max_records]
                total = len(rows)

                self.stdout.write(f"Found {total} records. Importing...")

                for row in rows:
                    try:
                        voter_id = row.get('voter_id', '').strip()
                        full_name = row.get('full_name', '').strip()
                        email = row.get('email', '').strip().lower()
                        age = int(row.get('age', 25))
                        gender = row.get('gender', 'M').strip().upper()[:1]
                        state = row.get('state', 'TG').strip().upper()[:2]
                        district = row.get('district', '').strip()
                        phone = row.get('phone', '').strip()

                        if not voter_id or not full_name:
                            failed += 1
                            continue

                        # Skip if voter_id already exists
                        if VoterProfile.objects.filter(voter_id=voter_id).exists():
                            failed += 1
                            continue

                        # Generate username from email or voter_id
                        username = email.split('@')[0] if email else voter_id.lower()
                        base_username = username
                        counter = 1
                        while User.objects.filter(username=username).exists():
                            username = f"{base_username}{counter}"
                            counter += 1

                        # Skip if email already exists
                        if email and User.objects.filter(email=email).exists():
                            email = f"{voter_id.lower()}@voter.in"

                        # Create user with a default password (voter_id + '@Vote')
                        password = voter_id + '@Vote123'
                        user = User.objects.create_user(
                            username=username,
                            email=email or f"{voter_id.lower()}@voter.in",
                            password=password,
                            first_name=full_name.split()[0] if full_name else '',
                            last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else '',
                        )

                        VoterProfile.objects.create(
                            user=user,
                            voter_id=voter_id,
                            full_name=full_name,
                            age=max(18, age),
                            gender=gender if gender in ['M', 'F', 'O'] else 'M',
                            state=state if len(state) == 2 else 'TG',
                            district=district,
                            phone=phone,
                            is_verified=True,
                        )
                        imported += 1

                        if imported % 50 == 0:
                            self.stdout.write(f"  Imported {imported} records...")

                    except Exception as e:
                        failed += 1
                        self.stdout.write(self.style.WARNING(f"  Row failed: {e}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        # Log the import
        VoterImport.objects.create(
            filename=csv_path,
            total_records=total,
            imported_count=imported,
            failed_count=failed,
        )

        self.stdout.write(self.style.SUCCESS(
            f"\nImport complete!\n"
            f"  Total records: {total}\n"
            f"  Imported:      {imported}\n"
            f"  Failed/Skipped:{failed}\n"
            f"  Default password format: <voter_id>@Vote123"
        ))
