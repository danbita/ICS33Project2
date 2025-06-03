from collections import namedtuple
from p2app.events import Country, CountrySavedEvent, CountryLoadedEvent, SaveCountryFailedEvent

Country = namedtuple('Country', ['country_id', 'country_code', 'name', 'continent_id',
                                 'wikipedia_link', 'keywords'])

def search_country(connection, country_code, name):
    """method for searching countries"""
    cursor = None
    if country_code and name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM country
            WHERE country_code = ? AND name = ?
            ''', (country_code, name)
        )
    elif country_code and not name:
        cursor = connection.execute(
            '''
            SELECT *
            From country
            WHERE country_code = ?
            ''', (country_code,)
        )
    elif not country_code and name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM country
            WHERE name = ?
            ''', (name,)
        )
    for data in cursor.fetchall():
        yield Country(*data)

def save_new_country(connection, country):
    """method for saving new country"""
    if not country.country_code or not country.name or country.continent_id is None:
        return SaveCountryFailedEvent('You are missing a required field')
    else:
        connection.execute(
            '''
            INSERT INTO country (country_code, name ,continent_id , wikipedia_link , keywords) VALUES (?, ?, ?, ?, ?)
            ''', (country.country_code, country.name, country.continent_id, country.wikipedia_link, country.keywords)
        )
        connection.commit()
        cursor = connection.execute(
            '''
            SELECT *
            FROM country
            WHERE country_code = ? AND name = ? AND continent_id = ? AND wikipedia_link = ? AND keywords = ?
            ''', (country.country_code, country.name, country.continent_id, country.wikipedia_link, country.keywords)
        )
        data = cursor.fetchone()
        return CountrySavedEvent(Country(*data))

def modify_country(connection, country):
    """method for modifying country"""
    if not country.country_code or not country.name or country.continent_id is None:
        return SaveCountryFailedEvent('You are missing a required field')
    connection.execute(
        '''
        UPDATE country
        SET country_code = ?, name = ?, continent_id = ?, wikipedia_link = ?, keywords = ?
        WHERE country_id = ?
        ''', (country.country_code, country.name, country.continent_id, country.wikipedia_link, country.keywords, country.country_id)
    )
    connection.commit()
    cursor = connection.execute(
        '''
        SELECT *
        FROM country
        WHERE country_id = ?
        ''', (country.country_id,)
    )
    data = cursor.fetchone()
    return CountrySavedEvent(Country(*data))

def load_country(connection, country_id):
    """method for loading a country"""
    cursor = None
    if country_id:
        cursor = connection.execute(
            '''
            SELECT *
            FROM country
            WHERE country_id = ?
            ''', (country_id,)
        )
    for data in cursor.fetchall():
        yield Country(*data)