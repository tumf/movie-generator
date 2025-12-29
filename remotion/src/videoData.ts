// Video composition data: mapping audio files to slides

export interface Scene {
  id: string;
  audioFile: string;
  slideFile?: string;
  subtitle?: string;
  duration: number; // in seconds
}

export const scenes: Scene[] = [
  // Opening (30s)
  { 
    id: "001_opening_hook", 
    audioFile: "001_opening_hook.wav", 
    slideFile: "01_title.png", 
    subtitle: "lazygit、yazi、lazydocker…\nなんでこんなにTUIアプリが増えたのか、知ってますか？",
    duration: 12.1 
  },
  { 
    id: "002_opening_theme", 
    audioFile: "002_opening_theme.wav", 
    slideFile: "01_title.png", 
    subtitle: "実は2023年、TUIの世界で\nカンブリア紀とも呼べる大爆発が起きていたんです",
    duration: 7.4 
  },
  { 
    id: "003_opening_pain", 
    audioFile: "003_opening_pain.wav", 
    slideFile: "01_title.png", 
    subtitle: "最近やたらとカッコいいターミナルアプリ見かけるけど\nなんで急に増えたの？って思ったことありませんか？",
    duration: 10.9 
  },
  
  // Intro (30s)
  { 
    id: "004_intro_self", 
    audioFile: "004_intro_self.wav", 
    subtitle: "どうも、ずんだもんなのだ\n普段はターミナルに住んでるタイプのエンジニアなのだ",
    duration: 6.1 
  },
  { 
    id: "005_intro_preview", 
    audioFile: "005_intro_preview.wav", 
    slideFile: "02_three_points.png", 
    subtitle: "今日は3つのポイントでお話しするのだ",
    duration: 22.4 
  },
  { 
    id: "006_intro_cta", 
    audioFile: "006_intro_cta.wav", 
    slideFile: "02_three_points.png", 
    subtitle: "ターミナル好きな方\nぜひチャンネル登録と高評価お願いするのだ",
    duration: 5.4 
  },
  
  // Main 1 - Libraries (3min)
  { 
    id: "007_main1_intro", 
    audioFile: "007_main1_intro.wav", 
    subtitle: "まず、なんでこんなにキレイなTUIアプリが\n作れるようになったのか。答えはライブラリの進化なのだ",
    duration: 8.1 
  },
  { 
    id: "008_main1_bubbletea1", 
    audioFile: "008_main1_bubbletea1.wav", 
    slideFile: "03_bubble_tea.png", 
    subtitle: "1つ目がBubble Tea\nGitHubスター3万7000以上。これ、すごい数字なのだ",
    duration: 13.1 
  },
  { 
    id: "009_main1_bubbletea2", 
    audioFile: "009_main1_bubbletea2.wav", 
    slideFile: "04_elm_architecture.png", 
    subtitle: "Elm Architectureっていう設計パターンを採用\nModel、Update、Viewの3つに分けて考える",
    duration: 20.3 
  },
  { 
    id: "010_main1_bubbletea3", 
    audioFile: "010_main1_bubbletea3.wav", 
    slideFile: "03_bubble_tea.png", 
    subtitle: "エコシステムが充実してて\nかなり洗練されたUIが作れちゃうのだ",
    duration: 16.8 
  },
  { 
    id: "011_main1_ratatui1", 
    audioFile: "011_main1_ratatui1.wav", 
    slideFile: "05_ratatui.png", 
    subtitle: "2つ目がRatatui。こっちはRust製なのだ",
    duration: 5.9 
  },
  { 
    id: "012_main1_ratatui2", 
    audioFile: "012_main1_ratatui2.wav", 
    slideFile: "05_ratatui.png", 
    subtitle: "元々tui-rsっていうライブラリだったんですけど\n2022年にメンテナンスが止まっちゃった",
    duration: 11.9 
  },
  { 
    id: "013_main1_ratatui3", 
    audioFile: "013_main1_ratatui3.wav", 
    slideFile: "06_timeline.png", 
    subtitle: "2023年2月、コミュニティが立ち上がってフォーク\n8月には正式に後継として認められたのだ",
    duration: 12.5 
  },
  { 
    id: "014_main1_ratatui4", 
    audioFile: "014_main1_ratatui4.wav", 
    slideFile: "05_ratatui.png", 
    subtitle: "GitHubスター1万6500以上、テストカバレッジ90%\nオープンソースコミュニティの力ってすごいのだ",
    duration: 15.3 
  },
  { 
    id: "015_main1_question", 
    audioFile: "015_main1_question.wav", 
    subtitle: "ちなみに皆さん、Go派ですか？Rust派ですか？\nコメントで教えてほしいのだ",
    duration: 7.6 
  },
  
  // Main 2 - Why 2023 (3min)
  { 
    id: "016_main2_intro1", 
    audioFile: "016_main2_intro1.wav", 
    slideFile: "07_cambrian.png", 
    subtitle: "で、ここからが本題\nなぜ2023年だったのか",
    duration: 4.9 
  },
  { 
    id: "017_main2_intro2", 
    audioFile: "017_main2_intro2.wav", 
    slideFile: "07_cambrian.png", 
    subtitle: "カンブリア紀って知ってます？\n2023年のTUI界隈、まさにこれと同じことが起きてたのだ",
    duration: 15.0 
  },
  { 
    id: "018_main2_reasons", 
    audioFile: "018_main2_reasons.wav", 
    slideFile: "08_six_factors.png", 
    subtitle: "理由は大きく6つあるのだ",
    duration: 2.3 
  },
  { 
    id: "019_main2_reason1", 
    audioFile: "019_main2_reason1.wav", 
    slideFile: "08_six_factors.png", 
    subtitle: "1つ目、アーキテクチャの改善\n複雑な状態管理が楽になったのだ",
    duration: 14.9 
  },
  { 
    id: "020_main2_reason2", 
    audioFile: "020_main2_reason2.wav", 
    slideFile: "08_six_factors.png", 
    subtitle: "2つ目、コミュニティ駆動の開発\nメンテナーが離れても、コミュニティが引き継ぐ",
    duration: 10.6 
  },
  { 
    id: "021_main2_reason3", 
    audioFile: "021_main2_reason3.wav", 
    slideFile: "08_six_factors.png", 
    subtitle: "3つ目、エコシステムの充実\nゼロから作る必要がないのだ",
    duration: 11.1 
  },
  { 
    id: "022_main2_reason4", 
    audioFile: "022_main2_reason4.wav", 
    slideFile: "08_six_factors.png", 
    subtitle: "4つ目、非同期I/Oのサポート\nキー入力への反応が爆速になったのだ",
    duration: 9.6 
  },
  { 
    id: "023_main2_reason5", 
    audioFile: "023_main2_reason5.wav", 
    slideFile: "08_six_factors.png", 
    subtitle: "5つ目、クロスプラットフォーム対応\nMac、Linux、Windows、全部動くのだ",
    duration: 11.2 
  },
  { 
    id: "024_main2_reason6", 
    audioFile: "024_main2_reason6.wav", 
    slideFile: "08_six_factors.png", 
    subtitle: "6つ目、開発者体験の向上\n開発が快適になったのだ",
    duration: 10.3 
  },
  { 
    id: "025_main2_enterprise1", 
    audioFile: "025_main2_enterprise1.wav", 
    slideFile: "09_enterprise.png", 
    subtitle: "Microsoft、NVIDIA、AWSなど\n大手企業が本番環境で使ってるのだ",
    duration: 24.2 
  },
  { 
    id: "026_main2_enterprise2", 
    audioFile: "026_main2_enterprise2.wav", 
    slideFile: "09_enterprise.png", 
    subtitle: "つまり、もうおもちゃじゃない\n本気で使えるレベルになったってことなのだ",
    duration: 5.6 
  },
  
  // Main 3 - Apps (2min)
  { 
    id: "027_main3_intro", 
    audioFile: "027_main3_intro.wav", 
    subtitle: "じゃあ実際、どんなアプリがあるのか\n僕が普段使ってるものを紹介するのだ",
    duration: 6.4 
  },
  { 
    id: "028_main3_lazygit", 
    audioFile: "028_main3_lazygit.wav", 
    subtitle: "まずlazygit。Git操作がこれ一つで完結\n全部キーボードだけでできる",
    duration: 16.2 
  },
  { 
    id: "029_main3_lazydocker", 
    audioFile: "029_main3_lazydocker.wav", 
    subtitle: "次にlazydocker\nDockerコンテナの管理がめちゃくちゃ楽になる",
    duration: 13.7 
  },
  { 
    id: "030_main3_yazi", 
    audioFile: "030_main3_yazi.wav", 
    subtitle: "ファイルマネージャーならyazi\nRatatui製で、とにかく速い",
    duration: 12.9 
  },
  { 
    id: "031_main3_glow", 
    audioFile: "031_main3_glow.wav", 
    subtitle: "あとはGlow\nMarkdownをターミナルでキレイに表示できる",
    duration: 12.1 
  },
  { 
    id: "032_main3_ghdash", 
    audioFile: "032_main3_ghdash.wav", 
    subtitle: "gh-dashはGitHub CLIの拡張\nPRとissueの管理ができる",
    duration: 14.3 
  },
  
  // Summary (40s)
  { 
    id: "033_summary_intro", 
    audioFile: "033_summary_intro.wav", 
    slideFile: "10_summary.png", 
    subtitle: "はい、ということで今日のまとめなのだ",
    duration: 3.3 
  },
  { 
    id: "034_summary_main", 
    audioFile: "034_summary_main.wav", 
    slideFile: "10_summary.png", 
    subtitle: "TUIアプリが急に増えた理由\nBubble TeaとRatatuiという2大ライブラリの成熟",
    duration: 18.2 
  },
  { 
    id: "035_summary_points", 
    audioFile: "035_summary_points.wav", 
    slideFile: "10_summary.png", 
    subtitle: "ポイントは3つ\n開発が楽に、エコシステムの充実、企業採用レベルの品質",
    duration: 14.7 
  },
  { 
    id: "036_summary_advice", 
    audioFile: "036_summary_advice.wav", 
    slideFile: "10_summary.png", 
    subtitle: "まずはlazygitかyaziから使ってみてほしいのだ\n一度使うと、もう戻れなくなるのだ",
    duration: 8.9 
  },
  
  // Ending (20s)
  { 
    id: "037_ending_cta", 
    audioFile: "037_ending_cta.wav", 
    slideFile: "11_endcard.png", 
    subtitle: "TUIアプリ作ってみたいなって思った方\n概要欄にチュートリアルリンク貼っておくのだ",
    duration: 11.5 
  },
  { 
    id: "038_ending_related", 
    audioFile: "038_ending_related.wav", 
    slideFile: "11_endcard.png", 
    subtitle: "ターミナル環境をもっと快適にしたい方は\nこちらの動画もおすすめなのだ",
    duration: 5.8 
  },
  { 
    id: "039_ending_close", 
    audioFile: "039_ending_close.wav", 
    slideFile: "11_endcard.png", 
    subtitle: "それでは、良いターミナルライフを\nまた次の動画でなのだ",
    duration: 4.9 
  },
];

// Calculate cumulative timing
export const getScenesWithTiming = () => {
  let cumulativeTime = 0;
  return scenes.map((scene) => {
    const startFrame = Math.round(cumulativeTime * 30); // 30 fps
    const durationFrames = Math.round(scene.duration * 30);
    cumulativeTime += scene.duration;
    return {
      ...scene,
      startFrame,
      durationFrames,
      endFrame: startFrame + durationFrames,
    };
  });
};

export const getTotalDuration = () => {
  return scenes.reduce((sum, scene) => sum + scene.duration, 0);
};

export const getTotalFrames = () => {
  return Math.round(getTotalDuration() * 30); // 30 fps
};
