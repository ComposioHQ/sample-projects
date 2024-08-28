import requests
import pymupdf
import io


def url_to_pdf_content(url: str) -> str:
    """
    Convert a URL to string of the PDF content.

    @param url: str
    @return: str
    """
    request = requests.get(url)  # Get the content of the URL
    filestream = io.BytesIO(request.content)  # Convert the content to a stream

    with pymupdf.open(stream=filestream, filetype="pdf") as doc:
        content = ""  # Initialize an empty string to store the content
        for page in doc:
            content += page.get_text()  # Append the text of each page to the content
    return content
