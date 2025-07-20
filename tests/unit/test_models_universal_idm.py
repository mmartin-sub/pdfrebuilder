"""
Tests for Universal IDM (Intermediate Document Model) classes.
"""

from pdfrebuilder.models.universal_idm import (
    Canvas,
    Document,
    DocumentMetadata,
    DrawingElement,
    ImageElement,
    Layer,
    Page,
    TextElement,
)


class TestDocumentMetadata:
    """Test DocumentMetadata class"""

    def test_document_metadata_creation(self):
        """Test creating DocumentMetadata instance"""
        metadata = DocumentMetadata(
            format="PDF 1.4",
            title="Test Document",
            author="Test Author",
            subject="Test Subject",
            keywords="test,keywords",
            creator="Test Creator",
            producer="Test Producer",
        )

        assert metadata.format == "PDF 1.4"
        assert metadata.title == "Test Document"
        assert metadata.author == "Test Author"
        assert metadata.subject == "Test Subject"
        assert metadata.keywords == "test,keywords"
        assert metadata.creator == "Test Creator"
        assert metadata.producer == "Test Producer"

    def test_document_metadata_to_dict(self):
        """Test converting DocumentMetadata to dictionary"""
        metadata = DocumentMetadata(format="PDF 1.4", title="Test Document")

        result = metadata.to_dict()

        assert isinstance(result, dict)
        assert result["format"] == "PDF 1.4"
        assert result["title"] == "Test Document"

    def test_document_metadata_defaults(self):
        """Test DocumentMetadata with default values"""
        metadata = DocumentMetadata()

        # Should not raise an exception
        result = metadata.to_dict()
        assert isinstance(result, dict)


class TestTextElement:
    """Test TextElement class"""

    def test_text_element_creation(self):
        """Test creating TextElement instance"""
        element = TextElement(
            element_id="text_1",
            bbox=[100, 100, 200, 120],
            text="Test text",
            raw_text="T e s t   t e x t",
            font_details={"name": "Arial", "size": 12, "color": 0},
        )

        assert element.element_id == "text_1"
        assert element.bbox == [100, 100, 200, 120]
        assert element.text == "Test text"
        assert element.raw_text == "T e s t   t e x t"
        assert element.font_details["name"] == "Arial"

    def test_text_element_to_dict(self):
        """Test converting TextElement to dictionary"""
        element = TextElement(element_id="text_1", bbox=[100, 100, 200, 120], text="Test text")

        result = element.to_dict()

        assert isinstance(result, dict)
        assert result["type"] == "text"
        assert result["id"] == "text_1"
        assert result["bbox"] == [100, 100, 200, 120]
        assert result["text"] == "Test text"

    def test_text_element_font_details_optional(self):
        """Test TextElement with optional font details"""
        element = TextElement(element_id="text_1", bbox=[100, 100, 200, 120], text="Test text")

        # Should not raise an exception
        result = element.to_dict()
        assert isinstance(result, dict)


class TestImageElement:
    """Test ImageElement class"""

    def test_image_element_creation(self):
        """Test creating ImageElement instance"""
        element = ImageElement(
            element_id="image_1",
            bbox=[200, 200, 400, 300],
            image_file="./images/test.jpg",
        )

        assert element.element_id == "image_1"
        assert element.bbox == [200, 200, 400, 300]
        assert element.image_file == "./images/test.jpg"

    def test_image_element_to_dict(self):
        """Test converting ImageElement to dictionary"""
        element = ImageElement(
            element_id="image_1",
            bbox=[200, 200, 400, 300],
            image_file="./images/test.jpg",
        )

        result = element.to_dict()

        assert isinstance(result, dict)
        assert result["type"] == "image"
        assert result["id"] == "image_1"
        assert result["bbox"] == [200, 200, 400, 300]
        assert result["image_file"] == "./images/test.jpg"


