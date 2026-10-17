import requests

BASE_URL = "https://api.worldbank.org/v2"

def fetch_indicator(indicator, year="2022"):
    url = f"{BASE_URL}/country/all/indicator/{indicator}"
    params = {
        "date": year,
        "format": "json",
        "per_page": 300
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(f"Unexpected API response for {indicator}")

    rows = payload[1] or []
    valid_rows = [row for row in rows if row.get("value") is not None]

    print(f"\nIndicator: {indicator}")
    print(f"Year: {year}")
    print(f"Valid observations: {len(valid_rows)}")

    if valid_rows:
        print("Example:", {
            "country": valid_rows[0]["country"]["value"],
            "country_code": valid_rows[0]["countryiso3code"],
            "value": valid_rows[0]["value"]
        })
    else:
        print("No non-missing observations returned.")

    return valid_rows


if __name__ == "__main__":
    male = fetch_indicator("SL.TLF.CACT.MA.ZS")
    female = fetch_indicator("SL.TLF.CACT.FE.ZS")

    if not male or not female:
        raise RuntimeError("At least one indicator returned no usable observations.")

    print("\nData-access probe completed successfully.")
