# Google Classroom File Downloader

This Python script automates the process of downloading files from Google Classroom courses. It connects to the Google Classroom API to retrieve course materials and announcements, then downloads these files to your local machine.

## Features

- Lists Google Classroom courses.
- Downloads course materials and announcements, organizing them by course.
- Supports multiple file types, including PDFs, DOCX, PPTX, and more.

## Prerequisites

- Python 3.x
- Google API credentials for Classroom and Drive
- Installed dependencies listed in `requirements.txt`

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/google-classroom-downloader.git
    cd google-classroom-downloader
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up Google API credentials:**
    - Download the `credentials.json` file from the Google Developer Console.
    - Place the `credentials.json` file in the root of the project directory.

## Usage

1. **Run the script:**
    ```bash
    python classroom_downloader.py
    ```

2. **Authorize the application:**
    - On first run, you will be prompted to authorize the application via a web browser.
    - A token will be saved locally (`classroom-token.json` and `drive-token.json`) for future use.

3. **View downloaded files:**
    - Files will be downloaded into folders named after the course titles.

## File Structure

- **classroom_downloader.py:** The main script that interacts with Google Classroom and Drive APIs.
- **credentials.json:** Google API credentials file.
- **requirements.txt:** List of Python dependencies.

## Notes

- Ensure that `credentials.json` and the generated tokens (`classroom-token.json` and `drive-token.json`) are kept secure and not shared publicly.
- The script checks for existing files to avoid re-downloading duplicates.

## Troubleshooting

- **HttpError:** Ensure that your API credentials are correct and that you have the necessary permissions for the API scopes.
- **Invalid file type:** The script skips unsupported file types, but you can extend the list of valid types in the `valid` function.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any improvements or suggestions.


Any questions dm or mail me : zeq.alidemaj @ gmail .com