class TestDrawingElement:
    """Test DrawingElement class"""

    def test_drawing_element_creation(self):
        """Test creating DrawingElement instance"""
        element = DrawingElement(
            element_id="drawing_1",
            bbox=[50, 50, 150, 100],
            drawing_commands=[
                {"cmd": "M", "pts": [50, 50]},
                {"cmd": "L", "pts": [150, 100]},
                {"cmd": "H"},
            ],
        )

        assert element.element_id == "drawing_1"
        assert element.bbox == [50, 50, 150, 100]
        assert len(element.drawing_commands) == 3
        assert element.drawing_commands[0]["cmd"] == "M"

    def test_drawing_element_to_dict(self):
        """Test converting DrawingElement to dictionary"""
        element = DrawingElement(
            element_id="drawing_1",
            bbox=[50, 50, 150, 100],
            drawing_commands=[
                {"cmd": "M", "pts": [50, 50]},
                {"cmd": "L", "pts": [150, 100]},
            ],
        )

        result = element.to_dict()

        assert isinstance(result, dict)
        assert result["type"] == "drawing"
        assert result["id"] == "drawing_1"
        assert result["bbox"] == [50, 50, 150, 100]
        assert len(result["drawing_commands"]) == 2

    def test_drawing_element_with_colors(self):
        """Test DrawingElement with color and fill"""
        element = DrawingElement(
            element_id="drawing_1",
            bbox=[50, 50, 150, 100],
            drawing_commands=[],
            color=[1.0, 0.0, 0.0],
            fill=[0.0, 1.0, 0.0],
        )

        result = element.to_dict()

        assert result["color"] == [1.0, 0.0, 0.0]
        assert result["fill"] == [0.0, 1.0, 0.0]


class TestLayer:
    """Test Layer class"""

    def test_layer_creation(self):
        """Test creating Layer instance"""
        layer = Layer(layer_id="layer_1", layer_name="Test Layer", bbox=[0, 0, 612, 792])

        assert layer.layer_id == "layer_1"
        assert layer.layer_name == "Test Layer"
        assert layer.bbox == [0, 0, 612, 792]
        assert layer.content == []

    def test_layer_add_element(self):
        """Test adding elements to layer"""
        layer = Layer(layer_id="layer_1", layer_name="Test Layer", bbox=[0, 0, 612, 792])

        text_element = TextElement(element_id="text_1", bbox=[100, 100, 200, 120], text="Test text")

        layer.add_element(text_element)

        assert len(layer.content) == 1
        assert layer.content[0] == text_element

    def test_layer_to_dict(self):
        """Test converting Layer to dictionary"""
        layer = Layer(layer_id="layer_1", layer_name="Test Layer", bbox=[0, 0, 612, 792])

        text_element = TextElement(element_id="text_1", bbox=[100, 100, 200, 120], text="Test text")
        layer.add_element(text_element)

        result = layer.to_dict()

        assert isinstance(result, dict)
        assert result["layer_id"] == "layer_1"
        assert result["layer_name"] == "Test Layer"
        assert result["bbox"] == [0, 0, 612, 792]
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"


class TestPage:
    """Test Page class"""

    def test_page_creation(self):
        """Test creating Page instance"""
        page = Page(page_number=0, size=[612, 792])

        assert page.page_number == 0
        assert page.size == [612, 792]
        assert page.layers == []

    def test_page_add_layer(self):
        """Test adding layers to page"""
        page = Page(page_number=0, size=[612, 792])

        layer = Layer(layer_id="layer_1", layer_name="Test Layer", bbox=[0, 0, 612, 792])

        page.add_layer(layer)

        assert len(page.layers) == 1
        assert page.layers[0] == layer

    def test_page_to_dict(self):
        """Test converting Page to dictionary"""
        page = Page(page_number=0, size=[612, 792])

        layer = Layer(layer_id="layer_1", layer_name="Test Layer", bbox=[0, 0, 612, 792])
        page.add_layer(layer)

        result = page.to_dict()

        assert isinstance(result, dict)
        assert result["type"] == "page"
        assert result["page_number"] == 0
        assert result["size"] == [612, 792]
        assert len(result["layers"]) == 1


