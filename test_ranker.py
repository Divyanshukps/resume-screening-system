import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from screener import rank_resumes  # noqa: E402

DATA = ROOT / "sample_data"


class RankerTest(unittest.TestCase):
    def test_relevant_resume_ranks_first(self):
        jd = (DATA / "job_description.txt").read_text()
        resumes = [
            {"name": p.stem, "text": p.read_text()} for p in sorted(DATA.glob("resume_*.txt"))
        ]
        ranking = rank_resumes(jd, resumes)
        self.assertEqual(ranking[0]["name"], "resume_asha_patil")
        self.assertEqual(ranking[-1]["name"], "resume_sneha_rao")
        self.assertGreater(ranking[0]["score"], ranking[1]["score"])

    def test_empty_job_description_raises(self):
        with self.assertRaises(ValueError):
            rank_resumes("  ", [{"name": "a", "text": "python"}])


if __name__ == "__main__":
    unittest.main()
