# Google Veo 3.1 API 利用ガイド

**作成日**: 2025年12月29日  
**対象**: Google Veo 3.1 API（Vertex AI / Gemini API）

---

## 目次

1. [概要](#概要)
2. [利用可能なモデル](#利用可能なモデル)
3. [API アクセス方法](#api-アクセス方法)
4. [機能と対応状況](#機能と対応状況)
5. [APIリクエスト仕様](#apiリクエスト仕様)
6. [パラメータ詳細](#パラメータ詳細)
7. [コード例](#コード例)
8. [料金と制限](#料金と制限)
9. [ベストプラクティス](#ベストプラクティス)

---

## 概要

**Google Veo 3.1** は、Googleの最新の動画生成AIモデルです。テキストや画像から高品質な動画を生成できます。

### 主な特徴

- **ネイティブオーディオ生成**: 自然な会話や効果音を同期生成
- **シネマティックスタイル制御**: 映画的な演出の理解が向上
- **画像から動画への変換**: プロンプト追従性と品質が向上
- **キャラクター一貫性**: 複数シーンでのキャラクター維持

### アクセス経路

| プラットフォーム | URL |
|-----------------|-----|
| Gemini API | https://ai.google.dev/gemini-api/docs/video |
| Vertex AI | https://console.cloud.google.com/vertex-ai/studio/media |
| Gemini アプリ | https://gemini.google.com/ |
| Flow | https://flow.google/ |

---

## 利用可能なモデル

### Veo 3.1 GA版（一般利用可能）

| モデルID | 用途 |
|---------|------|
| `veo-3.1-generate-001` | 高品質動画生成（標準） |
| `veo-3.1-fast-generate-001` | 高速動画生成（イテレーション向け） |

### Veo 3.1 Preview版

| モデルID | 用途 |
|---------|------|
| `veo-3.1-generate-preview` | 最新機能のプレビュー |
| `veo-3.1-fast-generate-preview` | 高速版プレビュー |

### その他のVeoモデル

| モデルID | バージョン |
|---------|-----------|
| `veo-3.0-generate-001` | Veo 3.0 |
| `veo-3.0-fast-generate-001` | Veo 3.0 高速版 |
| `veo-2.0-generate-001` | Veo 2.0 |
| `veo-2.0-generate-exp` | Veo 2.0 実験版 |

---

## API アクセス方法

### 1. Vertex AI（Google Cloud）経由

```bash
# 認証
gcloud auth print-access-token

# エンドポイント
POST https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL_ID}:predictLongRunning
```

### 2. Gemini API経由

```bash
# APIキーを使用
export GEMINI_API_KEY="your-api-key"

# エンドポイント
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent
```

---

## 機能と対応状況

### Veo 3.1 Generate（GA版）

| 機能 | 対応状況 |
|------|----------|
| テキストから動画 | ✅ サポート |
| 画像から動画 | ✅ サポート |
| プロンプトリライト | ✅ サポート |
| 最初と最後のフレーム指定 | ✅ サポート |
| 参照画像（アセット） | ❌ 非サポート |
| 動画延長 | ❌ 非サポート |

### Veo 3.1 Generate（Preview版）

| 機能 | 対応状況 |
|------|----------|
| テキストから動画 | ✅ プレビュー |
| 画像から動画 | ✅ プレビュー |
| プロンプトリライト | ✅ プレビュー |
| 最初と最後のフレーム指定 | ✅ プレビュー |
| 参照画像（アセット） | ✅ プレビュー |
| 動画延長 | ✅ プレビュー |

### 出力仕様

| 項目 | 値 |
|------|-----|
| アスペクト比 | 16:9, 9:16 |
| 解像度 | 720p, 1080p |
| フレームレート | 24 FPS |
| 動画長 | 4秒, 6秒, 8秒 |
| プロンプト言語 | 英語 |

### 制限

| 項目 | 制限値 |
|------|--------|
| 最大リクエスト/分/プロジェクト | 50（GA）, 10（Preview） |
| 最大動画数/リクエスト | 4 |

---

## APIリクエスト仕様

### リクエストボディ構造

```json
{
  "instances": [
    {
      "prompt": "テキストプロンプト",
      "image": {
        "bytesBase64Encoded": "base64文字列",
        "gcsUri": "gs://bucket/image.png",
        "mimeType": "image/png"
      },
      "lastFrame": {
        "bytesBase64Encoded": "base64文字列",
        "gcsUri": "gs://bucket/last.png",
        "mimeType": "image/png"
      },
      "video": {
        "bytesBase64Encoded": "base64文字列",
        "gcsUri": "gs://bucket/video.mp4",
        "mimeType": "video/mp4"
      },
      "referenceImages": [
        {
          "image": {
            "bytesBase64Encoded": "base64文字列",
            "mimeType": "image/png"
          },
          "referenceType": "asset"
        }
      ]
    }
  ],
  "parameters": {
    "aspectRatio": "16:9",
    "durationSeconds": 8,
    "generateAudio": true,
    "resolution": "720p",
    "sampleCount": 1,
    "storageUri": "gs://bucket/output/"
  }
}
```

---

## パラメータ詳細

### instances パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `prompt` | string | テキスト生成時必須 | 動画生成のテキストプロンプト |
| `image` | object | オプション | 入力画像（画像から動画生成用） |
| `lastFrame` | object | オプション | 最後のフレーム画像 |
| `video` | object | オプション | 延長元の動画 |
| `referenceImages` | array | オプション | 参照画像（最大3枚） |

### parameters パラメータ

| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|----------|------|
| `aspectRatio` | string | "16:9" | アスペクト比（"16:9" or "9:16"） |
| `durationSeconds` | integer | 8 | 動画長さ（4, 6, or 8秒） |
| `generateAudio` | boolean | - | 音声生成（Veo 3必須） |
| `resolution` | string | "720p" | 解像度（"720p" or "1080p"） |
| `sampleCount` | integer | 1 | 生成動画数（1-4） |
| `seed` | uint32 | - | 乱数シード（0-4,294,967,295） |
| `storageUri` | string | - | 出力先GCSパス |
| `negativePrompt` | string | - | 避けたい内容 |
| `personGeneration` | string | "allow_adult" | 人物生成設定 |
| `resizeMode` | string | "pad" | リサイズモード（"pad" or "crop"） |

### referenceType の値

| 値 | 説明 |
|----|------|
| `"asset"` | アセット画像（シーン、オブジェクト、キャラクター） |
| `"style"` | スタイル画像（色、照明、テクスチャ）※Veo 3.1非対応 |

---

## コード例

### Python（Gemini API SDK）

```python
from google import genai
from google.genai import types

# クライアント初期化
client = genai.Client()

# テキストから動画生成
operation = client.models.generate_videos(
    model="veo-3.1-generate-001",
    prompt="A peaceful Japanese garden with cherry blossoms falling gently",
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        duration_seconds=8,
        generate_audio=True,
        resolution="720p",
        sample_count=1,
    ),
)

# 結果取得（ポーリング）
result = operation.result()
for video in result.videos:
    print(f"Video URI: {video.uri}")
```

### Python（画像から動画）

```python
from google import genai
from google.genai import types
import base64

client = genai.Client()

# 画像を読み込み
with open("input_image.png", "rb") as f:
    image_bytes = base64.b64encode(f.read()).decode()

operation = client.models.generate_videos(
    model="veo-3.1-generate-001",
    prompt="The scene slowly comes to life with gentle movement",
    image=types.Image(
        bytes_base64_encoded=image_bytes,
        mime_type="image/png"
    ),
    config=types.GenerateVideosConfig(
        duration_seconds=8,
        generate_audio=True,
    ),
)

result = operation.result()
```

### Python（参照画像を使用）

```python
from google import genai
from google.genai import types

client = genai.Client()

# 参照画像を設定
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="The character walks through a forest",
    config=types.GenerateVideosConfig(
        reference_images=[
            types.ReferenceImage(
                image=types.Image(gcs_uri="gs://bucket/character.png"),
                reference_type="asset"
            ),
            types.ReferenceImage(
                image=types.Image(gcs_uri="gs://bucket/scene.png"),
                reference_type="asset"
            ),
        ],
        duration_seconds=8,
    ),
)
```

### Python（動画延長）

```python
from google import genai
from google.genai import types

client = genai.Client()

# 既存動画を延長
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="The story continues...",
    video=types.Video(gcs_uri="gs://bucket/existing_video.mp4"),
)
```

### Python（最初と最後のフレーム指定）

```python
from google import genai
from google.genai import types

client = genai.Client()

operation = client.models.generate_videos(
    model="veo-3.1-generate-001",
    prompt="A smooth transition between the two frames",
    image=first_frame,  # 最初のフレーム
    config=types.GenerateVideosConfig(
        last_frame=last_frame,  # 最後のフレーム
        duration_seconds=8,
    ),
)
```

### cURL（Vertex AI）

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/us-central1/publishers/google/models/veo-3.1-generate-001:predictLongRunning" \
  -d '{
    "instances": [
      {
        "prompt": "A peaceful Japanese garden with cherry blossoms falling gently"
      }
    ],
    "parameters": {
      "aspectRatio": "16:9",
      "durationSeconds": 8,
      "generateAudio": true,
      "resolution": "720p",
      "sampleCount": 1,
      "storageUri": "gs://your-bucket/output/"
    }
  }'
```

### 操作ステータスのポーリング

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/us-central1/publishers/google/models/veo-3.1-generate-001:fetchPredictOperation" \
  -d '{
    "operationName": "projects/${PROJECT_ID}/locations/us-central1/publishers/google/models/veo-3.1-generate-001/operations/${OPERATION_ID}"
  }'
```

---

## 料金と制限

### 料金（参考）

Veo 3.1とVeo 3は同一料金体系です。最新の料金は以下を参照:
- Gemini API: https://ai.google.dev/gemini-api/docs/pricing#veo-3.1
- Vertex AI: https://cloud.google.com/vertex-ai/generative-ai/pricing#veo

### 使用タイプ

| タイプ | GA版 | Preview版 |
|--------|------|-----------|
| Provisioned Throughput | ✅ | ✅ |
| Fixed Quota | ✅ | ✅ |
| Dynamic Shared Quota | ❌ | ❌ |

---

## ベストプラクティス

### 1. プロンプト作成のコツ

```
良い例:
"A fast-tracking shot through a bustling dystopian sprawl with bright neon signs, 
flying cars and mist, night, lens flare, volumetric lighting"

避けるべき例:
"A city scene"
```

**ポイント**:
- 具体的なカメラワーク（tracking shot, close-up等）
- 環境の詳細（neon signs, mist等）
- 照明条件（night, volumetric lighting等）
- 雰囲気（dystopian, peaceful等）

### 2. シード値の活用

同じシード値を使用すると、パラメータが同じ場合に同様の動画を再現できます。

```python
config=types.GenerateVideosConfig(
    seed=12345,  # 再現性のために固定
)
```

### 3. 解像度とアスペクト比の選択

| ユースケース | アスペクト比 | 解像度 |
|-------------|-------------|--------|
| YouTube横型 | 16:9 | 1080p |
| SNSストーリー | 9:16 | 720p |
| プロトタイプ | 16:9 | 720p |

### 4. エラーハンドリング

```python
try:
    operation = client.models.generate_videos(...)
    result = operation.result(timeout=600)  # 10分タイムアウト
except Exception as e:
    if "INVALID_ARGUMENT" in str(e):
        print("リクエストパラメータを確認してください")
    elif "Quota exceeded" in str(e):
        print("クォータを確認してください")
    else:
        raise
```

### 5. コスト最適化

1. **Fast版を活用**: イテレーション中は`veo-3.1-fast-generate-001`を使用
2. **短い動画で検証**: 最初は4秒で生成してから8秒に拡張
3. **sampleCount=1**: 最初のテストでは1つだけ生成

---

## 関連リンク

- [Gemini API Video Documentation](https://ai.google.dev/gemini-api/docs/video)
- [Vertex AI Veo Documentation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate)
- [Veo API Reference](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation)
- [Veo Prompt Guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide)
- [Veo Best Practices](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/best-practice)
- [Google AI Studio - Veo Studio](https://aistudio.google.com/apps/bundled/veo_studio)
- [Veo Cookbook (Colab)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Veo.ipynb)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2025-12-29 | 初版作成（Veo 3.1 GA版リリース対応） |

---

*このドキュメントは `/docs/google-veo-3.1-api-report.md` に保存されています。*
