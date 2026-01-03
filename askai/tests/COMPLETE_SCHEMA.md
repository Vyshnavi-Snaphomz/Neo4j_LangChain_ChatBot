# Complete Neo4j Property Schema (Zillow Data)

## Core Property Information

```python
Property {
    # Identifiers
    zpid: Integer,                    # Zillow Property ID
    parcelId: String,                 # "085650012000"
    
    # Address
    streetAddress: String,            # "137 N Marcin St"
    city: String,                     # "Visalia"
    state: String,                    # "CA"
    zipcode: String,                  # "93291"
    county: String,                   # "Tulare County"
    countyID: Integer,                # 1442
    countyFIPS: Integer,              # 6107
    country: String,                  # "USA"
    abbreviatedAddress: String,       # "137 N Marcin St"
    
    # Location
    latitude: Float,                  # 36.32977
    longitude: Float,                 # -119.363230
    timeZone: String,                 # "America/Los_Angeles"
    
    # Property Details
    bedrooms: Integer,                # 4
    bathrooms: Float,                 # 2.0
    livingArea: Integer,              # 1748 sqft
    livingAreaValue: Integer,         # 1748
    livingAreaUnits: String,          # "Square Feet"
    livingAreaUnitsShort: String,     # "sqft"
    
    # Lot Information
    lotSize: Integer,                 # 6577 sqft
    lotAreaValue: Float,              # 6577.0
    lotAreaUnits: String,             # "Square Feet"
    
    # Property Type
    homeType: String,                 # "SINGLE_FAMILY"
    homeStatus: String,               # "OTHER", "FOR_SALE", "SOLD", "RECENTLY_SOLD"
    propertyTypeDimension: String,    # "Single Family"
    listingTypeDimension: String,     # "Unknown Listed By"
    hdpTypeDimension: String,         # "Zestimate"
    
    # Pricing
    price: Float,                     # 441800
    currency: String,                 # "USD"
    lastSoldPrice: Integer,           # 225000
    dateSold: DateTime,               # 2014-03-20T00:00:00Z
    dateSoldString: String,           # "2014-03-20T00:00:00Z"
    
    # Zestimate
    zestimate: Integer,               # 441800
    zestimateLowPercent: Integer,     # 5
    zestimateHighPercent: Integer,    # 5
    zestimateMinus30: Integer,        # 444467
    rentZestimate: Integer,           # 2361
    
    # Redfin Estimate
    restimateLowPercent: Integer,     # 5
    restimateHighPercent: Integer,    # 5
    restimateMinus30: Boolean,        # false
    
    # Tax Information
    taxAssessedValue: Integer,        # 275818
    taxAssessedYear: Integer,         # 2025
    propertyTaxRate: Float,           # 1.09
    taxHistory: String,               # JSON array
    
    # Construction
    yearBuilt: Integer,               # 2009
    
    # Interior Details
    interior: String,                 # JSON with bedrooms_and_bathrooms, flooring, heating, other_interior_features
    interior_full: String,            # JSON array with detailed interior info
    
    # Description
    description: String,              # Full property description text
    
    # URLs & Media
    url: String,                      # "https://www.zillow.com/homedetails/..."
    hdpUrl: String,                   # "/homedetails/137-N-Marcin-St-Visalia-CA-93291/95066206_zpid/"
    listingUrl: String,               # Full listing URL
    photos: String,                   # JSON array of photo URLs
    photoCount: Integer,              # 16
    hasPublicVideo: Boolean,          # false
    has_3d_tour: Boolean,             # false
    
    # Listing Information
    daysOnZillow: Integer,            # 4268
    days_on_zillow: Integer,          # 4268
    isOffMarket: Boolean,             # false
    tags: String,                     # JSON array ["Off market"]
    priceHistory: String,             # JSON array of price changes
    
    # Nearby Information
    nearbyHomes: String,              # JSON array of nearby properties
    nearbyNeighborhoods: String,      # JSON array
    nearbyCities: String,             # JSON array
    nearbyZipcodes: String,           # JSON array
    
    # Schools
    schools: String,                  # JSON array with school info
    
    # Additional Details
    property: String,                 # JSON array with parking, features, lot, details
    construction: String,             # JSON array with type, materials, condition
    utilities: String,                # JSON array "[]"
    financial: String,                # JSON array
    community_details: String,        # JSON array
    hoa_details: String,              # JSON with HOA info
    
    # Climate & Transportation
    climate_risks: String,            # JSON with air, fire, flood, heat, wind factors
    getting_around: String,           # JSON with bike, transit, walk scores
    getting_around_scores: String,    # JSON with numeric scores
    
    # Search & Display
    citySearchUrl: String,            # JSON with path and text
    overview: String,                 # JSON with days_on_zillow
    
    # Flags & Status
    isUndisclosedAddress: Boolean,    # false
    isZillowOwned: Boolean,           # false
    isFeatured: Boolean,              # false
    is_showcased: Boolean,            # false
    isPremierBuilder: Boolean,        # false
    isHousingConnector: Boolean,      # false
    isInstantOfferEnabled: String,    # "No"
    isRentalsLeadCapMet: Boolean,     # false
    isRentalListingOffMarket: Boolean, # false
    isNonOwnerOccupied: Boolean,      # false
    hideZestimate: Boolean,           # false
    checked: Boolean,                 # true
    tourViewCount: Boolean,           # false
    hasApprovedThirdPartyVirtualTourUrl: Boolean, # false
    
    # User-specific
    isVerifiedClaimedByCurrentSignedInUser: String,      # "No"
    isCurrentSignedInUserVerifiedOwner: Boolean,         # false
    isListingClaimedByCurrentSignedInUser: Boolean,      # false
    isCurrentSignedInAgentResponsible: Boolean,          # false
    is_listed_by_management_company: Boolean,            # false
    
    # Rental
    rentalApplicationsAcceptedType: String,  # "REQUEST_TO_APPLY"
    selfTour: String,                        # JSON with hasSelfTour
    
    # Listing Provider
    listing_provided_by: String,             # JSON with company, email, name, phone
    listingDataSource: String,               # "Legacy"
    
    # Mortgage
    mortgageRates: String,                   # JSON with thirtyYearFixedRate
    
    # Home Valuation
    homeValuation: String,                   # JSON with comparables
    
    # Embeddings
    embedding_text: String,                  # "Visalia CA 441800 4 beds 2.0 baths"
    embedding: Vector                        # 1536-dimensional vector
}
```

