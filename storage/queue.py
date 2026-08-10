"""
AI NEWS FACTORY
TASK QUEUE

Controls the movement of stories through the factory.

Pipeline:

COLLECTED
    ↓
QUEUED
    ↓
PROCESSING
    ↓
READY
    ↓
PUBLISHING
    ↓
PUBLISHED

Failed jobs can be retried without duplicating successful work.
"""

import time
import uuid
from typing import Any, Dict, List, Optional


class NewsQueue:

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    # =====================================================
    # ADD
    # =====================================================

    def add(
        self,
        story_id: str,
        payload: Optional[Dict[str, Any]] = None,
        priority: int = 50
    ) -> str:

        job_id = str(
            uuid.uuid4()
        )

        self.jobs[job_id] = {

            "job_id":
                job_id,

            "story_id":
                story_id,

            "payload":
                payload or {},

            "priority":
                priority,

            "status":
                "QUEUED",

            "attempts":
                0,

            "created_at":
                time.time(),

            "updated_at":
                time.time()
        }

        return job_id

    # =====================================================
    # NEXT JOB
    # =====================================================

    def next(
        self
    ) -> Optional[Dict[str, Any]]:

        available = [

            job

            for job in self.jobs.values()

            if job["status"] == "QUEUED"
        ]

        if not available:

            return None

        available.sort(
            key=lambda job: (
                -job["priority"],
                job["created_at"]
            )
        )

        job = available[0]

        job["status"] = "PROCESSING"

        job["attempts"] += 1

        job["updated_at"] = time.time()

        return dict(
            job
        )

    # =====================================================
    # COMPLETE
    # =====================================================

    def complete(
        self,
        job_id: str,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:

        job = self.jobs.get(
            job_id
        )

        if not job:

            return False

        job["status"] = "COMPLETED"

        job["result"] = (
            result or {}
        )

        job["updated_at"] = time.time()

        return True

    # =====================================================
    # FAIL
    # =====================================================

    def fail(
        self,
        job_id: str,
        error: str,
        retry: bool = True
    ) -> bool:

        job = self.jobs.get(
            job_id
        )

        if not job:

            return False

        job["error"] = str(
            error
        )

        job["updated_at"] = time.time()

        if retry:

            job["status"] = "QUEUED"

        else:

            job["status"] = "FAILED"

        return True

    # =====================================================
    # CANCEL
    # =====================================================

    def cancel(
        self,
        job_id: str
    ) -> bool:

        job = self.jobs.get(
            job_id
        )

        if not job:

            return False

        job["status"] = "CANCELLED"

        job["updated_at"] = time.time()

        return True

    # =====================================================
    # GET
    # =====================================================

    def get(
        self,
        job_id: str
    ) -> Optional[Dict[str, Any]]:

        job = self.jobs.get(
            job_id
        )

        if not job:

            return None

        return dict(
            job
        )

    # =====================================================
    # LIST
    # =====================================================

    def list_jobs(
        self,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        jobs = list(
            self.jobs.values()
        )

        if status:

            jobs = [

                job

                for job in jobs

                if job["status"] == status
            ]

        jobs.sort(
            key=lambda job:
                job["created_at"]
        )

        return [
            dict(job)
            for job in jobs
        ]

    # =====================================================
    # RETRY FAILED
    # =====================================================

    def retry_failed(
        self,
        job_id: str
    ) -> bool:

        job = self.jobs.get(
            job_id
        )

        if not job:

            return False

        if job["status"] != "FAILED":

            return False

        job["status"] = "QUEUED"

        job["updated_at"] = time.time()

        return True

    # =====================================================
    # SIZE
    # =====================================================

    def size(
        self,
        status: Optional[str] = None
    ) -> int:

        if status:

            return len([
                job

                for job in self.jobs.values()

                if job["status"] == status
            ])

        return len(
            self.jobs
        )


# =========================================================
# HELPER
# =========================================================

def create_queue() -> NewsQueue:

    return NewsQueue()
