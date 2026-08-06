from dataclasses import dataclass

@dataclass
class DataFrameDataTypes:
	dtype = {
		"ID": str,
		"Festival": str,
		"Year": int,
		"Website": str,
		"Code": str,
		"Title": str,
		"Subtitle": str,
		"Teaser": str,
		"Description": str,
		"Genre": str,
		"Genre tags": str,
		"Warnings": str,
		"Artist":  str,
		"Artist type": str,
		"Age category": str,
		"Country": str,
		"Performers #": int,
		"Venue": str,
		"Venue code": str,
		"Venue address": str,
		"Venue postcode": str,
		"Venue website": str,
		"Venue description": str,
		"Venue accessibility": str,
		"Latitude": float,
		"Longitude": float,
		"Performances #": int,
		"Lowest full price": float,
		"Lowest concession price": float
	}

	parse_dates = [
		"Last updated",
		"First performance date",
		"Last performance date"
	]