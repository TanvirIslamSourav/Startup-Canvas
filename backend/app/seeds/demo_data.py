"""Demo seed data for local development.

Run via:
    python -m app.seeds            # bootstrap SQLite + insert demo rows
or
    python -m app.seeds.demo_data  # just insert demo rows into the configured DB
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    BusinessCanvas,
    Competitor,
    CustomerPersona,
    Document,
    Idea,
    LeanCanvas,
    Milestone,
    Note,
    ProgressTracker,
    Roadmap,
    RoadmapStage,
    StartupProject,
    Swot,
    Task,
    User,
)
from app.seeds.bootstrap import create_all_tables, get_engine


def _now() -> datetime:
    return datetime.now(UTC)


def _get_or_create(db: Session, model, defaults: dict | None = None, **filters):
    """Return an existing row or insert a new one."""
    instance = db.execute(select(model).filter_by(**filters)).scalar_one_or_none()
    if instance:
        return instance, False
    params = {**filters, **(defaults or {})}
    instance = model(**params)
    db.add(instance)
    db.flush()
    return instance, True


def run_demo_seed(db: Session | None = None) -> dict:
    """Insert a representative set of rows so the UI has data on first launch.

    Returns a summary dict with counts.
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        # Ensure all tables exist (idempotent).
        engine = get_engine()
        create_all_tables(engine)

        summary = {
            "users": 0,
            "projects": 0,
            "ideas": 0,
            "lean_canvas": 0,
            "business_canvas": 0,
            "swot": 0,
            "progress_tracker": 0,
            "competitors": 0,
            "personas": 0,
            "tasks": 0,
            "milestones": 0,
            "documents": 0,
            "notes": 0,
            "roadmaps": 0,
        }

        # ------------------------------------------------------------------
        # User + project
        # ------------------------------------------------------------------
        user, created = _get_or_create(
            db,
            User,
            email="demo@startupcanvas.local",
            defaults={
                "display_name": "Demo Founder",
                "locale": "en",
                "theme": "system",
                "is_active": True,
            },
        )
        summary["users"] += 1 if created else 0

        project, created = _get_or_create(
            db,
            StartupProject,
            owner_id=user.id,
            name="Demo Startup",
            defaults={
                "description": "A sample project created by the demo seeder.",
                "stage": "validation",
                "status": "active",
                "tags": ["demo", "seed"],
                "metadata": {"source": "seed"},
            },
        )
        summary["projects"] += 1 if created else 0

        # ------------------------------------------------------------------
        # Three ideas to populate the dashboard
        # ------------------------------------------------------------------
        idea_specs = [
            {
                "title": "AI Tutor for Grade School",
                "problem": "Students in underserved areas lack personalised tutoring.",
                "solution": "An AI tutor that adapts to each student's pace and curriculum.",
                "audience": "Grade 5-8 students in Tier 2/3 cities",
                "category": "education",
                "status": "validating",
                "priority": 3,
                "score": 72,
                "tags": ["ai", "education"],
            },
            {
                "title": "Marketplace for Local Tutors",
                "problem": "Parents struggle to find verified local tutors.",
                "solution": "Two-sided marketplace with verified reviews and escrow payments.",
                "audience": "Urban parents, K-12 students",
                "category": "marketplace",
                "status": "planned",
                "priority": 2,
                "score": 64,
                "tags": ["marketplace", "education"],
            },
            {
                "title": "Compliance-First Health Coach",
                "problem": "Health coaches can't easily track outcomes for payers.",
                "solution": "Outcome-tracking app with built-in compliance reporting.",
                "audience": "Independent health coaches, payers",
                "category": "health",
                "status": "draft",
                "priority": 1,
                "score": 55,
                "tags": ["health", "saas"],
            },
        ]
        ideas: list[Idea] = []
        for spec in idea_specs:
            idea, created = _get_or_create(
                db,
                Idea,
                project_id=project.id,
                title=spec["title"],
                defaults={**spec},
            )
            ideas.append(idea)
            summary["ideas"] += 1 if created else 0

        # ------------------------------------------------------------------
        # 1:1 rows for the first idea
        # ------------------------------------------------------------------
        first = ideas[0]
        if not db.execute(
            select(LeanCanvas).filter_by(idea_id=first.id)
        ).scalar_one_or_none():
            db.add(
                LeanCanvas(
                    idea_id=first.id,
                    problem="Lack of personalised attention in low-income schools.",
                    solution="Adaptive AI tutor tuned to local curriculum.",
                    key_metrics="Engagement, mastery, NPS.",
                    unique_value_prop="Personalised at scale, affordable.",
                    unfair_advantage="Partnership with state curriculum boards.",
                    channels="Schools, NGOs, word-of-mouth.",
                    customer_segments="Tier 2/3 families, schools.",
                    cost_structure="Server + curriculum ops.",
                    revenue_streams="School licensing + family subscription.",
                )
            )
            summary["lean_canvas"] += 1
        if not db.execute(
            select(BusinessCanvas).filter_by(idea_id=first.id)
        ).scalar_one_or_none():
            db.add(
                BusinessCanvas(
                    idea_id=first.id,
                    key_partners="State education boards, NGOs.",
                    key_activities="Content design, AI tuning.",
                    key_resources="Curriculum team, ML engineers.",
                    value_propositions="Affordable personalised tutoring.",
                    customer_relationships="Self-serve + school account managers.",
                    channels="Direct sales to schools, online.",
                    customer_segments="Families, schools.",
                    cost_structure="Fixed content, variable compute.",
                    revenue_streams="Subscriptions + licensing.",
                )
            )
            summary["business_canvas"] += 1
        if not db.execute(select(Swot).filter_by(idea_id=first.id)).scalar_one_or_none():
            db.add(
                Swot(
                    idea_id=first.id,
                    strengths="Strong pedagogy team.",
                    weaknesses="Long sales cycle.",
                    opportunities="Government ed-tech push.",
                    threats="Big competitors entering market.",
                    score=68,
                    summary="Promising if execution holds.",
                )
            )
            summary["swot"] += 1
        if not db.execute(
            select(ProgressTracker).filter_by(idea_id=first.id)
        ).scalar_one_or_none():
            db.add(
                ProgressTracker(
                    idea_id=first.id,
                    overall_completion=25,
                    health_score=70,
                    milestone_progress=20,
                    task_completion=30,
                    last_computed_at=_now(),
                )
            )
            summary["progress_tracker"] += 1

        # ------------------------------------------------------------------
        # 1:N rows for the first idea
        # ------------------------------------------------------------------
        if not db.execute(
            select(Competitor).filter_by(idea_id=first.id)
        ).first():
            db.add_all(
                [
                    Competitor(
                        idea_id=first.id,
                        name="Byju's",
                        website_url="https://byjus.com",
                        pricing=4999.0,
                        pricing_currency="INR",
                        strengths="Brand, content depth.",
                        weaknesses="Expensive for low-income families.",
                        features=["video lessons", "quizzes"],
                        market_position="leader",
                    ),
                    Competitor(
                        idea_id=first.id,
                        name="Vedantu",
                        website_url="https://vedantu.com",
                        pricing=3000.0,
                        pricing_currency="INR",
                        strengths="Live tutors, price.",
                        weaknesses="Limited personalisation.",
                        features=["live classes"],
                        market_position="challenger",
                    ),
                ]
            )
            summary["competitors"] += 2

        if not db.execute(
            select(CustomerPersona).filter_by(idea_id=first.id)
        ).first():
            db.add_all(
                [
                    CustomerPersona(
                        idea_id=first.id,
                        name="Anika (Parent)",
                        age=34,
                        occupation="Teacher",
                        goals="Help her child excel without expensive tuition.",
                        pain_points="Time, cost, trust.",
                        needs="Affordable, trustworthy tool.",
                        behaviour="Researches online, asks friends.",
                    ),
                    CustomerPersona(
                        idea_id=first.id,
                        name="Ravi (Student)",
                        age=12,
                        occupation="Grade 7 student",
                        goals="Understand maths better.",
                        pain_points="Boring lessons, no personal help.",
                        needs="Interactive practice, encouragement.",
                        behaviour="Uses phone after school.",
                    ),
                ]
            )
            summary["personas"] += 2

        if not db.execute(select(Task).filter_by(idea_id=first.id)).first():
            db.add_all(
                [
                    Task(
                        idea_id=first.id,
                        title="Run 5 customer interviews",
                        description="Validate problem with parents and teachers.",
                        priority="high",
                        status="in_progress",
                        progress=40,
                    ),
                    Task(
                        idea_id=first.id,
                        title="Build MVP outline",
                        description="List features for first prototype.",
                        priority="medium",
                        status="todo",
                        progress=0,
                        due_date=(_now() + timedelta(days=14)).date(),
                    ),
                ]
            )
            summary["tasks"] += 2

        if not db.execute(select(Milestone).filter_by(idea_id=first.id)).first():
            db.add_all(
                [
                    Milestone(
                        idea_id=first.id,
                        title="Validated problem",
                        description="At least 10 in-depth interviews completed.",
                        completion=100,
                        completed_at=_now(),
                    ),
                    Milestone(
                        idea_id=first.id,
                        title="MVP launched to 5 schools",
                        description="Prototype tested with 5 pilot schools.",
                        completion=0,
                        target_date=(_now() + timedelta(days=90)).date(),
                    ),
                ]
            )
            summary["milestones"] += 2

        if not db.execute(select(Document).filter_by(idea_id=first.id)).first():
            db.add_all(
                [
                    Document(
                        idea_id=first.id,
                        kind="business_plan",
                        title="AI Tutor Business Plan v1",
                        notes="Living document.",
                    ),
                    Document(
                        idea_id=first.id,
                        kind="pitch_deck",
                        title="Investor pitch deck",
                        notes="First draft.",
                    ),
                ]
            )
            summary["documents"] += 2

        if not db.execute(select(Note).filter_by(idea_id=first.id)).first():
            db.add_all(
                [
                    Note(
                        idea_id=first.id,
                        body="Interviewed 3 teachers — they want offline mode.",
                        pinned=True,
                    ),
                    Note(
                        idea_id=first.id,
                        body="Follow up with school in Lucknow next week.",
                        pinned=False,
                    ),
                ]
            )
            summary["notes"] += 2

        if not db.execute(select(Roadmap).filter_by(idea_id=first.id)).scalar_one_or_none():
            roadmap = Roadmap(idea_id=first.id, title="Q3-Q4 Roadmap", summary="Validation to pilot.")
            db.add(roadmap)
            db.flush()
            db.add_all(
                [
                    RoadmapStage(
                        roadmap_id=roadmap.id,
                        title="Customer discovery",
                        position=1,
                        target_date=(_now() + timedelta(days=14)).date(),
                        completion=100,
                    ),
                    RoadmapStage(
                        roadmap_id=roadmap.id,
                        title="MVP build",
                        position=2,
                        target_date=(_now() + timedelta(days=45)).date(),
                        completion=30,
                    ),
                    RoadmapStage(
                        roadmap_id=roadmap.id,
                        title="Pilot in 5 schools",
                        position=3,
                        target_date=(_now() + timedelta(days=90)).date(),
                        completion=0,
                    ),
                ]
            )
            summary["roadmaps"] += 1

        db.commit()
        return summary
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":  # pragma: no cover
    counts = run_demo_seed()
    print("Seed complete:", counts)