class TestCanvas:
    """Test Canvas class"""

    def test_canvas_creation(self):
        """Test creating Canvas instance"""
        canvas = Canvas(canvas_size=[1920, 1080])

        assert canvas.canvas_size == [1920, 1080]
        assert canvas.layers == []

    def test_canvas_add_layer(self):
        """Test adding layers to canvas"""
        canvas = Canvas(canvas_size=[1920, 1080])

        layer = Layer(layer_id="layer_1", layer_name="Test Layer", bbox=[0, 0, 1920, 1080])

        canvas.add_layer(layer)

        assert len(canvas.layers) == 1
        assert canvas.layers[0] == layer

    def test_canvas_to_dict(self):
        """Test converting Canvas to dictionary"""
        canvas = Canvas(canvas_size=[1920, 1080])

        layer = Layer(layer_id="layer_1", layer_name="Test Layer", bbox=[0, 0, 1920, 1080])
        canvas.add_layer(layer)

        result = canvas.to_dict()

        assert isinstance(result, dict)
        assert result["type"] == "canvas"
        assert result["canvas_size"] == [1920, 1080]
        assert len(result["layers"]) == 1


class TestDocument:
    """Test Document class"""

    def test_document_creation(self):
        """Test creating Document instance"""
        metadata = DocumentMetadata(title="Test Document")

        document = Document(
            version="1.0",
            engine="fitz",
            engine_version="PyMuPDF 1.26.23",
            metadata=metadata,
        )

        assert document.version == "1.0"
        assert document.engine == "fitz"
        assert document.engine_version == "PyMuPDF 1.26.23"
        assert document.metadata == metadata
        assert document.document_structure == []

    def test_document_add_page(self):
        """Test adding pages to document"""
        document = Document(version="1.0", engine="fitz")

        page = Page(page_number=0, size=[612, 792])

        document.add_document_unit(page)

        assert len(document.document_structure) == 1
        assert document.document_structure[0] == page

    def test_document_add_canvas(self):
        """Test adding canvas to document"""
        document = Document(version="1.0", engine="psd_tools")

        canvas = Canvas(canvas_size=[1920, 1080])

        document.add_document_unit(canvas)

        assert len(document.document_structure) == 1
        assert document.document_structure[0] == canvas

    def test_document_to_dict(self):
        """Test converting Document to dictionary"""
        metadata = DocumentMetadata(title="Test Document")

        document = Document(
            version="1.0",
            engine="fitz",
            engine_version="PyMuPDF 1.26.23",
            metadata=metadata,
        )

        page = Page(page_number=0, size=[612, 792])
        document.add_document_unit(page)

        result = document.to_dict()

        assert isinstance(result, dict)
        assert result["version"] == "1.0"
        assert result["engine"] == "fitz"
        assert result["engine_version"] == "PyMuPDF 1.26.23"
        assert "metadata" in result
        assert len(result["document_structure"]) == 1
        assert result["document_structure"][0]["type"] == "page"

    def test_document_get_pages(self):
        """Test getting pages from document"""
        document = Document(version="1.0", engine="fitz")

        page1 = Page(page_number=0, size=[612, 792])
        page2 = Page(page_number=1, size=[612, 792])
        canvas = Canvas(canvas_size=[1920, 1080])

        document.add_document_unit(page1)
        document.add_document_unit(page2)
        document.add_document_unit(canvas)

        pages = document.get_pages()

        assert len(pages) == 2
        assert all(isinstance(p, Page) for p in pages)
        assert pages[0].page_number == 0
        assert pages[1].page_number == 1

    def test_document_get_canvases(self):
        """Test getting canvases from document"""
        document = Document(version="1.0", engine="psd_tools")

        page = Page(page_number=0, size=[612, 792])
        canvas1 = Canvas(canvas_size=[1920, 1080])
        canvas2 = Canvas(canvas_size=[1280, 720])

        document.add_document_unit(page)
        document.add_document_unit(canvas1)
        document.add_document_unit(canvas2)

        canvases = document.get_canvases()

        assert len(canvases) == 2
        assert all(isinstance(c, Canvas) for c in canvases)
        assert canvases[0].canvas_size == [1920, 1080]
        assert canvases[1].canvas_size == [1280, 720]