## Key Fields for Search & Display

### Essential Display Fields:
- `price`, `bedrooms`, `bathrooms`
- `streetAddress`, `city`, `state`, `zipcode`
- `livingArea`, `lotSize`
- `yearBuilt`, `homeType`
- `description` ⭐ **Rich text description**
- `url`, `photos`

### Search/Filter Fields:
- `price`, `bedrooms`, `bathrooms`
- `city`, `state`, `zipcode`, `county`
- `livingArea`, `lotSize`
- `homeStatus`, `homeType`
- `yearBuilt`
- `description` ⭐ **For keyword search**

### Additional Rich Data:
- `schools` - School ratings and info
- `nearbyHomes` - Comparable properties
- `priceHistory` - Historical pricing
- `taxHistory` - Tax assessment history
- `interior` - Detailed interior features
- `climate_risks` - Environmental factors
- `getting_around_scores` - Walk/bike/transit scores

## Example Description Field:

```
"We have a lovely home in a great neighborhood supported by a great school district. 
We have recently installed new floors, have updated the paint through out the interior 
home, new base boards and trim as well as blinds all installed. The front and back 
yard are landscaped as well as concrete walkway on the south side of the home, 
extended patio as well as a concrete slab to the north side of the home with a nice 
clean tough shed installed which provides the perfect place to store extra items..."
```

This field is **perfect** for keyword searches like "aesthetic", "countryside", "modern", "luxury", etc.!
