
import re

from app.services.file_reader import read_repository_file
from app.services.file_scanner import scan_repository


def tokenize(text: str) -> list[str]:
    """Convert text into searchable lowercase tokens."""
    return re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())


def search_codebase(
    repository_path: str,
    query: str,
    limit: int = 10,
) -> dict:
    """
    Search repository files using keyword matching.

    Results are ranked by the number of query-term occurrences.
    """
    query_terms = set(tokenize(query))

    if not query_terms:
        raise ValueError("Search query must contain searchable words.")

    if limit < 1 or limit > 50:
        raise ValueError("Limit must be between 1 and 50.")

    files = scan_repository(repository_path)
    results = []

    for file_path in files:
        try:
            file_data = read_repository_file(
                repository_path=repository_path,
                relative_file_path=file_path,
            )
        except ValueError:
            # Skip files that cannot safely be read.
            continue

        lines = file_data["content"].splitlines()

        matching_lines = []
        matched_terms = set()
        total_occurrences = 0

        for line_number, line in enumerate(lines, start=1):
            line_terms = tokenize(line)
            line_term_set = set(line_terms)

            matching = query_terms.intersection(line_term_set)

            if not matching:
                continue

            matched_terms.update(matching)
            total_occurrences += sum(
                line_terms.count(term) for term in matching
            )

            # Include a small amount of surrounding context.
            start = max(0, line_number - 3)
            end = min(len(lines), line_number + 2)

            matching_lines.append({
                "line": line_number,
                "matched_terms": sorted(matching),
                "snippet": "\n".join(lines[start:end]),
                "context_start_line": start + 1,
            })

        if not matching_lines:
            continue

        # Prioritize files matching more query terms and occurrences.
        score = (
            len(matched_terms) * 10
            + total_occurrences
        )

        results.append({
            "file_path": file_path,
            "score": score,
            "matched_terms": sorted(matched_terms),
            "matching_lines": matching_lines,
        })

    results.sort(
        key=lambda item: (
            -item["score"],
            item["file_path"],
        )
    )

    return {
        "query": query,
        "total_files_searched": len(files),
        "total_matching_files": len(results),
        "results": results[:limit],
    }
