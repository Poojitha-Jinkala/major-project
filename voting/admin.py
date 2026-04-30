from django.contrib import admin
from .models import VoterProfile, Election, Candidate, Vote, VoterImport


@admin.register(VoterProfile)
class VoterProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'voter_id', 'user', 'age', 'gender', 'state', 'is_verified', 'registered_at']
    list_filter = ['gender', 'state', 'is_verified']
    search_fields = ['full_name', 'voter_id', 'user__username', 'user__email']
    list_editable = ['is_verified']
    ordering = ['-registered_at']
    readonly_fields = ['registered_at']


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active', 'show_results', 'total_votes']
    list_filter = ['is_active', 'show_results']
    search_fields = ['title']
    list_editable = ['is_active', 'show_results']
    ordering = ['-start_date']

    def total_votes(self, obj):
        return obj.total_votes
    total_votes.short_description = 'Total Votes'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'party', 'election', 'age', 'qualification', 'vote_count']
    list_filter = ['election', 'party']
    search_fields = ['name', 'party']

    def vote_count(self, obj):
        return obj.vote_count
    vote_count.short_description = 'Votes Received'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'election', 'candidate', 'timestamp']
    list_filter = ['election', 'candidate__party']
    search_fields = ['voter__username', 'election__title']
    readonly_fields = ['voter', 'election', 'candidate', 'vote_hash', 'timestamp']
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False  # Votes must be cast through the voting system only


@admin.register(VoterImport)
class VoterImportAdmin(admin.ModelAdmin):
    list_display = ['filename', 'total_records', 'imported_count', 'failed_count', 'imported_at']
    readonly_fields = ['imported_at', 'filename', 'total_records', 'imported_count', 'failed_count']


# Customize admin site header
admin.site.site_header = "🗳️ Smart Voting System — Admin"
admin.site.site_title = "Voting Admin"
admin.site.index_title = "Election Management Dashboard"
