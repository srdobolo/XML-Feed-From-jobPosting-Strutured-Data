# Job Listing RSS Feed Generator

This repository contains a Python script to generate an RSS feed for job listings from the SmartRecruitments website. The script fetches job postings from the specified URL, extracts relevant details, and creates an RSS feed in XML format.

## Overview

The script performs the following steps:

1. Loads the main jobs page and extracts links to individual job postings.
2. Fetches and parses each job posting page to retrieve job details.
3. Extracts relevant information from the JSON-LD script embedded in each job posting.
4. Compiles the job details into an RSS feed format.
5. Saves the RSS feed to an XML file.

## Variables

The script does not require manual variable replacements. It dynamically retrieves and processes job data directly from the target website.

## Usage

1. **Install Dependencies**: Ensure you have the required Python packages. Install them using:
    ```bash
    pip install requests beautifulsoup4
    ```

2. **Run the Script**: Execute the script using Python:
    ```bash
    python script.py
    ```

3. **Output**: The script will generate a [feed.xml](https://srdobolo.github.io/XML-Feed-From-jobPosting-Strutured-Data/feed.xml) file in the same directory containing the RSS feed.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests with improvements or suggestions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
