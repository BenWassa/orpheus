# Data Directory

This directory contains all data files for Project Orpheus.

## Structure

- **`raw/`** - Original, unprocessed data files
  - `x_rap_x.csv` - Sample Spotify playlist export from Exportify
  - Add additional raw music data files here

- **`processed/`** - Cleaned and processed data ready for analysis
  - Processed CSV files with additional features
  - Aggregated listening patterns
  - Emotional analysis results

## Data Sources

- **Spotify Exports**: CSV files from [Exportify](https://github.com/watsonbox/exportify)
- **Additional streaming services**: Future expansion for Apple Music, etc.
- **Manual annotations**: Emotional tagging and life event correlations

## Notes

- Keep raw data files immutable
- Document any processing steps in the notebooks directory
- See `docs/exportify_data_dictionary.md` for CSV column definitions
