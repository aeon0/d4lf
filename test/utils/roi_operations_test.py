from utils.roi_operations import get_center, intersect, pad, bounding_box, to_grid, is_in_roi, translate


def test_translate():
    # Define the bounds
    bounds = (1280, 720)

    # Define test cases
    test_cases = [
        # Test moving within bounds
        {
            "roi": (100, 100, 200, 200),
            "translation_vector": (100, 200),
            "resize": False,
            "expected": (200, 300, 200, 200),
        },
        # Test moving outside bounds without resizing
        {
            "roi": (100, 100, 100, 100),
            "translation_vector": (2000, 2000),
            "resize": False,
            "expected": (1180, 620, 100, 100),  # Rectangle is moved back to fit within bounds
        },
        # Test moving outside bounds with resizing
        {
            "roi": (100, 100, 100, 100),
            "translation_vector": (1100, 600),
            "resize": True,
            "expected": (1200, 700, 80, 20),  # Rectangle is resized to fit within bounds
        },
        # Test moving outside bounds with resizing 2
        {
            "roi": (100, 100, 100, 100),
            "translation_vector": (1300, 800),
            "resize": True,
            "expected": (1279, 719, 1, 1),  # Rectangle is resized to fit within bounds
        },
    ]

    # Run test cases
    for test_case in test_cases:
        assert translate(*test_case["translation_vector"], test_case["roi"], *bounds, resize=test_case["resize"]) == test_case["expected"]


def test_get_center():
    # Test with a rectangle
    roi = (2, 2, 6, 6)
    center = get_center(roi)
    assert center == (5, 5)


def test_intersect():
    # Test with intersecting rectangles
    rects = [(2, 2, 6, 6), (4, 4, 6, 6)]
    intersection = intersect(rects)
    assert intersection == (4, 4, 4, 4)

    # Test with non-intersecting rectangles
    rects = [(2, 2, 2, 2), (5, 5, 2, 2)]
    intersection = intersect(rects)
    assert intersection is None


def test_pad():
    rectangle = (5, 5, 10, 10)
    max_x, max_y = 20, 20

    # Test with each valid direction
    directions = {
        "left": (3, 5, 12, 10),
        "right": (5, 5, 12, 10),
        "up": (5, 3, 10, 12),
        "down": (5, 5, 10, 12),
        "width": (3, 5, 14, 10),
        "height": (5, 3, 10, 14),
        "all": (3, 3, 14, 14),
    }

    for direction, expected in directions.items():
        padded = pad(rectangle, 2, direction, max_x, max_y)
        assert padded == expected, f"Failed for direction '{direction}'"

    # Test with an invalid direction
    padded = pad(rectangle, 2, "invalid_direction", max_x, max_y)
    assert padded == rectangle


def test_bounding_box():
    # Test with rectangles
    rects = [(2, 2, 2, 2), (4, 4, 2, 2)]
    bounding = bounding_box(rects)
    assert bounding == (2, 2, 4, 4)

    # Test with coordinates
    coords = [(2, 2), (6, 6)]
    bounding = bounding_box(coords)
    assert bounding == (2, 2, 4, 4)

    # Test with a mix of coordinates and rectangles
    mixed = [(2, 2), (4, 4, 2, 2)]
    bounding = bounding_box(mixed)
    assert bounding == (2, 2, 4, 4)

    # Test with multiple inputs
    bounding = bounding_box((0, 0, 2, 2), (4, 4))
    assert bounding == (0, 0, 4, 4)

    # Test with an invalid argument
    invalid_arg = [(2, 2, 2, 2, 2)]
    bounding = bounding_box(invalid_arg)
    assert bounding is None


def test_to_grid():
    roi = (0, 0, 10, 10)
    rows, columns = 2, 2

    expected_rectangles = {(0, 0, 5, 5), (0, 5, 5, 5), (5, 0, 5, 5), (5, 5, 5, 5)}

    actual_rectangles = to_grid(roi, rows, columns)

    assert actual_rectangles == expected_rectangles, f"Expected {expected_rectangles}, but got {actual_rectangles}"

    original_area = roi[2] * roi[3]
    total_area = sum([width * height for x, y, width, height in actual_rectangles])

    assert original_area == total_area, f"Expected total area to be {original_area}, but got {total_area}"


def test_is_coor_in_roi():
    rectangle = (0, 0, 10, 10)

    # Points inside the rectangle
    for coor in [(5, 5), (0, 10), (10, 0), (10, 10)]:
        assert is_in_roi(coor, rectangle), f"Expected {coor} to be inside {rectangle}"

    # Points outside the rectangle
    for coor in [(-1, 0), (0, -1), (11, 0), (0, 11)]:
        assert not is_in_roi(coor, rectangle), f"Expected {coor} to be outside {rectangle}"
