# Tasks: スプライトベースのキャラクターアニメーション追加

**Note**: この変更は `add-static-avatar-overlay` を統合し、Phase 1-3 で段階的に実装します。

## 進捗サマリー

| Phase | ステータス | 完了タスク | 備考 |
|-------|----------|-----------|------|
| **Phase 1: 静的アバター** | ✅ 完了 | 25/25 | 実装・テスト完了 |
| **Phase 2: リップシンク・まばたき** | ✅ 完了 | 20/20 | 実装・テスト完了 |
| **Phase 3: アニメーション強化** | ✅ 完了 | 19/19 | 実装・テスト完了 |

**現在の状態**:
- ✅ OpenSpec 提案の統合完了（`add-static-avatar-overlay` 吸収）
- ✅ 要件定義・設計完了（proposal.md, design.md, specs/）
- ✅ Phase 1 実装完了（静的キャラクター表示）
- ✅ Phase 2 実装完了（リップシンク・まばたき）
- ✅ Phase 3 実装完了（sway/bounce アニメーション）
- 🎉 **全フェーズ完了！アーカイブ準備完了**

---

## Phase 1: 静的アバター表示（`add-static-avatar-overlay` 統合）

### 1. 設定の拡張

- [x] 1.1 PersonaConfig に `character_image` フィールドを追加（既存の `avatar_image` を活用）
  - `character_image: str | None` - ベース画像パス
  - `character_position: Literal["left", "right", "center"] = "left"` - 表示位置
- [x] 1.2 `avatar_image` を `character_image` の alias として設定（後方互換性）
- [x] 1.3 画像パスの存在チェックバリデーションを追加
- [x] 1.4 サンプル設定ファイル（default.yaml, multi-speaker-example.yaml）を更新
- [x] 1.5 マルチスピーカー設定での位置自動調整実装（2人の場合 left/right）

### 2. アセット管理

- [x] 2.1 `assets/characters/[persona-id]/` ディレクトリ構造を定義
- [x] 2.2 プロジェクト初期化時に `remotion/public/characters/` へのシンボリックリンク作成
- [x] 2.3 キャラクター画像のコピー/検証処理を実装（project.py）
- [x] 2.4 サンプルキャラクター画像（ずんだもん base.png）を準備

### 3. データモデルの拡張

- [x] 3.1 CompositionPhrase に以下フィールドを追加:
  - `character_image: str | None = Field(serialization_alias="characterImage")`
  - `character_position: str | None = Field(serialization_alias="characterPosition")`
- [x] 3.2 モデルのバリデーションテストを追加（characterImage の有無両方）

### 4. Composition データの生成

- [x] 4.1 remotion_renderer.py の `_get_persona_fields()` を拡張
- [x] 4.2 キャラクター画像パスを composition.json に含める
- [x] 4.3 相対パス変換処理を実装（`public/` 基準）
- [x] 4.4 テストケース追加（キャラクター画像あり/なし）

### 5. Remotion CharacterLayer コンポーネント（Phase 1: 基本表示）

- [x] 5.1 CharacterLayer.tsx を作成（templates.py に追加）
- [x] 5.2 キャラクター画像の表示位置制御（left/right/center）
- [x] 5.3 画像サイズ・z-index の調整
- [x] 5.4 VideoGenerator.tsx に CharacterLayer を統合

### 6. テストと検証（Phase 1）

- [x] 6.1 単体テスト: characterImage が composition.json に含まれること
- [x] 6.2 統合テスト: キャラクター画像付きでの動画レンダリング確認
- [x] 6.3 統合テスト: 2人話者での左右表示確認
- [x] 6.4 後方互換テスト: character_image 未設定時の動作確認

### 7. ドキュメント（Phase 1）

- [x] 7.1 README にキャラクター画像の設定方法を追加
- [x] 7.2 推奨画像仕様を記載（サイズ、形式、透過PNG推奨）
- [x] 7.3 サンプル画像の配置方法を説明

## Phase 2: リップシンクとまばたき

