#!/usr/bin/env python
# This file is part of CERE.
#
# Copyright (c) 2013-2015, Universite de Versailles St-Quentin-en-Yvelines
#
# CERE is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# CERE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CERE.  If not, see <http://www.gnu.org/licenses/>.
import os
import argparse
import logging
import subprocess
import cere_configure
import errno
import common.variables as var

logger = logging.getLogger('Hybrid')

def init_module(subparsers, cere_plugins):
  cere_plugins["hybrid"] = run
  hybrid_parser = subparsers.add_parser("hybrid", help="test optimal optimization flags")
  hybrid_parser.add_argument('--regions-file', required=True, help="file to compile")
  hybrid_parser.add_argument('--extraction-lvl', default="loop", choices=["loop","function"], help="Extract region at loop or function granularity. Default is loop")
  hybrid_parser.add_argument('--noinstrumentation', action='store_true', help="Hybrid without instrumentation")

def run(args):
  if not cere_configure.init():
    return False

  args.regions_file = os.path.realpath(args.regions_file)
  if not os.path.isfile(cere_configure.cere_config["regions_infos"]):
    logger.error("No such file: {0}".format(cere_configure.cere_config["regions_infos"]))
    logger.error("Did you run cere regions?")
    return False

  #Check for instrumentation
  if args.noinstrumentation:
    instru_cmd = ""
    logger.info("Compiling hybrid binary without instrumentation")
  else:
    instru_cmd = "--instrument --wrapper={0}".format(var.RDTSC_WRAPPER)
    logger.info("Compiling hybrid binary with instrumentation")

  #Remove objects file
  try:
    os.remove(os.path.realpath("__cere__objects"))
  except OSError as e:
    if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
      raise #re-raise exception if a different error occured

  #Compile hybrid binary
  try:
    logger.debug(subprocess.check_output("{0} CERE_MODE=\"original --hybrid {1} --hybrid-regions={2} \
    --regions-infos={3} --cere-objects={4} --extraction-lvl={5}\" -B".format(cere_configure.cere_config["build_cmd"], instru_cmd, args.regions_file,\
    cere_configure.cere_config["regions_infos"], os.path.realpath("__cere__objects"), args.extraction_lvl), stderr=subprocess.STDOUT, shell=True))
  except subprocess.CalledProcessError as err:
    logger.critical(str(err))
    logger.critical(err.output)
    return False
  logger.info("Hybrid compiled successfully")
  return True
