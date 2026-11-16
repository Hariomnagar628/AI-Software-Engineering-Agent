
from app.services.repository_overview import get_repository_overview
from app.services.repository_stats import get_repository_stats


def get_repository_summary(repository_path: str) -> dict:
    overview = get_repository_overview(repository_path)
    stats = get_repository_stats(repository_path)

    return {
        **overview,
        "statistics": stats["extension_counts"],
    }
