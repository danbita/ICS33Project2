from collections import namedtuple
from p2app.events import SaveRegionFailedEvent, SaveRegionEvent, SaveNewRegionEvent, \
    RegionSavedEvent


Region = namedtuple('Region', ['region_id', 'region_code', 'local_code',
                               'name', 'continent_id', 'country_id', 'wikipedia_link', 'keywords'])


def search_region(connection, region_code, local_code, name):
    """method for searching regions"""
    cursor = None
    if region_code and local_code and name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE region_code = ? AND local_code = ? AND name = ?
            ''', (region_code, local_code, name)
        )
    elif region_code and local_code and not name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE region_code = ? AND local_code = ?
            ''', (region_code, local_code)
        )
    elif region_code and not local_code and name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE region_code = ? AND name = ?
            ''', (region_code, name)
        )
    elif not region_code and local_code and name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE local_code = ? AND name = ?
            ''', (local_code, name)
        )
    elif region_code and not local_code and not name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE region_code = ?
            ''', (region_code,)
        )
    elif not region_code and local_code and not name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE local_code = ?
            ''', (local_code,)
        )
    elif not region_code and not local_code and name:
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE name = ?
            ''', (name,)
        )

    for data in cursor.fetchall():
        yield Region(*data)


def save_new_region(connection, region):
    """method for saving new region"""
    if not region.local_code or not region.name or region.continent_id is None or region.country_id is None:
        return SaveRegionFailedEvent('You are missing a required field')
    else:
        connection.execute(
            '''
            INSERT INTO region (region_code, local_code, name ,continent_id ,country_id, wikipedia_link , keywords) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (region.region_code, region.local_code, region.name, region.continent_id,
              region.country_id, region.wikipedia_link, region.keywords))
        connection.commit()
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE region_code = ? and local_code = ? and name = ? and continent_id = ? and  country_id = ? and wikipedia_link  = ? and keywords = ?

            ''', (region.region_code, region.local_code, region.name, region.continent_id,
                  region.country_id, region.wikipedia_link, region.keywords)
        )

        data = cursor.fetchone()
        return RegionSavedEvent(Region(*data))


def modify_region(connection, region):
    """method for modifying a region"""
    connection.execute(
        '''
        UPDATE region
        SET region_code = ?, local_code = ?, name = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ?
        WHERE region_id = ?
        ''',
        (region.region_code, region.local_code, region.name, region.continent_id, region.country_id,
         region.wikipedia_link, region.keywords, region.region_id)
    )
    connection.commit()
    cursor = connection.execute(
        '''
        SELECT *
        FROM region
        WHERE region_id = ?
        ''',
        (region.region_id,)
    )
    data = cursor.fetchone()
    return RegionSavedEvent(Region(*data))


def load_region(connection, region_id):
    """method for loading a region"""
    cursor = None
    if region_id:
        cursor = connection.execute(
            '''
            SELECT *
            FROM region
            WHERE region_id = ?
            ''', (region_id,)
        )
    for data in cursor.fetchall():
        yield Region(*data)
