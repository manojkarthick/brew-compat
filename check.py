import csv
import logging
import os
import re
import sys
from argparse import ArgumentParser
from collections import namedtuple
from typing import List, Dict

import requests
from prettytable import PrettyTable  # type: ignore

logger = logging.getLogger("brew-compat")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

macos_versions = ["arm64_big_sur", "big_sur", "catalina", "mojave", "high_sierra", "sierra", "el_capitan"]
support_matrix = {
    # Big Sur is denoted as either 11.0 or 10.16 in various places
    ">=11.0": ["arm64big_sur", "big_sur"],
    ">=10.16": ["arm64big_sur", "big_sur"],
    ">=10.15": ["arm64big_sur", "big_sur", "catalina"],
    ">=10.14": ["arm64big_sur", "big_sur", "catalina", "mojave"],
    ">=10.13": ["arm64big_sur", "big_sur", "catalina", "mojave", "high_sierra"],
    ">=10.12": ["arm64big_sur", "big_sur", "catalina", "mojave", "high_sierra", "sierra"],
    ">=10.11": ["arm64big_sur", "big_sur", "catalina", "mojave", "high_sierra", "el_capitan"]
}
metadata = {
    "brew": "https://formulae.brew.sh/api/formula",
    "cask": "https://formulae.brew.sh/api/cask"
}
pattern = r'\"(.+?)\"'
export_file = "compatibility.csv"
SupportStatus = namedtuple("SupportStatus", ["kind", "formula_name", "status"])


def get_formulae(brewfile: str, formula_type: str) -> List[str]:
    """
    Get a list of formulae from the Brewfile. Can support brew and cask.
    :param brewfile: Path to the brewfile
    :param formula_type: Type of formula
    :return: Formulae of the given type
    """
    # if the formula type is not supported, exit immediately.
    if formula_type not in metadata.keys():
        logger.error("Unsupported formula type: {}. Exiting...".format(formula_type))
        sys.exit(1)

    formulae = []
    with open(brewfile, "r") as f:
        for line in f.readlines():
            if line.startswith(formula_type):
                # get the formula name from the Brewfile
                match = re.search(pattern, line)
                if match is not None:
                    formula_name = match.group().replace('"', "")
                    formulae.append(formula_name)
    return formulae


def get_supported_versions(data: Dict, formula_type: str) -> List[str]:
    """
    Get list of supported macOS versions for a formula
    :param data: the response from homebrew API
    :param formula_type: Type of formula
    :return: List of versions
    """
    versions = []
    if formula_type == "brew":
        # the `files` dict contains a bottle file for each macOS version
        # in case no bottle is present, homebrew would try to compile the formula
        # on the local machine - which may or may not succeed
        versions = data["bottle"]["stable"]["files"].keys()
    if formula_type == "cask":
        # the `depends_on` info tells what versions of macOS this cask depends on
        # the `support_matrix` dictionary lists out all the possibilities for each version
        depends_on = ">={}".format(data["depends_on"]["macos"][">="][0])
        versions = support_matrix[depends_on]
    return versions


def get_type(formula_type: str) -> str:
    """
    Get the kind of homebrew resource the formula refers to
    :param formula_type: Type of formula
    :return: Kind of Resource: either of Bottle, Application or unknown
    """
    kind = "Unknown"
    if formula_type == "brew":
        kind = "Bottle"
    if formula_type == "cask":
        kind = "Application"
    return kind


def get_status(formulae: List[str], formula_type: str, macos_version: str) -> List[SupportStatus]:
    """
    Check and return the support status of the formula from the homebrew API
    :param formulae: Name of the formula
    :param formula_type: Type of the formula
    :param macos_version: macOS version identifier
    :return: Return a List of tuples of the form (formula, status)
    """
    statuses = []
    kind = get_type(formula_type)
    for formula_name in formulae:
        # choose the right endpoint based on the formula type
        endpoint = "{}/{}.json".format(metadata.get(formula_type), formula_name)
        logger.debug("Querying: {}".format(endpoint))
        response = requests.get(endpoint)
        # if HTTP 200, then we found the formula on the API
        if response.status_code == 200:
            content = response.json()
            try:
                supported_versions = get_supported_versions(content, formula_type)
                logger.debug("Supported versions for {} are: {}".format(formula_name, supported_versions))
                if macos_version in supported_versions:
                    status = SupportStatus(kind=kind, formula_name=formula_name, status="Supported")
                else:
                    status = SupportStatus(kind=kind, formula_name=formula_name, status="Unsupported")
            except KeyError:
                logger.debug("Could not get details for formula: {}".format(formula_name))
                status = SupportStatus(kind=kind, formula_name=formula_name, status="No info")
        # if the formula is not found, the API returns a HTTP 404
        else:
            logger.warning("Unknown formula: {}".format(formula_name))
            status = SupportStatus(kind=kind, formula_name=formula_name, status="Unknown")
        statuses.append(status)
    return statuses


def display(support_statuses: List[SupportStatus]):
    """
    Display the statuses on stdout
    :param support_statuses: Status of formulae as returned by the check method
    :return:
    """
    tbl = PrettyTable()
    tbl.field_names = ["Kind", "Formula", "Status"]
    for support_status in support_statuses:
        tbl.add_row([support_status.kind, support_status.formula_name, support_status.status])
    tbl.align = "l"
    print(tbl)


def export(support_statuses: List[SupportStatus]):
    """
    Write the statuses to a CSV file
    :param support_statuses: Status of formulae as returned by the check method
    :return:
    """
    with open(export_file, "w") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["kind", "formula", "status"])
        for support_status in support_statuses:
            writer.writerow([support_status.kind, support_status.formula_name, support_status.status])


def cli():
    parser = ArgumentParser(description="Check compatibility of brew formula against macOS versions")
    parser.add_argument("brewfile", nargs="?", type=str, default=os.path.join(os.getcwd(), "Brewfile"),
                        help="Path to Brewfile")
    parser.add_argument("--macos-version", type=str, default="big_sur", choices=macos_versions,
                        help="macOS version")
    parser.add_argument("--verbose", action="store_true", help="Use verbose logging")
    parser.add_argument("--export", action="store_true", help="Export results in CSV format")
    args = parser.parse_args()

    if args.verbose:
        ch.setLevel(logging.DEBUG)

    if not os.path.exists(args.brewfile):
        logger.error("Brewfile does not exist: {}. Exiting".format(args.brewfile))
        sys.exit(1)

    logger.info("Brewfile exists!")

    logger.info("Using Brewfile: {}".format(args.brewfile))
    logger.info("Checking compatibility for {}".format(args.macos_version))
    logger.info("Getting details from Homebrew API for formulae, hold on...")
    core_formulae = get_formulae(args.brewfile, "brew")
    cask_formulae = get_formulae(args.brewfile, "cask")
    logger.debug("The core formulae are: [{}]".format(", ".join(core_formulae)))
    logger.debug("The cask formulae are: [{}]".format(", ".join(cask_formulae)))
    result = get_status(core_formulae, "brew", args.macos_version)
    cask_result = get_status(cask_formulae, "cask", args.macos_version)
    result.extend(cask_result)

    display(result)

    if args.export:
        export(result)
        logger.info("Exported results to {}".format(export_file))

    logger.debug("FIN.")
