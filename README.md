CSV -> Structured JSON -> X12 837D (Batch or Single Claim) --
This project provides an automated workflow for generating American National Standards Institute X12 837D dental claim files from simple structured data. It converts flat CSV claim records into properly nested JSON and produces a fully compliant X12 output, either as a single batch or as individual X12 files for each claim. The system builds all required loops and segments including provider, subscriber, payer, claim,
service lines, dates, and tooth elements—following the 005010X224A2 specification. This tool is designed to simplify claim submission, reduce manual formatting, and provide a reliable, repeatable way to generate
clean .837D files for clearinghouses or direct payer submission.

