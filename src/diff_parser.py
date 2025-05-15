# diff_parser.py
from dataclasses import dataclass
from typing import List, Optional
from unidiff import PatchSet

@dataclass
class LineChange:
    content: str
    type: str  # 'added', 'removed', 'context'

@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    changes: List[LineChange]

@dataclass
class FileDiff:
    old_file: Optional[str]
    new_file: Optional[str]
    hunks: List[Hunk]

class DiffParser:
    def parse(self, diff_text: str) -> List[FileDiff]:
        parsed_files = []
        patch_set = PatchSet(diff_text)

        for patched_file in patch_set:
            # Handle file renames and deletions
            old_file = patched_file.source_file
            new_file = patched_file.target_file

            # Cleanup prefixes like 'a/' and 'b/' (common in Git diffs)
            if old_file.startswith('a/'):
                old_file = old_file[2:]
            if new_file.startswith('b/'):
                new_file = new_file[2:]

            hunks = []
            for hunk in patched_file:
                changes = []
                for line in hunk:
                    if line.is_added:
                        line_type = 'added'
                    elif line.is_removed:
                        line_type = 'removed'
                    else:
                        line_type = 'context'

                    changes.append(
                        LineChange(content=line.value.rstrip('\n'), type=line_type)
                    )

                hunks.append(
                    Hunk(
                        old_start=hunk.source_start,
                        old_count=hunk.source_length,
                        new_start=hunk.target_start,
                        new_count=hunk.target_length,
                        changes=changes,
                    )
                )

            parsed_files.append(
                FileDiff(
                    old_file=old_file if old_file != '/dev/null' else None,
                    new_file=new_file if new_file != '/dev/null' else None,
                    hunks=hunks,
                )
            )

        return parsed_files