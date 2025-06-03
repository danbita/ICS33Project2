# p2app/engine/main.py
#
# ICS 33 Spring 2025
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.

import sqlite3
from p2app.events.app import ErrorEvent, QuitInitiatedEvent, EndApplicationEvent
from p2app.events.continents import StartContinentSearchEvent, ContinentSearchResultEvent, LoadContinentEvent, \
    ContinentLoadedEvent, SaveNewContinentEvent, SaveContinentEvent, ContinentLoadedEvent, SaveContinentFailedEvent
from p2app.events.countries import StartCountrySearchEvent, CountrySearchResultEvent, LoadCountryEvent, CountryLoadedEvent, \
    SaveNewCountryEvent, SaveCountryEvent, CountrySavedEvent, CountryLoadedEvent, SaveCountryFailedEvent
from p2app.events.database import OpenDatabaseEvent, CloseDatabaseEvent, DatabaseOpenedEvent, \
    DatabaseClosedEvent, DatabaseOpenFailedEvent
from p2app.events.event_bus import EventBus
from p2app.events.regions import StartRegionSearchEvent, RegionSearchResultEvent, LoadRegionEvent, RegionLoadedEvent, \
    SaveNewRegionEvent, SaveRegionEvent, RegionSavedEvent, SaveRegionFailedEvent
from p2app.views.event_handling import EventHandler
from p2app.engine.region_methods import search_region, save_new_region, modify_region, load_region
from p2app.engine.continent_methods import search_continent, save_new_continent, modify_continent, load_continent
from p2app.engine.country_methods import search_country, save_new_country, modify_country, load_country


class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self._connection = None

    def process_event(self, event):
        """Processes a single event sent from the UI, yielding zero or more events in response."""
        try:
            # Application-level events
            if type(event) is QuitInitiatedEvent:
                yield EndApplicationEvent()

            elif type(event) is OpenDatabaseEvent:
                self._connection = sqlite3.connect(event.path())
                self._connection.execute("PRAGMA foreign_keys = ON;")
                yield DatabaseOpenedEvent(event.path())

            elif type(event) is CloseDatabaseEvent:
                self._connection.close()
                yield DatabaseClosedEvent()

            # Region-related events
            elif type(event) is StartRegionSearchEvent:
                for region in search_region(self._connection, event.region_code(),
                                            event.local_code(), event.name()):
                    yield RegionSearchResultEvent(region)

            elif type(event) is LoadRegionEvent:
                for region in load_region(self._connection, event.region_id()):
                    yield RegionLoadedEvent(region)

            elif type(event) is SaveNewRegionEvent:
                new_reg = save_new_region(self._connection, event.region())
                yield new_reg

            elif type(event) is SaveRegionEvent:
                modify_reg = modify_region(self._connection, event.region())
                yield RegionSavedEvent(modify_reg)

            # Continent-related events
            elif type(event) is StartContinentSearchEvent:
                for continent in search_continent(self._connection, event.continent_code(),
                                                  event.name()):
                    yield ContinentSearchResultEvent(continent)

            elif type(event) is LoadContinentEvent:
                for continent in load_continent(self._connection, event.continent_id()):
                    yield ContinentLoadedEvent(continent)

            elif type(event) is SaveNewContinentEvent:
                new_cont = save_new_continent(self._connection, event.continent())
                yield new_cont

            elif type(event) is SaveContinentEvent:
                modify_cont = modify_continent(self._connection, event.continent())
                yield modify_cont

            # Country-related events
            elif type(event) is StartCountrySearchEvent:
                for country in search_country(self._connection, event.country_code(), event.name()):
                    yield CountrySearchResultEvent(country)

            elif type(event) is LoadCountryEvent:
                for country in load_country(self._connection, event.country_id()):
                    yield CountryLoadedEvent(country)

            elif type(event) is SaveNewCountryEvent:
                new_coun = save_new_country(self._connection, event.country())
                yield new_coun

            elif type(event) is SaveCountryEvent:
                modify_coun = modify_country(self._connection, event.country())
                yield CountrySavedEvent(modify_coun)

        except sqlite3.Error as error:
            yield ErrorEvent(str(error))
