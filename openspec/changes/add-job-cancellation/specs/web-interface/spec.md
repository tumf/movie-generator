# web-interface Specification Delta

## MODIFIED Requirements

### Requirement: Job Cancellation UI

The system SHALL provide a cancel button for jobs in `pending` or `processing` status.
The cancel button SHALL be displayed in the job status partial template.
The cancel button SHALL use HTMX to call the cancellation API without page reload.
The cancel button SHALL show a confirmation dialog before cancelling using `hx-confirm`.
The cancel button SHALL NOT be displayed for jobs in `completed`, `failed`, or `cancelled` status.

#### Scenario: User cancels a pending job

- **GIVEN** a job with status `pending`
- **WHEN** user views the job detail page
- **THEN** a "キャンセル" button is displayed
- **WHEN** user clicks the cancel button
- **THEN** a confirmation dialog appears with message "このジョブをキャンセルしますか？"
- **WHEN** user confirms
- **THEN** the job status changes to `cancelled`
- **AND** the status badge displays "🚫 キャンセル"
- **AND** the cancel button disappears

#### Scenario: User cancels a processing job

- **GIVEN** a job with status `processing`
- **WHEN** user views the job detail page
- **THEN** a "キャンセル" button is displayed
- **WHEN** user clicks the cancel button and confirms
- **THEN** the job status changes to `cancelled`
- **AND** the worker stops processing the job
- **AND** partial output files are cleaned up

#### Scenario: Cancel button not shown for completed jobs

- **GIVEN** a job with status `completed`
- **WHEN** user views the job detail page
- **THEN** no cancel button is displayed
- **AND** only the download button is shown

#### Scenario: Cancel button not shown for failed jobs

- **GIVEN** a job with status `failed`
- **WHEN** user views the job detail page
- **THEN** no cancel button is displayed

#### Scenario: Cancel button not shown for already cancelled jobs

- **GIVEN** a job with status `cancelled`
- **WHEN** user views the job detail page
- **THEN** no cancel button is displayed

### Requirement: Job Cancellation API Endpoint

The system SHALL provide a `POST /api/jobs/{job_id}/cancel` endpoint for job cancellation.
The endpoint SHALL only allow cancellation of jobs with status `pending` or `processing`.
The endpoint SHALL update the job status to `cancelled` and set `completed_at` timestamp.
The endpoint SHALL return HTTP 400 for jobs that cannot be cancelled (completed, failed, already cancelled).
The endpoint SHALL return HTTP 404 if the job does not exist.
The endpoint SHALL return HTTP 200 with `{"status": "cancelled"}` on success.

#### Scenario: Successfully cancel a pending job via API

- **GIVEN** a job with ID `abc123` and status `pending`
- **WHEN** client sends `POST /api/jobs/abc123/cancel`
- **THEN** the response status is 200
- **AND** the response body is `{"status": "cancelled"}`
- **AND** the job status in database is `cancelled`
- **AND** the `completed_at` field is set to current timestamp

#### Scenario: Successfully cancel a processing job via API

- **GIVEN** a job with ID `def456` and status `processing`
- **WHEN** client sends `POST /api/jobs/def456/cancel`
- **THEN** the response status is 200
- **AND** the response body is `{"status": "cancelled"}`
- **AND** the job status in database is `cancelled`
- **AND** the `completed_at` field is set to current timestamp

#### Scenario: Cannot cancel a completed job

- **GIVEN** a job with ID `xyz789` and status `completed`
- **WHEN** client sends `POST /api/jobs/xyz789/cancel`
- **THEN** the response status is 400
- **AND** the response body contains error message "Cannot cancel a completed job"

#### Scenario: Cannot cancel an already cancelled job

- **GIVEN** a job with ID `aaa111` and status `cancelled`
- **WHEN** client sends `POST /api/jobs/aaa111/cancel`
- **THEN** the response status is 400
- **AND** the response body contains error message "Job is already cancelled"

#### Scenario: Cancel non-existent job

- **GIVEN** no job with ID `nonexistent`
- **WHEN** client sends `POST /api/jobs/nonexistent/cancel`
- **THEN** the response status is 404
- **AND** the response body contains error message "Job not found"

### Requirement: Worker Cancellation Detection

The worker SHALL periodically check job status during processing.
The worker SHALL detect when a job status changes to `cancelled`.
The worker SHALL immediately stop processing when cancellation is detected.
The worker SHALL clean up partial output files (script, audio, slides, video) for cancelled jobs.
The worker SHALL log cancellation events with job ID.

#### Scenario: Worker detects cancellation during script generation

- **GIVEN** a job is in `processing` status at script generation step
- **WHEN** the job status changes to `cancelled` in the database
- **AND** the worker checks job status before next step
- **THEN** the worker stops processing immediately
- **AND** the worker deletes the job directory `/app/data/jobs/{job_id}`
- **AND** the worker logs "Job {job_id} was cancelled"
- **AND** the worker does not update job status (already cancelled)

#### Scenario: Worker detects cancellation during video rendering

- **GIVEN** a job is in `processing` status at video rendering step
- **WHEN** the job status changes to `cancelled` in the database
- **AND** the worker checks job status before next rendering frame
- **THEN** the worker stops the Remotion process
- **AND** the worker deletes partial video files
- **AND** the worker logs "Job {job_id} was cancelled during video rendering"

#### Scenario: Worker cleans up cancelled job files

- **GIVEN** a job with ID `cleanup123` is cancelled during processing
- **WHEN** the worker detects the cancellation
- **THEN** the worker deletes `/app/data/jobs/cleanup123/` directory
- **AND** all subdirectories (script, audio, slides, remotion) are removed
- **AND** the worker logs "Cleaned up cancelled job cleanup123"

### Requirement: Cancelled Job Status Display

The system SHALL display a clear message when a job is cancelled.
The cancelled status SHALL use a distinct visual style (gray badge).
The cancelled message SHALL inform users they can create a new job.
The cancelled status SHALL stop HTMX polling (no auto-refresh).

#### Scenario: Display cancelled job status

- **GIVEN** a job with status `cancelled`
- **WHEN** user views the job detail page
- **THEN** a gray badge displays "🚫 キャンセル"
- **AND** a message box displays "このジョブはキャンセルされました。新しいジョブを作成できます。"
- **AND** no progress bar is shown
- **AND** no cancel button is shown
- **AND** the page stops auto-refreshing

#### Scenario: Cancelled job polling stops

- **GIVEN** a job with status `processing` and auto-refresh enabled
- **WHEN** the job status changes to `cancelled`
- **AND** HTMX fetches the updated status partial
- **THEN** the response includes `HX-Stop-Polling: true` header
- **AND** the browser stops polling for updates

## ADDED Requirements

None. All requirements are modifications to existing web-interface capabilities.

## REMOVED Requirements

None.
