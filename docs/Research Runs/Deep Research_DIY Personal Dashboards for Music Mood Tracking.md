# Deep Search — Personal Music Mood Visualization Project Playbooks
Practical approaches to building personal music mood visualization pipelines.

## 1. Research Question
This deep search investigates practical methods and open-source examples for creating personal music mood visualization pipelines, from Spotify data acquisition and local feature extraction to clustering, dimensionality reduction, and diverse visualization styles, primarily focusing on hobbyist and research prototypes.

## 2. Core Findings
-   **F-1:** Numerous lightweight, personal mood-tracking dashboards and apps leverage the Spotify API and local machine learning to visualize daily or weekly music mood, often focusing on single-user, local deployments.
-   **F-2:** Common approaches involve clustering Spotify audio features (e.g., valence, danceability, energy) or lyrics embeddings (derived from NLP models like BERT) to discover natural mood or genre groupings.
-   **F-3:** Visualization extensively uses dimensionality reduction techniques (PCA, t-SNE, UMAP) to project high-dimensional data into 2D/3D spaces, employing scatter plots, bubble charts, timelines, and heatmaps, often with color-coding, to represent mood patterns and trends.
-   **F-4:** Local deployment is favored for privacy and data control, but necessitates careful management of Spotify API rate limits (e.g., 50 items per "Get Recently Played" call) and involves manual data updating for full listening histories.
-   **F-5:** Projects demonstrate the practical process of computing "emotion embeddings" from music data and subsequently mapping these into interpretable mood/affective states using simple machine learning or unsupervised clustering.

## 3. Evidence & Examples
| Ref | Source / Link | Key Insight | Why It Matters |
|-----|---------------|-------------|----------------|
| 1, 3 | Build a Flask-Heroku Mood Tracker Web App Using the Spotify API by Irene Chang | Details a Flask app for daily mood tracking using Spotify features and logistic regression, highlighting the need to loop through the API for full-day data. | Provides a concrete example of a Flask-based personal mood app and illustrates challenges with Spotify API data retrieval limits. |
| 4 | Portfolio Project | Spotify Mood Ring by Jack Joseph | Describes a React app comparing recent Spotify track audio features to population averages and assigning emoji-based mood labels. | Illustrates a client-side approach for personal mood labeling based on comparative audio feature analysis. |
| 5 | MusicMood by Sebastian Raschka | Classifies songs as "happy" or "sad" using lyrics with a binary classifier, deployed via Flask/PythonAnywhere. | Demonstrates an NLP-driven method for mood classification from lyrical content, emphasizing local/personal deployment. |
| 6 | GitHub - raffg/spotify_analysis | Provides an example of analyzing the distribution of Spotify's valence score across different regions. | Shows how data analysis notebooks can be used to visualize broad mood patterns within music listening data. |
| 7 | GitHub - chingisooinar/Clustering-my-songs-on-Spotify | Focuses on clustering a user's saved Spotify songs via K-means on audio features, visualizing embeddings with PCA/UMAP, and labeling clusters with moods/genres. | A direct, open-source example of applying unsupervised clustering and dimensionality reduction for mood discovery. |
| 8, 9 | Explorify: A Personalized Interactive Visualization Tool for Spotify Listening History | Visualizes Spotify tracks as similarity-linked nodes, using audio features (danceability, valence, energy) to define axes or colors. | Highlights interactive visualization of listening history, enabling exploration of mood-related audio feature space. |
| 10, 11 | GitHub - Merrimack-Computer-Club/Spotify_NLP_Service | Trains a BERT model on song lyrics to tag emotion categories from a user's Spotify listening history. | Provides a specific open-source example of using advanced NLP (BERT) for emotion analysis on music lyrics. |
| 12 | How to Add Spotify Playlists or Tracks to Your Day One Journal | Notes the capability to embed Spotify tracks into Day One journal entries for manual annotation. | Illustrates a practical method for users to manually integrate music listening into personal reflective tools, suggesting a hybrid approach for mood tracking. |
| 13 | Web API Reference | Spotify for Developers - Get Recently Played endpoint | Confirms Spotify's "Get Recently Played" API limit of 50 items per call. | Crucial for understanding data collection limitations and informing strategies for comprehensive data acquisition. |

