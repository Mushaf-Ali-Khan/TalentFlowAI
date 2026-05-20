"""
Stress test: Upload files through the full pipeline multiple times.
Tests single file, batch of 2, and repeated batches to verify the
event loop / DB session fix.

Run: .venv\Scripts\python.exe stress_test.py
"""
import requests
import time
import json
import os
import sys

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"x-dev-user": "true"}

# Use the existing test CV files
BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))
MOCK_STORAGE = os.path.join(BACKEND_ROOT, "_mock_storage", "raw")

def find_test_files():
    """Find uploaded CV files to use for testing."""
    files = []
    for f in os.listdir(MOCK_STORAGE):
        path = os.path.join(MOCK_STORAGE, f)
        if os.path.isfile(path):
            files.append((f, path))
    return files

def get_or_create_job():
    """Get an existing job or create one."""
    r = requests.get(f"{BASE_URL}/jobs", headers=HEADERS)
    if r.ok and r.json().get("data"):
        job = r.json()["data"][0]
        print(f"  Using existing job: {job['title']} ({job['id']})")
        return job["id"]
    
    # Create a new job
    job_data = {
        "title": "Senior Backend Engineer",
        "description": "We need a senior backend engineer with Python, FastAPI, PostgreSQL experience.",
        "requirements": {"skills": ["Python", "FastAPI", "PostgreSQL", "Docker"]},
    }
    r = requests.post(f"{BASE_URL}/jobs", json=job_data, headers=HEADERS)
    if not r.ok:
        print(f"  ERROR creating job: {r.status_code} {r.text}")
        sys.exit(1)
    job_id = r.json()["data"]["id"]
    print(f"  Created job: {job_id}")
    return job_id

def upload_and_submit(job_id, file_paths, test_name):
    """Upload files and submit a batch. Returns batch_id."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"  Files: {len(file_paths)}")
    
    # 1. Get upload URLs
    files_payload = []
    for fname, fpath in file_paths:
        files_payload.append({
            "filename": fname,
            "content_type": "application/pdf" if fname.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "size_bytes": os.path.getsize(fpath)
        })
    
    r = requests.post(f"{BASE_URL}/pipeline/upload-urls", json=files_payload, headers=HEADERS)
    if not r.ok:
        print(f"  ERROR getting upload URLs: {r.status_code} {r.text}")
        return None
    
    upload_data = r.json()["data"]
    
    # 2. Upload files via mock-upload
    for i, item in enumerate(upload_data):
        fname, fpath = file_paths[i]
        r2_key = item["r2_key"]
        with open(fpath, "rb") as f:
            r = requests.put(f"{BASE_URL}/pipeline/mock-upload?key={r2_key}", data=f.read(), headers=HEADERS)
        if not r.ok:
            print(f"  ERROR uploading {fname}: {r.status_code}")
            return None
        print(f"  Uploaded: {fname}")
    
    # 3. Submit batch
    submit_payload = {
        "job_id": job_id,
        "files": [
            {
                "r2_key": upload_data[i]["r2_key"],
                "filename": file_paths[i][0],
                "size_bytes": os.path.getsize(file_paths[i][1]),
                "content_type": files_payload[i]["content_type"],
            }
            for i in range(len(file_paths))
        ]
    }
    
    r = requests.post(f"{BASE_URL}/pipeline/submit", json=submit_payload, headers=HEADERS)
    if not r.ok:
        print(f"  ERROR submitting batch: {r.status_code} {r.text}")
        return None
    
    batch_id = str(r.json()["data"]["id"])
    print(f"  Batch submitted: {batch_id}")
    return batch_id

def wait_for_batch(batch_id, timeout=120):
    """Poll batch status until completed or timeout."""
    print(f"  Waiting for batch {batch_id[:8]}... ", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{BASE_URL}/pipeline/{batch_id}", headers=HEADERS)
        if r.ok:
            data = r.json()["data"]
            status = data.get("status")
            processed = data.get("processed_cvs", 0)
            total = data.get("total_cvs", 0)
            if status in ("completed", "failed"):
                elapsed = time.time() - start
                print(f"{status.upper()} ({processed}/{total}) in {elapsed:.1f}s")
                return status == "completed"
        time.sleep(2)
    
    print(f"TIMEOUT after {timeout}s")
    return False

def check_candidates(job_id):
    """Verify candidates have real data."""
    r = requests.get(f"{BASE_URL}/jobs/{job_id}/candidates", headers=HEADERS)
    if not r.ok:
        print(f"  ERROR fetching candidates: {r.status_code}")
        return False
    
    candidates = r.json().get("data", [])
    all_ok = True
    for c in candidates:
        profile = c.get("profile")
        name = profile.get("name") if profile else "N/A"
        score = c.get("total_score")
        status = c.get("processing_status")
        semantic = c.get("semantic_score", 0)
        
        ok = status == "completed" and profile is not None and score is not None and score > 0
        marker = "[OK]" if ok else "[ERR]"
        print(f"  {marker} {name}: score={score}, semantic={semantic:.3f}, status={status}")
        if not ok:
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("TalentFlowAI Pipeline Stress Test")
    print("=" * 60)
    
    # Health check
    r = requests.get(f"{BASE_URL}/health")
    if not r.ok:
        print("ERROR: Backend is not running!")
        sys.exit(1)
    print("Backend health: OK")
    
    # Find test files
    test_files = find_test_files()
    if not test_files:
        print("ERROR: No test files found in _mock_storage/raw/")
        sys.exit(1)
    print(f"Found {len(test_files)} test files")
    
    # Get/create job
    job_id = get_or_create_job()
    
    # Test 1: Single file upload (PDF)
    pdf_files = [f for f in test_files if f[0].endswith(".pdf")]
    if pdf_files:
        batch_id = upload_and_submit(job_id, [pdf_files[0]], "Single PDF upload")
        if batch_id:
            success = wait_for_batch(batch_id)
            if not success:
                print("  FAILED: Single PDF test")
    
    # Test 2: Single file upload (DOCX)
    docx_files = [f for f in test_files if f[0].endswith(".docx")]
    if docx_files:
        batch_id = upload_and_submit(job_id, [docx_files[0]], "Single DOCX upload")
        if batch_id:
            success = wait_for_batch(batch_id)
            if not success:
                print("  FAILED: Single DOCX test")
    
    # Test 3: Batch of 2 files (both PDF and DOCX)
    if pdf_files and docx_files:
        batch_id = upload_and_submit(job_id, [pdf_files[0], docx_files[0]], "Batch: PDF + DOCX")
        if batch_id:
            success = wait_for_batch(batch_id)
            if not success:
                print("  FAILED: Batch test")
    
    # Test 4: Quick sequential submissions (stress test the event loop)
    print(f"\n{'='*60}")
    print("TEST: 3 rapid sequential batches (event loop stress test)")
    batch_ids = []
    for i in range(3):
        if pdf_files:
            batch_id = upload_and_submit(job_id, [pdf_files[0]], f"Rapid batch #{i+1}")
            if batch_id:
                batch_ids.append(batch_id)
    
    for bid in batch_ids:
        wait_for_batch(bid)
    
    # Final verification
    print(f"\n{'='*60}")
    print("FINAL VERIFICATION")
    check_candidates(job_id)
    
    print(f"\n{'='*60}")
    print("STRESS TEST COMPLETE")

if __name__ == "__main__":
    main()
