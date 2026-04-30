from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class VoterProfile(models.Model):
    """Extended voter profile linked to Django's built-in User model."""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    STATE_CHOICES = [
        ('AP', 'Andhra Pradesh'), ('AR', 'Arunachal Pradesh'), ('AS', 'Assam'),
        ('BR', 'Bihar'), ('CG', 'Chhattisgarh'), ('GA', 'Goa'), ('GJ', 'Gujarat'),
        ('HR', 'Haryana'), ('HP', 'Himachal Pradesh'), ('JH', 'Jharkhand'),
        ('KA', 'Karnataka'), ('KL', 'Kerala'), ('MP', 'Madhya Pradesh'),
        ('MH', 'Maharashtra'), ('MN', 'Manipur'), ('ML', 'Meghalaya'),
        ('MZ', 'Mizoram'), ('NL', 'Nagaland'), ('OD', 'Odisha'), ('PB', 'Punjab'),
        ('RJ', 'Rajasthan'), ('SK', 'Sikkim'), ('TN', 'Tamil Nadu'),
        ('TG', 'Telangana'), ('TR', 'Tripura'), ('UP', 'Uttar Pradesh'),
        ('UK', 'Uttarakhand'), ('WB', 'West Bengal'), ('DL', 'Delhi'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voter_profile')
    voter_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField(default=18)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default='TG')
    district = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.voter_id})"

    class Meta:
        verbose_name = "Voter Profile"
        verbose_name_plural = "Voter Profiles"
        ordering = ['-registered_at']


class Election(models.Model):
    """Represents an election event."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    show_results = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_elections')
    created_at = models.DateTimeField(auto_now_add=True)
    banner = models.ImageField(upload_to='elections/', blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @property
    def has_ended(self):
        return timezone.now() > self.end_date

    @property
    def total_votes(self):
        return Vote.objects.filter(election=self).count()

    class Meta:
        ordering = ['-start_date']


class Candidate(models.Model):
    """Represents a candidate in an election."""
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=150)
    party = models.CharField(max_length=100)
    party_symbol = models.CharField(max_length=50, blank=True, help_text="Emoji or short symbol")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    manifesto = models.TextField(blank=True)
    age = models.PositiveIntegerField(default=35)
    qualification = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.name} ({self.party})"

    @property
    def vote_count(self):
        return Vote.objects.filter(candidate=self).count()

    @property
    def vote_percentage(self):
        total = self.election.total_votes
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100, 1)

    class Meta:
        ordering = ['name']


class Vote(models.Model):
    """Represents a single encrypted vote cast by a verified voter."""
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    vote_hash = models.CharField(max_length=64, unique=True)  # SHA-256 hash
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'election')  # One vote per voter per election
        ordering = ['-timestamp']

    def __str__(self):
        return f"Vote by {self.voter.username} in {self.election.title}"


class VoterImport(models.Model):
    """Tracks Kaggle CSV imports of voter data."""
    imported_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    total_records = models.PositiveIntegerField()
    imported_count = models.PositiveIntegerField()
    failed_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Import {self.filename} — {self.imported_count} voters on {self.imported_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-imported_at']
