import pytest
from unittest.mock import patch, MagicMock
from backend.scraper import scrape_faculty_directory, scrape_faculty_profile

""" 
Unit tests for backend.scraper module.
Goals:
  - correct parsing when HTML is well formed
  - handle missing data gracefully
  - no network calls during tests (used mock requests)
"""

def fake_response(html):
    r = MagicMock()
    r.content = html.encode("utf-8")
    r.status_code = 200
    r.raise_for_status = lambda: None
    return r

@patch("backend.scraper.requests.get")
def test_scrape_faculty_directory_basic(mock_get, tmp_path, monkeypatch):
    # Basic test with one faculty entry

    html = """
    <div class="col-12 list-name">
      <a href="https://engineering.purdue.edu/ECE/People/ptProfile?resource_id=242740">
        Hadiseh  
        <strong>Alaeian</strong>
      </a>
    </div>
    """
    mock_get.return_value = fake_response(html)

    monkeypatch.setattr("backend.scraper.LOG_FILE", tmp_path / "log.txt")

    out = scrape_faculty_directory()
    assert len(out) == 1
    assert out[0]["name"] == "Hadiseh Alaeian"
    assert out[0]["profile_url"] == "https://engineering.purdue.edu/ECE/People/ptProfile?resource_id=242740"

@patch("backend.scraper.requests.get")
def test_scrape_faculty_profile(mock_get):
    # HTML with both webpage and research interests

    html = """
    <div>
        <strong>Webpage:</strong>
        <a href="https://engineering.purdue.edu/qnp"></a>
    </div>

    <div>
        <h2>Research</h2>
        <p class='profile-research'>
            Hybrid, scalable, and integrated photonic quantum technologies and theoretical and experimental quantum optics/photonics . In particular, I am interested in theoretical and experimental investigations of interacting and correlated open quantum optical systems. We engineer light-matter interactions and employ highly excited Rydberg states to create large optical non-linearity, which leads to exotic states of light required for many different quantum technologies based on photons.
        </p>
    </div>
    """
    mock_get.return_value = fake_response(html)
    page, interest = scrape_faculty_profile(
        "https://engineering.purdue.edu/ECE/People/ptProfile?resource_id=242740",
        "Hadiesh Alaeian"
    )
    
    assert page == "https://engineering.purdue.edu/qnp"
    assert interest == "Hybrid, scalable, and integrated photonic quantum technologies and theoretical and experimental quantum optics/photonics . In particular, I am interested in theoretical and experimental investigations of interacting and correlated open quantum optical systems. We engineer light-matter interactions and employ highly excited Rydberg states to create large optical non-linearity, which leads to exotic states of light required for many different quantum technologies based on photons."

@patch("backend.scraper.requests.get")
def test_scrape_faculty_profile_missing_data(mock_get):
    # HTML with no webpage and no research interests

    html = """
    <div>
        <strong>Some other field:</strong>
        <a href="https://example.com"></a>
    </div>

    <div>
        <h2>Research</h2>
        <p class='some-other-class'>
            This paragraph won't be picked up because it has wrong class
        </p>
    </div>
    """
    mock_get.return_value = fake_response(html)
    
    page, interest = scrape_faculty_profile(
        "https://engineering.purdue.edu/ECE/People/ptProfile?resource_id=123456",
        "Test Faculty"
    )
    
    # Both should be None since the data is not present in expected format
    assert page is None
    assert interest is None