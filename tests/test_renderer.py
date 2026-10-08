from app.certificate.renderer import render_certificate
from datetime import date

def test_renderer_creates_pdf(tmp_path):
    output_path = tmp_path / "test.pdf"
    
    render_certificate(
        recipient_name="John Doe",
        course="Python basics",
        event_name="Bootcamp",
        issue_date=date(2026, 10, 8),
        output_path=output_path
    )
    
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    with open(output_path, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"
