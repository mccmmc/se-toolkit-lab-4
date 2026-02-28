"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1

def test_filter_excludes_interaction_with_different_learner_id() -> None:
    """Test that filtering by item_id includes interactions with matching item_id 
    even when learner_id is different."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 1),
        _make_log(3, 2, 2)
    ]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 2
    assert {log.id for log in result} == {1, 2}
    assert all(log.item_id == 1 for log in result)

def test_filter_returns_empty_when_no_matching_item_id() -> None:
    """Test that filter returns empty list when no interactions have the specified item_id."""
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2), _make_log(3, 3, 3)]
    result = _filter_by_item_id(interactions, 999)  # Non-existent item_id
    assert result == []


def test_filter_handles_duplicate_item_ids() -> None:
    """Test that filter returns all interactions with matching item_id, even if they have duplicate IDs."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 1), 
        _make_log(3, 3, 1)  # Все с item_id = 1
    ]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 3
    assert result == interactions  # Должны вернуться все три в том же порядке