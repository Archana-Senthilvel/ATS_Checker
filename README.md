# ATS Checker
ATS Checker is a web application designed to analyze resumes for compatibility with Applicant Tracking Systems (ATS). It provides users with insights into their resumes to improve their chances of passing through automated filtering systems used by employers.

## Features

1. Resume Upload: Upload resumes in PDF format for analysis.
   
2. ATS Analysis: Evaluate resumes based on ATS-friendly metrics.
 
3. Detailed Reports: Generate insights into formatting, keywords, and other ATS-related factors.
 
4. User-Friendly Interface: Simple and clean interface for seamless user experience.

## Installation

1. Clone the Repository:

git clone <repository-url>
cd ATS_Checker-main

2. Create a Virtual Environment:

python -m venv venv

source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install Dependencies:

pip install -r requirements.txt

4. Apply Migrations:

python manage.py migrate

5. Run the Development Server:

python manage.py runserver

Open your browser and visit http://127.0.0.1:8000.

## Usage
Navigate to the upload page and upload your resume (PDF format only).

Wait for the analysis to complete.

View the detailed results page for insights into your resume.
