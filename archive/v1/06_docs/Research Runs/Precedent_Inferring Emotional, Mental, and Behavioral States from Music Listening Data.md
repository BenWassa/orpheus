# Precedent Search — Inferring Emotional, Mental, and Behavioral States from Music Listening Data

## 1. Purpose
This precedent scan covers studies that analyze music listening data, including Spotify playlists, to infer emotions, mental states, and behavioral patterns, identifying relevant methodologies, tools, and best practices.

## 2. Key Precedent Areas
*   Music listening & mood/personality regulation
*   Large-scale behavioral data analysis (Spotify)
*   Music and mental health inference
*   Emotion recognition from music (audio features, physiological signals, facial expressions)

## 3. Notable Studies & Sources
| Ref | Title | Authors | Venue | Key Context |
|-----|-------|---------|-------|--------------|
| 1.1 | Modeling and Influencing Music Preferences on Streaming Platforms | [Not provided] | 2024 | Early studies establishing links between music listening and mood regulation (e.g., Saarikallio’s strategies, North & Hargreaves). |
| 2.1 | “Just the Way You Are”: Linking Music Listening on Spotify and Personality | Ian Anderson, Santiago Gil, Clay Gibson, Scott Wolf, Will Shapiro, Oguz Semerci, David M. Greenberg | Social Psychological and Personality Science, May 2021 | Large-scale investigations using Spotify data to predict personality traits and mood states. |
| 3.1 | Twitter-MusicPD: melody of minds - navigating user-level data on multiple mental health disorders and music preferences | Soroush Zamani Alavijeh, Xingwei Yang, Zeinab Noorian, Amira Ghenai, Fattane Zarrinkalam | EPJ Data Science, Apr 2025 | Integrates music track data with social media signals to analyze mental health and music preferences. |
| 4.1 | CLASSIFYING MENTAL DISORDERS BASED ON MUSICAL PREFERENCES: A MACHINE LEARNING AND DEEP LEARNING APPROACH | [Not provided] | [Not provided] | Work on classifying mental disorders based on musical preferences using machine learning from audio features. |
| 5.1 | The Emotion-to-Music Mapping Atlas (EMMA): A systematically organized online database of emotionally evocative music excerpts | Hannah Strauss, Julia Vigl, Peer-Ole Jacobsen, Martin Bayer, Francesca Talamini, Wolfgang Vigl, Eva Zangerle, Marcel Zentner | Behavior Research Methods, Jan 2024 | Studies focusing on emotion recognition from music using physiological signals and audio embeddings. |
| 6.1 | Emotion Sensitive Music Broadcasting by Analysing Facial Expressions using Machine Learning | [Not provided] | 2023 | Additional studies on emotion recognition from music using facial expression analyses. |
| 7.1 | Soundscapes of morality: Linking music preferences and moral values through lyrics and audio | Vjosa Preniqi, Kyriaki Kalimeri, C. Saitis | PLOS ONE, Nov 2023 | Discusses limitations such as sample diversity constraints and potential biases from curated playlists. |

## 4. Methods & Frameworks Used
*   **Data sources:** Spotify’s API for large-scale, real-life listening histories; Twitter-MusicPD dataset integrating music track data with social media signals.
*   **Core ML/analytical pipelines:** Regression models, deep learning pipelines, embedding techniques (e.g., Song2Vec), machine learning and deep learning approaches for classification.
*   **Special tools, toolkits, open frameworks:** OpenSMILE and Matlab toolboxes for extracting acoustic features; Convolutional Neural Networks (CNNs) for facial expression recognition.

## 5. Lessons Learned
*   **What worked well:**
    *   Studies using large-scale behavioral data improved prediction accuracy of personality and mood over traditional self-reports, providing better ecological validity.
    *   Incorporating contextual metadata such as location, weather, and time enhances inferences from streaming data.
*   **Limitations & failures:**
    *   Sample diversity constraints.
    *   Potential biases from curated playlists.
    *   Challenges in standardizing emotion taxonomies.

## 6. Best Practices Extracted
*   Leverage large-scale, actual streaming behaviors combined with contextual metadata rather than sole reliance on self-report measures.
*   Use robust machine learning pipelines and embedding methods to extract features that correlate with psychological constructs.
*   Ensure ethical data governance (e.g., IRB approval) when dealing with personal digital histories.
*   Future research directions include integrating multimodal signals (audio, facial expressions, physiological data) to enhance emotion recognition from music.

## 7. Direct Links / DOIs
*   Twitter-MusicPD dataset (3.1): https://doi.org/10.1140/epjds/s13688-025-00549-7
*   “Just the Way You Are” (2.2): https://doi.org/10.1177/1948550620923228

---
**Status:** ✅ Precedent established