from sentinelpay.ml.synthetic import generate


def test_synthetic_generation_is_reproducible() -> None:
    first_matrix, first_labels = generate(100, 42)
    second_matrix, second_labels = generate(100, 42)
    assert (first_matrix == second_matrix).all()
    assert (first_labels == second_labels).all()
    assert first_matrix.shape == (100, 10)
