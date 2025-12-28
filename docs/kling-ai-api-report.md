# Kling AI API 利用ガイド

**作成日**: 2025年12月29日  
**対象**: Kling AI API（Kuaishou Technology）

---

## 目次

1. [概要](#概要)
2. [利用可能なモデル](#利用可能なモデル)
3. [API アクセス方法](#api-アクセス方法)
4. [機能と対応状況](#機能と対応状況)
5. [APIリクエスト仕様](#apiリクエスト仕様)
6. [パラメータ詳細](#パラメータ詳細)
7. [コード例](#コード例)
8. [料金](#料金)
9. [サードパーティAPI](#サードパーティapi)
10. [ベストプラクティス](#ベストプラクティス)

---

## 概要

**Kling AI** は、中国のショート動画プラットフォーム「快手（Kuaishou）」が開発したAI動画生成モデルです。2024年6月のリリース以来、最大1080p・30fpsの高品質動画生成能力で注目を集めています。

### 主な特徴

- **高解像度出力**: 最大1080p、30FPS
- **Text-to-Video**: テキストプロンプトから動画生成
- **Image-to-Video**: 画像を起点とした動画生成
- **カメラコントロール**: パン、チルト、ズームなどのカメラ動作制御
- **ネイティブオーディオ生成**: v2.6からは音声も同時生成可能
- **エフェクト機能**: Squish、Expansionなどの特殊効果
- **リップシンク**: 動画内の口の動きを音声に同期

### アクセス経路

| プラットフォーム | URL | 説明 |
|-----------------|-----|------|
| Kling AI公式 | https://klingai.com/ | 公式Webアプリ |
| Kling AI開発者 | https://klingai.com/global/dev | 公式API |
| PiAPI | https://piapi.ai/kling-api | サードパーティAPI |
| AI/ML API | https://aimlapi.com/ | サードパーティAPI |
| Kie.ai | https://kie.ai/ | サードパーティAPI |
| fal.ai | https://fal.ai/ | サードパーティAPI |

---

## 利用可能なモデル

### バージョン一覧

| バージョン | モード | 特徴 |
|-----------|--------|------|
| 1.5 | std / pro | 初期安定版 |
| 1.6 | std / pro | 品質向上、エフェクト対応 |
| 2.1 | std / pro | 動的アクション改善 |
| 2.1-master | pro のみ | 最高品質モデル |
| 2.5 | std / pro（turbo） | 高速生成、低コスト |
| 2.6 | std / pro | ネイティブオーディオ対応 |
| O1 | - | 推論強化モデル（最新） |

### モデルID一覧（AI/ML API経由）

#### Text-to-Video

| モデルID | 説明 |
|---------|------|
| `klingai/v1-standard-text-to-video` | v1 標準 |
| `klingai/v1-pro-text-to-video` | v1 プロ |
| `klingai/v1.6-standard-text-to-video` | v1.6 標準 |
| `klingai/v1.6-pro-text-to-video` | v1.6 プロ |
| `klingai/v2-master-text-to-video` | v2 マスター |
| `klingai/v2.1-master-text-to-video` | v2.1 マスター |
| `klingai/v2.5-turbo-text-to-video` | v2.5 ターボ |
| `klingai/v2.5-pro-text-to-video` | v2.5 プロ |
| `klingai/v2.6-pro-text-to-video` | v2.6 プロ |

#### Image-to-Video

| モデルID | 説明 |
|---------|------|
| `klingai/v1-standard-image-to-video` | v1 標準 |
| `klingai/v1-pro-image-to-video` | v1 プロ |
| `klingai/v1.6-standard-image-to-video` | v1.6 標準 |
| `klingai/v1.6-pro-image-to-video` | v1.6 プロ |
| `klingai/v2-master-image-to-video` | v2 マスター |
| `klingai/v2.1-standard-image-to-video` | v2.1 標準 |
| `klingai/v2.1-pro-image-to-video` | v2.1 プロ |
| `klingai/v2.1-master-image-to-video` | v2.1 マスター |
| `klingai/v2.5-turbo-image-to-video` | v2.5 ターボ |
| `klingai/v2.5-pro-image-to-video` | v2.5 プロ |
| `klingai/v2.6-pro-image-to-video` | v2.6 プロ |

#### 特殊機能

| モデルID | 説明 |
|---------|------|
| `klingai/v1.6-standard-effects` | エフェクト（標準） |
| `klingai/v1.6-pro-effects` | エフェクト（プロ） |
| `klingai/avatar-standard` | アバター生成（標準） |
| `klingai/avatar-pro` | アバター生成（プロ） |
| `klingai/video-o1-image-to-video` | O1推論モデル |

---

## API アクセス方法

### 公式API（Kling AI）

公式APIは現在、主に中国国内向けに提供されています。グローバルアクセスにはサードパーティAPIの利用が推奨されます。

### サードパーティAPI経由（推奨）

#### 1. PiAPI

```bash
# エンドポイント
POST https://api.piapi.ai/api/v1/task

# ヘッダー
x-api-key: your_api_key
Content-Type: application/json
```

#### 2. AI/ML API

```bash
# エンドポイント
POST https://api.aimlapi.com/v2/video/generations

# ヘッダー
Authorization: Bearer your_api_key
Content-Type: application/json
```

---

## 機能と対応状況

### タスクタイプ

| タスクタイプ | 説明 |
|-------------|------|
| `video_generation` | テキスト/画像から動画生成 |
| `extend_video` | 既存動画の延長 |
| `lip_sync` | リップシンク（口パク同期） |
| `effects` | エフェクト適用 |

### 出力仕様

| 項目 | 値 |
|------|-----|
| アスペクト比 | 16:9, 9:16, 1:1 |
| 解像度 | 720p, 1080p |
| フレームレート | 30 FPS |
| 動画長 | 5秒, 10秒 |
| フォーマット | MP4 |

### バージョン別機能対応

| 機能 | v1.5/1.6 | v2.1 | v2.5 | v2.6 |
|------|----------|------|------|------|
| Text-to-Video | ✅ | ✅ | ✅ | ✅ |
| Image-to-Video | ✅ | ✅ | ✅ | ✅ |
| カメラコントロール | ✅ | ✅ | ✅ | ✅ |
| Motion Brush | ✅ | ✅ | ✅ | ✅ |
| ネイティブオーディオ | ❌ | ❌ | ❌ | ✅（proのみ） |
| エフェクト | ✅（v1.6のみ） | ❌ | ❌ | ❌ |

---

## APIリクエスト仕様

### PiAPI リクエストボディ構造

```json
{
  "model": "kling",
  "task_type": "video_generation",
  "input": {
    "prompt": "テキストプロンプト",
    "negative_prompt": "除外したい要素",
    "cfg_scale": 0.5,
    "duration": 5,
    "aspect_ratio": "16:9",
    "mode": "std",
    "version": "2.6",
    "image_url": "https://example.com/image.png",
    "image_tail_url": "https://example.com/last_frame.png",
    "camera_control": {
      "type": "simple",
      "config": {
        "horizontal": 0,
        "vertical": 0,
        "pan": 0,
        "tilt": 0,
        "roll": 0,
        "zoom": 0
      }
    },
    "enable_audio": true
  },
  "config": {
    "service_mode": "public",
    "webhook_config": {
      "endpoint": "https://your-webhook.com/callback",
      "secret": "your_secret"
    }
  }
}
```

### AI/ML API リクエストボディ構造

```json
{
  "model": "klingai/v2.1-master-text-to-video",
  "prompt": "テキストプロンプト",
  "aspect_ratio": "16:9",
  "duration": 5,
  "negative_prompt": "除外したい要素",
  "cfg_scale": 0.5,
  "camera_control": "forward_up"
}
```

---

## パラメータ詳細

### 基本パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `prompt` | string | ✅ | 動画生成のテキストプロンプト（最大2500文字） |
| `negative_prompt` | string | ❌ | 除外したい要素（最大2500文字） |
| `cfg_scale` | float | ❌ | プロンプト追従度（0-1、推奨: 0.5） |
| `duration` | integer | ❌ | 動画長さ（5秒 or 10秒） |
| `aspect_ratio` | string | ❌ | アスペクト比（"16:9", "9:16", "1:1"） |
| `mode` | string | ❌ | モード（"std" or "pro"） |
| `version` | string | ❌ | モデルバージョン |

### Image-to-Video パラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `image_url` | string | ✅ | 開始フレーム画像URL（10MB以下、各辺300px以上） |
| `image_tail_url` | string | ❌ | 終了フレーム画像URL |

### カメラコントロール

| パラメータ | 値域 | 説明 |
|-----------|------|------|
| `horizontal` | -10〜10 | 水平移動 |
| `vertical` | -10〜10 | 垂直移動 |
| `pan` | -10〜10 | 左右回転 |
| `tilt` | -10〜10 | 上下回転 |
| `roll` | -10〜10 | 回転 |
| `zoom` | -10〜10 | ズーム |

### プリセットカメラコントロール（AI/ML API）

| 値 | 説明 |
|----|------|
| `down_back` | 下方向へ後退 |
| `forward_up` | 前方上昇 |
| `right_turn_forward` | 右旋回しながら前進 |
| `left_turn_forward` | 左旋回しながら前進 |

### リップシンクパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `origin_task_id` | string | 元動画のタスクID |
| `tts_text` | string | 音声合成用テキスト |
| `tts_speed` | float | 音声速度（0.8-2.0） |
| `tts_timbre` | string | 声質（音色）ID |
| `local_dubbing_url` | string | カスタム音声ファイルURL（MP3/WAV/FLAC/OGG、20MB以下、60秒以内） |

### エフェクトパラメータ

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `effect` | `squish` | 押しつぶしエフェクト |
| `effect` | `expansion` | 膨張エフェクト |

---

## コード例

### Python（PiAPI経由）- テキストから動画

```python
import requests
import time

API_KEY = "your_piapi_key"
BASE_URL = "https://api.piapi.ai"

def create_video_task(prompt: str, duration: int = 5, version: str = "2.6"):
    """動画生成タスクを作成"""
    url = f"{BASE_URL}/api/v1/task"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model": "kling",
        "task_type": "video_generation",
        "input": {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": "16:9",
            "mode": "std",
            "version": version,
            "cfg_scale": 0.5
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def get_task_result(task_id: str):
    """タスク結果を取得"""
    url = f"{BASE_URL}/api/v1/task/{task_id}"
    headers = {"x-api-key": API_KEY}
    
    response = requests.get(url, headers=headers)
    return response.json()

def generate_video(prompt: str):
    """動画生成（ポーリング付き）"""
    # タスク作成
    result = create_video_task(prompt)
    task_id = result["data"]["task_id"]
    print(f"Task ID: {task_id}")
    
    # ポーリング
    while True:
        status = get_task_result(task_id)
        current_status = status["data"]["status"]
        print(f"Status: {current_status}")
        
        if current_status == "Completed":
            return status["data"]["output"]
        elif current_status == "Failed":
            raise Exception(status["data"]["error"]["message"])
        
        time.sleep(10)

# 使用例
result = generate_video("A cat playing with a ball in a sunny garden")
print(f"Video URL: {result['video_url']}")
```

### Python（AI/ML API経由）- テキストから動画

```python
import requests
import time

API_KEY = "your_aimlapi_key"
BASE_URL = "https://api.aimlapi.com/v2"

def generate_video(prompt: str, model: str = "klingai/v2.1-master-text-to-video"):
    """動画生成タスクを作成"""
    url = f"{BASE_URL}/video/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "duration": 5
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def get_video_result(generation_id: str):
    """生成結果を取得"""
    url = f"{BASE_URL}/video/generations"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"generation_id": generation_id}
    
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def create_video_with_polling(prompt: str, timeout: int = 600):
    """動画生成（ポーリング付き）"""
    # タスク作成
    result = generate_video(prompt)
    generation_id = result["id"]
    print(f"Generation ID: {generation_id}")
    
    # ポーリング
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = get_video_result(generation_id)
        current_status = status.get("status")
        print(f"Status: {current_status}")
        
        if current_status == "completed":
            return status["video"]["url"]
        elif current_status == "failed":
            raise Exception(status.get("error", {}).get("message", "Unknown error"))
        
        time.sleep(10)
    
    raise TimeoutError("Video generation timed out")

# 使用例
video_url = create_video_with_polling("A dragon flying over mountains at sunset")
print(f"Video URL: {video_url}")
```

### Python（画像から動画）

```python
def create_image_to_video(image_url: str, prompt: str):
    """画像から動画を生成"""
    url = f"{BASE_URL}/api/v1/task"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model": "kling",
        "task_type": "video_generation",
        "input": {
            "prompt": prompt,
            "image_url": image_url,
            "duration": 5,
            "aspect_ratio": "16:9",
            "mode": "pro",
            "version": "2.6"
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 使用例
result = create_image_to_video(
    image_url="https://example.com/my_image.png",
    prompt="The scene slowly comes to life with gentle wind"
)
```

### Python（カメラコントロール付き）

```python
def create_video_with_camera(prompt: str, camera_settings: dict):
    """カメラコントロール付きで動画生成"""
    url = f"{BASE_URL}/api/v1/task"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model": "kling",
        "task_type": "video_generation",
        "input": {
            "prompt": prompt,
            "duration": 5,
            "aspect_ratio": "16:9",
            "mode": "std",
            "version": "2.6",
            "camera_control": {
                "type": "simple",
                "config": camera_settings
            }
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 使用例：ズームインしながら右パン
camera = {
    "horizontal": 0,
    "vertical": 0,
    "pan": 5,
    "tilt": 0,
    "roll": 0,
    "zoom": 3
}
result = create_video_with_camera("A beautiful landscape", camera)
```

### cURL（PiAPI）

```bash
# タスク作成
curl --location 'https://api.piapi.ai/api/v1/task' \
--header 'x-api-key: YOUR_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "model": "kling",
    "task_type": "video_generation",
    "input": {
        "prompt": "White egrets fly over the vast paddy fields",
        "negative_prompt": "",
        "cfg_scale": 0.5,
        "duration": 5,
        "aspect_ratio": "1:1",
        "mode": "std",
        "version": "2.6"
    }
}'

# 結果取得
curl --location 'https://api.piapi.ai/api/v1/task/YOUR_TASK_ID' \
--header 'x-api-key: YOUR_API_KEY'
```

---

## 料金

### PiAPI料金表

| バージョン | モード | 5秒あたり（USD） |
|-----------|--------|-----------------|
| 1.5/1.6/2.1 | std | $0.26 |
| 1.5/1.6/2.1 | pro | $0.46 |
| 2.1-master | pro | $0.96 |
| 2.5/2.6 | std | $0.195 |
| 2.5/2.6 | pro | $0.33 |

**注意事項**:
- 10秒動画 = 5秒料金 × 2
- v2.6のネイティブオーディオ = proモード料金 × 2
- 例: 10秒 pro + audio = $0.33 × 2 × 2 = $1.32

### fal.ai料金表

| モデル | オーディオなし | オーディオあり |
|--------|--------------|---------------|
| Kling 2.6 Pro | $0.07/秒 | $0.14/秒 |

### Kie.ai料金表

| 長さ | オーディオなし | オーディオあり |
|------|--------------|---------------|
| 5秒 | $0.28 | $0.55 |
| 10秒 | $0.55 | ~$1.10 |

---

## サードパーティAPI

### 主要プロバイダー比較

| プロバイダー | 特徴 | 公式サイト |
|-------------|------|-----------|
| **PiAPI** | 最も包括的、全バージョン対応 | https://piapi.ai/kling-api |
| **AI/ML API** | OpenAI互換SDK対応 | https://aimlapi.com/ |
| **fal.ai** | シンプルな従量課金 | https://fal.ai/ |
| **Kie.ai** | 固定料金、統一プラットフォーム | https://kie.ai/ |
| **Replicate** | コミュニティ運営モデル | https://replicate.com/ |

### 選択のポイント

1. **PiAPI**: 最新バージョン（v2.6, O1）をすぐに使いたい場合
2. **AI/ML API**: 既存のOpenAI SDK統合がある場合
3. **fal.ai**: シンプルな秒単位課金を好む場合
4. **Kie.ai**: 複数のKlingモデルを一括管理したい場合

---

## ベストプラクティス

### 1. プロンプト作成のコツ

```
良い例:
"A majestic eagle soaring over snow-capped mountains, 
golden hour lighting, cinematic wide shot, smooth gliding motion"

避けるべき例:
"Bird flying"
```

**ポイント**:
- 具体的な被写体（majestic eagle）
- 環境の詳細（snow-capped mountains）
- 照明条件（golden hour lighting）
- カメラワーク（cinematic wide shot）
- 動きの説明（smooth gliding motion）

### 2. cfg_scale の調整

| 値 | 効果 |
|----|------|
| 0.3 | 創造的な解釈、プロンプトから離れやすい |
| 0.5 | バランス（推奨） |
| 0.7 | プロンプトに忠実 |
| 1.0 | 非常に忠実だが硬い印象 |

### 3. モード選択

| ユースケース | 推奨モード |
|-------------|-----------|
| プロトタイプ作成 | std（標準） |
| 最終版制作 | pro |
| 高速イテレーション | v2.5 turbo |
| 最高品質 | v2.1-master |

### 4. エラーハンドリング

```python
def safe_generate_video(prompt: str, max_retries: int = 3):
    """リトライ付き動画生成"""
    for attempt in range(max_retries):
        try:
            result = create_video_task(prompt)
            if result.get("code") == 200:
                return result
            
            error_msg = result.get("message", "Unknown error")
            if "rate limit" in error_msg.lower():
                time.sleep(60)  # レート制限時は1分待機
                continue
            
            raise Exception(error_msg)
        
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            raise
    
    raise Exception("Max retries exceeded")
```

### 5. コスト最適化

1. **標準モードで検証**: 最初はstdモードで内容確認
2. **短い動画で確認**: 5秒で生成してから10秒に拡張
3. **オーディオは最後に**: ネイティブオーディオは料金が2倍なので最終版のみ
4. **v2.5 turboを活用**: イテレーション時は低コスト・高速のv2.5

### 6. Webhook活用

```python
# Webhook設定例
config = {
    "webhook_config": {
        "endpoint": "https://your-server.com/kling-callback",
        "secret": "your_webhook_secret"
    }
}

# サーバー側のWebhook受信例
from flask import Flask, request
import hmac

app = Flask(__name__)

@app.route("/kling-callback", methods=["POST"])
def handle_webhook():
    # 署名検証
    signature = request.headers.get("X-Signature")
    payload = request.get_data()
    expected = hmac.new(
        b"your_webhook_secret",
        payload,
        "sha256"
    ).hexdigest()
    
    if signature != expected:
        return "Invalid signature", 401
    
    data = request.json
    task_id = data["task_id"]
    status = data["status"]
    
    if status == "Completed":
        video_url = data["output"]["video_url"]
        # 動画処理ロジック
    
    return "OK", 200
```

---

## タスクステータス

| ステータス | 説明 |
|-----------|------|
| `Pending` | キュー待機中 |
| `Processing` | 処理中 |
| `Completed` | 完了 |
| `Failed` | 失敗 |
| `Staged` | 同時実行制限による待機 |

---

## 制限事項

### 入力制限

| 項目 | 制限値 |
|------|--------|
| プロンプト長 | 最大2500文字 |
| 画像サイズ | 最大10MB |
| 画像最小サイズ | 各辺300px以上 |
| 音声ファイル（リップシンク） | 最大20MB、60秒以内 |

### API制限

| 項目 | 値 |
|------|-----|
| 同時実行タスク | プランにより異なる |
| ステージングキュー | 最大50タスク |

---

## 関連リンク

- [Kling AI 公式サイト](https://klingai.com/)
- [Kling AI 開発者ポータル](https://klingai.com/global/dev)
- [PiAPI Kling API ドキュメント](https://piapi.ai/docs/kling-api/create-task)
- [AI/ML API Kling ドキュメント](https://docs.aimlapi.com/api-references/video-models/kling-ai)
- [Kie.ai Kling 2.6](https://kie.ai/kling-2-6)
- [fal.ai Kling モデル](https://fal.ai/models/fal-ai/kling-video)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2025-12-29 | 初版作成（Kling AI v2.6対応） |

---

*このドキュメントは `/docs/kling-ai-api-report.md` に保存されています。*
