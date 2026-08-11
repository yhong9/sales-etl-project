from time import perf_counter
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import text

from load_raw_orders import main as load_orders
from quality_raw_orders import main as check_orders
from build_staging_orders import build_staging_orders

from load_raw_customers import main as load_customers
from quality_raw_customers import main as check_customers
from build_staging_customers import build_staging_customers

from load_raw_order_items import main as load_order_items
from quality_raw_order_items import (
    main as check_order_items,
)
from build_staging_order_items import (
    build_staging_order_items,
)

from load_raw_products import load_raw_products
from quality_raw_products import main as check_products
from build_staging_products import build_staging_products

from load_raw_order_reviews import main as load_reviews
from quality_raw_order_reviews import (
    main as check_reviews,
)
from build_staging_order_reviews import (
    build_staging_order_reviews,
)

from build_fact_sales import build_fact_sales
from build_sales_marts import build_sales_marts
from build_review_marts import build_review_marts
from db import get_engine


PIPELINE_STEPS = [
    (
        "Load raw orders",
        load_orders,
    ),
    (
        "Check raw orders",
        check_orders,
    ),
    (
        "Build staging orders",
        build_staging_orders,
    ),
    (
        "Load raw customers",
        load_customers,
    ),
    (
        "Check raw customers",
        check_customers,
    ),
    (
        "Build staging customers",
        build_staging_customers,
    ),
    (
        "Load raw order items",
        load_order_items,
    ),
    (
        "Check raw order items",
        check_order_items,
    ),
    (
        "Build staging order items",
        build_staging_order_items,
    ),
    (
        "Load raw products",
        load_raw_products,
    ),
    (
        "Check raw products",
        check_products,
    ),
    (
        "Build staging products",
        build_staging_products,
    ),
    (
        "Load raw order reviews",
        load_reviews,
    ),
    (
        "Check raw order reviews",
        check_reviews,
    ),
    (
        "Build staging order reviews",
        build_staging_order_reviews,
    ),
    (
        "Build sales fact table",
        build_fact_sales,
    ),
    (
        "Build sales marts",
        build_sales_marts,
    ),
    (
        "Build review marts",
        build_review_marts,
    ),
]


def initialize_pipeline_audit(run_id, started_at):
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS audit;"))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
                run_id UUID PRIMARY KEY,
                pipeline_name TEXT NOT NULL,
                started_at TIMESTAMPTZ NOT NULL,
                completed_at TIMESTAMPTZ,
                duration_seconds NUMERIC(12, 2),
                total_steps INTEGER NOT NULL,
                completed_steps INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                failed_step TEXT,
                error_message TEXT
            );
        """))
        connection.execute(
            text("""
                INSERT INTO audit.pipeline_runs (
                    run_id,
                    pipeline_name,
                    started_at,
                    total_steps,
                    completed_steps,
                    status
                )
                VALUES (
                    :run_id,
                    'Olist ETL/ELT Pipeline',
                    :started_at,
                    :total_steps,
                    0,
                    'Running'
                );
            """),
            {
                "run_id": run_id,
                "started_at": started_at,
                "total_steps": len(PIPELINE_STEPS),
            },
        )


def update_pipeline_audit(
    run_id,
    completed_steps,
    status="Running",
    completed_at=None,
    duration_seconds=None,
    failed_step=None,
    error_message=None,
):
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE audit.pipeline_runs
                SET completed_steps = :completed_steps,
                    status = :status,
                    completed_at = :completed_at,
                    duration_seconds = :duration_seconds,
                    failed_step = :failed_step,
                    error_message = :error_message
                WHERE run_id = :run_id;
            """),
            {
                "run_id": run_id,
                "completed_steps": completed_steps,
                "status": status,
                "completed_at": completed_at,
                "duration_seconds": duration_seconds,
                "failed_step": failed_step,
                "error_message": error_message,
            },
        )


def run_pipeline():
    pipeline_start = perf_counter()
    started_at = datetime.now(timezone.utc)
    run_id = uuid4()
    completed_steps = 0

    initialize_pipeline_audit(run_id, started_at)

    print("=" * 70)
    print("Starting Olist ETL/ELT Pipeline")
    print("=" * 70)

    for step_number, (step_name, step_function) in enumerate(
        PIPELINE_STEPS,
        start=1,
    ):
        step_start = perf_counter()

        print()
        print(
            f"[{step_number}/{len(PIPELINE_STEPS)}] "
            f"{step_name}"
        )
        print("-" * 70)

        try:
            step_function()
        except Exception as error:
            elapsed = perf_counter() - step_start
            total_elapsed = perf_counter() - pipeline_start

            update_pipeline_audit(
                run_id=run_id,
                completed_steps=completed_steps,
                status="Failed",
                completed_at=datetime.now(timezone.utc),
                duration_seconds=round(total_elapsed, 2),
                failed_step=step_name,
                error_message=str(error)[:2000],
            )

            print()
            print(
                f"FAILED: {step_name} "
                f"after {elapsed:.2f} seconds"
            )

            # 保留原始错误和完整 traceback。
            raise

        elapsed = perf_counter() - step_start
        completed_steps = step_number

        update_pipeline_audit(
            run_id=run_id,
            completed_steps=completed_steps,
        )

        print(
            f"Completed: {step_name} "
            f"in {elapsed:.2f} seconds"
        )

    total_elapsed = perf_counter() - pipeline_start

    update_pipeline_audit(
        run_id=run_id,
        completed_steps=completed_steps,
        status="Successful",
        completed_at=datetime.now(timezone.utc),
        duration_seconds=round(total_elapsed, 2),
    )

    print()
    print("=" * 70)
    print("Olist pipeline completed successfully!")
    print(f"Total runtime: {total_elapsed:.2f} seconds")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
