import pandas as pd

from quality_raw_order_reviews import check_raw_order_reviews


def issue_count(report, check_name):
    return int(
        report.loc[
            report["check_name"].eq(check_name),
            "issue_count",
        ].iloc[0]
    )


def make_review(
    review_id="review-1",
    order_id="order-1",
    review_score="5",
):
    return {
        "review_id": review_id,
        "order_id": order_id,
        "review_score": review_score,
        "review_comment_title": None,
        "review_comment_message": None,
        "review_creation_date": "2018-01-06 00:00:00",
        "review_answer_timestamp": "2018-01-06 12:00:00",
    }


def test_invalid_review_scores_are_detected():
    reviews = pd.DataFrame(
        [
            make_review("review-1", "order-1", "0"),
            make_review("review-2", "order-2", "6"),
            make_review("review-3", "order-3", "bad"),
            make_review("review-4", "order-4", "4.5"),
        ]
    )
    orders = pd.DataFrame(
        {"order_id": ["order-1", "order-2", "order-3", "order-4"]}
    )

    report = check_raw_order_reviews(reviews, orders)

    assert issue_count(report, "invalid_review_score") == 4


def test_duplicate_reviews_and_multiple_reviews_are_detected():
    review = make_review()
    reviews = pd.DataFrame([review, review.copy()])
    orders = pd.DataFrame({"order_id": ["order-1"]})

    report = check_raw_order_reviews(reviews, orders)

    assert issue_count(report, "exact_duplicate_rows") == 2
    assert issue_count(report, "duplicate_review_id_rows") == 2
    assert issue_count(report, "orders_with_multiple_reviews") == 1


def test_unmatched_review_order_is_detected():
    reviews = pd.DataFrame(
        [make_review(order_id="missing-order")]
    )
    orders = pd.DataFrame({"order_id": ["order-1"]})

    report = check_raw_order_reviews(reviews, orders)

    assert issue_count(report, "unmatched_order_id") == 1
