"""Checks of the points of a curve before they are saved."""
import math

from rest_framework.serializers import ValidationError

MAX_POINTS = 20000
MAX_SECONDS = 24 * 60 * 60
MAX_PERCENT = 100
MAX_TEXT = 1000
# The old screens report the mouse a few pixels outside of the 640 x 320 graph.
OVERSHOOT = 0.05


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def is_extra(value):
    """Points also carry short values such as axis, type, state and index."""
    return (value is None or isinstance(value, bool) or is_number(value) or
            isinstance(value, str) and len(value) <= MAX_TEXT)


def clean_values(values, version, is_text):
    if not isinstance(values, list) or not 2 <= len(values) <= MAX_POINTS:
        raise ValidationError(f"点は2〜{MAX_POINTS}個で指定してください。")
    for point in values:
        if not isinstance(point, dict) or not is_number(point.get("x")) or not is_number(point.get("y")):
            raise ValidationError("各点の x と y を数値で指定してください。")
        if not all(is_extra(value) for value in point.values()):
            raise ValidationError("点に保存できない値が含まれています。")
    if version != "arc-1":
        left = -OVERSHOOT * max(point["x"] for point in values)
        values = [{**point,
                   "x": 0 if left <= point["x"] < 0 else point["x"],
                   "y": 1 if 1 < point["y"] <= 1 + OVERSHOOT else point["y"]} for point in values]
    limit = MAX_PERCENT if is_text else MAX_SECONDS
    xs = [point["x"] for point in values]
    if min(xs) < 0 or max(xs) > limit:
        raise ValidationError(f"x は 0〜{limit} で指定してください。")
    if any(not -1 <= point["y"] <= 1 for point in values):
        raise ValidationError("y は -1〜1 で指定してください。")
    if any(a > b for a, b in zip(xs, xs[1:])) or xs[0] == xs[-1]:
        raise ValidationError("点を x の小さい順に並べてください。")
    return values
