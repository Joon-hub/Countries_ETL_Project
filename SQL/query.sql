-- SQL queries for data querying and analysis on the country database

-- Query 1: Find all countries in Asia with a population greater than 100 million.
SELECT
    name,
    population
FROM
    country
WHERE
    region = 'Asia' AND population > 100000000;

-- Query 2: List currencies used in European countries.

SELECT DISTINCT
    cur.name,
    cur.symbol
FROM
    currency cur
JOIN
    country_currency cc ON cur.id = cc.currency_id
JOIN
    country c ON cc.country_id = c.id
WHERE
    c.region = 'Europe';

-- Query 3: Count the countries which uses multiple currencies.

SELECT
    c.name, c.region,
    COUNT(*) as no_of_currencies
FROM
    country c
JOIN
    country_currency cc ON c.id = cc.country_id
GROUP BY
    c.id
HAVING
    COUNT(*) > 1;