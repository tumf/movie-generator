# web-interface Specification

## Purpose

This specification defines the web-based user interface for the movie generator system.
It covers the presentation layer including job status displays, video playback capabilities,
and user interactions with generated content.
## Requirements
### Requirement: Movie Player in Completed Job View

The system SHALL display an inline HTML5 video player when a job status is `completed`.
The video player SHALL be placed above the download button.
The video player SHALL use browser-native controls (play/pause, seek, volume, fullscreen).
The video player SHALL be responsive and adapt to the container width.

#### Scenario: User views completed job with video player

- **WHEN** user opens a completed job page
- **THEN** an inline video player is displayed above the download button
- **AND** the video can be played, paused, and seeked
- **AND** the download button remains available below the player

#### Scenario: Video streaming with seek support

- **WHEN** user seeks to a specific position in the video
- **THEN** the video plays from the requested position
- **AND** the API supports HTTP Range requests for efficient streaming

### Requirement: Video Streaming API Endpoint

The system SHALL provide a `/api/jobs/{job_id}/video` endpoint for video streaming.
The endpoint SHALL support HTTP Range requests for seek functionality.
The endpoint SHALL return appropriate `Content-Type` header (`video/mp4`).
The endpoint SHALL return 404 if the job is not completed or video file is missing.

#### Scenario: Streaming video for completed job

- **WHEN** client requests `/api/jobs/{job_id}/video`
- **AND** the job status is `completed`
- **AND** the video file exists
- **THEN** the system returns the video with `Content-Type: video/mp4`
- **AND** the response supports Range requests

#### Scenario: Video not ready

- **WHEN** client requests `/api/jobs/{job_id}/video`
- **AND** the job status is not `completed`
- **THEN** the system returns HTTP 400 with error message

#### Scenario: Video file missing

- **WHEN** client requests `/api/jobs/{job_id}/video`
- **AND** the job status is `completed`
- **AND** the video file does not exist
- **THEN** the system returns HTTP 404 with error message

### Requirement: Firecrawl summaryによる事前コンテンツ品質チェック
システムは、WebUIの`/jobs/create`とAPIの`/api/jobs`におけるジョブ作成要求に対して、Firecrawlのsummaryを取得して品質チェックを実施しなければならない (SHALL)。
summaryは前後の空白を除去したうえで200文字以上を合格とする。
品質チェックに失敗した場合、システムはエラーメッセージを返しジョブを作成してはならない。

#### Scenario: WebUI/APIで品質チェックが合格する
- **WHEN** ユーザーがURLでジョブ作成を要求する
- **AND** Firecrawl summaryが200文字以上である
- **THEN** ジョブが作成される

#### Scenario: Summaryが短すぎる
- **WHEN** ユーザーがURLでジョブ作成を要求する
- **AND** Firecrawl summaryが200文字未満である
- **THEN** エラーメッセージが返され、ジョブは作成されない

#### Scenario: Firecrawlのsummary取得に失敗する
- **WHEN** ユーザーがURLでジョブ作成を要求する
- **AND** Firecrawl APIキー未設定、タイムアウト、または取得エラーが発生する
- **THEN** エラーメッセージが返され、ジョブは作成されない
