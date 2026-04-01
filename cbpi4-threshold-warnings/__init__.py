
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.dataclasses import NotificationType

logger = logging.getLogger(__name__)


class CustomSensor(CBPiExtension):
    
    def __init__(self,cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.run())

    async def run(self):
        plugin = await self.cbpi.plugin.load_plugin_list("cbpi4-threshold-warnings")
        self.version=plugin[0].get("Version","0.0.0")
        self.name=plugin[0].get("Name","cbpi4-threshold-warnings")

        self.threshold_warnings_update = self.cbpi.config.get(self.name+"_update", None)

        logger.info('Starting Warnings background task')
        print('Starting Warnings background task')


        await asyncio.sleep(5)
        while True:
            await self.threshold_warnings_settings()

            PRESSURE_HW = self.cbpi.config.get("Threshold_Pressure_HW", None)
            PRESSURE_LW = self.cbpi.config.get("Threshold_Pressure_LW", None)
            TEMP_HW = self.cbpi.config.get("Threshold_Temp_HW", None)
            TEMP_LW = self.cbpi.config.get("Threshold_Temp_LW", None)
            TEMP_FERMENTER_DIV = self.cbpi.config.get("Threshold_Temp_Fermenter_DIV", None)
            PRESSURE_FERMENTER_DIV = self.cbpi.config.get("Threshold_Pressure_Fermenter_DIV", None)

            for fermenter in self.cbpi.fermenter.data:
                logger.info("Fermenter")

                print("FPP {} {}".format(fermenter, fermenter.name))
                #if not fermenter.state:
                #    continue

                fermenter_name = "<NO NAME>"
                if fermenter.name != None or fermenter.name.strip() != "":
                    fermenter_name = fermenter.name

                #print("NAME")
                #print(fermenter.sensor)
                #print("MID")
                #print(fermenter)
                #print(fermenter.target_pressure)
                
                if fermenter.sensor != None and fermenter.sensor.strip() != "":
                    try:
                        logger.info(self.cbpi.sensor.get_sensor_value(fermenter.sensor))
                        temp = self.cbpi.sensor.get_sensor_value(fermenter.sensor).get("value")
                        if temp != None and temp != "":
                            if TEMP_HW != None and TEMP_HW != "":
                                if float(temp) > float(TEMP_HW):
                                    self.cbpi.notify("Threshold Warning", "{}: Temp High Warning {}".format(fermenter_name, temp), NotificationType.ERROR)
                            if TEMP_LW != None and TEMP_LW != "":
                                if float(temp) < float(TEMP_LW):
                                    self.cbpi.notify("Threshold Warning", "{}: Temp Low Warning {}".format(fermenter_name, temp), NotificationType.ERROR)

                            try:
                                if fermenter.target_temp != None and str(fermenter.target_temp).strip() != "":
                                    if TEMP_FERMENTER_DIV != None and TEMP_FERMENTER_DIV != "":
                                        if abs(float(fermenter.target_temp) - float(temp)) > float(TEMP_FERMENTER_DIV):
                                            self.cbpi.notify("Threshold Warning", "{}: Fermenter Step Target Diviation Warning {} - Target: {}".format(fermenter_name, temp, fermenter.target_temp), NotificationType.WARNING)

                            except Exception as e:
                                logger.error("Error Temp: " + str(e))

                    except Exception as e:
                        logger.error("Error Temp: " + str(e))
                
                if fermenter.pressure_sensor != None and fermenter.pressure_sensor.strip() != "":
                    try:
                        logger.info(self.cbpi.sensor.get_sensor_value(fermenter.pressure_sensor))
                        pressure = self.cbpi.sensor.get_sensor_value(fermenter.pressure_sensor).get("value")
                        if pressure != None and pressure != "":
                            if PRESSURE_HW != None and PRESSURE_HW != "":
                                if float(pressure) > float(PRESSURE_HW):
                                    self.cbpi.notify("Threshold Warning", "{}: Pressure High Warning {}".format(fermenter_name, pressure), NotificationType.ERROR)
                            if PRESSURE_LW != None and PRESSURE_LW != "":
                                if float(pressure) < float(PRESSURE_LW):
                                    self.cbpi.notify("Threshold Warning", "{}: Pressure Low Warning {}".format(fermenter_name, pressure), NotificationType.ERROR)

                            try:
                                if fermenter.target_pressure != None and str(fermenter.target_pressure).strip() != "":
                                    if PRESSURE_FERMENTER_DIV != None and PRESSURE_FERMENTER_DIV != "":
                                        if abs(float(fermenter.target_pressure) - float(pressure)) > float(PRESSURE_FERMENTER_DIV):
                                            self.cbpi.notify("Threshold Warning", "{}: Fermenter Target Pressure Diviation Warning {} - Target: {}".format(fermenter_name, pressure, fermenter.target_pressure), NotificationType.WARNING)

                            except Exception as e:
                                logger.error("Error Pressure: " + str(e))

                    except Exception as e:
                        logger.error("Error Pressure: " + str(e))
                
                logger.info("DONE")

            await asyncio.sleep(900)
            #await asyncio.sleep(10)

    async def threshold_warnings_settings(self):
        PRESSURE_HW = self.cbpi.config.get("Threshold_Pressure_HW", None)
        PRESSURE_LW = self.cbpi.config.get("Threshold_Pressure_LW", None)
        TEMP_HW = self.cbpi.config.get("Threshold_Temp_HW", None)
        TEMP_LW = self.cbpi.config.get("Threshold_Temp_LW", None)
        TEMP_FERMENTER_DIV = self.cbpi.config.get("Threshold_Temp_Fermenter_DIV", None)
        PRESSURE_FERMENTER_DIV = self.cbpi.config.get("Threshold_Pressure_Fermenter_DIV", None)

        if PRESSURE_HW is None:
            logger.info("INIT Pressure HW")
            try:
                await self.cbpi.config.add("Threshold_Pressure_HW", "", type=ConfigType.NUMBER, description="Pressure High Warning",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.threshold_warnings_update == None or self.threshold_warnings_update != self.version:
                try:                
                    await self.cbpi.config.add("Threshold_Pressure_HW", PRESSURE_HW, type=ConfigType.NUMBER, description="Pressure High Warning",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if PRESSURE_LW is None:
            logger.info("INIT Pressure LW")
            try:
                await self.cbpi.config.add("Threshold_Pressure_LW", "", type=ConfigType.NUMBER, description="Pressure Low Warning",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.threshold_warnings_update == None or self.threshold_warnings_update != self.version:
                try:                
                    await self.cbpi.config.add("Threshold_Pressure_LW", PRESSURE_LW, type=ConfigType.NUMBER, description="Pressure Low Warning",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)




        if TEMP_HW is None:
            logger.info("INIT Temp HW")
            try:
                await self.cbpi.config.add("Threshold_Temp_HW", "", type=ConfigType.NUMBER, description="Temp High Warning",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.threshold_warnings_update == None or self.threshold_warnings_update != self.version:
                try:
                    await self.cbpi.config.add("Threshold_Temp_HW", TEMP_HW, type=ConfigType.NUMBER, description="Temp High Warning",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if TEMP_LW is None:
            logger.info("INIT Temp LW")
            try:
                await self.cbpi.config.add("Threshold_Temp_LW", "", type=ConfigType.NUMBER, description="Temp Low Warning",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.threshold_warnings_update == None or self.threshold_warnings_update != self.version:
                try:
                    await self.cbpi.config.add("Threshold_Temp_LW", TEMP_LW, type=ConfigType.NUMBER, description="Temp Low Warning",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)




        if TEMP_FERMENTER_DIV is None:
            logger.info("INIT Temp Fermenter DIV")
            try:
                await self.cbpi.config.add("Threshold_Temp_Fermenter_DIV", "", type=ConfigType.NUMBER, description="Temp Fermenter Target Diviation Warning",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.threshold_warnings_update == None or self.threshold_warnings_update != self.version:
                try:
                    await self.cbpi.config.add("Threshold_Temp_Fermenter_DIV", TEMP_FERMENTER_DIV, type=ConfigType.NUMBER, description="Temp Fermenter Target Diviation Warning",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if PRESSURE_FERMENTER_DIV is None:
            logger.info("INIT Pressure Fermenter DIV")
            try:
                await self.cbpi.config.add("Threshold_Pressure_Fermenter_DIV", "", type=ConfigType.NUMBER, description="Pressure Fermenter Target Diviation Warning",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.threshold_warnings_update == None or self.threshold_warnings_update != self.version:
                try:
                    await self.cbpi.config.add("Threshold_Pressure_Fermenter_DIV", PRESSURE_FERMENTER_DIV, type=ConfigType.NUMBER, description="Pressure Fermenter Target Diviation Warning",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)






        if self.threshold_warnings_update == None or self.threshold_warnings_update != self.version:
            try:
                await self.cbpi.config.add(self.name+"_update", self.version, type=ConfigType.STRING, description="Threshold Warnings Update Version",source="hidden")
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)


def setup(cbpi):
    cbpi.plugin.register("Threshold Warnings", CustomSensor)
    pass
