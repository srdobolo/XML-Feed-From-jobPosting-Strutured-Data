This repository is designed to generate an XML feed based on job posting structured data using a Python script. It automates the process of generating an XML file for job postings, ensuring compliance with structured data standards and facilitating integrations with third-party systems.

[XML Feed](https://feed.recruityard.com/feed.xml) | [RSS](https://feed.recruityard.com/rss.xml) | [Jobatus](https://feed.recruityard.com/jobatus.xml)

## Overview

The script performs the following steps:

1. Loads the main jobs page and extracts links to individual job postings.
2. Fetches and parses each job posting page to retrieve job details.
3. Extracts relevant information from the JSON-LD script embedded in each job posting.
4. Compiles the job details into an RSS feed format.
5. Saves the RSS feed to an XML file.

## Features

- Generates an XML feed (`feed.xml`) for job postings.
- Scheduled updates using GitHub Actions.
- Customizable logic for parsing and generating structured data.
- Lightweight and efficient.

---

## Requirements

- Python 3.7 or higher.
- Required Python dependencies (see `requirements.txt`).
- GitHub Actions configured with appropriate permissions for automation.

---

## GitHub Actions Workflow

The repository includes a GitHub Actions workflow to automate the generation and commit of the `feed.xml` file:

### **Workflow Trigger**

The workflow is triggered by:
- **Scheduled runs** (every hour).
- **Manual dispatch**.

### **How It Works**
1. The script runs via GitHub Actions.
2. The `feed.xml` file is updated with the latest job posting data.
3. Changes are committed and pushed to the repository.

### Secrets Configuration

Ensure the following secrets are added to your GitHub repository:
- **`GH_TOKEN`**: A GitHub token with `write` permissions to allow automated commits.

### Modifying the Schedule

The schedule is defined in the workflow file (`.github/workflows/run-main.yml`). To update the schedule:

```yaml
schedule:
  - cron: '0 * * * *' # Runs every hour
```
Modify the cron expression as needed.

---

## File Structure

```
├── main.py              # Python script to generate the XML feed
├── feed.xml             # Generated XML file
├── requirements.txt     # Python dependencies
├── .github/workflows    # GitHub Actions workflow configuration
├── README.md            # Project documentation
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support

If you encounter any issues or have questions, feel free to open an issue in this repository.
