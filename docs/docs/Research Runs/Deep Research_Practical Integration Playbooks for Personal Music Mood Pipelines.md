# Deep Search — Practical Integration Playbooks for Personal Music Mood Pipelines
Short phrase capturing the specific focus: Practical approaches to clustering music embeddings for mood inference.

## 1. Research Question
This deep search set out to discover practical methods, notebooks, or tutorials for applying heuristics and unsupervised clustering to music embeddings (from models like MuLan or YAMNet) to discover natural mood or emotion groups, including mapping to valence/arousal axes, validation with metadata, visualization, and data size recommendations.

## 2. Core Findings
-   **F-1:** High-quality music embeddings from pre-trained models (e.g., MuLan, YAMNet) can be effectively processed using unsupervised clustering (K-Means, DBSCAN) and dimensionality reduction (PCA, t-SNE, UMAP) to reveal natural mood groupings.
-   **F-2:** Clusters can be meaningfully mapped onto valence/arousal axes and validated using external metadata like genre or listening history, supporting applications such as mood-based playlist generation and recommendation.
-   **F-3:** Practical pipelines emphasize rigorous data preprocessing, feature selection (prioritizing valence and energy), and careful interpretation of clusters through visual inspection (color mapping, nearest neighbors) and quantitative metrics.
-   **F-4:** Stable and generalizable mood clustering benefits from large datasets (tens of thousands of tracks), though personalized applications can work with smaller, individual listening histories (hundreds to thousands of tracks).
-   **F-5:** Open-source examples and code repositories (e.g., EMER-CL) provide concrete starting points for implementing these end-to-end workflows in Python, combining audio feature extractors with advanced embedding and clustering techniques.

## 3. Evidence & Examples
| Ref | Source / Link | Key Insight | Why It Matters |
|-----|---------------|-------------|----------------|
| 1.1, 1.2, 1.3 | Mahta Bakhshizadeh et al., 2019 9th International Conference on Computer and Knowledge Engineering (ICCKE) | Describes aggregating and clustering audio features (valence, danceability, energy, mode) using K-Means for mood group formation, mapping to valence/arousal, and visualizing. | Provides a foundational practical workflow for applying clustering to audio features for mood. |
| 2.1, 2.2, 2.3, 2.4 | Naoki Takashima et al., IEEE Access, Jan 2023 | Highlights MuLan and YAMNet for extracting emotion-nuanced embeddings, and the use of composite loss functions (CCA, KL-divergence) to create affect-relevant embedding spaces amenable to clustering (K-Means). Discusses cosine similarity for clustering and practical tips like adjusting origin for valence/arousal mapping. | Confirms the use of advanced embeddings and specific loss functions for creating better clusterable spaces, and offers practical metric and mapping advice. |
| 2.5 | EMER-CL Open Repository: https://mu-lab.info/naoki_takashima/emer-cl | Provides sample code for embedding-based music emotion recognition using composite loss functions, including steps for embedding extraction, unsupervised clustering, and t-SNE visualization. | Offers a direct, open-source code example for implementing a modern music emotion inference pipeline. |
| 4.1, 4.2 | Alessandro B. Melchiorre et al., International Journal of Multimedia Information Retrieval, June 2023 | Describes the EmoMTB system which clusters nearly half a million songs, uses PCA then t-SNE/UMAP for visualization, and employs color mapping to emotion-related features. Discusses cluster interpretation and scalability. | Demonstrates a large-scale practical application, visualization techniques (UMAP), and tips for meaningful cluster interpretation with color coding. |
| 5.1, 5.2 | ArXiv, 2020 (Mood classification using listening data) | Suggests that datasets of tens of thousands of tracks are needed for robust and generalizable clustering, with some studies using upwards of 67,000 tracks. | Provides concrete recommendations on minimum data size for stable and generalizable mood clustering. |

