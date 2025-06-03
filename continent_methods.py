from collections import namedtuple
from p2app.events import SaveContinentFailedEvent, ContinentSavedEvent, ContinentLoadedEvent

Continent = namedtuple('Continent', ['continent_id', 'continent_code', 'name'])

def search_continent(connection, continent_code, name):
    """method for searching continents"""
    cursor = None
    if continent_code and name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM continent
            WHERE continent_code = ? AND name = ?
            ''', (continent_code, name)
        )
    elif continent_code and not name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM continent
            WHERE continent_code = ?
            ''', (continent_code, )
        )
    elif not continent_code and name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM continent
            WHERE name = ?
            ''', (name,)
        )

    for data in cursor.fetchall():
        yield Continent(*data)

def save_new_continent(connection, continent):
    """method for saving new continent"""
    if continent.continent_code == '' or continent.name == '':
        return SaveContinentFailedEvent('You are missing a required field')
    else:
        connection.execute(
            '''
            INSERT INTO continent (continent_code, name) VALUES (?, ?)
            ''', (continent.continent_code, continent.name)
        )
        connection.commit()
        cursor = connection.execute(
            '''
            SELECT *
            FROM continent
            WHERE continent_code = ? AND name = ?  
            ''', (continent.continent_code, continent.name)
        )
        data = cursor.fetchone()
        return ContinentSavedEvent(Continent(*data))

def modify_continent(connection, continent):
    """method for modifying continent"""
    if continent.continent_code is None or continent.name is None:
        return SaveContinentFailedEvent('Missing a required field')
    else:
        connection.execute(
            '''
            UPDATE continent
            SET continent_code = ?, name = ?
            WHERE continent_id = ?
            ''', (continent.continent_code, continent.name, continent.continent_id)
        )
        connection.commit()
        cursor = connection.execute(
            '''
            SELECT *
            FROM continent
            WHERE continent_id = ?
            ''', (continent.continent_id,)
        )
        data = cursor.fetchone()
        return ContinentSavedEvent(Continent(*data))

def load_continent(connection, continent_id):
    """method for loading a continent"""
    cursor = None
    if continent_id:
        cursor = connection.execute(
            '''
            SELECT *
            FROM continent
            WHERE continent_id = ?
            ''', (continent_id,)
        )
        for data in cursor.fetchall():
            yield Continent(*data)
