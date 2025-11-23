# Major Crime Indicators

## This project uses selected columns from the Toronto Crime dataset to build SafeRoute AI, a system that recommends the safest walking path in the city.

Below is a simple explanation of why each column is required.

Selected Columns & Why They Matter
1. event_unique_id

What it is: A unique identifier for each crime record.

Why we need it:

Helps track individual crime events.

Prevents duplicate entries.

Useful for merging datasets safely.

2. offence

What it is: The specific crime committed (e.g., Assault, Robbery, Auto Theft).

Why we need it:

Helps classify crimes into Major Crime Indicators (MCI).

Used to determine crime type severity.

Improves model accuracy by distinguishing violent vs. non-violent crimes.

3. location

What it is: Description of where the crime occurred (e.g., “On Street”, “Apartment”, “Parking Lot”).

Why we need it:

Certain locations are more dangerous (dark alleys, transit stops, etc.).

Helps add context for risk scoring.

Useful feature for ML model (location-based risk).

4. premises_type

What it is: Type of building or place involved (e.g., “Outside”, “Commercial”, “Residential”).

Why we need it:

Predictive factor: crimes occur more in some premises types.

Helps the model understand environmental risk.

Useful for identifying hotspots (e.g., assaults near bars at night).

5. neighbourhood_158

What it is: Toronto’s 158 standardized neighbourhood IDs.

Why we need it:

Allows mapping crime to neighbourhoods.

Enables neighbourhood-level risk scoring.

Lets us create a Safety Heatmap of the city.

Useful for demographic + geographic analysis

6. LATITUDE

What it is: The geographic latitude of the crime.

Why we need it:
Used to place crime events on a map and calculate risk near specific streets or intersections.

7. LONGITUDE

What it is: The geographic longitude of the crime.

Why we need it:
Works with latitude to map crime locations and build the risk heatmap.

8. OCCURRED_ON_DATE

What it is: Date and timestamp of when the crime happened.

Why we need it:

Extract time of day → risk changes at night.

Determine day/night patterns.

Identify seasonal trends.

9. hour (derived column)

What it is: Hour of the day (0–23), extracted from the timestamp.

Why we need it:

Crime risk varies heavily by hour.

Night-time hours (10 PM – 5 AM) are more dangerous.

Used as an input to the ML model.

10. MCI_CATEGORY

What it is: Toronto Police classification of major crimes:

Assault

Break and Enter

Robbery

Auto Theft

Theft Over

Homicide

Why we need it:

Filters dataset to serious crimes only.

Used to assign a severity score.

Improves accuracy of safety prediction.

11. severity (derived column)

What it is: Numerical score (e.g., 2–5) representing crime seriousness.

Why we need it:

Higher severity = higher risk on surrounding streets.

Used for weighting routes in the safe path algorithm.