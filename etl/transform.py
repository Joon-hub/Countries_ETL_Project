import logging

# Transformation -----
    
def transform_country_data(raw_data):
    """
    Transforms the raw API data into a format suitable for the database schema.
    """
    logging.info("starting data transformation")
    transformed = {
        'countries':[],
        'currencies':{},
        'languages':{},
        'country_currency':[],
        'country_language':[]
    }

    for country in raw_data:
        cca2 = country['cca2']
        if not cca2: # skip contries without a valid cca2 code
            logging.warning(f"Skipping country with missing cca2: {country.get('name', {}).get('common', 'Unknown')}")
            continue

        name = country.get('name', {}).get('common')
        capital = country.get('capital', [None])[0] # Take the first capital if available
        region = country.get('region')
        subregion = country.get('subregion')
        population = country.get('population')
        area = country.get('area')

        transformed['countries'].append({
            'cca2': cca2,
            'name': name,
            'capital': capital,
            'region': region,
            'subregion': subregion,
            'population': population,
            'area': area
        })

        # Process currencies 
        currencies = country.get('currencies', {})
        for code, details in currencies.items():
            currency_name = details.get('name')
            currency_symbol = details.get('symbol')

            if code and currency_name: # Ensure code and name are present
                # Add to unique currencies dictionary if not already present
                if code not in transformed['currencies']:
                    transformed['currencies'][code] = {'code': code,'name': currency_name,'symbol': currency_symbol}

                # Add entry for country_currency junction table (uses cca2 for now, will link by ID later)
                transformed['country_currency'].append({'country_cca2': cca2, 'currency_code': code})


        # Process language
        # columns in languages are code, name
        languages = country.get('languages', {})
        for code, name in languages.items():
            if code and name: # Ensure code and name are present
                # Add to unique languages dictionary if not already present
                if code not in transformed['languages']:
                    transformed['languages'][code] = {'code': code, 'name': name}

                # Add entry for country_language junction table (uses cca2 for now, will link by ID later)
                transformed['country_language'].append({'country_cca2': cca2, 'language_code': code})

    # Convert unique currency and language dictionaries back to lists of dictionaries
    transformed['currencies'] = list(transformed['currencies'].values())
    transformed['languages'] = list(transformed['languages'].values())

    logging.info(f"Transformation complete. Found {len(transformed['countries'])} countries, {len(transformed['currencies'])} unique currencies, and {len(transformed['languages'])} unique languages.")
    return transformed
