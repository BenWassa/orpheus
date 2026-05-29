from __future__ import annotations



from orpheus.score.depth import _count_syllables, _lexical_density, _acoustic_complexity, _topic_depth, score_depth
from orpheus.score.emotion import EmotionScorer, EMOTION_CATEGORIES
from orpheus.score.theme import ThemeScorer, THEME_CATEGORIES


class TestEmotionAcoustic:
    def test_high_valence_high_arousal_maps_to_joy(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        scores = scorer._score_acoustic({"valence": 0.9, "arousal": 0.8})
        top = max(scores, key=scores.get)
        assert top in ("joyful_activation", "triumphant_power")

    def test_low_valence_low_arousal_maps_to_sadness(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        scores = scorer._score_acoustic({"valence": 0.1, "arousal": 0.2})
        top = max(scores, key=scores.get)
        assert top == "sadness_melancholy"

    def test_low_valence_high_arousal_maps_to_anger(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        scores = scorer._score_acoustic({"valence": 0.15, "arousal": 0.9})
        top = max(scores, key=scores.get)
        assert top in ("anger_defiance", "tension_anxiety")

    def test_high_valence_low_arousal_maps_to_peace(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        scores = scorer._score_acoustic({"valence": 0.9, "arousal": 0.15})
        top = max(scores, key=scores.get)
        assert top == "peacefulness"

    def test_acoustic_none_returns_none(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        assert scorer._score_acoustic(None) is None

    def test_acoustic_missing_valence_returns_none(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        assert scorer._score_acoustic({"arousal": 0.5}) is None

    def test_all_scores_positive(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        scores = scorer._score_acoustic({"valence": 0.5, "arousal": 0.5})
        for cat, val in scores.items():
            assert val >= 0, f"{cat} has negative score"


class TestEmotionFusion:
    def test_fuse_weights_negative_valence_toward_lyrics(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        acoustic = {cat: 0.1 for cat in EMOTION_CATEGORIES}
        lyrical = {cat: 0.1 for cat in EMOTION_CATEGORIES}
        lyrical["sadness_melancholy"] = 0.9
        acoustic["sadness_melancholy"] = 0.1

        fused = scorer._fuse(acoustic, lyrical)
        # Lyrics dominate for sadness (0.7 weight)
        assert fused["sadness_melancholy"] > fused["joyful_activation"]

    def test_score_track_acoustic_only(self):
        scorer = EmotionScorer.__new__(EmotionScorer)
        scorer._classifier = None
        result = scorer.score_track({"valence": 0.5, "arousal": 0.5}, None)
        assert "emotion_scores" in result
        assert abs(sum(result["emotion_scores"].values()) - 1.0) < 0.01
        assert result["confidence"] == 0.5


class TestThemeSVSM:
    def test_svsm_removes_repeated_lines(self):
        scorer = ThemeScorer.__new__(ThemeScorer)
        scorer._model = None
        lyrics = "I love you baby\n" * 5 + "Walking down the street alone\nFeeling the rain on my face"
        filtered = scorer._svsm_filter(lyrics)
        assert "I love you baby" not in filtered
        assert "Walking down the street alone" in filtered

    def test_svsm_removes_short_lines(self):
        scorer = ThemeScorer.__new__(ThemeScorer)
        scorer._model = None
        lyrics = "Oh yeah\nThis is a longer meaningful line about life\nHmm\nAnother real sentence here"
        filtered = scorer._svsm_filter(lyrics)
        assert "Oh yeah" not in filtered
        assert "Hmm" not in filtered
        assert "longer meaningful" in filtered


class TestThemeHeuristic:
    def test_low_valence_low_energy(self):
        scorer = ThemeScorer.__new__(ThemeScorer)
        scorer._model = None
        scores = scorer._acoustic_heuristic({"valence": 0.1, "energy": 0.1})
        assert scores["existentialism_spirituality"] > scores["hedonism_escape"]

    def test_high_valence_high_energy(self):
        scorer = ThemeScorer.__new__(ThemeScorer)
        scorer._model = None
        scores = scorer._acoustic_heuristic({"valence": 0.9, "energy": 0.9})
        assert scores["hedonism_escape"] > scores["existentialism_spirituality"]


class TestDepth:
    def test_syllable_count(self):
        assert _count_syllables("hello") == 2
        assert _count_syllables("the") == 1
        assert _count_syllables("beautiful") == 3
        assert _count_syllables("a") == 1

    def test_lexical_density_basic(self):
        text = "the cat sat on the mat and the cat ate the fish"
        density = _lexical_density(text)
        assert density is not None
        assert 0.0 < density < 1.0

    def test_lexical_density_none_for_short_text(self):
        assert _lexical_density("hello") is None
        assert _lexical_density(None) is None

    def test_lexical_density_not_length_biased(self):
        # Two texts with the SAME per-segment variety (a 60-word vocabulary
        # cycled) but very different lengths should score comparably. Plain
        # type/token ratio would tank the long one (60/1200 vs 60/120) purely
        # for being longer; mean-segmental TTR should not.
        import string

        vocab = [a + b for a in string.ascii_lowercase for b in string.ascii_lowercase][:60]
        short = _lexical_density(" ".join(vocab[i % 60] for i in range(120)))
        long = _lexical_density(" ".join(vocab[i % 60] for i in range(1200)))
        assert short is not None and long is not None
        assert abs(short - long) < 0.05

    def test_acoustic_complexity_none_for_none(self):
        assert _acoustic_complexity(None) is None

    def test_acoustic_complexity_with_features(self):
        features = {"tempo": 140, "loudness": -3.0, "spectral_complexity": 0.7, "acousticness": 0.5}
        result = _acoustic_complexity(features)
        assert result is not None
        assert 0.0 <= result <= 1.0

    def test_topic_depth_uniform(self):
        scores = {cat: 0.125 for cat in THEME_CATEGORIES}
        result = _topic_depth(scores)
        assert result is not None
        assert result > 0.9  # near max entropy

    def test_topic_depth_concentrated(self):
        scores = {cat: 0.01 for cat in THEME_CATEGORIES}
        scores["heartbreak_loss"] = 0.93
        result = _topic_depth(scores)
        assert result is not None
        assert result < 0.5  # low entropy

    def test_score_depth_bucketing(self):
        score, label = score_depth(
            {"tempo": 120, "loudness": -5, "acousticness": 0.1},
            "the " * 50,
        )
        assert label in ("surface", "engaged", "immersive")
        assert 0.0 <= score <= 1.0

    def test_score_depth_no_inputs(self):
        score, label = score_depth(None, None)
        assert score == 0.5
        assert label == "engaged"
