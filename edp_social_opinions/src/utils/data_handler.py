"""
Persists collected opinions to CSV and JSON, with deduplication and basic stats.
"""

import json
import logging
import os
from datetime import datetime
from typing import List

import pandas as pd

from src.models.opinion import Opinion

logger = logging.getLogger(__name__)


class DataHandler:
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, opinions: List[Opinion], run_tag: str = "") -> dict:
        if not opinions:
            logger.info("No opinions to save.")
            return {}

        tag = run_tag or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        records = [o.to_dict() for o in opinions]
        df = pd.DataFrame(records)
        df = self._deduplicate(df)

        csv_path = os.path.join(self.output_dir, f"edp_opinions_{tag}.csv")
        json_path = os.path.join(self.output_dir, f"edp_opinions_{tag}.json")
        master_csv = os.path.join(self.output_dir, "edp_opinions_all.csv")

        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        df.to_json(json_path, orient="records", force_ascii=False, indent=2)
        self._append_master(df, master_csv)

        summary = self._summary(df)
        summary_path = os.path.join(self.output_dir, f"edp_opinions_{tag}_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(
            "Saved %d opinions → %s | %s | master: %s",
            len(df), csv_path, json_path, master_csv,
        )
        return summary

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate(df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates(subset=["source", "text"], keep="first")
        df = df[df["text"].str.strip().astype(bool)]
        after = len(df)
        if before != after:
            logger.info("Removed %d duplicate/empty opinions.", before - after)
        return df

    def _append_master(self, df: pd.DataFrame, master_path: str) -> None:
        if os.path.exists(master_path):
            existing = pd.read_csv(master_path, encoding="utf-8-sig")
            combined = pd.concat([existing, df], ignore_index=True)
            combined = self._deduplicate(combined)
        else:
            combined = df
        combined.to_csv(master_path, index=False, encoding="utf-8-sig")

    @staticmethod
    def _summary(df: pd.DataFrame) -> dict:
        summary: dict = {
            "total": len(df),
            "by_source": df["source"].value_counts().to_dict(),
            "avg_rating_by_source": {},
            "date_range": {
                "earliest": None,
                "latest": None,
            },
            "employment_status": df["employment_status"].value_counts(dropna=False).to_dict(),
        }

        if "rating" in df.columns:
            rating_means = (
                df[df["rating"].notna()]
                .groupby("source")["rating"]
                .mean()
                .round(2)
                .to_dict()
            )
            summary["avg_rating_by_source"] = rating_means

        if "date" in df.columns:
            dates = df["date"].dropna().tolist()
            if dates:
                summary["date_range"]["earliest"] = min(dates)
                summary["date_range"]["latest"] = max(dates)

        return summary
