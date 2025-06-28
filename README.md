# gmail-mcp

`gmail-mcp` is a powerful and extensible backend service designed to integrate and automate workflows across email, calendar, and spreadsheet services. It provides a solid foundation for building custom productivity and management tools.

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

-  `gmail-mcp/app/handlers/`: Contains the core logic for interacting with external services (email, calendar, sheets).
-  `gmail-mcp/app/utils/`: Provides utility functions for common tasks like logging and email processing.
-  `gmail-mcp/app/state.py`: Manages the application's state.
-  `gmail-mcp/main.py`: The main entry point for the application.
-  `gmail-mcp/pyproject.toml`: Defines project dependencies and metadata.

## Getting Started

### Prerequisites

-  Python 3.9+
-  A package manager like `pip`

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

### Configuration

Before running the application, you may need to configure credentials for the services you want to use (e.g., Google Workspace, Microsoft 365).

1. Navigate to `gmail-mcp/app/handlers/config.py`.
2. Follow the instructions in the file to add your API keys, client secrets, and other necessary configuration details.

## Usage

To run the application, execute the main script:

```sh
python gmail-mcp/main.py
```

Make sure your environment is properly configured and dependencies are installed.

## Contributing

Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request.
