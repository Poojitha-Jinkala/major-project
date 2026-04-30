from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse

from .models import Election, Candidate, Vote, VoterProfile
from .forms import VoterRegistrationForm, LoginForm, VoteForm
from .utils import generate_vote_hash, mask_voter_id


# ─── Home Page ────────────────────────────────────────────────────────────────

def home(request):
    active_elections = Election.objects.filter(is_active=True)
    total_voters = VoterProfile.objects.count()
    total_votes_cast = Vote.objects.count()
    total_elections = Election.objects.count()
    context = {
        'active_elections': active_elections[:3],
        'total_voters': total_voters,
        'total_votes_cast': total_votes_cast,
        'total_elections': total_elections,
    }
    return render(request, 'home.html', context)


# ─── Authentication ───────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.voter_profile.full_name}! Your voter account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = VoterRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    now = timezone.now()
    active_elections = Election.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)
    upcoming_elections = Election.objects.filter(is_active=True, start_date__gt=now)
    ended_elections = Election.objects.filter(end_date__lt=now)
    voted_election_ids = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)

    context = {
        'active_elections': active_elections,
        'upcoming_elections': upcoming_elections,
        'ended_elections': ended_elections,
        'voted_election_ids': list(voted_election_ids),
    }
    return render(request, 'dashboard.html', context)


# ─── Voting ───────────────────────────────────────────────────────────────────

@login_required
def election_detail(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    now = timezone.now()
    already_voted = Vote.objects.filter(voter=request.user, election=election).exists()

    try:
        profile = request.user.voter_profile
        if not profile.is_verified:
            messages.error(request, "Your voter account is not yet verified. Please contact the administrator.")
            return redirect('dashboard')
    except VoterProfile.DoesNotExist:
        messages.error(request, "Voter profile not found. Please contact support.")
        return redirect('dashboard')

    if request.method == 'POST':
        if already_voted:
            messages.error(request, "You have already cast your vote in this election!")
            return redirect('election_detail', election_id=election_id)

        if not election.is_ongoing:
            messages.error(request, "This election is not currently active.")
            return redirect('dashboard')

        form = VoteForm(election, request.POST)
        if form.is_valid():
            candidate = form.cleaned_data['candidate']
            vote_hash = generate_vote_hash(request.user.id, election.id, candidate.id)
            Vote.objects.create(
                voter=request.user,
                election=election,
                candidate=candidate,
                vote_hash=vote_hash,
            )
            messages.success(request, f"Your vote for {candidate.name} has been securely recorded!")
            return redirect('vote_success', election_id=election_id)
        else:
            messages.error(request, "Please select a candidate.")
    else:
        form = VoteForm(election)

    candidates = Candidate.objects.filter(election=election)
    context = {
        'election': election,
        'candidates': candidates,
        'form': form,
        'already_voted': already_voted,
        'now': now,
    }
    return render(request, 'election_detail.html', context)


@login_required
def vote_success(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    vote = Vote.objects.filter(voter=request.user, election=election).first()
    return render(request, 'vote_success.html', {'election': election, 'vote': vote})


# ─── Results ──────────────────────────────────────────────────────────────────

def results(request, election_id):
    election = get_object_or_404(Election, pk=election_id)

    if not election.show_results and not election.has_ended:
        if not request.user.is_staff:
            messages.warning(request, "Results are not yet available for this election.")
            return redirect('dashboard')

    candidates = Candidate.objects.filter(election=election).annotate(
        votes_count=Count('votes')
    ).order_by('-votes_count')

    total_votes = election.total_votes
    winner = candidates.first() if candidates else None

    chart_labels = [c.name for c in candidates]
    chart_data = [c.votes_count for c in candidates]
    chart_colors = [
        '#6C63FF', '#FF6584', '#43E97B', '#F7971E', '#4FACFE',
        '#a18cd1', '#fda085', '#f093fb', '#30cfd0', '#667eea'
    ][:len(candidates)]

    context = {
        'election': election,
        'candidates': candidates,
        'total_votes': total_votes,
        'winner': winner,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'chart_colors': chart_colors,
    }
    return render(request, 'results.html', context)


def all_results(request):
    ended = Election.objects.filter(end_date__lt=timezone.now())
    public = Election.objects.filter(show_results=True)
    elections = (ended | public).distinct()
    return render(request, 'all_results.html', {'elections': elections})


# ─── Profile ──────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    try:
        voter_profile = request.user.voter_profile
    except VoterProfile.DoesNotExist:
        voter_profile = None

    votes_cast = Vote.objects.filter(voter=request.user).select_related('election', 'candidate')
    context = {
        'voter_profile': voter_profile,
        'votes_cast': votes_cast,
        'masked_voter_id': mask_voter_id(voter_profile.voter_id) if voter_profile else '',
    }
    return render(request, 'profile.html', context)


# ─── Live Vote Count API ──────────────────────────────────────────────────────

def live_vote_count(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = Candidate.objects.filter(election=election).annotate(votes_count=Count('votes'))
    data = {
        'election': election.title,
        'total_votes': election.total_votes,
        'candidates': [{'name': c.name, 'party': c.party, 'votes': c.votes_count} for c in candidates]
    }
    return JsonResponse(data)
