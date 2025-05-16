DROP TABLE IF EXISTS country_currency;
DROP TABLE IF EXISTS country_language;
DROP TABLE IF EXISTS country;
DROP TABLE IF EXISTS currency;
DROP TABLE IF EXISTS language;

-- create the 'country' table
CREATE TABLE country (
    id SERIAL PRIMARY KEY,  -- AUTO INCREMENT PRIMARY KEY
    cca2 VARCHAR(3) UNIQUE NOT NULL, -- Alpha-3 code
    name VARCHAR(255) NOT NULL,
    capital VARCHAR(255),
    region VARCHAR(255),
    subregion VARCHAR(255),
    population BIGINT,
    area DECIMAL -- in km^2
);

-- create the 'currency' table
CREATE TABLE currency (
    id SERIAL PRIMARY KEY,  -- AUTO INCREMENT PRIMARY KEY
    code VARCHAR UNIQUE NOT NULL, -- Currency code
    name VARCHAR NOT NULL, -- currency name
    symbol VARCHAR
);

-- create the 'language' table
CREATE TABLE language (
    id SERIAL PRIMARY KEY,  -- AUTO INCREMENT PRIMARY KEY
    code VARCHAR UNIQUE NOT NULL, -- Language code
    name VARCHAR NOT NULL -- Language name
);

-- create the 'country_currency' junction table many-to-many relationship
CREATE TABLE country_currency (
    country_id INT NOT NULL REFERENCES country(id) ON DELETE CASCADE, -- foreign key and cascade delete means if a country is deleted, its currencies will also be deleted
    currency_id INT NOT NULL REFERENCES currency(id) ON DELETE CASCADE,
    PRIMARY KEY (country_id, currency_id)  -- composite primary key to ensure unique relationships
);

-- create the 'country_language' junction table many-to-many relationship
CREATE TABLE country_language (
    country_id INT NOT NULL REFERENCES country(id) ON DELETE CASCADE, 
    language_id INT NOT NULL REFERENCES language(id) ON DELETE CASCADE,
    PRIMARY KEY (country_id, language_id) 
);

-- create indexes for faster querying
CREATE INDEX idx_country_currency_country_id ON country_currency(country_id);
CREATE INDEX idx_country_currency_currency_id ON country_currency(currency_id);
CREATE INDEX idx_country_language_country_id ON country_language(country_id);
CREATE INDEX idx_country_language_language_id ON country_language(language_id);


-- Adding comments to table
COMMENT ON TABLE country IS 'Stores information about countries.';
COMMENT ON TABLE currency IS 'Stores information about currencies.';
COMMENT ON TABLE language IS 'Stores information about languages.';
COMMENT ON TABLE country_currency IS 'Stores the many-to-many relationship between countries and currencies.';
COMMENT ON TABLE country_language IS 'Stores the many-to-many relationship between countries and languages.';
