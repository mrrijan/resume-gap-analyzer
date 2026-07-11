"""
End-to-end test for M4 (gap analysis).

Sends 5 constructed job postings through the pipeline:
    1. POST /parse-posting  (M2) for each posting
    2. POST /match           (M3) for each parsed posting vs. Sarah's resume
    3. POST /gap-analysis    (M4) for all 5 match results together

Prints the ranked gaps to verify M4's acceptance criterion:
    "given 5+ postings with known overlapping requirements, correctly identifies
     and ranks the shared missing skills as highest priority."

Run:
    cd ml-service
    source venv/bin/activate
    python scripts/test_m4_gap_analysis.py

Requires the FastAPI server to be running:
    uvicorn main:app --reload --port 8001
"""

import json
import sys

import requests


BASE_URL = "http://127.0.0.1:8001"


# ---------- Test resume (Sarah Chen) ----------
SARAH_RESUME = {
    "resume_skills": [
        "Python", "Go", "TypeScript", "SQL", "Rust", "FastAPI", "Django", "gRPC", "React",
        "AWS", "Kubernetes", "Docker", "Terraform", "Kafka", "PostgreSQL", "Redis",
        "Git", "Datadog", "Grafana", "Prometheus", "Linear",
    ],
    "resume_experience": [
        "Senior Software Engineer",
        "Stripe, Remote",
        "March 2023 – Present",
        "Led migration of legacy payment reconciliation service from monolith to microservices, reducing p99 latency by 60%.",
        "Designed and shipped a real-time fraud detection pipeline processing 12,000 events per second using Kafka and Go.",
        "Mentored 3 junior engineers through onboarding and quarterly design reviews.",
        "Owned on-call rotation for the Payments Infrastructure team.",
        "Software Engineer",
        "Datadog, New York, NY",
        "June 2021 – February 2023",
        "Built internal SDK for distributed tracing adopted by 40+ engineering teams across the company.",
        "Reduced infrastructure costs by 25% through query optimization on time-series database.",
        "Contributed to open-source OpenTelemetry Python instrumentation library.",
        "Software Engineering Intern",
        "Airbnb, San Francisco, CA",
        "May 2020 – August 2020",
        "Prototyped experimentation platform feature that shipped to production and impacts 100M+ users.",
    ],
    "resume_education": [
        "Bachelor of Science in Computer Science",
        "Carnegie Mellon University, Pittsburgh, PA",
        "August 2017 – May 2021",
        "GPA: 3.8 / 4.0",
        "Relevant Coursework: Distributed Systems, Machine Learning, Compilers, Operating Systems",
    ],
    "resume_certifications": [
        "AWS Certified Solutions Architect – Associate",
        "Amazon Web Services, Issued August 2023",
        "Certified Kubernetes Administrator (CKA)",
        "Cloud Native Computing Foundation, Issued January 2024",
    ],
}


# ---------- Five test postings with deliberate overlap ----------
# Overlap map (designed to test M4b ranking):
#     Docker           — required in ALL 5 (universal, Sarah has strong match)
#     Shopify          — required in 3 of 5 (Sarah has ZERO — top gap candidate)
#     Rust             — mentioned in 4 of 5 (Sarah has in skills, weak experience)
#     Kubernetes prod  — 4 of 5 (Sarah has cert, no explicit prod experience)
#     Japanese         — 1 of 5 (rare — should rank low despite high deficiency)
#     Communication    — 5 of 5 (universal but low deficiency; should not top-rank)
POSTINGS = [
    ("shopify-lead-1", """About the Role

We're hiring a Shopify Backend Lead to own our merchant platform infrastructure.

Required Qualifications

* 5+ years of backend development experience
* Deep expertise with Shopify, Shopify Plus, and Shopify integrations
* Strong Docker and container orchestration skills
* Experience with Python or Node.js in production
* Strong problem-solving and communication skills

Preferred Qualifications

* Familiarity with Kubernetes in production environments
* Rust experience for performance-critical services
* Experience mentoring junior engineers
"""),
    ("payments-platform", """Senior Payments Engineer

Join our payments infrastructure team.

Required Qualifications

* 4+ years backend engineering in production systems
* Experience with Docker and containerization
* Strong understanding of distributed systems
* Proficiency in Go or Rust
* Excellent written and verbal communication skills

Preferred Qualifications

* Kubernetes production operations experience
* Experience with high-throughput event processing (Kafka, similar)
* Contributions to open source infrastructure projects
"""),
    ("ecommerce-backend", """Backend Engineer - E-commerce Platform

We're a fast-growing marketplace and need engineers who can scale our platform.

Required Qualifications

* Solid backend development experience with Python, Ruby, or Node.js
* Working knowledge of Shopify or comparable e-commerce platforms
* Docker-based development workflows
* Rust or systems programming background is essential
* Strong communication and cross-functional collaboration

Preferred Qualifications

* Kubernetes production experience
* Japanese language proficiency (we work with Japanese merchants)
* Experience with internationalization and localization
"""),
    ("infra-devops", """Infrastructure Engineer

Own our production Kubernetes clusters.

Required Qualifications

* 3+ years operating containerized production infrastructure
* Extensive Docker and Kubernetes production experience
* Strong Rust or Go for tooling and services
* Deep understanding of observability (Prometheus, Grafana, Datadog)
* Excellent communication with product and engineering teams

Preferred Qualifications

* Terraform infrastructure-as-code experience
* On-call rotation experience for production systems
"""),
    ("shopify-full-stack", """Full-Stack Engineer, Shopify Ecosystem

Build merchant-facing tools on top of Shopify.

Required Qualifications

* 3+ years full-stack development
* Strong Shopify platform knowledge (theme development, storefront APIs, admin API)
* Docker for local development and deployment
* Backend proficiency in Node.js, Ruby, or Python
* Clear communication and teamwork skills

Preferred Qualifications

* Kubernetes production familiarity
* Rust for performance-sensitive backend services
"""),
]


