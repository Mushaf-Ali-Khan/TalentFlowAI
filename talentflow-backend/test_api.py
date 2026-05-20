"""Quick API test to verify candidates data"""
import requests

# Test health
r = requests.get('http://localhost:8000/api/v1/health')
print(f"Health: {r.status_code}")

# Test candidates for the most recent job
job_id = 'e86f4f3a-596f-451c-887a-3b2f15e0a670'
r = requests.get(
    f'http://localhost:8000/api/v1/jobs/{job_id}/candidates',
    headers={'x-dev-user': 'true'}
)
print(f"\nCandidates API: {r.status_code}")
if r.ok:
    data = r.json()
    for c in data.get('data', []):
        profile = c.get('profile')
        name = profile.get('name') if profile else 'N/A'
        score = c.get('total_score')
        status = c.get('processing_status')
        semantic = c.get('semantic_score')
        llm = c.get('llm_score')
        skills = ', '.join([s.get('name', '') for s in (profile.get('skills', []) or [])[:5]]) if profile else 'N/A'
        print(f"  {name}: total={score}, semantic={semantic}, llm={llm}, status={status}")
        print(f"    Skills: {skills}")
else:
    print(f"  Error: {r.text}")