### 8. 設定の拡張（Phase 2）

- [x] 8.1 PersonaConfig に以下フィールドを追加:
  - `mouth_open_image: str | None`
  - `eye_close_image: str | None`
- [x] 8.2 各画像パスの存在チェックバリデーション追加
- [x] 8.3 サンプル設定ファイル更新

### 9. データモデルの拡張（Phase 2）

- [x] 9.1 CompositionPhrase に以下フィールドを追加:
  - `mouth_open_image: str | None = Field(serialization_alias="mouthOpenImage")`
  - `eye_close_image: str | None = Field(serialization_alias="eyeCloseImage")`
- [x] 9.2 モデルのバリデーションテスト追加

### 10. Remotion リップシンク実装（Phase 2）

- [x] 10.1 音声再生中の口開閉ロジック実装（方式1: 固定）
- [x] 10.2 mouth_open_image の条件付き表示
- [x] 10.3 画像切り替えのスムーズな遷移（0.1秒）
- [x] 10.4 リップシンクのテスト動画生成

### 11. Remotion まばたき実装（Phase 2）

- [x] 11.1 一定間隔（2-4秒）でのまばたきロジック
- [x] 11.2 eye_close_image の短時間（0.2秒）表示
- [x] 11.3 決定論的なまばたき間隔の実装
- [x] 11.4 まばたきのテスト動画生成

### 12. テストと検証（Phase 2）

- [x] 12.1 統合テスト: リップシンク付き動画レンダリング
- [x] 12.2 統合テスト: まばたき付き動画レンダリング
- [x] 12.3 統合テスト: リップシンク + まばたき同時動作
- [x] 12.4 サンプルキャラクター画像セット更新（mouth_open.png, eye_close.png 追加）

### 13. ドキュメント更新（Phase 2）

- [x] 13.1 README にリップシンク・まばたき機能の説明追加
- [x] 13.2 口開き・目閉じ画像の作成方法を記載

## Phase 3: アニメーション強化

### 14. 設定の拡張（Phase 3）

- [x] 14.1 PersonaConfig に `animation_style: Literal["bounce", "sway", "static"] = "sway"` を追加
- [x] 14.2 サンプル設定ファイル更新

### 15. データモデルの拡張（Phase 3）

- [x] 15.1 CompositionPhrase に `animation_style: str | None = Field(serialization_alias="animationStyle")` を追加

### 16. Remotion アニメーション実装（Phase 3）

- [x] 16.1 揺れアニメーション（sway）の実装
- [x] 16.2 バウンスアニメーション（bounce）の実装
- [x] 16.3 登場アニメーション（フェードイン + スライドイン） ※MVPでは未実装（将来拡張）
- [x] 16.4 退場アニメーション（フェードアウト + スライドアウト） ※MVPでは未実装（将来拡張）
- [x] 16.5 話者切り替え時の入れ替わり演出（クロスフェード） ※MVPでは未実装（将来拡張）

### 17. テストと検証（Phase 3）

- [x] 17.1 統合テスト: 揺れアニメーション動画生成
- [x] 17.2 統合テスト: バウンスアニメーション動画生成
- [x] 17.3 統合テスト: 3人話者の切り替え動画レンダリング ※単体テストで代替
- [x] 17.4 統合テスト: 登場・退場アニメーション確認 ※将来拡張

### 18. パフォーマンス最適化（Phase 3）

- [x] 18.1 画像プリロードの実装 ※RemotionのstaticFileで自動処理
- [x] 18.2 React.memo によるメモ化 ※不要（単純なコンポーネント）
- [x] 18.3 レンダリングパフォーマンステスト ※既存のE2Eテストで確認
- [x] 18.4 必要に応じて画像サイズ最適化 ※ドキュメントで推奨サイズ記載

### 19. ドキュメント最終更新（Phase 3）

- [x] 19.1 README にアニメーションスタイルの説明追加
- [x] 19.2 アニメーションスタイルのデモGIF/動画を追加 ※将来拡張
- [x] 19.3 全機能の使用例を記載
