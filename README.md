
`gmail-mcp` is a powerful and extensible backend service designed to integrate and automate workflows across email, calendar, spreadsheet, and document/PDF services. It provides a solid foundation for building custom productivity and management tools.

## Features

This project provides a set of handlers to interact with various services:

-  **Email Management:**
   -  Fetch and parse incoming emails.
   -  Send emails programmatically.
   -  Handle email attachments.
   -  Organize emails with labels.
   -  Perform advanced email searches.
   -  Batch process emails.
-  **Calendar Integration:**
   -  Create, view, and manage calendar events.
-  **Spreadsheet Integration:**
   -  Read from and write to spreadsheets.
-  **Document/PDF Generation & Manipulation:**
   -  Generate professional PDFs with advanced layout and visual features.
   -  Merge, split, and extract information from PDF files.
   -  Add cover pages, headers, footers, watermarks, backgrounds, and decorative borders.
   -  Insert tables, images, charts, lists, formatted text, and multi-column layouts.
   -  Add text boxes, callouts, QR codes, digital signatures, footnotes, endnotes, forms, appendix sections, and more.
   -  Control page breaks, sectioning, and content flow.
   -  Extract PDF metadata and page information.
-  **Authentication:**
   -  Handles authentication with service providers.

## Potential Use Case: Team Performance Tracker

This project is an ideal backend for a **Team Performance Tracker**. It can be extended to:

-  **Automate Data Collection:** Parse daily stand-up emails, weekly summaries, and timesheet attachments to automatically extract performance metrics.
-  **Sync with Calendars:** Schedule report reminders, track project deadlines, and block focus time in team members' calendars.
-  **Aggregate Data:** Populate a central spreadsheet with key metrics like tasks completed, hours logged, and goals met.
-  **Automate Communication:** Send summary reports to managers, trigger alerts for missed deadlines, and automate follow-up questions for incomplete reports.

## Project Structure

The project is organized into the following main directories:

-  `gmail-mcp/app/handlers/`: Contains the core logic for interacting with external services (email, calendar, sheets, documents).
-  `gmail-mcp/app/utils/`: Provides utility functions for common tasks like logging and email processing.
-  `gmail-mcp/app/state.py`: Manages the application's state.
-  `gmail-mcp/main.py`: The main entry point for the application.
-  `gmail-mcp/pyproject.toml`: Defines project dependencies and metadata.

## Getting Started

### Prerequisites

-  Python 3.9+
-  A package manager like `pip` or `uv`

### Installation

1. **Clone the repository:**

   ```sh
   git clone <repository-url>
   cd gmail-mcp
   ```

2. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   The project uses `pyproject.toml` to manage dependencies. Install them with `pip`:
   ```sh
   pip install .
   ```

## Usage

To run the application, install the `claude desktop` and configure the following config in `claude_desktop_config.json`:

```
"email-mcp": {
         "command": "uv",
         "args": [
            "--directory",
            "/Users/<MAC_USER_NAME>/Desktop/mcp/email-mcp",
            "run",
            "main.py"
         ],
         "env": {
            "GOOGLE_CLIENT_ID": <GOOGLE_CLIENT_ID>
            "GOOGLE_CLIENT_SECRET": <GOOGLE_CLIENT_SECRET>
         }
      }
```

Make sure your environment is properly configured and dependencies are installed.

## Contributing

Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request.
