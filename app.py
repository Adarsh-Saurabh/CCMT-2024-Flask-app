# app.py
from flask import Flask, render_template, request, jsonify, send_file, Response
import pandas as pd
import numpy as np
import os
import io
import tempfile

app = Flask(__name__)

# Load the Excel file
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'admissions_data.xlsx')
    df = pd.read_excel(file_path)
    return df

@app.route('/')
def index():
    df = load_data()
    
    # Get unique values for each filter
    round_numbers = sorted(df['Round'].unique())
    institutes = sorted(df['Institute'].unique())
    programs = sorted(df['PG Program'].unique())
    categories = sorted(df['Category'].unique())
    groups = sorted(df['Group'].unique())
    
    # Get total count
    total_records = len(df)
    
    return render_template('index.html', 
                           round_numbers=round_numbers,
                           institutes=institutes,
                           programs=programs,
                           categories=categories,
                           groups=groups,
                           total_records=total_records)

@app.route('/data')
def get_data():
    df = load_data()
    
    # Get filter parameters
    round_number = request.args.get('round')
    institute = request.args.get('institute')
    program = request.args.get('program')
    category = request.args.get('category')
    group = request.args.get('group')
    min_score = request.args.get('minScore')
    max_score = request.args.get('maxScore')
    search = request.args.get('search')
    
    # Apply filters if provided
    if round_number and round_number != '--- All Round ---':
        df = df[df['Round'] == round_number]
    if institute and institute != '--- All Institute ---':
        df = df[df['Institute'] == institute]
    if program and program != '--- All Programs ---':
        df = df[df['PG Program'] == program]
    if category and category != '--- All Category ---':
        df = df[df['Category'] == category]
    if group and group != '--- All Groups ---':
        df = df[df['Group'] == group]
    
    # Apply score range filter if provided
    if min_score and max_score:
        min_score = int(min_score)
        max_score = int(max_score)
        df = df[
            ((df['Max GATE Score'] >= min_score) & (df['Max GATE Score'] <= max_score)) |
            ((df['Min GATE Score'] >= min_score) & (df['Min GATE Score'] <= max_score))
        ]
    
    # Apply search if provided
    if search:
        search = search.lower()
        df = df[df.apply(lambda row: any(str(cell).lower().find(search) != -1 for cell in row), axis=1)]
    
    # Pagination
    length = int(request.args.get('length', 25))
    start = int(request.args.get('start', 0))
    
    # Sorting
    order_column = request.args.get('order[0][column]')
    order_dir = request.args.get('order[0][dir]')
    
    if order_column and order_dir:
        order_column = int(order_column)
        columns = ['sr_no', 'Round', 'Institute', 'PG Program', 'Group', 'Category', 'Max GATE Score', 'Min GATE Score']
        
        if order_column > 0 and order_column < len(columns):
            col_name = columns[order_column]
            ascending = order_dir != 'desc'
            df = df.sort_values(by=col_name, ascending=ascending)
    
    # Get total filtered count
    total_filtered = len(df)
    
    # Slice data for pagination
    if length != -1:
        df = df.iloc[start:start + length]
    
    # Convert dataframe to list of dicts for JSON response
    data = df.to_dict('records')
    
    # Add index for display
    for i, item in enumerate(data, start=start + 1):
        item['sr_no'] = i
    
    return jsonify({
        'data': data,
        'recordsTotal': total_filtered,
        'recordsFiltered': total_filtered
    })

@app.route('/export')
def export_data():
    df = load_data()
    
    # Get filter parameters (same as in get_data)
    round_number = request.args.get('round')
    institute = request.args.get('institute')
    program = request.args.get('program')
    category = request.args.get('category')
    group = request.args.get('group')
    min_score = request.args.get('minScore')
    max_score = request.args.get('maxScore')
    search = request.args.get('search')
    export_format = request.args.get('format', 'csv')
    
    # Apply filters (reusing same logic as in get_data)
    if round_number and round_number != '--- All Round ---':
        df = df[df['Round'] == round_number]
    if institute and institute != '--- All Institute ---':
        df = df[df['Institute'] == institute]
    if program and program != '--- All Programs ---':
        df = df[df['PG Program'] == program]
    if category and category != '--- All Category ---':
        df = df[df['Category'] == category]
    if group and group != '--- All Groups ---':
        df = df[df['Group'] == group]
    
    # Apply score range filter if provided
    if min_score and max_score:
        min_score = int(min_score)
        max_score = int(max_score)
        df = df[
            ((df['Max GATE Score'] >= min_score) & (df['Max GATE Score'] <= max_score)) |
            ((df['Min GATE Score'] >= min_score) & (df['Min GATE Score'] <= max_score))
        ]
    
    # Apply search if provided
    if search:
        search = search.lower()
        df = df[df.apply(lambda row: any(str(cell).lower().find(search) != -1 for cell in row), axis=1)]
    
    # Add serial number column
    df.insert(0, 'Sr.No', range(1, len(df) + 1))
    
    # Export based on format
    if export_format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=admissions_data.csv"}
        )
    
    elif export_format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Admissions Data')
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="admissions_data.xlsx"
        )
    
    elif export_format == 'pdf':
        # This is a simplified PDF export using HTML
        # For production, you might want to use a proper PDF library
        import pdfkit
        
        html = df.to_html(index=False)
        css = """
        <style>
            table { border-collapse: collapse; width: 100%; font-size: 10px; }
            th, td { border: 1px solid #ddd; padding: 4px; }
            th { background-color: #f2f2f2; }
        </style>
        """
        html = f"<html><head>{css}</head><body>{html}</body></html>"
        
        try:
            pdf = pdfkit.from_string(html, False)
            return Response(
                pdf,
                mimetype="application/pdf",
                headers={"Content-disposition": "attachment; filename=admissions_data.pdf"}
            )
        except Exception as e:
            # Fallback to Excel if PDF generation fails
            return Response(
                f"PDF generation failed: {str(e)}. Try exporting to Excel instead.",
                mimetype="text/plain"
            )
    
    else:
        return Response("Unsupported export format", mimetype="text/plain")

if __name__ == '__main__':
    app.run(debug=True)