# ---------- Pipeline steps ----------
def check_health() -> None:
    """Fail fast if the server isn't running."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Cannot reach server at {BASE_URL}. Is uvicorn running?")
        print(f"   {e}")
        sys.exit(1)


def parse_posting(text: str) -> dict:
    r = requests.post(f"{BASE_URL}/parse-posting", json={"text": text}, timeout=30)
    r.raise_for_status()
    return r.json()


def match_resume_vs_posting(parsed_posting: dict) -> dict:
    payload = {
        **SARAH_RESUME,
        "posting_required": parsed_posting["required"],
        "posting_preferred": parsed_posting["preferred"],
    }
    r = requests.post(f"{BASE_URL}/match", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def gap_analysis(all_match_results: list[tuple[str, dict]]) -> dict:
    payload = {
        "posting_matches": [
            {"posting_id": pid, "match_result": mr}
            for pid, mr in all_match_results
        ]
    }
    r = requests.post(f"{BASE_URL}/gap-analysis", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


# ---------- Reporting ----------
def print_per_posting_summary(gap_result: dict) -> None:
    print("\n" + "=" * 72)
    print("PER-POSTING FIT SUMMARY")
    print("=" * 72)
    for pc in gap_result["per_posting_classifications"]:
        print(f"\n  {pc['posting_id']:<25} overall_fit={pc['overall_fit']:>6.2f}%   "
              f"strong={len(pc['strong'])}  partial={len(pc['partial'])}  missing={len(pc['missing'])}")


def print_ranked_gaps(gap_result: dict) -> None:
    print("\n" + "=" * 72)
    print(f"RANKED GAPS ACROSS {gap_result['total_postings']} POSTINGS")
    print("=" * 72)
    for i, gap in enumerate(gap_result["ranked_gaps"], start=1):
        print(f"\n  #{i}  gap_score={gap['gap_score']:.3f}   "
              f"frequency={gap['frequency']:.2f}   "
              f"avg_sim={gap['avg_similarity']:.3f}")
        print(f"      canonical: {gap['canonical_text']}")
        print(f"      affects postings ({len(gap['affected_posting_ids'])}): "
              f"{', '.join(gap['affected_posting_ids'])}")
        if len(gap['example_requirements']) > 1:
            print(f"      clustered {len(gap['example_requirements'])} similar requirements:")
            for ex in gap['example_requirements']:
                print(f"        - {ex}")


# ---------- Main ----------
def main() -> None:
    check_health()
    print(f"✓ Server up at {BASE_URL}")

    match_results: list[tuple[str, dict]] = []

    for posting_id, raw_text in POSTINGS:
        print(f"\n→ Processing {posting_id}...")
        parsed = parse_posting(raw_text)
        print(f"  parsed  ({parsed['parse_strategy']}): "
              f"{len(parsed['required'])} required, "
              f"{len(parsed['preferred'])} preferred, "
              f"{len(parsed['responsibilities'])} responsibilities")

        match = match_resume_vs_posting(parsed)
        print(f"  matched: overall_fit={match['overall_fit']}%")

        match_results.append((posting_id, match))

    print("\n→ Running gap analysis on all 5 match results...")
    gap_result = gap_analysis(match_results)

    print_per_posting_summary(gap_result)
    print_ranked_gaps(gap_result)

    # Also save the full JSON output for later inspection.
    output_path = "scripts/last_gap_analysis_result.json"
    with open(output_path, "w") as f:
        json.dump(gap_result, f, indent=2)
    print(f"\n✓ Full result written to {output_path}")


if __name__ == "__main__":
    main()