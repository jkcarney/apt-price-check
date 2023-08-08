import requests
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from persist import Apartment

# my current one is A8
TRACKED_APARTMENTS = ["S1", "A2", "A8", "A11", "A12", "A1D"]

# backend URL to the complexes graphQL endpoint
URL = "https://inventory.g5marketingcloud.com/graphql"


def main():
    req_date = datetime.datetime.now().date()
    # user-agent has to be set otherwise we get forbidden
    header = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0'
    }

    # This is the GraphQL query that has to go out
    # thanks chatgpt
    request_payload = {"operationName": "ApartmentComplex",
                       "variables": {
                            "locationUrn": "g5-cl-1kqc76wdwn-solaire-silver-spring",
                            "beds": [1],
                            "baths": [1],
                            "moveInDate": "",
                            "unitsLimit": 9
                       },

                       "query": """
                            query ApartmentComplex(
                              $floorplanId: Int,
                              $beds: [Int!],
                              $baths: [Float!],
                              $sqft: Int,
                              $startRate: Int,
                              $endRate: Int,
                              $floorplanGroupId: [Int!],
                              $amenities: [Int!],
                              $locationUrn: String!,
                              $moveInDate: String!,
                              $unitsLimit: Int,
                              $dateFlexibility: Int
                            ) {
                              apartmentComplex(locationUrn: $locationUrn) {
                                floorplans(
                                  id: $floorplanId,
                                  beds: $beds,
                                  baths: $baths,
                                  sqft: $sqft,
                                  startRate: $startRate,
                                  endRate: $endRate,
                                  floorplanGroupId: $floorplanGroupId,
                                  amenities: $amenities,
                                  moveInDate: $moveInDate,
                                  dateFlexibility: $dateFlexibility
                                ) {
                                  id
                                  altId
                                  externalIds
                                  name
                                  totalAvailableUnits
                                  unitsAvailableByFilters(
                                    moveInDate: $moveInDate,
                                    dateFlexibility: $dateFlexibility,
                                    amenities: $amenities,
                                    minPrice: $startRate,
                                    maxPrice: $endRate,
                                    limit: $unitsLimit
                                  )
                                  allowableMoveInDays
                                  beds
                                  baths
                                  sqft
                                  sqftDisplay
                                  rateDisplay
                                  startingRate
                                  endingRate
                                  locationCode
                                  virtualImageUrl
                                  depositDisplay
                                  floorplanGroupIds
                                  brochurePdf
                                  hasSpecials
                                  floorplanSpecials {
                                    id
                                    name
                                    __typename
                                  }
                                  floorplanAmenities {
                                    id
                                    name
                                    __typename
                                  }
                                  floorplanCta {
                                    name
                                    url
                                    actionType
                                    redirectUrl
                                    redirectUrlActionType
                                    ownerType
                                    vendorKey
                                    redirectVendorKey
                                    isExternal
                                    __typename
                                  }
                                  __typename
                                }
                                floorplanFilters {
                                  beds
                                  baths
                                  sqftMax
                                  sqftMin
                                  lastAvailableDate
                                  floorplanGroups {
                                    id
                                    description
                                    __typename
                                  }
                                  amenities {
                                    id
                                    name
                                    __typename
                                  }
                                  __typename
                                }
                                __typename
                              }
                            }
                                    
                       """}

    # send post (it has to be a post)
    body = requests.post(URL, headers=header, json=request_payload)
    floorplans = body.json()['data']['apartmentComplex']['floorplans']

    # Create the engine for SQLAlchemy
    engine = create_engine('sqlite:///prices.db', echo=True)
    Apartment.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # iterate through the floorplans
    for floorplan in floorplans:
        name = floorplan["name"]
        # if the apartment isnt one we care about dont track it
        if name not in TRACKED_APARTMENTS:
            continue
        rate = floorplan["startingRate"]
        # construct new apartment object with info
        apt = Apartment(current_date=req_date, identifier_name=name, price=rate)
        session.add(apt)

    # commit all the stuff and close
    session.commit()
    session.close()


if __name__ == "__main__":
    main()
