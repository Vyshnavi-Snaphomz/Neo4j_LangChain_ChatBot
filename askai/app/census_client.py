"""
US Census Bureau API Client

Integrates with:
1. SOMA (Survey of Market Absorption) - Multifamily unit absorption rates
2. RHFS (Rental Housing Finance Survey) - Rental property financial characteristics
3. GEOINFO (Geography Information) - Geographic coordinates and spatial data
4. ACS (American Community Survey) - Demographic and socioeconomic data
"""

import requests
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime, timedelta
import math

class CensusAPIClient:
    """Client for US Census Bureau APIs"""
    
    BASE_URL_SOMA = "https://api.census.gov/data/timeseries/soma"
    BASE_URL_RHFS = "https://api.census.gov/data/{year}/rhfs"
    BASE_URL_GEOINFO = "https://api.census.gov/data/{year}/geoinfo"
    BASE_URL_ACS = "https://api.census.gov/data/{year}/acs/acs{period}"
    
    # Census API Key (provided by user)
    API_KEY = "e36997c7df21e06d9ad3123ae1fd6049ff4a8f8d"
    
    # State FIPS codes for API calls
    STATE_FIPS = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
        "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
        "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
        "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
        "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
        "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
        "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
        "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
        "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
        "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
        "DC": "11"
    }
    
    # Reverse mapping: Full state name to abbreviation
    STATE_NAME_TO_ABBREV = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
        "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
        "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
        "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
        "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
        "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
        "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
        "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
        "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
        "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
        "district of columbia": "DC"
    }
    
    def __init__(self):
        """Initialize Census API client"""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Snaphomz-RealEstate-Agent/1.0"
        })
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours
    
    def _get_state_fips(self, state: str) -> Optional[str]:
        """Convert state abbreviation or full name to FIPS code"""
        state_normalized = state.strip()
        
        # Try as abbreviation first
        state_upper = state_normalized.upper()
        if state_upper in self.STATE_FIPS:
            return self.STATE_FIPS[state_upper]
        
        # Try as full name
        state_lower = state_normalized.lower()
        abbrev = self.STATE_NAME_TO_ABBREV.get(state_lower)
        if abbrev:
            return self.STATE_FIPS[abbrev]
        
        return None
    
    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if not expired"""
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Dict):
        """Store data in cache with timestamp"""
        self.cache[cache_key] = (data, datetime.now())
    
    def get_absorption_data(self, state: str, year: Optional[int] = None) -> Optional[Dict]:
        """
        Fetch SOMA absorption data for multifamily units
        
        Args:
            state: State abbreviation (e.g., "TX", "CA")
            year: Optional year filter
            
        Returns:
            Dict with absorption rates and market data, or None if error
        """
        cache_key = f"soma:{state}:{year or 'latest'}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        fips = self._get_state_fips(state)
        if not fips:
            print(f"[Census API] Invalid state code: {state}")
            return None
        
        try:
            # Note: Actual SOMA API parameters may vary - this is a template
            params = {
                "get": "NAME,ABSORPTION_3MO,ABSORPTION_6MO,ABSORPTION_12MO,MEDIAN_RENT",
                "for": f"state:{fips}"
            }
            
            if year:
                params["time"] = str(year)
            
            response = self.session.get(self.BASE_URL_SOMA, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = self._parse_soma_response(data)
                self._set_cache(cache_key, result)
                return result
            else:
                print(f"[Census API] SOMA request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[Census API] Error fetching SOMA data: {e}")
            return None
    
    def _parse_soma_response(self, data: List) -> Dict:
        """Parse SOMA API response"""
        if not data or len(data) < 2:
            return {}
        
        # First row is headers, second row is data
        headers = data[0]
        values = data[1]
        
        result = {}
        for i, header in enumerate(headers):
            if i < len(values):
                result[header.lower()] = values[i]
        
        return result
    
    def get_rental_expenses(self, state: str, year: int = 2021) -> Optional[Dict]:
        """
        Fetch RHFS operational expenses data
        
        Args:
            state: State abbreviation
            year: Year (2015, 2018, or 2021)
            
        Returns:
            Dict with rental expense data, or None if error
        """
        cache_key = f"rhfs_expenses:{state}:{year}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        fips = self._get_state_fips(state)
        if not fips:
            return None
        
        try:
            url = self.BASE_URL_RHFS.format(year=year)
            
            # Fetch property characteristics and expenses
            params = {
                "get": "NAME,ESTIMATE_PROPERTIES,ESTIMATE_UNITS",
                "for": f"state:{fips}"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = self._parse_rhfs_response(data)
                self._set_cache(cache_key, result)
                return result
            else:
                print(f"[Census API] RHFS request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[Census API] Error fetching RHFS data: {e}")
            return None
    
    def _parse_rhfs_response(self, data: List) -> Dict:
        """Parse RHFS API response"""
        if not data or len(data) < 2:
            return {}
        
        headers = data[0]
        values = data[1]
        
        result = {}
        for i, header in enumerate(headers):
            if i < len(values):
                result[header.lower()] = values[i]
        
        return result
    
    def get_market_insights(self, state: str, city: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive market insights for a location
        
        Args:
            state: State abbreviation
            city: Optional city name
            
        Returns:
            Dict with market insights including absorption rates, expenses, trends
        """
        insights = {
            "location": f"{city}, {state}" if city else state,
            "absorption_data": None,
            "rental_expenses": None,
            "data_year": 2021,
            "has_data": False
        }
        
        # Fetch absorption data
        absorption = self.get_absorption_data(state)
        if absorption:
            insights["absorption_data"] = absorption
            insights["has_data"] = True
        
        # Fetch rental expenses
        expenses = self.get_rental_expenses(state, year=2021)
        if expenses:
            insights["rental_expenses"] = expenses
            insights["has_data"] = True
        
        return insights
    
    def format_market_insights(self, insights: Dict[str, Any]) -> str:
        """
        Format market insights for user display
        
        Args:
            insights: Market insights dict from get_market_insights()
            
        Returns:
            Formatted markdown string
        """
        if not insights.get("has_data"):
            return ""
        
        output = f"\n\n## 📊 Market Insights for {insights['location']}\n\n"
        
        # Absorption data
        if insights.get("absorption_data"):
            absorption = insights["absorption_data"]
            output += "**Market Absorption** (Multifamily Units):\n"
            
            if "absorption_3mo" in absorption:
                output += f"- 3-month absorption: {absorption['absorption_3mo']}%\n"
            if "absorption_6mo" in absorption:
                output += f"- 6-month absorption: {absorption['absorption_6mo']}%\n"
            if "absorption_12mo" in absorption:
                output += f"- 12-month absorption: {absorption['absorption_12mo']}%\n"
            
            if "median_rent" in absorption:
                output += f"- Median rent: ${absorption['median_rent']}/month\n"
            
            output += "\n"
        
        # Rental expenses
        if insights.get("rental_expenses"):
            expenses = insights["rental_expenses"]
            output += "**Rental Market Data**:\n"
            
            if "estimate_properties" in expenses:
                output += f"- Rental properties: {expenses['estimate_properties']:,}\n"
            if "estimate_units" in expenses:
                output += f"- Rental units: {expenses['estimate_units']:,}\n"
            
            output += f"\n*Data source: US Census Bureau ({insights['data_year']})*\n"
        
        return output
    
    def get_city_coordinates(self, city: str, state: str, year: int = 2023) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude for a city using GEOINFO dataset
        
        Args:
            city: City name
            state: State abbreviation
            year: Year (2020 or 2023)
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        cache_key = f"geoinfo:{city}:{state}:{year}"
        cached = self._get_cached(cache_key)
        if cached:
            return (cached.get("lat"), cached.get("lon"))
        
        fips = self._get_state_fips(state)
        if not fips:
            return None
        
        try:
            url = self.BASE_URL_GEOINFO.format(year=year)
            
            # Query for place (city) geography
            params = {
                "get": "NAME,INTPTLAT,INTPTLON",  # Internal point lat/lon
                "for": f"place:*",
                "in": f"state:{fips}",
                "key": self.API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Find matching city
                for row in data[1:]:  # Skip header row
                    name = row[0]
                    if city.lower() in name.lower():
                        lat = float(row[1])
                        lon = float(row[2])
                        
                        # Cache the result
                        self._set_cache(cache_key, {"lat": lat, "lon": lon})
                        return (lat, lon)
                
                print(f"[Census API] City '{city}' not found in GEOINFO")
                return None
            else:
                print(f"[Census API] GEOINFO request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[Census API] Error fetching GEOINFO data: {e}")
            return None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in miles
        """
        # Earth radius in miles
        R = 3959.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        distance = R * c
        return distance
    
    def get_demographic_data(self, state: str, year: int = 2024, period: int = 1) -> Optional[Dict]:
        """
        Get demographic data from American Community Survey (ACS)
        
        Args:
            state: State abbreviation
            year: Year (default 2024)
            period: ACS period (1 = 1-year, 5 = 5-year)
            
        Returns:
            Dict with demographic data or None if error
        """
        cache_key = f"acs:{state}:{year}:{period}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        fips = self._get_state_fips(state)
        if not fips:
            return None
        
        try:
            url = self.BASE_URL_ACS.format(year=year, period=period)
            
            # Get population and demographic data
            params = {
                "get": "NAME,group(B01001)",  # Population by age and sex
                "for": f"state:{fips}",
                "key": self.API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = self._parse_acs_response(data)
                self._set_cache(cache_key, result)
                return result
            else:
                print(f"[Census API] ACS request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[Census API] Error fetching ACS data: {e}")
            return None
    
    def _parse_acs_response(self, data: List) -> Dict:
        """Parse ACS API response"""
        if not data or len(data) < 2:
            return {}
        
        headers = data[0]
        values = data[1]
        
        result = {}
        for i, header in enumerate(headers):
            if i < len(values):
                result[header.lower()] = values[i]
        
        return result


# Singleton instance
census_client = CensusAPIClient()


if __name__ == "__main__":
    # Test the Census API client
    print("=== Testing Census API Client ===\n")
    
    # Test SOMA data
    print("1. Testing SOMA (Market Absorption) for Texas:")
    absorption = census_client.get_absorption_data("TX")
    print(f"   Result: {absorption}\n")
    
    # Test RHFS data
    print("2. Testing RHFS (Rental Expenses) for California:")
    expenses = census_client.get_rental_expenses("CA", year=2021)
    print(f"   Result: {expenses}\n")
    
    # Test market insights
    print("3. Testing Market Insights for Dallas, TX:")
    insights = census_client.get_market_insights("TX", "Dallas")
    formatted = census_client.format_market_insights(insights)
    print(formatted)
    
    # Test GEOINFO geocoding
    print("\n4. Testing GEOINFO Geocoding for Dallas, TX:")
    coords = census_client.get_city_coordinates("Dallas", "TX")
    print(f"   Coordinates: {coords}")
    
    # Test distance calculation
    if coords:
        print("\n5. Testing Distance Calculation:")
        # Dallas to Fort Worth (approx 32 miles)
        dallas_coords = coords
        fortworth_coords = (32.7555, -97.3308)
        distance = census_client.calculate_distance(
            dallas_coords[0], dallas_coords[1],
            fortworth_coords[0], fortworth_coords[1]
        )
        print(f"   Dallas to Fort Worth: {distance:.2f} miles")
    
    # Test ACS demographic data
    print("\n6. Testing ACS Demographic Data for Texas:")
    demographics = census_client.get_demographic_data("TX", year=2024)
    print(f"   Result: {demographics}")

