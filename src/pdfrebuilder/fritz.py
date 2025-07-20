# Dummy classes for testing purposes if fitz is not installed
import logging

logger = logging.getLogger(__name__)

try:
    import fitz
except ImportError:
    logger.warning("PyMuPDF (fitz) not found. Using dummy classes for fitz types.")

    class Rect:
        def __init__(self, x0, y0, x1, y1):
            self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

        def __iter__(self):
            return iter([self.x0, self.y0, self.x1, self.y1])

        def __repr__(self):
            return f"Rect({self.x0}, {self.y0}, {self.x1}, {self.y1})"

        def intersects(self, other):
            return not (self.x1 < other.x0 or self.x0 > other.x1 or self.y1 < other.y0 or self.y0 > other.y1)

        def contains(self, other):
            return self.x0 <= other.x0 and self.y0 <= other.y0 and self.x1 >= other.x1 and self.y1 >= other.y1

        @property
        def width(self):
            return self.x1 - self.x0

        @property
        def height(self):
            return self.y1 - self.y0

        @property
        def top_left(self):
            return Point(self.x0, self.y0)

        def get_area(self):
            width = self.x1 - self.x0
            height = self.y1 - self.y0
            if abs(width) > 1e6 or abs(height) > 1e6:
                raise OverflowError("Rectangle dimensions too large")
            return width * height

        def __and__(self, other):
            x0, y0 = max(self.x0, other.x0), max(self.y0, other.y0)
            x1, y1 = min(self.x1, other.x1), min(self.y1, other.y1)
            return Rect(x0, y0, x1, y1) if x0 < x1 and y0 < y1 else Rect(0, 0, 0, 0)

    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def __iter__(self):
            return iter([self.x, self.y])

        def __repr__(self):
            return f"Point({self.x}, {self.y})"

    class Matrix:
        def __init__(self, a, b, c, d, e, f):
            self.a, self.b, self.c, self.d, self.e, self.f = a, b, c, d, e, f

        def __iter__(self):
            return iter([self.a, self.b, self.c, self.d, self.e, self.f])

        def __repr__(self):
            return f"Matrix({self.a}, {self.b}, {self.c}, {self.d}, {self.e}, {self.f})"

    class DummyPage:
        def draw_rect(self, *args, **kwargs):
            pass

        def insert_textbox(self, *args, **kwargs):
            return 0  # Assume success in dummy mode

        def insert_image(self, *args, **kwargs):
            pass

        def insert_font(self, *args, **kwargs):
            pass

        def draw_line(self, *args, **kwargs):
            pass

        def draw_bezier(self, *args, **kwargs):
            pass

        @property
        def rect(self):
            return Rect(0, 0, 612, 792)

    fitz = type(
        "module",
        (object,),
        {
            "Rect": Rect,
            "Point": Point,
            "Matrix": Matrix,
            "Page": DummyPage,
            "get_text_length": lambda t, **k: len(t) * 8,
            "open": lambda *a, **k: type(
                "doc",
                (object,),
                {
                    "page_count": 1,
                    "__getitem__": lambda s, i: DummyPage(),
                    "metadata": {},
                    "close": lambda: None,
                    "new_page": lambda w, h: DummyPage(),
                    "save": lambda p: None,
                    "get_text": lambda *a, **k: {"blocks": []},
                    "get_drawings": lambda: [],
                },
            )(),
        },
    )()
