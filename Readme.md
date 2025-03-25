# Flask Excel Data Viewer

This is a Flask application for viewing and filtering Excel data, specifically designed for admissions data from an Excel file named `admissions_data.xlsx`.

## Features

- Load and display data from an Excel file
- Advanced filtering options:
  - Filter by Round Number, Institute, Program, Category, and Group
  - GATE Score range slider for min/max scores
  - Column visibility toggle
  - Compact/Normal view modes
- Export options (CSV, Excel, PDF)
- Compare selected rows feature
- Fullscreen toggle
- Search functionality across all columns
- Pagination with adjustable page size
- Sortable columns
- Compact UI design to maximize data visibility
- Responsive design

## Prerequisites

- Python 3.6 or higher
- Flask
- pandas
- openpyxl (for reading Excel files)

## Installation

1. Clone this repository or download the files

2. Create a virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages
   ```bash
   pip install Flask pandas openpyxl pdfkit
   ```

   Note: For PDF export functionality, you'll need to install wkhtmltopdf:
   - On Windows: Download from https://wkhtmltopdf.org/downloads.html
   - On Ubuntu/Debian: `sudo apt-get install wkhtmltopdf`
   - On macOS: `brew install wkhtmltopdf`
   
   The application uses several JavaScript libraries that are loaded from CDNs:
   - jQuery for DOM manipulation
   - Bootstrap for UI components
   - DataTables for table functionality
   - Select2 for searchable dropdowns

4. Place your `admissions_data.xlsx` file in the project directory

5. Make sure your Excel file has the following columns:
   - Round
   - Institute
   - PG Program
   - Group
   - Category
   - Max GATE Score
   - Min GATE Score

## Project Structure

```
flask-excel-app/
├── app.py                # Flask application
├── admissions_data.xlsx  # Your Excel data file
└── templates/
    └── index.html        # HTML template
```

## Running the Application

1. Run the Flask application
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:5000/`

## Customization

- To change the Excel file name, modify the `file_path` in the `load_data()` function in `app.py`
- To add or remove columns, update the `columns` array in the DataTable initialization in `index.html`
- To change the styling, modify the CSS in the `<style>` section of `index.html`

## How It Works

1. The Flask application reads the Excel file using pandas
2. The unique values from each column are provided as filter options
3. When filters are applied, the data is filtered on the server-side
4. The DataTables library handles the client-side display, pagination, and sorting

## For Django Developers

If you're familiar with Django, note that this Flask app follows a similar pattern:
- The `app.py` file is similar to a combination of Django's `views.py` and `urls.py`
- The template structure is similar to Django's templates
- The data API endpoint follows RESTful principles like Django REST Framework

To adapt this to Django:
1. Create a Django model to represent the Excel data
2. Use Django's ORM instead of pandas for filtering
3. Create a Django template with the same HTML structure
4. Use Django's URL routing instead of Flask's decorators