## 4. Implementation Highlights
-   **Pipelines / Code Repos:**
    -   `Irene Chang's "Mood Journaling"` – [https://medium.com/data-science/build-a-flask-heroku-mood-tracker-web-app-using-the-spotify-api-14b3b5c92ac9](https://medium.com/data-science/build-a-flask-heroku-mood-tracker-web-app-using-the-spotify-api-14b3b5c92ac9) — Flask app for daily mood tracking.
    -   `Jack Joseph's Spotify Mood Ring` – [https://javascript.plainenglish.io/portfolio-project-spotify-mood-ring-dba09b6da1e0](https://javascript.plainenglish.io/portfolio-project-spotify-mood-ring-dba09b6da1e0) — React web app for comparing audio features.
    -   `Sebastian Raschka's MusicMood` – [https://sebastianraschka.com/blog/2014/musicmood.html](https://sebastianraschka.com/blog/2014/musicmood.html) — Blog/repo for lyric-based mood classification.
    -   `raffg/spotify_analysis` – [https://github.com/raffg/spotify_analysis](https://github.com/raffg/spotify_analysis) — GitHub repo for Spotify valence score analysis.
    -   `chingisooinar/Clustering-my-songs-on-Spotify` – [https://github.com/chingisooinar/Clustering-my-songs-on-Spotify](https://github.com/chingisooinar/Clustering-my-songs-on-Spotify) — GitHub repo for K-means clustering on Spotify audio features.
    -   `Merrimack-Computer-Club/Spotify_NLP_Service` – [https://github.com/Merrimack-Computer-Club/Spotify_NLP_Service](https://github.com/Merrimack-Computer-Club/Spotify_NLP_Service) — GitHub repo for BERT-based lyric emotion analysis.
-   **Key Config / Setup Tips:**
    1.  Store sensitive Spotify API credentials locally (e.g., in `.env` files) and exclude from version control (`.gitignore`).
    2.  Manage Spotify API rate limits by implementing looping and cursor paging, especially for endpoints like "Get Recently Played" (50 items/call).
    3.  Automate daily data pulls from Spotify and store intermediate JSONs locally to reduce API calls and manage dependencies.
    4.  Utilize Spotify's built-in audio features (e.g., `valence`, `energy`, `danceability`) or leverage pre-trained NLP models for lyrics to keep projects lightweight and avoid retraining large models.
-   **Dependencies / Toolchain:** Flask, React, PythonAnywhere, Jupyter/Python notebooks, Spotipy (for Spotify API interaction), K-means (for clustering), PCA, UMAP (for dimensionality reduction), BERT (for NLP), HTML/CSS/JavaScript (for web applications).

## 5. Performance & Practical Notes
| Metric | Reported Value | Environment |
|--------|----------------|-------------|
| Data Fetch Time | Longer due to API limits (50 items/call for "recently played") requiring looping/cursor paging | Single laptop without cloud services |
| Model Training Speed | Data-intensive ML models or network graphs may run slowly | Laptop |
| Deployment Scale | DIY dashboards trade scale for privacy; everything can run on a single laptop. | Single laptop |

## 6. Best Practices
1.  **Prioritize Local & Private Deployment:** Build mood-tracking apps to run locally or on small, private servers (e.g., Flask/Streamlit/Dash) to ensure user data privacy and control.
2.  **Implement Robust API Management:** Securely store API credentials and actively manage Spotify API rate limits through techniques like looping, cursor paging, and data caching to ensure comprehensive data collection over time.
3.  **Leverage Existing Features & Models:** For lightweight implementations, rely on Spotify's pre-computed audio features (valence, energy) or readily available pre-trained NLP models to infer mood without intensive local model training.
4.  **Visualize for Insight:** Employ dimensionality reduction (PCA, t-SNE, UMAP) and diverse chart types (scatter, bubble, timelines, heatmaps with color-coding) to intuitively interpret and validate mood clusters and trends.
5.  **Automate Data Processes:** Automate daily data pulls and judiciously store intermediate JSON data to streamline workflows and minimize repetitive API calls.

## 7. Limitations & Open Questions
-   **API Data Completeness:** Spotify's API limits (e.g., 50 items per call for "recently played") make collecting a full day's granular listening data challenging, often requiring complex looping.
-   **Local Processing Scalability:** Running data-intensive machine learning models or complex network graphs locally on a laptop can be slow, limiting the sophistication of models used in hobbyist projects.
-   **Manual Data Management Burden:** The emphasis on local, private deployment often leads to longer data fetch times and a reliance on manual data updating, which can be cumbersome.
-   **Limited Manual Annotation Integration:** Most demo tools do not natively support direct integration of user's manual notes or tags, missing a rich source of subjective mood data.
-   **Dependency Management:** Managing heavy and numerous software dependencies can pose a challenge for hobbyist projects.

## 8. Next Actions for Project Orpheus
-   **A-1:** Design and prototype a Spotify API data acquisition module focusing on efficient handling of "Get Recently Played" limits using looping and cursor paging to build comprehensive daily listening histories.
-   **A-2:** Implement initial mood inference using Spotify's native audio features (valence, energy, danceability) and simple logistic regression or K-means clustering for a lightweight, local-first approach.
-   **A-3:** Explore and integrate existing open-source Python notebooks (e.g., `chingisooinar/Clustering-my-songs-on-Spotify`) to visualize Spotify audio features using PCA or t-SNE, color-coding by inferred mood clusters.
-   **A-4:** Research and document secure methods for storing Spotify API credentials locally (e.g., environment variables, `.env` files) for all project development.