## 4. Implementation Highlights
-   **Pipelines / Code Repos:**
    -   `EMER-CL` – [https://mu-lab.info/naoki_takashima/emer-cl](https://mu-lab.info/naoki_takashima/emer-cl) — Sample code for embedding-based music emotion recognition with composite loss, including clustering and t-SNE visualization.
-   **Key Config / Setup Tips:**
    1.  Pre-process raw audio by extracting high-quality embeddings from models like MuLan, YAMNet, or VGGish.
    2.  Prioritize affect-relevant features (e.g., valence, energy, danceability, acousticness, speechiness) for feature vector construction.
    3.  Normalize and standardize embeddings prior to clustering.
    4.  Consider using cosine similarity over Euclidean distance for clustering when directional information is key.
    5.  Adjust the origin/mid-point in the valence/arousal space (e.g., using a barycenter) for balanced clusters.
    6.  For visualization, apply PCA first for noise reduction, then t-SNE or UMAP for intuitive 2D/3D plots.
-   **Dependencies / Toolchain:** Essentia, OpenSMILE (for feature extraction), TensorFlow (for YAMNet), scikit-learn (for K-Means, DBSCAN, PCA), matplotlib, Seaborn (for visualization), Python (general scripting).

## 5. Performance & Practical Notes
| Metric | Reported Value | Environment |
|--------|----------------|-------------|
| Accuracy (lyric-based emotion) | Up to 95% | Transformer-based models |
| Pearson correlation (valence/arousal) | ~0.80 for valence, ~0.79 for arousal | Fine-tuned language models on social media data |
| Data size for stable clustering | Tens of thousands of tracks (large-scale); hundreds to thousands (personalized) | General recommendation / EmoMTB (4.1) / Mood classification (5.1) |
| Scalability | UMAP scales well to very large datasets | Standard laptop (YAMNet) / Portable devices (YOLO-V3) |

## 6. Best Practices
1.  **Robust Embedding Extraction:** Start with high-quality embeddings from pre-trained models (MuLan, YAMNet) as they capture nuanced emotional information.
2.  **Strategic Feature Selection:** Focus on acoustic features or embedding dimensions demonstrably linked to mood (valence, energy, danceability).
3.  **Appropriate Clustering Algorithms:** Use K-Means for speed and simplicity on large datasets, or DBSCAN for unknown cluster numbers with careful parameter tuning.
4.  **Meaningful Visualization:** Employ PCA, t-SNE, or UMAP to project embeddings into visualizable spaces, annotating clusters with color mappings to emotion-related features for intuitive interpretation.
5.  **Multimodal Cluster Validation:** Validate clusters both quantitatively (e.g., silhouette scores, intra/inter-cluster similarity) and qualitatively by correlating with genre labels, mood annotations, or user feedback.
6.  **Ethical Data Handling:** Ensure rigorous filtering of missing/erroneous metadata to prevent spurious clusters.

## 7. Limitations & Open Questions
-   **Direct Spotify Integration:** A comprehensive open-source library that directly maps Spotify track data into advanced emotion embeddings is still emerging; current solutions often require combining different tools.
-   **Subjectivity & Context:** Music mood perception is highly subjective; integrating multiple forms of validation (e.g., crowd-sourced evaluations) is resource-intensive but crucial for real-world utility.
-   **Temporal Dynamics:** How to effectively incorporate temporal mood transitions within listening sessions into clustering or recommendation systems remains an area of ongoing research.
-   **Disentangled Representations:** How can deep embedding models be explicitly trained to separate out different semantic dimensions (e.g., mood vs. genre vs. instrumentation) for more precise clustering?

## 8. Next Actions for Project Orpheus
-   **A-1:** Experiment with extracting embeddings from Spotify track data using publicly available API features and integrating them with pre-trained models (e.g., exploring how MuLan/YAMNet embeddings can be applied to Spotify audio).
-   **A-2:** Implement a proof-of-concept mood clustering pipeline using `scikit-learn` (K-Means) and visualization tools (t-SNE/UMAP) on a sample dataset, mapping the resulting clusters to valence/arousal axes based on the provided best practices.
-   **A-3:** Investigate the `EMER-CL` repository (https://mu-lab.info/naoki_takashima/emer-cl) as a starting point for building a practical, local-first mood inference system, assessing its applicability to real-world Spotify listening data.