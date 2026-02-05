# Product Overview

Uriscan Web is a middleware dashboard application for managing and reviewing urine test strip submissions. The system serves as an administrative interface between lab technicians who submit test results and reviewers/admins who validate them.

## Core Functionality

- **Submission Review**: Admins review pending submissions with strip images, pad detection, and test results
- **Multi-Source Comparison**: Compare results from URS-14EA readings, URIT readings, and MEDITAPE UC-11A analyzer
- **Approval Workflow**: Accept or reject submissions with detailed feedback
- **Analytics Dashboard**: Track submission trends, acceptance rates, and daily statistics
- **Transaction Management**: Export transaction data for accounting and mark payments as processed
- **Research Dataset Export**: Generate Excel exports of complete dataset for research purposes

## User Roles

- **REVIEWER**: Access to research dataset exports
- **ADMIN**: Full access to submissions, transactions, exports, and analytics
- **Lab Technician**: Submit test results (backend integration, not in this UI)

## Key Features

- Role-based access control with JWT authentication
- Visual comparison of urine characteristics (color, turbidity)
- Image viewing for strip photos, detected pads, and urine samples
- Bulk transaction processing
- Real-time dashboard metrics
