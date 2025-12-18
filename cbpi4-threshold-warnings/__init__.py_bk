
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.config import ConfigType
import requests
import json #FIXME: Remove

logger = logging.getLogger(__name__)

brewfather_url = "http://log.brewfather.net/stream"
brewfather_id = None
brewfather_ext_temp = None

class CustomSensor(CBPiExtension):
    
    def __init__(self,cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.run())

    async def run(self):
        plugin = await self.cbpi.plugin.load_plugin_list("cbpi4-brewfather")
        self.version=plugin[0].get("Version","0.0.0")
        self.name=plugin[0].get("Name","cbpi4-brewfather")

        self.brewfather_update = self.cbpi.config.get(self.name+"_update", None)

        logger.info('Starting Brewfather background task')
        print('Starting Brewfather background task')

        await asyncio.sleep(5)
        while True:
            await self.brewfather_settings()

            if brewfather_id is None or brewfather_id == "" or not brewfather_id:
                logger.warning('Check Brewfather Stream ID is set')
                await asyncio.sleep(60)
                continue
            
            logger.info("Start")
            aux_temp = None
            ext_temp = None
            self.PRESSURE_UNIT = self.cbpi.config.get("PRESSURE_UNIT", "kPa").upper()
            self.TEMP_UNIT = self.cbpi.config.get("TEMP_UNIT", "C").upper()
            temp_target = None
            device_state = None
            heater_state = None
            cooler_state = None

            values = {}
            for fermenter in self.cbpi.fermenter.data:
                logger.info("Fermenter")
                if fermenter.name == None or fermenter.name.strip() == "":
                    logger.warning("Fermenter does not have a name. Give the fermenter a name for brewfather plugin to work!")
                    continue
                
                values["name"] = fermenter.name

                logger.info("NAME")
                logger.info(fermenter.sensor)
                
                if brewfather_ext_temp != None and brewfather_ext_temp != "" and not brewfather_ext_temp:
                    values["ext_temp"] = brewfather_ext_temp
                
                try:
                    if fermenter.brewname != None and fermenter.brewname.strip() != "":
                        values["beer"] = fermenter.brewname
                except Exception as e:
                    logger.error("Error Temp: " + str(e))
                
                try:
                    if fermenter.target_temp != None and str(fermenter.target_temp).strip() != "":
                        values["temp_target"] = fermenter.target_temp
                        values["aux_temp"] = fermenter.target_temp
                except Exception as e:
                    logger.error("Error Temp: " + str(e))

                
                logger.info("MID")

                logger.info(fermenter.pressure_sensor)
                
                if fermenter.sensor != None and fermenter.sensor.strip() != "":
                    try:
                        logger.info(self.cbpi.sensor.get_sensor_value(fermenter.sensor))
                        temp = self.cbpi.sensor.get_sensor_value(fermenter.sensor).get("value")
                        if temp != None and temp != "":
                            values["temp"] = temp
                            values["temp_unit"] = self.TEMP_UNIT
                    except Exception as e:
                        logger.error("Error Temp: " + str(e))
                
                if fermenter.pressure_sensor != None and fermenter.pressure_sensor.strip() != "":
                    try:
                        logger.info(self.cbpi.sensor.get_sensor_value(fermenter.pressure_sensor))
                        pressure = self.cbpi.sensor.get_sensor_value(fermenter.pressure_sensor).get("value")
                        if pressure != None and pressure != "":
                            values["pressure"] = pressure
                            values["pressure_unit"] = self.PRESSURE_UNIT
                    except Exception as e:
                        logger.error("Error Pressure: " + str(e))
                
                logger.info("COOLER")
                logger.info(fermenter.cooler)
                if fermenter.cooler != None and fermenter.cooler.strip() != "":
                    try:
                        logger.info("COOLER")
                        cooler_actor = self.cbpi.actor.find_by_id(fermenter.cooler)
                        cooler_state = cooler_actor.instance.state
                    except Exception as e:
                        logger.error("COOLER ERROR: " + str(e))
                
                logger.info("HEATER")
                logger.info(fermenter.heater)
                if fermenter.heater != None and fermenter.heater.strip() != "":
                    logger.info("HEATER")
                    try:
                        heater_actor = self.cbpi.actor.find_by_id(fermenter.heater)
                        heater_state = heater_actor.instance.state
                    except Exception as e:
                        logger.error("HEATER ERROR: " + str(e))

                logger.info(cooler_state)
                logger.info(heater_state)

                if heater_state and not cooler_state:
                    values["device_state"] = "Heating"
                elif cooler_state and not heater_state:
                    values["device_state"] = "Cooling"
                elif cooler_state and heater_state:
                    values["device_state"] = "Heating and Cooling!!!"

                logger.info(json.dumps(values))

                logger.info("DONE")

                try:
                    queryString = {
                      "id": brewfather_id
                    }
                    
                    response = requests.post(brewfather_url, params=queryString, json=values)

                    if response.status_code != 200:
                        logger.error("Brewfather Error: Received unsuccessful response. Ensure Id is correct. HTTP Error Code: " + str(response.status_code))

                except BaseException as error:
                    logger.error("Brewfather Error: Unable to send message." + str(error))
                    pass

            await asyncio.sleep(900)
    
    async def brewfather_settings(self):
        global brewfather_id
        global brewfather_ext_temp

        brewfather_id = self.cbpi.config.get("brewfather_id", None)
        brewfather_ext_temp = self.cbpi.config.get("brewfather_ext_temp", None)

        if brewfather_id is None:
            logger.info("INIT Brewfather ID")
            try:
                await self.cbpi.config.add("brewfather_id", "", type=ConfigType.STRING, description="Brewfather Stream ID",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.brewfather_update == None or self.brewfather_update != self.version:
                try:                
                    await self.cbpi.config.add("brewfather_id", brewfather_id, type=ConfigType.STRING, description="Brewfather Stream ID",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if brewfather_ext_temp is None:
            logger.info("INIT Brewfather External Temp")
            try:
                await self.cbpi.config.add("brewfather_ext_temp", "", type=ConfigType.SENSOR, description="Brewfather External Temp Sensor",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.brewfather_update == None or self.brewfather_update != self.version:
                try:                
                    await self.cbpi.config.add("brewfather_ext_temp", brewfather_ext_temp, type=ConfigType.STRING, description="Brewfather External Temp Sensor",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if self.brewfather_update == None or self.brewfather_update != self.version:
            try:
                await self.cbpi.config.add(self.name+"_update", self.version, type=ConfigType.STRING, description="Grainfather Update Version",source="hidden")
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)


def setup(cbpi):
    cbpi.plugin.register("Brewfather", CustomSensor)
    pass
