
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

## PDF/Document Generation & Manipulation

The document handler provides a robust API for creating and manipulating PDFs with a wide range of features:

-  **Cover Page:**
   -  Add a premium cover with logo, title, subtitle, author, date, company, and contact info.
-  **Headers & Footers:**
   -  Customizable text, alignment, and optional page numbers.
-  **Watermarks:**
   -  Text or image watermarks with configurable opacity, rotation, color, and size.
-  **Backgrounds:**
   -  Solid color or gradient backgrounds (vertical/horizontal).
-  **Decorative Borders:**
   -  Single, double, or decorative borders with custom color, width, and margin.
-  **Tables:**
   -  Flexible tables with custom styles, column widths, and optional titles.
-  **Images:**
   -  Local or remote images with size, alignment, and captions.
-  **Charts:**
   -  Bar, pie, line, histogram, scatter, and horizontal bar charts with full data/config support.
-  **Lists:**
   -  Bullet or numbered lists with optional titles.
-  **Formatted Text:**
   -  Rich text with bold, italic, underline, color, and hyperlinks.
-  **Multi-Column Layouts:**
   -  Newsletter-style multi-column sections with adjustable spacing.
-  **Text Boxes & Callouts:**
   -  Highlighted text boxes and callout boxes for info, warnings, success, or errors.
-  **QR Codes:**
   -  Embed QR codes with custom data, size, and captions.
-  **Digital Signatures:**
   -  Add signature blocks with name, date, position, and font size.
-  **Footnotes & Endnotes:**
   -  Add references and notes at the bottom or end of the document.
-  **Forms:**
   -  Add interactive form fields (text, date, checkbox, signature).
-  **Appendix:**
   -  Add appendix sections with titles and content.
-  **Page Breaks & Sectioning:**
   -  Fine-grained control over page breaks and document sections.
-  **PDF Manipulation:**
   -  Merge multiple PDFs, split PDFs into parts, and extract PDF metadata (page count, size, encryption, etc.).

### PDF Manipulation Utilities

-  **Merge PDFs:**
   -  Combine multiple PDF files into one.
-  **Split PDFs:**
   -  Split a PDF into multiple files by page count.
-  **Extract PDF Info:**
   -  Get metadata, page count, size, and encryption status.

## Potential Use Case: Team Performance Tracker

This project is an ideal backend for a **Team Performance Tracker**. It can be extended to:

-  **Automate Data Collection:** Parse daily stand-up emails, weekly summaries, and timesheet attachments to automatically extract performance metrics.
-  **Sync with Calendars:** Schedule report reminders, track project deadlines, and block focus time in team members' calendars.
-  **Aggregate Data:** Populate a central spreadsheet with key metrics like tasks completed, hours logged, and goals met.
-  **Automate Communication:** Send summary reports to managers, trigger alerts for missed deadlines, and automate follow-up questions for incomplete reports.

## Project Structure

The project is organized into the following main directories:

-  `gmail-mcp/app/handlers/`: Contains the core logic for interacting with external services (email, calendar, sheets, documents).
-  `gmail-mcp/app/handlers/document/`: PDF/document generation and manipulation logic.
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
