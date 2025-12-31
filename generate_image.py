#!/usr/bin/env python3
"""
汎用イラスト生成スクリプト

OpenRouter の Gemini 3 Pro Image Preview (Nano Banana Pro) を使って、
プロンプトからイラストを生成します。

Usage:
    python scripts/generate_image.py "プロンプト" --output output.png
    python scripts/generate_image.py "プロンプト" --size 1024x1024 --output image.png
"""

import argparse
import base64
import os
import sys
from pathlib import Path

import requests


class ImageGenerator:
    """イラスト生成クラス"""

    # サポートされているアスペクト比（Gemini 3 Pro Image Preview）
    ASPECT_RATIOS = {
        "1:1": {"ratio": "1:1", "example": "1024x1024"},
        "16:9": {"ratio": "16:9", "example": "1536x864"},
        "9:16": {"ratio": "9:16", "example": "864x1536"},
        "4:3": {"ratio": "4:3", "example": "1536x1152"},
        "3:4": {"ratio": "3:4", "example": "1152x1536"},
        "21:9": {"ratio": "21:9", "example": "1536x672"},
    }

    # スタイル定義（generate_cover_image.py と共通）
    STYLES = {
        "light": {
            "name": "Light & Clean",
            "description": "Light background with dark text, clean and professional",
            "prompt_suffix": "Style: Light background with soft colors, clean and professional aesthetic. High contrast for readability.",
        },
        "dark": {
            "name": "Dark & Modern",
            "description": "Dark background with light elements, modern and sleek",
            "prompt_suffix": "Style: Dark background with light elements, modern and sleek aesthetic. Subtle lighting effects.",
        },
        "gradient": {
            "name": "Gradient Blend",
            "description": "Smooth gradient background, modern and eye-catching",
            "prompt_suffix": "Style: Smooth gradient background with modern color blends. Eye-catching and contemporary.",
        },
        "minimal": {
            "name": "Minimalist",
            "description": "Minimalist design with clean lines",
            "prompt_suffix": "Style: Minimalist design with clean lines and simple shapes. Maximum clarity and elegance.",
        },
        "tech": {
            "name": "Tech Circuit",
            "description": "Tech-themed with circuit patterns",
            "prompt_suffix": "Style: Tech-inspired design with circuit patterns or digital elements. Futuristic and technical aesthetic.",
        },
        "geometric": {
            "name": "Geometric Shapes",
            "description": "Modern geometric patterns and shapes",
            "prompt_suffix": "Style: Modern geometric shapes and patterns. Clean, structured, and contemporary design.",
        },
        "neon": {
            "name": "Neon Glow",
            "description": "Dark background with neon accents",
            "prompt_suffix": "Style: Dark background with vibrant neon glow effects. Cyberpunk-inspired and energetic.",
        },
        "glass": {
            "name": "Glassmorphism",
            "description": "Frosted glass effect with blur",
            "prompt_suffix": "Style: Glassmorphism design with frosted glass effect and soft blur. Modern and translucent.",
        },
        "retro": {
            "name": "Retro Wave",
            "description": "80s-inspired synthwave style",
            "prompt_suffix": "Style: Retro wave aesthetic with 80s-inspired colors and grid patterns. Nostalgic yet modern.",
        },
        "watercolor": {
            "name": "Watercolor Pastel",
            "description": "Soft watercolor with gentle pastel tones",
            "prompt_suffix": "Style: Watercolor illustration with soft transparency and gentle pastel tones. Serene and dreamy aesthetic.",
        },
        "realistic": {
            "name": "Realistic Photo",
            "description": "Photorealistic rendering",
            "prompt_suffix": "Style: Photorealistic rendering with natural lighting and realistic textures. High-quality photography aesthetic.",
        },
        "illustration": {
            "name": "Digital Illustration",
            "description": "Digital art illustration style",
            "prompt_suffix": "Style: Digital illustration with vibrant colors and artistic details. Professional digital art aesthetic.",
        },
    }

    @classmethod
    def list_styles(cls):
        """利用可能なスタイル一覧を表示"""
        print("\n" + "=" * 70)
        print("Available Styles:")
        print("=" * 70)
        for key, style in cls.STYLES.items():
            print(f"\n  {key:12} - {style['name']}")
            print(f"               {style['description']}")
        print("\n" + "=" * 70 + "\n")

    def __init__(self, api_key: str = None, reference_images: list = None):
        """
        初期化

        Args:
            api_key: OpenRouter APIキー（指定がない場合は環境変数から取得）
            reference_images: 参照画像のパスリスト（ロゴなどを含める場合）
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. "
                "Set OPENROUTER_API_KEY environment variable or use --api-key option."
            )

        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # Gemini 3 Pro Image Preview (Nano Banana Pro)
        self.model = "google/gemini-3-pro-image-preview"
        self.reference_images = reference_images or []

    @staticmethod
    def parse_size(size_str: str) -> str:
        """
        サイズ指定文字列をアスペクト比に変換

        Args:
            size_str: サイズ指定（例: "1024x1024", "16:9", "1920x1080"）

        Returns:
            アスペクト比文字列（例: "1:1", "16:9"）
        """
        if not size_str:
            return "1:1"  # デフォルト

        # アスペクト比が直接指定されている場合
        if size_str in ImageGenerator.ASPECT_RATIOS:
            return size_str

        # ピクセルサイズからアスペクト比を推定
        if "x" in size_str.lower():
            try:
                width, height = map(int, size_str.lower().split("x"))
                ratio = width / height

                # 近いアスペクト比を選択
                if abs(ratio - 1.0) < 0.1:
                    return "1:1"
                elif abs(ratio - 16 / 9) < 0.1:
                    return "16:9"
                elif abs(ratio - 9 / 16) < 0.1:
                    return "9:16"
                elif abs(ratio - 4 / 3) < 0.1:
                    return "4:3"
                elif abs(ratio - 3 / 4) < 0.1:
                    return "3:4"
                elif abs(ratio - 21 / 9) < 0.1:
                    return "21:9"
                else:
                    # デフォルトに最も近いものを選択
                    if ratio > 1.0:
                        return "16:9"  # 横長
                    else:
                        return "9:16"  # 縦長
            except ValueError:
                print(f"Warning: Invalid size format '{size_str}', using default 1:1")
                return "1:1"

        # 不明な形式の場合はデフォルト
        print(f"Warning: Unknown size format '{size_str}', using default 1:1")
        return "1:1"

    def encode_image_to_base64(self, image_path: Path) -> str:
        """
        画像をbase64エンコード

        Args:
            image_path: 画像ファイルのパス

        Returns:
            base64エンコードされた画像データURL
        """
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # MIMEタイプを判定
        ext = image_path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_types.get(ext, "image/png")

        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        style: str = None,
        output_path: Path = None,
    ) -> bool:
        """
        画像を生成して保存

        Args:
            prompt: 画像生成プロンプト
            aspect_ratio: アスペクト比（例: "1:1", "16:9"）
            style: 画像スタイル（例: "light", "watercolor", "tech"）
            output_path: 出力ファイルパス（Noneの場合は保存しない）

        Returns:
            成功した場合True
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # スタイルを適用したプロンプトを構築
        final_prompt = prompt
        if style and style in self.STYLES:
            style_config = self.STYLES[style]
            final_prompt = f"{prompt}\n\n{style_config['prompt_suffix']}"
            print(f"🎨 Using style: {style_config['name']}")

        # メッセージコンテンツを構築
        if self.reference_images:
            # 参照画像がある場合、マルチモーダルコンテンツとして送信
            content = [
                {
                    "type": "text",
                    "text": f"{final_prompt}\n\nIMPORTANT: Use the logo(s) or element(s) from the reference image(s) provided. Include these in the generated image as specified in the prompt.",
                }
            ]

            # 各参照画像を追加
            for ref_img in self.reference_images:
                if ref_img.exists():
                    image_data_url = self.encode_image_to_base64(ref_img)
                    content.append({"type": "image_url", "image_url": {"url": image_data_url}})
                    print(f"  Reference image: {ref_img}")
                else:
                    print(f"  ⚠ Warning: Reference image not found: {ref_img}")
        else:
            # 参照画像がない場合、テキストのみ
            content = final_prompt

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": aspect_ratio},
        }

        try:
            print("Generating image...")
            print(f"  Model: {self.model}")
            print(f"  Aspect ratio: {aspect_ratio}")
            if style:
                print(f"  Style: {style}")
            print(f"  Prompt: {prompt}\n")

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()

            # レスポンスから画像を抽出
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                images = message.get("images", [])

                if images and len(images) > 0:
                    # 最初の画像を取得
                    image_data = images[0]
                    image_url_obj = image_data.get("image_url", {})
                    data_url = image_url_obj.get("url", "")

                    if data_url.startswith("data:image"):
                        # base64データURLをデコード
                        header, encoded = data_url.split(",", 1)
                        img_bytes = base64.b64decode(encoded)

                        # 画像を保存
                        if output_path:
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            output_path.write_bytes(img_bytes)
                            print(f"✓ Image saved to: {output_path}")
                            print(f"  Size: {len(img_bytes):,} bytes")

                        return True
                    else:
                        print(f"✗ Unexpected image URL format: {data_url[:100]}...")
                        return False
                else:
                    print("✗ No images in response")
                    return False
            else:
                print("✗ No choices in response")
                return False

        except requests.exceptions.RequestException as e:
            print(f"✗ API request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Generate images using OpenRouter Nano Banana Pro (Gemini 3 Pro Image Preview)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 基本的な使用方法
  python scripts/generate_image.py "A cute cat playing with a ball" --output cat.png

  # スタイルを指定
  python scripts/generate_image.py "System architecture diagram" --style tech --output diagram.png
  python scripts/generate_image.py "Tutorial illustration" --style watercolor --output tutorial.png

  # サイズを指定（アスペクト比）
  python scripts/generate_image.py "Landscape photo" --size 16:9 --output landscape.png

  # サイズを指定（ピクセル）
  python scripts/generate_image.py "Portrait photo" --size 1080x1920 --output portrait.png

  # スタイル + サイズ
  python scripts/generate_image.py "Workflow diagram" --style geometric --size 16:9 --output workflow.png

  # 参照画像を使用（ロゴなど）
  python scripts/generate_image.py "Blog cover with logo" --style dark --output cover.png --reference-image logo.png

  # 複数の参照画像を使用
  python scripts/generate_image.py "Combined design" --style minimal --output result.png --reference-image logo1.png logo2.png

  # スタイル一覧を表示
  python scripts/generate_image.py --list-styles

Supported aspect ratios:
  1:1   (1024x1024)  - Square
  16:9  (1536x864)   - Landscape
  9:16  (864x1536)   - Portrait
  4:3   (1536x1152)  - Classic landscape
  3:4   (1152x1536)  - Classic portrait
  21:9  (1536x672)   - Wide banner
        """,
    )

    parser.add_argument("prompt", type=str, nargs="?", help="Image generation prompt")

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file path (e.g., output.png)",
    )

    parser.add_argument(
        "--size",
        type=str,
        default="1:1",
        help='Image size as aspect ratio (1:1, 16:9, etc.) or pixels (1024x1024). Default: "1:1"',
    )

    parser.add_argument(
        "--style",
        type=str,
        help="Image style (e.g., light, dark, watercolor, tech). See --list-styles for options.",
    )

    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        help="OpenRouter API key (default: OPENROUTER_API_KEY env var)",
    )

    parser.add_argument(
        "--list-styles",
        "-ls",
        action="store_true",
        help="List all available styles and exit",
    )

    parser.add_argument(
        "--list-ratios",
        "-lr",
        action="store_true",
        help="List supported aspect ratios and exit",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing file (default: skip if file exists)",
    )

    parser.add_argument(
        "--reference-image",
        "-r",
        type=Path,
        nargs="+",
        help="Reference image(s) to include (e.g., logo files). Can specify multiple images.",
    )

    args = parser.parse_args()

    # スタイル一覧表示
    if args.list_styles:
        ImageGenerator.list_styles()
        sys.exit(0)

    # アスペクト比一覧表示
    if args.list_ratios:
        print("Supported aspect ratios:\n")
        for ratio, info in ImageGenerator.ASPECT_RATIOS.items():
            print(f"  {ratio:6s} - Example size: {info['example']}")
        print()
        sys.exit(0)

    # prompt と output が必須（一覧表示以外の場合）
    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    if not args.output:
        print("Error: --output is required")
        parser.print_help()
        sys.exit(1)

    # 既存ファイルのチェック
    if args.output.exists() and not args.overwrite:
        file_size = args.output.stat().st_size
        print(f"ℹ File already exists: {args.output} ({file_size:,} bytes)")
        print("  Use --overwrite option to regenerate.")
        sys.exit(0)

    # 上書き警告
    if args.output.exists() and args.overwrite:
        file_size = args.output.stat().st_size
        print(f"⚠ Overwriting existing file: {args.output} ({file_size:,} bytes)\n")

    # 参照画像の確認
    reference_images = []
    if args.reference_image:
        for ref_img in args.reference_image:
            if not ref_img.exists():
                print(f"Error: Reference image not found: {ref_img}")
                sys.exit(1)
            reference_images.append(ref_img)

    # スタイルの検証
    if args.style and args.style not in ImageGenerator.STYLES:
        print(f"Error: Unknown style '{args.style}'")
        print("Run 'python scripts/generate_image.py --list-styles' to see available styles.")
        sys.exit(1)

    # 画像生成
    try:
        generator = ImageGenerator(api_key=args.api_key, reference_images=reference_images)

        # サイズをアスペクト比に変換
        aspect_ratio = generator.parse_size(args.size)

        # 画像生成
        success = generator.generate_image(
            args.prompt, aspect_ratio, style=args.style, output_path=args.output
        )

        if success:
            print("\n✓ Image generation completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Image generation failed.")
            sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
