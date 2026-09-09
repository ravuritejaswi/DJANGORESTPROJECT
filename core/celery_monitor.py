import logging
import time

from celery.signals import (
    task_prerun,
    task_postrun,
    task_failure,
    task_retry,
)

logger = logging.getLogger("celery.monitor")


@task_prerun.connect
def task_started(sender=None, task_id=None, task=None, **kwargs):
    task.request._monitor_start_time = time.monotonic()

    logger.info(
        "Celery task started | task=%s | task_id=%s",
        sender.name if sender else "unknown",
        task_id,
    )


@task_postrun.connect
def task_completed(
    sender=None,
    task_id=None,
    task=None,
    retval=None,
    state=None,
    **kwargs,
):
    start_time = getattr(
        task.request,
        "_monitor_start_time",
        None,
    )

    execution_time = (
        time.monotonic() - start_time
        if start_time is not None
        else None
    )

    logger.info(
        "Celery task completed | task=%s | task_id=%s | "
        "state=%s | execution_time=%.4fs",
        sender.name if sender else "unknown",
        task_id,
        state,
        execution_time if execution_time is not None else 0,
    )


@task_failure.connect
def task_failed(
    sender=None,
    task_id=None,
    exception=None,
    traceback=None,
    einfo=None,
    **kwargs,
):
    logger.error(
        "Celery task failed | task=%s | task_id=%s | "
        "exception=%s",
        sender.name if sender else "unknown",
        task_id,
        exception,
    )


@task_retry.connect
def task_retried(
    sender=None,
    request=None,
    reason=None,
    **kwargs,
):
    retry_count = request.retries if request else 0

    logger.warning(
        "Celery task retry | task=%s | task_id=%s | "
        "retry_count=%s | reason=%s",
        sender.name if sender else "unknown",
        request.id if request else "unknown",
        retry_count,
        reason,
    )