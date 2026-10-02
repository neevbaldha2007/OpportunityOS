import csv
import os
import sys
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

# Ensure backend root is in sys.path for direct execution
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import SessionLocal, Base, engine
from app.models.skill import Skill
from app.core.logging import logger


def find_skills_csv(custom_path: Optional[str] = None) -> str:
    """Resolve the location of the skills.csv seed file."""
    if custom_path and os.path.exists(custom_path):
        return custom_path

    candidates = [
        os.path.join(str(current_dir), "skills.csv"),
        os.path.join(str(backend_dir), "seeds", "skills.csv"),
        os.path.join(str(backend_dir), "app", "seeds", "skills.csv"),
        os.path.join(os.getcwd(), "backend", "seeds", "skills.csv"),
        os.path.join(os.getcwd(), "seeds", "skills.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]


def load_skills_from_csv(db: Session, csv_path: Optional[str] = None) -> int:
    """Load or update canonical skills catalog from CSV into database.

    Returns the number of newly added skills.
    """
    resolved_path = find_skills_csv(csv_path)

    if not os.path.exists(resolved_path):
        logger.error(f"Skills CSV not found at {resolved_path}")
        return 0

    added_count = 0
    updated_count = 0

    with open(resolved_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"].strip()
            slug = row["slug"].strip()
            category = row.get("category", "").strip() or None
            aliases_raw = row.get("aliases", "")
            aliases = [a.strip() for a in aliases_raw.split(";") if a.strip()]
            is_verified = row.get("is_verified", "true").lower() == "true"

            existing = db.query(Skill).filter(
                (Skill.slug == slug) | (Skill.name == name)
            ).first()

            if not existing:
                skill = Skill(
                    name=name,
                    slug=slug,
                    category=category,
                    aliases=aliases,
                    is_verified=is_verified,
                )
                db.add(skill)
                added_count += 1
            else:
                existing.category = category
                existing.aliases = aliases
                existing.is_verified = is_verified
                updated_count += 1

    db.commit()
    logger.info(
        f"Skills catalog synchronized: {added_count} added, {updated_count} updated "
        f"from {resolved_path}."
    )
    return added_count


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        added = load_skills_from_csv(db)
        total = db.query(Skill).count()
        print(f"Skills seeding completed: {added} new skills added. Total canonical skills: {total}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
